from typing import List

from fastapi import APIRouter, Request
from starlette import status

from app.schemas.__schemes import OrderModel, CompletedOrderModel

order = APIRouter()


@order.post(
    "/orders",
    status_code=status.HTTP_200_OK,
    description='Receives a list with order data in json format',
    name='Create order'
)
async def create_order(orders: List[OrderModel]):
    return None


@order.get(
    "/orders/{order_id}",
    status_code=status.HTTP_200_OK,
    description='Returns order info by id',
    name='Get order',
)
async def get_order() -> OrderModel:
    return None


@order.get(
    "/orders",
    status_code=status.HTTP_200_OK,
    description='Returns all orders info',
    name='Get orders',
)
async def get_orders() -> List[OrderModel]:
    return None


@order.post(
    "/orders/complete",
    status_code=status.HTTP_200_OK,
    description='Receives a list with completed order data in json format',
    name='Complete order'
)
async def complete_order(completed_orders: List[CompletedOrderModel]):
    # request = await request.json()
    return None
