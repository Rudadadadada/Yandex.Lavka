from fastapi import APIRouter
from starlette import status

from app.schemas.__schemes import CourierModel, CouriersModel
from app.view.couriers import post_couriers, get_courier_by_id, get_all_couriers

courier = APIRouter()


@courier.post(
    "/couriers",
    status_code=status.HTTP_200_OK,
    description='Receives a list with courier data in json format',
    name='Create couriers'
)
async def create_courier(couriers: CouriersModel):
    CouriersModel.validate(couriers)
    await post_couriers(couriers)


@courier.get(
    "/couriers/{courier_id}",
    status_code=status.HTTP_200_OK,
    description='Returns courier info by id',
    name='Get courier',
)
async def get_courier(courier_id: int) -> CourierModel:
    courier_info = await get_courier_by_id(courier_id)
    return CourierModel.parse_obj(courier_info)


@courier.get(
    "/couriers",
    status_code=status.HTTP_200_OK,
    description='Returns all couriers info',
    name='Get couriers',
)
async def get_couriers(offset: int = 0, limit: int = 1) -> CouriersModel:
    couriers_info = await get_all_couriers()
    return CouriersModel.parse_obj(couriers_info)