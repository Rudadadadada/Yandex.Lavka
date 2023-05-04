from fastapi import HTTPException
from starlette import status

from app.database.__models import Order, OrderDeliveryHour
from app.database.db_session import create_session
from app.schemas.__schemes import OrdersModel, OrderModel
from app.utils.time import time_to_string


async def post_orders(orders: OrdersModel):
    session = create_session()

    for order in orders.orders:
        new_order = Order(weight=order.weight, region=order.region, cost=order.cost)
        session.add(new_order)
        session.commit()

        for cur_dh in order.delivery_hours:
            separated_dh = cur_dh.split('-')
            start_time = separated_dh[0]
            end_time = separated_dh[1]

            new_dh = OrderDeliveryHour(order_id=new_order.id, start_time=start_time, end_time=end_time)
            session.add(new_dh)
            session.commit()


async def get_order_by_id(order_id: int) -> OrderModel:
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

    order_info['weight'] = order_weight
    order_info['region'] = order_region
    order_info['delivery_hours'] = order_delivery_hours
    order_info['cost'] = order_cost

    return OrderModel.parse_obj(order_info)


async def get_all_orders(offset: int = 0, limit: int = 1) -> OrdersModel:
    session = create_session()
    orders_info = {'orders': []}

    orders_data = list(session.query(Order.id, Order.weight, Order.region, Order.cost).
                       filter(offset <= Order.id, Order.id < offset + limit))
    delivery_hours_data = list(map(lambda data: (data[0], time_to_string([data[1], data[2]])),
                                   session.query(OrderDeliveryHour.order_id,
                                                 OrderDeliveryHour.start_time,
                                                 OrderDeliveryHour.end_time).
                                   filter(offset <= OrderDeliveryHour.order_id,
                                          OrderDeliveryHour.order_id < offset + limit)))
    session.close()

    for order in orders_data:
        order_info = {}

        order_delivery_hours = list(map(lambda data: data[1],
                                        filter(lambda data: data[0] == order.id, delivery_hours_data)))

        order_info['weight'] = order.weight
        order_info['region'] = order.region
        order_info['delivery_hours'] = order_delivery_hours
        order_info['cost'] = order.cost

        orders_info['orders'].append(order_info)

    return OrdersModel.parse_obj(orders_info)
