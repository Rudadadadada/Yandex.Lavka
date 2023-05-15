from datetime import datetime, timedelta
from typing import List, Optional
import pytz
from app.utils.time import HH_MM

from fastapi import HTTPException
from pydantic import BaseModel, validator
from starlette import status


class PostOrderModel(BaseModel):
    weight: int
    region: int
    delivery_hours: List[str]
    cost: int

    @validator('weight')
    @classmethod
    def weight_validator(cls, weight):
        if weight <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return weight

    @validator('region')
    @classmethod
    def region_validator(cls, region):
        if region <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return region

    @validator('delivery_hours')
    @classmethod
    def delivery_hours_validator(cls, delivery_hours):
        delivery_hours = set(delivery_hours)
        for cur_dh in delivery_hours:
            data = cur_dh.split('-')
            if cur_dh.count('-') != 1:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

            for time in data:
                try:
                    datetime.strptime(time, HH_MM)
                    hours, mintues = time.split(':')
                    if len(hours) != 2 or len(mintues) != 2:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
            start_time = datetime.strptime(data[0], HH_MM)
            end_time = datetime.strptime(data[1], HH_MM)
            if start_time > end_time:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return delivery_hours

    @validator('cost')
    @classmethod
    def cost_validator(cls, cost):
        if cost <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return cost


class PostOrdersModel(BaseModel):
    orders: List[PostOrderModel]

    @validator('orders')
    @classmethod
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
    @classmethod
    def complete_time_validator(cls, complete_time):
        utc = pytz.UTC
        if not complete_time <= datetime.now().replace(tzinfo=utc) + timedelta(days=2):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return complete_time


class CompleteOrdersModel(BaseModel):
    complete_info: List[CompleteOrderModel]

    @validator('complete_info')
    @classmethod
    def complete_info_validator(cls, complete_info):
        for complete_order in complete_info:
            CompleteOrderModel.validate(complete_order)
        return complete_info
