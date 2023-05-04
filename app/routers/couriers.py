from fastapi import APIRouter, Request
from starlette import status

from app.schemas.__schemes import CourierModel, CouriersModel
from app.view.couriers import post_couriers, get_courier_by_id, get_all_couriers
from app.limiter import limiter

courier = APIRouter()


@courier.post(
    "/couriers",
    status_code=status.HTTP_200_OK,
    description='Receives a list with courier data in json format',
    name='Create couriers'
)
@limiter.limit("10/second")
async def create_couriers(request: Request, couriers: CouriersModel):
    CouriersModel.validate(couriers)
    await post_couriers(couriers)


@courier.get(
    "/couriers/{courier_id}",
    status_code=status.HTTP_200_OK,
    description='Returns courier info by id',
    name='Get courier'
)
@limiter.limit("10/second")
async def get_courier(request: Request, courier_id: int) -> CourierModel:
    return await get_courier_by_id(courier_id)


@courier.get(
    "/couriers",
    status_code=status.HTTP_200_OK,
    description='Returns all couriers info',
    name='Get couriers',
)
@limiter.limit("10/second")
async def get_couriers(request: Request, offset: int = 0, limit: int = 1) -> CouriersModel:
    return await get_all_couriers(offset, limit)
