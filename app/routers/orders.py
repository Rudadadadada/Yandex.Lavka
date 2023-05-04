from fastapi import APIRouter, Request
from starlette import status

from app.schemas.__schemes import OrderModel, OrdersModel
from app.limiter import limiter
from app.view.orders import post_orders, get_order_by_id, get_all_orders

order = APIRouter()


@order.post(
    "/orders",
    status_code=status.HTTP_200_OK,
    description='Receives a list with order data in json format',
    name='Create order'
)
@limiter.limit("10/second")
async def create_orders(request: Request, orders: OrdersModel):
    OrdersModel.validate(orders)
    await post_orders(orders)


@order.get(
    "/orders/{order_id}",
    status_code=status.HTTP_200_OK,
    description='Returns order info by id',
    name='Get order',
)
@limiter.limit("10/second")
async def get_order(request: Request, order_id: int) -> OrderModel:
    return await get_order_by_id(order_id)


@order.get(
    "/orders",
    status_code=status.HTTP_200_OK,
    description='Returns all orders info',
    name='Get orders',
)
@limiter.limit("10/second")
async def get_orders(request: Request, offset: int = 0, limit: int = 1) -> OrdersModel:
    return await get_all_orders(offset, limit)

# @order.post(
#     "/orders/complete",
#     status_code=status.HTTP_200_OK,
#     description='Receives a list with completed order data in json format',
#     name='Complete order'
# )
# async def complete_order(completed_orders: List[CompletedOrderModel]):
#     # request = await request.json()
#     return None
