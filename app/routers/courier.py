from fastapi import APIRouter, Request
from starlette import status

courier = APIRouter()


@courier.post(
    "/couriers",
    status_code=status.HTTP_200_OK,
    description='Receives a list with courier data in json format',
    name='Create courier'
)
async def create_courier(request: Request):
    request = await request.json()
    return None


@courier.get(
    "/couriers/{courier_id}",
    status_code=status.HTTP_200_OK,
    description='Returns courier info by id',
    name='Get courier',
)
async def get_courier():
    return None


@courier.get(
    "/couriers",
    status_code=status.HTTP_200_OK,
    description='Returns all couriers info',
    name='Get couriers',
)
async def get_couriers(offset: int = 0, limit: int = 1):
    return None
