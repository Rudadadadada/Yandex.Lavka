from datetime import datetime, timezone
import pytz

from fastapi import HTTPException
from pydantic import BaseModel, validator
from typing import List, Optional

from starlette import status

from app.schemas.__couriers import PostCourierModel, GetCourierModel


class OrderIds(BaseModel):
    order_ids: List[int]


class PostOrderModel(BaseModel):
    weight: int
    region: int
    delivery_hours: List[str]
    cost: int

    @validator('weight')
    def weight_validator(cls, weight):
        if weight <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Incorrect weight: {weight}. Value should be above zero")
        return weight

    @validator('region')
    def region_validator(cls, region):
        if region <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Incorrect region: {region}. Value should be above zero")
        return region

    @validator('delivery_hours')
    def delivery_hours_validator(cls, delivery_hours):
        for cur_dh in delivery_hours:
            if cur_dh.count('-') != 1:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Incorrect delivery hours format: quantity of '-' is not equal to one")

            data = cur_dh.split('-')
            start_time = 0
            end_time = 0

            for time in data:
                identifier = 'start time' if data.index(time) == 0 else 'end time'
                if time.count(':') != 1:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=f"Incorrect delivery hours format in {identifier}: "
                                               f"quantity of ':' is not equal to one")
                separated_time = time.split(':')
                try:
                    hours = int(separated_time[0])
                    minutes = int(separated_time[1])
                    if identifier[0] == 's':
                        start_time += hours * 60 + minutes
                    else:
                        end_time += hours * 60 + minutes
                except ValueError:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=f"Incorrect delivery hours format in {identifier}: "
                                               f"separation hours and minutes done incorrectly."
                                               f" hours = {data[0]}, minutes = {data[1]}")
                if not 0 <= hours <= 23:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=f"Incorrect delivery hours format in {identifier}: "
                                               f"{hours} out of hours range")
                if not 0 <= minutes <= 59:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=f"Incorrect delivery hours format in {identifier}: "
                                               f"{minutes} out of minutes range")
            if start_time >= end_time:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Incorrect delivery hours values: start time greater then end time")
        return delivery_hours

    @validator('cost')
    def cost_validator(cls, cost):
        if cost <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Incorrect cost: {cost}. Value should be above zero")
        return cost


class PostOrdersModel(BaseModel):
    orders: List[PostOrderModel]

    @validator('orders')
    def orders_validator(cls, orders):
        for order in orders:
            PostOrderModel.validate(order)
        return orders


class GetOrderModel(BaseModel):
    order_id: int
    weight: int
    region: int
    delivery_hours: List[str]
    cost: int
    completed_time: Optional[datetime] = None


class GetOrdersModel(BaseModel):
    orders: List[GetOrderModel]


class CompleteOrderModel(BaseModel):
    courier_id: int
    order_id: int
    complete_time: datetime

    @validator('complete_time')
    def complete_time_validator(cls, complete_time):
        utc = pytz.UTC
        date = datetime.fromisoformat(complete_time[:-1]).astimezone(timezone.utc)
        if not date.replace(tzinfo=utc) <= datetime.now().replace(tzinfo=utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Incorrect date: {date}. Value should be less than current one")
        return date


class CompleteOrdersModel(BaseModel):
    complete_info: List[CompleteOrderModel]

    @validator('complete_info')
    def complete_info_validator(cls, complete_info):
        for complete_order in complete_info:
            CompleteOrderModel.validate(complete_order)
        return complete_info

