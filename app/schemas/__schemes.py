from fastapi import HTTPException
from pydantic import BaseModel, validator
from typing import List

from starlette import status


class CourierModel(BaseModel):
    courier_type: str
    regions: List[int]
    working_hours: List[str]

    @validator('courier_type')
    def courier_type_validator(cls, courier_type):
        if courier_type not in ['FOOT', 'BIKE', 'AUTO']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Incorrect courier_type value: {courier_type} "
                                       f"whereas one of ['BIKE', 'FOOT', 'AUTO'] should be")
        return courier_type

    @validator('regions')
    def regions_validator(cls, regions):
        for region in regions:
            if region <= 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Incorrect region: {region}. Value should be above zero")
        return regions

    @validator('working_hours')
    def working_hours_validator(cls, working_hours):
        for cur_wh in working_hours:
            if cur_wh.count('-') != 1:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Incorrect working hours format: quantity of '-' is not equal to one")

            data = cur_wh.split('-')
            start_time = 0
            end_time = 0

            for time in data:
                identifier = 'start time' if data.index(time) == 0 else 'end time'
                if time.count(':') != 1:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=f"Incorrect working hours format in {identifier}: "
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
                                        detail=f"Incorrect working hours format in {identifier}: "
                                               f"separation hours and minutes done incorrectly."
                                               f" hours = {data[0]}, minutes = {data[1]}")
                if not 0 <= hours <= 23:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=f"Incorrect working hours format in {identifier}: "
                                               f"{hours} out of hours range")
                if not 0 <= minutes <= 59:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=f"Incorrect working hours format in {identifier}: "
                                               f"{minutes} out of minutes range")
            if start_time >= end_time:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Incorrect working hours values: start time greater then end time")
        return working_hours


class CouriersModel(BaseModel):
    couriers: List[CourierModel]

    @validator('couriers')
    def couriers_validator(cls, couriers):
        for courier in couriers:
            CourierModel.validate(courier)
        return couriers


class OrderModel(BaseModel):
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


class OrdersModel(BaseModel):
    orders: List[OrderModel]

    @validator('orders')
    def orders_validator(cls, orders):
        for order in orders:
            OrderModel.validate(order)
        return orders

# class CompletedOrderModel(BaseModel):
#     courier_id: int
#     order_id: int
#     complete_time: datetime.date
