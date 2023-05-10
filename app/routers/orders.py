from fastapi import APIRouter, Request
from starlette import status

from app.schemas.__orders import OrderIds, PostOrdersModel, GetOrderModel, GetOrdersModel, CompleteOrdersModel
from app.limiter import limiter
from app.view.assignment import distribute_orders
from app.view.orders import post_orders, get_order_by_id, get_all_orders, post_complete_orders

order = APIRouter(tags=['order-controller'])


@order.post(
    "/orders",
    status_code=status.HTTP_200_OK,
    description='Receives a list with order data in json format',
    name='Create order'
)
@limiter.limit("10/second")
async def create_orders(request: Request, orders: PostOrdersModel) -> OrderIds:
    PostOrdersModel.validate(orders)
    return await post_orders(orders)


@order.get(
    "/orders/{order_id}",
    status_code=status.HTTP_200_OK,
    description='Returns order info by id',
    name='Get order',
)
@limiter.limit("10/second")
async def get_order(request: Request, order_id: int) -> GetOrderModel:
    return await get_order_by_id(order_id)


@order.get(
    "/orders",
    status_code=status.HTTP_200_OK,
    description='Returns all orders info',
    name='Get orders',
)
@limiter.limit("10/second")
async def get_orders(request: Request, limit: int = 1, offset: int = 0) -> GetOrdersModel:
    return await get_all_orders(limit, offset)


@order.post(
    "/orders/complete",
    status_code=status.HTTP_200_OK,
    description='Receives a list with completed order data in json format',
    name='Complete order'
)
@limiter.limit("10/second")
async def complete_orders(request: Request, complete_info: CompleteOrdersModel):
    await post_complete_orders(complete_info)


@order.post(
    "/orders/assign",
    status_code=status.HTTP_201_CREATED,
    description='Distribute orders between couriers',
    name='Distribution of orders'
)
@limiter.limit("10/second")
async def assign_orders(request: Request):
    await distribute_orders()
