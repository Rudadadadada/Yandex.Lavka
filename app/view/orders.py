from typing import List

from fastapi import HTTPException
from starlette import status

from app.database.__models import Order, OrderDeliveryHour, DistributedOrders, CourierWorkingHour
from app.database.db_session import create_session
from app.schemas.__orders import PostOrdersModel, GetOrderModel, GetOrdersModel, CompleteOrdersModel
from app.utils.time import split_time, HH_MM


async def post_orders(orders: PostOrdersModel) -> GetOrdersModel:
    session = create_session()

    orders_info = {'orders': []}

    for order in orders.orders:
        new_order = Order(weight=order.weight, region=order.region, cost=order.cost, completed_time=None)
        session.add(new_order)
        session.commit()

        for cur_dh in order.delivery_hours:
            start_time, end_time = split_time(cur_dh)

            new_dh = OrderDeliveryHour(order_id=new_order.id, start_time=start_time, end_time=end_time)
            session.add(new_dh)
            session.commit()

        orders_info['orders'].append({'order_id': new_order.id, 'weight': order.weight, 'region': order.region,
                                      'delivery_hours': order.delivery_hours, 'cost': order.cost,
                                      'completed_time': None})

    return GetOrdersModel.parse_obj(orders_info)


async def get_order_by_id(order_id: int) -> GetOrderModel:
    if order_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    session = create_session()

    order_data = session.query(Order).filter(Order.id == order_id).all()

    if not order_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    order_weight = order_data[0].weight
    order_region = order_data[0].region
    order_delivery_hours = list(map(lambda data: data[0].strftime(HH_MM) + '-' + data[1].strftime(HH_MM),
                                    session.query(OrderDeliveryHour.start_time, OrderDeliveryHour.end_time).
                                    filter(OrderDeliveryHour.order_id == order_id)))
    order_cost = order_data[0].cost
    order_completed_time = order_data[0].completed_time

    session.close()

    order_info = {'order_id': order_id, 'weight': order_weight, 'region': order_region,
                  'delivery_hours': order_delivery_hours, 'cost': order_cost, 'completed_time': None}
    if order_completed_time is not None:
        order_info['completed_time'] = order_completed_time.isoformat()

    return GetOrderModel.parse_obj(order_info)


async def get_all_orders(limit: int = 1, offset: int = 0, time_interval: str = None, regions: List[int] = None,
                         weight: int = None) -> GetOrdersModel:
    if limit < 1 or offset < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    session = create_session()

    orders_info = {'orders': []}

    orders_data = session.query(Order.id, Order.weight,
                                Order.region, Order.cost, Order.completed_time).filter(offset < Order.id,
                                                                                       Order.id <= offset + limit)

    if weight and regions:
        orders_data = orders_data.filter(Order.weight <= weight).filter(Order.region.in_(regions))
    orders_data = orders_data.all()
    delivery_hours_data = session.query(OrderDeliveryHour.order_id,
                                        OrderDeliveryHour.start_time,
                                        OrderDeliveryHour.end_time).filter(offset < OrderDeliveryHour.order_id,
                                                                           OrderDeliveryHour.order_id <= offset + limit)
    if time_interval:
        start_time, end_time = split_time(time_interval)
        delivery_hours_data_first_interval = delivery_hours_data. \
            filter(start_time <= OrderDeliveryHour.start_time, OrderDeliveryHour.start_time <= end_time)
        delivery_hours_data_second_interval = delivery_hours_data. \
            filter(start_time <= OrderDeliveryHour.end_time, OrderDeliveryHour.end_time <= end_time)
        delivery_hours_data_third_interval = delivery_hours_data. \
            filter(start_time <= OrderDeliveryHour.start_time, OrderDeliveryHour.end_time <= end_time)

        delivery_hours_data = set(delivery_hours_data_first_interval) | set(delivery_hours_data_second_interval) | set(
            delivery_hours_data_third_interval)
        delivery_hours_data = list(delivery_hours_data)
    delivery_hours_data = list(map(lambda data: (data[0], data[1].strftime(HH_MM) + '-' + data[2].strftime(HH_MM)),
                                   delivery_hours_data))
    session.close()

    for order in orders_data:
        order_delivery_hours = list(map(lambda data: data[1],
                                        filter(lambda data: data[0] == order.id, delivery_hours_data)))
        if not order_delivery_hours:
            continue

        order_info = {'order_id': order.id, 'weight': order.weight, 'region': order.region,
                      'delivery_hours': order_delivery_hours, 'cost': order.cost, 'completed_time': None}
        if order.completed_time is not None:
            order_info['completed_time'] = order.completed_time.isoformat()

        orders_info['orders'].append(order_info)

    return GetOrdersModel.parse_obj(orders_info)


async def post_complete_orders(complete_info: CompleteOrdersModel) -> GetOrdersModel:
    session = create_session()

    orders_info = {'orders': []}

    for order_complete_info in complete_info.complete_info:
        order_info_in_all_orders = session.query(Order.id).filter(Order.id == order_complete_info.order_id).all()
        if not order_info_in_all_orders:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        after_fact_time = order_complete_info.complete_time.time()

        order_info = session.query(DistributedOrders.order_id, DistributedOrders.courier_id,
                                   DistributedOrders.start_time, DistributedOrders.end_time,
                                   DistributedOrders.date, DistributedOrders.after_fact_time). \
            filter(DistributedOrders.order_id == order_complete_info.order_id). \
            filter(DistributedOrders.date == order_complete_info.complete_time.date()).all()

        if not order_info:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        order_id, courier_id, order_start_time, order_end_time, order_date, was_delivered = order_info[0]
        if order_complete_info.courier_id != courier_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        courier_start_time, courier_end_time = session.query(CourierWorkingHour.start_time,
                                                             CourierWorkingHour.end_time
                                                             ).filter(CourierWorkingHour.courier_id ==
                                                                      courier_id).all()[0]

        if not courier_start_time <= after_fact_time <= courier_end_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        if not order_start_time <= after_fact_time <= order_end_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        if was_delivered is None:
            session.query(DistributedOrders). \
                filter(DistributedOrders.order_id == order_id). \
                filter(DistributedOrders.date == order_complete_info.complete_time.date()). \
                update({'after_fact_time': order_complete_info.complete_time.isoformat()})
            session.query(Order).filter(Order.id == order_id). \
                filter(DistributedOrders.date == order_complete_info.complete_time.date()). \
                update({'completed_time': order_complete_info.complete_time.isoformat()})

        session.commit()
        orders_info['orders'].append(await get_order_by_id(order_id))

    return GetOrdersModel.parse_obj(orders_info)
