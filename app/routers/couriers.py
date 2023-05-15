from typing import Annotated

from fastapi import APIRouter, Request, Query, Path
import datetime

from starlette import status

from app.schemas.__couriers import PostCouriersModel, GetCourierModel, GetCouriersModel, GetMetaInfoModel
from app.schemas.__assignment import AssignmentInfoModel
from app.view.assignment import get_all_assignment_info
from app.view.couriers import post_couriers, get_courier_by_id, get_all_couriers, get_meta_info
from app.limiter import limiter, LIMIT

courier = APIRouter(tags=['courier-controller'])


@courier.post(
    "/couriers",
    responses={
        200: {"model": GetCouriersModel, "description": 'ok'},
        400: {"model": dict, "description": 'bad request'},
        429: {"model": dict}
    },
    status_code=status.HTTP_200_OK,
    description='Receives a list with courier data in json format',
    name='Create couriers'
)
@limiter.limit("1/second")
async def create_couriers(request: Request, couriers: PostCouriersModel) -> GetCouriersModel | None:
    PostCouriersModel.validate(couriers)
    return await post_couriers(couriers)


@courier.get(
    "/couriers/{courier_id}",
    responses={
        200: {"model": GetCourierModel, "description": 'ok'},
        400: {"model": dict, "description": 'bad request'},
        404: {"model": dict, "description": 'not found'},
    },
    status_code=status.HTTP_200_OK,
    description='Returns courier info by id',
    name='Get courier'
)
@limiter.limit(LIMIT)
async def get_courier(request: Request,
                      courier_id: Annotated[int, Path(description='Courier identifier')]
                      ) -> GetCourierModel | None:
    return await get_courier_by_id(courier_id)


@courier.get(
    "/couriers",
    responses={
        200: {"model": GetCouriersModel, "description": 'ok'},
        400: {"model": dict, "description": 'bad request'}
    },
    status_code=status.HTTP_200_OK,
    description='Returns all couriers info',
    name='Get couriers',
)
@limiter.limit(LIMIT)
async def get_couriers(request: Request,
                       limit:
                       Annotated[int, Query(
                           description='Максимальное количество курьеров в выдаче. '
                                       'Если параметр не передан, то значение по умолчанию равно 1.',
                           example=1)] = 1,
                       offset:
                       Annotated[int, Query(
                           description='Количество курьеров, которое нужно пропустить для отображения '
                                       'текущей страницы. Если параметр не передан, то значение '
                                       'по умолчанию равно 0.',
                           example=0)] = 0
                       ) -> GetCouriersModel | None:
    return await get_all_couriers(limit, offset)


@courier.get(
    "/couriers/meta-info/{courier_id}",
    responses={
        200: {"model": GetMetaInfoModel, "description": 'ok'}
    },
    status_code=status.HTTP_200_OK,
    description='Returns courier earnings and rating',
    name='Get courier meta-info'
)
@limiter.limit(LIMIT)
async def get_courier_meta_info(request: Request,
                                courier_id: Annotated[int, Path(description='Courier identifier')],
                                start_date: Annotated[datetime.date, Query(description='Rating calculation start date',
                                                                           example='2023-01-20')],
                                end_date: Annotated[datetime.date, Query(description='Rating calculation end date',
                                                                         example='2023-01-21')]
                                ) -> GetMetaInfoModel | None:
    return await get_meta_info(courier_id, start_date, end_date)


@courier.get(
    "/courier/assignments",
    responses={
        200: {"model": AssignmentInfoModel, "description": 'ok'},
        400: {"model": dict, "description": 'bad request'}
    },
    status_code=status.HTTP_200_OK,
    description='Returns assignment info',
    name='Assignment info'
)
@limiter.limit(LIMIT)
async def get_assignment_info(request: Request,
                              date:
                              Annotated[
                                  datetime.date,
                                  Query(description='Дата распределения заказов. '
                                                    'Если не указана, то используется текущий день')] =
                              datetime.date.today(),
                              courier_id:
                              Annotated[
                                  int,
                                  Query(
                                      description='Идентификатор курьера для получения списка распредленных заказов. '
                                                  'Если не указан, возвращаются данные по всем курьерам.')] = None
                              ) -> AssignmentInfoModel | None:
    return await get_all_assignment_info(date, courier_id)
