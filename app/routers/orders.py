from fastapi import APIRouter, Request
from starlette import status

order = APIRouter()


@order.post(
    "/orders",
    status_code=status.HTTP_200_OK,
    description='Receives a list with order data in json format',
    name='Create order'
)
async def create_order(request: Request):
    request = await request.json()
    return None


@order.get(
    "/orders/{order_id}",
    status_code=status.HTTP_200_OK,
    description='Returns order info by id',
    name='Get order',
)
async def get_order():
    return None


@order.get(
    "/orders",
    status_code=status.HTTP_200_OK,
    description='Returns all orders info',
    name='Get orders',
)
async def get_orders():
    return None


@order.post(
    "/orders/complete",
    status_code=status.HTTP_200_OK,
    description='Receives a list with completed order data in json format',
    name='Complete order'
)
async def complete_order(request: Request):
    request = await request.json()
    return None
