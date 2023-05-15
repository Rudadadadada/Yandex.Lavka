import datetime
from typing import List

from fastapi import HTTPException
from starlette import status

from app.database.__models import Order, DistributedOrders, Courier
from app.database.db_session import create_session
from app.schemas.__couriers import GetCouriersModel
from app.schemas.__orders import GetOrderModel
from app.schemas.__assignment import AssignmentInfoModel
from app.utils.time import split_time, HH_MM
from app.view.couriers import get_all_couriers, get_courier_by_id
from app.view.orders import get_all_orders, get_order_by_id

COURIER_ASSIGNMENT_INFO = {'FOOT': [2, 10, 25, 10], 'BIKE': [4, 20, 12, 8], 'AUTO': [7, 40, 8, 4]}

COURIER_ORDER_GROUP = {}
ORDERS_IN_PROCESS = {}


# чем больше интервал, тем менее срочный заказ,
# чем больше стоимость, тем менее срочный заказ
def metric(cost: int, wh: str, dh: str) -> float:
    courier_start_time = split_time(wh, to_intervals=True)[0]
    order_end_time = split_time(dh, to_intervals=True)[1]

    return cost * (order_end_time - courier_start_time) / datetime.timedelta(minutes=3600)


# оптимизированный жадный алгоритм при помощи эвристики и двух указателей
async def greedy(couriers: GetCouriersModel, type_params: List[int], number_of_all_orders: int):
    orders_in_group, weight, first_time_order, rest_time_orders = type_params

    # подготавливаем параметры
    orders_in_group -= 1
    first_time_order = datetime.timedelta(minutes=first_time_order)
    rest_time_orders = datetime.timedelta(minutes=rest_time_orders)

    for courier in couriers.couriers:
        courier_groups = []
        for wh in courier.working_hours:
            courier_start_time, courier_end_time = split_time(wh, to_intervals=True)
            # за такое время работы курьера нельзя доставить ни один заказ
            if courier_end_time - courier_start_time < first_time_order:
                continue

            possible_orders = await get_all_orders(limit=number_of_all_orders,
                                                   offset=0, time_interval=wh,
                                                   regions=courier.regions, weight=weight)

            possible_orders_with_duplicates = []

            for order in possible_orders.orders:
                if ORDERS_IN_PROCESS.get(order.order_id) == 1:
                    continue
                if order.completed_time is not None:
                    continue
                for dh in order.delivery_hours:
                    # курьер не успеет доставить заказ, даже если начнет работать сразу
                    order_start_time, order_end_time = split_time(dh, to_intervals=True)
                    if order_end_time - courier_start_time < first_time_order:
                        continue

                    order_data = {'order_id': order.order_id,
                                  'weight': order.weight,
                                  'region': order.region,
                                  'delivery_hours': [dh],
                                  'cost': order.cost,
                                  'completed_time': None}
                    possible_orders_with_duplicates.append(GetOrderModel.parse_obj(order_data))

            possible_orders_with_duplicates = sorted(possible_orders_with_duplicates,
                                                     key=lambda data: metric(data.cost, wh, data.delivery_hours[0]))

            i, j = 0, len(possible_orders_with_duplicates) - 1

            cur_time = courier_start_time
            cur_weight = weight
            courier_group = []

            while i < j:
                # распределение первого заказа в группе

                # скипаем уже взятые заказы
                while i < j and ORDERS_IN_PROCESS.get(possible_orders_with_duplicates[i].order_id) == 1:
                    i += 1

                first_order = possible_orders_with_duplicates[i]

                # проверка на то, что заказ уже находится в исполнении
                if ORDERS_IN_PROCESS.get(first_order.order_id) == 1:
                    i += 1
                    continue

                # проверка веса
                if cur_weight - first_order.weight < 0:
                    i += 1
                    continue

                # проверки подходимости по времени
                first_order_start_time, first_order_end_time = \
                    split_time(first_order.delivery_hours[0], to_intervals=True)

                if first_order_start_time <= cur_time + first_time_order <= first_order_end_time:
                    if cur_time + first_time_order > courier_end_time:
                        i += 1
                        continue
                    cur_time += first_time_order
                    courier_group.append([cur_time, first_order])
                    cur_weight -= first_order.weight
                    i += 1
                    ORDERS_IN_PROCESS[first_order.order_id] = 1
                elif first_order_start_time > cur_time + first_time_order:
                    if first_order_start_time - first_time_order > courier_end_time:
                        i += 1
                        continue
                    cur_time = first_order_start_time - first_time_order
                    continue
                else:
                    i += 1
                    continue

                # счетчик последующих заказов
                count = 0
                # набираем группу с количеством - 1, потому что первый заказ уже взяли
                while i < j and count < orders_in_group:
                    # скипаем все те заказы, которые уже взяты
                    while i < j and ORDERS_IN_PROCESS.get(possible_orders_with_duplicates[j].order_id) == 1:
                        j -= 1
                    if j == i:
                        break
                    next_order = possible_orders_with_duplicates[j]

                    # проверка на то, что заказ находится в исполнении
                    if ORDERS_IN_PROCESS.get(next_order.order_id) == 1:
                        j -= 1
                        continue

                    # весовая проверка
                    if cur_weight - next_order.weight < 0:
                        j -= 1
                        if j == i:
                            break
                        continue

                    next_order_start_time, next_order_end_time = split_time(next_order.delivery_hours[0],
                                                                            to_intervals=True)

                    # временная проверка
                    if next_order_start_time <= cur_time + rest_time_orders <= next_order_end_time:
                        if cur_time + rest_time_orders > courier_end_time:
                            j -= 1
                            if j == i:
                                break
                            continue
                        cur_time += rest_time_orders
                        courier_group.append([cur_time, next_order])
                        cur_weight -= next_order.weight
                        j -= 1
                        ORDERS_IN_PROCESS[next_order.order_id] = 1
                    elif next_order_start_time > cur_time + rest_time_orders:
                        if next_order_start_time - rest_time_orders > courier_end_time:
                            j -= 1
                            if j == i:
                                break
                            continue
                        cur_time = next_order_start_time - rest_time_orders
                        continue
                    else:
                        j -= 1
                        if j == i:
                            break
                        continue
                    count += 1
                courier_groups.append(courier_group)
                courier_group = []
                cur_weight = weight

                if j - i == 1:
                    break
                i, j = 0, len(possible_orders_with_duplicates) - 1
            COURIER_ORDER_GROUP[courier.courier_id] = courier_groups


async def distribute_orders() -> AssignmentInfoModel:
    session = create_session()

    number_of_all_orders = session.query(Order).count()

    for courier_type in COURIER_ASSIGNMENT_INFO:  # 3 times
        number_of_couriers_of_type = list(session.query(Courier).filter(Courier.courier_type == courier_type))
        if number_of_couriers_of_type:
            number_of_couriers_of_type = number_of_couriers_of_type[-1].id
        else:
            number_of_couriers_of_type = 1
        couriers = await get_all_couriers(limit=number_of_couriers_of_type,
                                          offset=0, courier_type=courier_type)
        await greedy(couriers, COURIER_ASSIGNMENT_INFO[courier_type], number_of_all_orders)

    assignment_info = {'date': datetime.date.today(), 'couriers': []}

    for courier in COURIER_ORDER_GROUP.keys():
        courier_info = {'courier_id': courier, 'orders': []}
        group_order_id = 1

        for order_group in COURIER_ORDER_GROUP[courier]:
            order_group_info = {'group_order_id': group_order_id, 'orders': []}
            next_order_cost = 1.0

            for order_data in order_group:
                predictable_time, order = order_data
                predictable_time = predictable_time.time()
                start_time, end_time = split_time(order.delivery_hours[0])

                new_order = DistributedOrders(order_id=order.order_id, courier_id=courier,
                                              group_order_id=group_order_id,
                                              date=datetime.date.today(),
                                              start_time=start_time,
                                              end_time=end_time, predictable_time=predictable_time,
                                              after_fact_time=None,
                                              earnings=order.cost * next_order_cost)
                session.add(new_order)

                next_order_cost = 0.8
                order_info = {'order_id': order.order_id, 'weight': order.weight, 'region': order.region,
                              'delivery_hours': order.delivery_hours, 'cost': order.cost, 'completed_time': None}

                order_group_info['orders'].append(order_info)
            group_order_id += 1

            courier_info['orders'].append(order_group_info)
        assignment_info['couriers'].append(courier_info)

    COURIER_ORDER_GROUP.clear()
    ORDERS_IN_PROCESS.clear()
    session.commit()

    return AssignmentInfoModel.parse_obj(assignment_info)


async def get_all_assignment_info(date: datetime.date = datetime.date.today(),
                                  courier_id: int = None) -> AssignmentInfoModel:
    session = create_session()

    if not date <= datetime.date.today():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    if courier_id:
        try:
            await get_courier_by_id(courier_id)
        except HTTPException:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    assignment_data = session.query(DistributedOrders).filter(DistributedOrders.date == date)
    if courier_id:
        assignment_data = assignment_data.filter(DistributedOrders.courier_id == courier_id)
    assignment_data = list(assignment_data)

    assignment_info = {'date': date, 'couriers': []}

    couriers_info = {}
    if not courier_id:
        for courier in session.query(Courier).all():
            if couriers_info.get(courier.id) is None:
                couriers_info[courier.id] = {'orders': {}}
    else:
        couriers_info[courier_id] = {'orders': {}}

    for entry in assignment_data:
        if couriers_info[entry.courier_id]['orders'].get(entry.group_order_id) is None:
            couriers_info[entry.courier_id]['orders'][entry.group_order_id] = {'orders': {}}

    for entry in assignment_data:
        order_info = await get_order_by_id(entry.order_id)
        if couriers_info[entry.courier_id]['orders'][entry.group_order_id].get(entry.order_id) is None:
            couriers_info[entry.courier_id]['orders'][entry.group_order_id]['orders'][entry.order_id] = \
                {'weight': order_info.weight,
                 'region': order_info.region,
                 'delivery_hours': [entry.start_time.strftime(HH_MM) + '-' + entry.end_time.strftime(HH_MM)],
                 'cost': order_info.cost,
                 'completed_time': order_info.completed_time}

    for courier in couriers_info.keys():
        assignment_info['couriers'].append({'courier_id': courier, 'orders': []})

    for courier in assignment_info['couriers']:
        cur_courier_id = courier['courier_id']
        for group_order_id in couriers_info[cur_courier_id]['orders'].keys():
            courier['orders'].append({'group_order_id': group_order_id, 'orders': []})

    for courier in assignment_info['couriers']:
        cur_courier_id = courier['courier_id']
        for orders in courier['orders']:
            cur_group_order_id = orders['group_order_id']
            for order in couriers_info[cur_courier_id]['orders'][cur_group_order_id]['orders'].keys():
                real_order = couriers_info[cur_courier_id]['orders'][cur_group_order_id]['orders'][order]
                orders['orders'].append(
                    {'order_id': order, 'weight': real_order['weight'], 'region': real_order['region'],
                     'delivery_hours': real_order['delivery_hours'], 'cost': real_order['cost'],
                     'completed_time': real_order['completed_time']})

    return AssignmentInfoModel.parse_obj(assignment_info)
