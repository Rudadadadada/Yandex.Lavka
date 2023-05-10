from fastapi import HTTPException
from starlette import status

from app.database.__models import Order, OrderDeliveryHour, DistributedOrders
from app.database.db_session import create_session
from app.schemas.__orders import OrderIds, PostOrdersModel, GetOrderModel, GetOrdersModel, CompleteOrdersModel
from app.utils.time import time_to_string, split_time


async def post_orders(orders: PostOrdersModel) -> OrderIds:
    session = create_session()

    order_ids = {'order_ids': []}

    for order in orders.orders:
        new_order = Order(weight=order.weight, region=order.region, cost=order.cost, completed_time=None)
        session.add(new_order)
        session.commit()

        for cur_dh in order.delivery_hours:
            start_time, end_time = split_time(cur_dh)

            new_dh = OrderDeliveryHour(order_id=new_order.id, start_time=start_time, end_time=end_time)
            session.add(new_dh)
            session.commit()

        order_ids['order_ids'].append(new_order.id)

    return OrderIds.parse_obj(order_ids)


async def get_order_by_id(order_id: int) -> GetOrderModel:
    session = create_session()

    order_info = {}

    order_data = list(session.query(Order).filter(Order.id == order_id))
    if not order_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"There is no order with id = {order_id}")
    order_weight = order_data[0].weight
    order_region = order_data[0].region
    order_delivery_hours = list(map(lambda data: time_to_string([data[0], data[1]]),
                                    session.query(OrderDeliveryHour.start_time, OrderDeliveryHour.end_time).
                                    filter(OrderDeliveryHour.order_id == order_id)))
    order_cost = order_data[0].cost

    session.close()

    order_info['order_id'] = order_id
    order_info['weight'] = order_weight
    order_info['region'] = order_region
    order_info['delivery_hours'] = order_delivery_hours
    order_info['cost'] = order_cost
    # need check
    order_info['completed_time'] = None

    return GetOrderModel.parse_obj(order_info)


async def get_all_orders(limit: int = 1, offset: int = 0, time_interval=None, regions=None,
                         weight=None) -> GetOrdersModel:
    session = create_session()

    orders_info = {'orders': []}

    orders_data = session.query(Order.id, Order.weight, Order.region, Order.cost). \
        filter(offset <= Order.id, Order.id < offset + limit)
    if weight and regions:
        orders_data = orders_data.filter(Order.weight <= weight).filter(Order.region.in_(regions))
    orders_data = list(orders_data)

    delivery_hours_data = session.query(OrderDeliveryHour.order_id,
                                        OrderDeliveryHour.start_time,
                                        OrderDeliveryHour.end_time).filter(offset <= OrderDeliveryHour.order_id,
                                                                           OrderDeliveryHour.order_id < offset + limit)
    if time_interval:
        start_time, end_time = split_time(time_interval)
        delivery_hours_data_first_interval = delivery_hours_data.\
            filter(start_time <= OrderDeliveryHour.start_time, OrderDeliveryHour.start_time <= end_time)
        delivery_hours_data_second_interval = delivery_hours_data.\
            filter(start_time <= OrderDeliveryHour.end_time, OrderDeliveryHour.end_time <= end_time)
        delivery_hours_data_third_interval = delivery_hours_data.\
            filter(start_time <= OrderDeliveryHour.start_time, OrderDeliveryHour.end_time <= end_time)

        delivery_hours_data = set(delivery_hours_data_first_interval) | \
                              set(delivery_hours_data_second_interval) | \
                              set(delivery_hours_data_third_interval)
        delivery_hours_data = list(delivery_hours_data)

    delivery_hours_data = list(map(lambda data: (data[0], time_to_string([data[1], data[2]])),
                                   delivery_hours_data))
    session.close()

    for order in orders_data:
        order_info = {}

        order_delivery_hours = list(map(lambda data: data[1],
                                        filter(lambda data: data[0] == order.id, delivery_hours_data)))
        if not order_delivery_hours:
            continue
        order_info['order_id'] = order.id
        order_info['weight'] = order.weight
        order_info['region'] = order.region
        order_info['delivery_hours'] = order_delivery_hours
        order_info['cost'] = order.cost
        # need check
        order_info['completed_time'] = None

        orders_info['orders'].append(order_info)

    return GetOrdersModel.parse_obj(orders_info)


async def post_complete_orders(complete_info: CompleteOrdersModel):
    session = create_session()
    for order_complete_info in complete_info.complete_info:
        order_id = list(
            session.query(DistributedOrders.order_id,
                          DistributedOrders.courier_id).filter(
                DistributedOrders.order_id == order_complete_info.order_id))
        print(order_id)
        if not order_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"There is no order with id = {order_id}")
