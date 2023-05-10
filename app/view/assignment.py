import datetime

from fastapi import HTTPException
from starlette import status

from app.database.__models import Order, OrderDeliveryHour, DistributedOrders, CourierWorkingHour, Courier, \
    CourierRegion, Region
from app.database.db_session import create_session
from app.schemas.__orders import OrderIds, PostOrdersModel, GetOrderModel, GetOrdersModel, CompleteOrdersModel
from app.utils.time import time_to_string, get_minutes_from_string, split_time
from app.view.couriers import get_all_couriers
from app.view.orders import get_all_orders

COURIER_ORDER_GROUP = {}
COURIER_TYPES_WEIGHT = {'FOOT': [2, 10], 'BIKE': [4, 20], 'AUTO': [7, 40]}


def metric(cost, weight, delivery_hours):
    total_time = 0
    for dh in delivery_hours:  # count of dh
        start_order_time, end_order_time = split_time(dh)
        start_order_time_minutes = get_minutes_from_string(start_order_time)
        end_order_time_minutes = get_minutes_from_string(end_order_time)

        total_time += (end_order_time_minutes - start_order_time_minutes) / 3600

    return cost * weight + total_time


# optimized greed by heuristic and two pointers
async def greedy(couriers, type_params):
    orders_in_group, weight = type_params
    for courier in couriers.couriers:  # n where n is count of couriers
        courier_groups = []
        for wh in courier.working_hours:  # count of wh
            possible_orders = await get_all_orders(limit=100, offset=0, time_interval=wh,
                                                   regions=courier.regions, weight=weight)

            possible_orders = sorted(possible_orders.orders,
                                     key=lambda order: metric(order.cost, order.weight, order.delivery_hours))

            # здесь должен быть норм два указателя
            i, j = 0, len(possible_orders) - 1
            cur_weight = weight

            while i < j:
                if cur_weight - possible_orders[i].weight >= 0:
                    if cur_weight - possible_orders[i].weight - possible_orders[j].weight >= 0:
                        courier_groups.append([possible_orders[i], possible_orders[j]])
                        i += 1
                        j -= 1
                    else:
                        j -= 1
                else:
                    i += 1
        COURIER_ORDER_GROUP[courier.courier_id] = courier_groups


async def distribute_orders():
    session = create_session()

    number_foot_couriers = session.query(Courier).filter(Courier.courier_type == "FOOT").count()
    number_bike_couriers = session.query(Courier).filter(Courier.courier_type == "BIKE").count()
    number_auto_couriers = session.query(Courier).filter(Courier.courier_type == "AUTO").count()

    for courier_type in COURIER_TYPES_WEIGHT:  # 3 times
        couriers = await get_all_couriers(limit=10, offset=0, courier_type=courier_type)
        await greedy(couriers, COURIER_TYPES_WEIGHT[courier_type])

    session.commit()
