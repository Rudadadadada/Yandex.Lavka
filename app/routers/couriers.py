from fastapi import APIRouter, Request
from starlette import status

from app.schemas.__couriers import CourierIds, PostCouriersModel, GetCourierModel, GetCouriersModel
from app.view.couriers import post_couriers, get_courier_by_id, get_all_couriers
from app.limiter import limiter

courier = APIRouter(tags=['courier-controller'])


@courier.post(
    "/couriers",
    status_code=status.HTTP_200_OK,
    description='Receives a list with courier data in json format',
    name='Create couriers'
)
@limiter.limit("10/second")
async def create_couriers(request: Request, couriers: PostCouriersModel) -> CourierIds:
    PostCouriersModel.validate(couriers)
    return await post_couriers(couriers)


@courier.get(
    "/couriers/{courier_id}",
    status_code=status.HTTP_200_OK,
    description='Returns courier info by id',
    name='Get courier'
)
@limiter.limit("10/second")
async def get_courier(request: Request, courier_id: int) -> GetCourierModel:
    return await get_courier_by_id(courier_id)


@courier.get(
    "/couriers",
    status_code=status.HTTP_200_OK,
    description='Returns all couriers info',
    name='Get couriers',
)
@limiter.limit("10/second")
async def get_couriers(request: Request, limit: int = 1, offset: int = 0) -> GetCouriersModel:
    return await get_all_couriers(limit, offset)
