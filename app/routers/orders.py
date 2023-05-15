from typing import Annotated

from fastapi import APIRouter, Request, Query, Path
from starlette import status

from app.schemas.__orders import PostOrdersModel, GetOrderModel, GetOrdersModel, CompleteOrdersModel
from app.schemas.__assignment import AssignmentInfoModel
from app.view.assignment import distribute_orders
from app.view.orders import post_orders, get_order_by_id, get_all_orders, post_complete_orders
from app.limiter import limiter, LIMIT

order = APIRouter(tags=['order-controller'])


@order.post(
    "/orders",
    responses={
        200: {"model": GetOrdersModel, "description": 'ok'},
        400: {"model": dict, "description": 'bad request'},
    },
    status_code=status.HTTP_200_OK,
    description='Receives a list with order data in json format',
    name='Create order'
)
@limiter.limit(LIMIT)
async def create_orders(request: Request, orders: PostOrdersModel) -> GetOrdersModel | None:
    PostOrdersModel.validate(orders)
    return await post_orders(orders)


@order.get(
    "/orders/{order_id}",
    responses={
        200: {"model": GetOrderModel, "description": 'ok'},
        400: {"model": dict, "description": 'bad request'},
        404: {"model": dict, "description": 'not found'},
    },
    status_code=status.HTTP_200_OK,
    description='Returns order info by id',
    name='Get order',
)
@limiter.limit(LIMIT)
async def get_order(request: Request,
                    order_id: Annotated[int, Path(description='Order identifier')]) -> GetOrderModel | None:
    return await get_order_by_id(order_id)


@order.get(
    "/orders",
    responses={
        200: {"model": GetOrdersModel, "description": 'ok'},
        400: {"model": dict, "description": 'bad request'}
    },
    status_code=status.HTTP_200_OK,
    description='Returns all orders info',
    name='Get orders',
)
@limiter.limit(LIMIT)
async def get_orders(request: Request,
                     limit:
                     Annotated[int, Query(
                         description='Максимальное количество заказов к выдаче. '
                                     'Если параметр не передан, то значение по умолчанию равно 1.',
                         example=1)] = 1,
                     offset:
                     Annotated[int, Query(
                         description='Количество заказов, которое нужно пропустить для отображения '
                                     'текущей страницы. Если параметр не передан, то значение '
                                     'по умолчанию равно 0.',
                         example=0)] = 0
                     ) -> GetOrdersModel | None:
    return await get_all_orders(limit, offset)


@order.post(
    "/orders/complete",
    responses={
        200: {"model": GetOrdersModel, "description": 'ok'},
        400: {"model": dict, "description": 'bad request'},
    },
    status_code=status.HTTP_200_OK,
    description='Receives a list with completed order data in json format',
    name='Complete order'
)
@limiter.limit(LIMIT)
async def complete_orders(request: Request, complete_info: CompleteOrdersModel) -> GetOrdersModel | None:
    return await post_complete_orders(complete_info)


@order.post(
    "/orders/assign",
    responses={
        201: {"model": AssignmentInfoModel, "description": 'ok'},
    },
    status_code=status.HTTP_201_CREATED,
    description='Distribute orders between couriers',
    name='Distribution of orders'
)
@limiter.limit(LIMIT)
async def assign_orders(request: Request) -> AssignmentInfoModel:
    return await distribute_orders()
