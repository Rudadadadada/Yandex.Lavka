from datetime import datetime
from typing import List

from fastapi import HTTPException
from pydantic import BaseModel, validator
from starlette import status

from app.utils.time import HH_MM


class PostCourierModel(BaseModel):
    courier_type: str
    regions: List[int]
    working_hours: List[str]

    @validator('courier_type')
    @classmethod
    def courier_type_validator(cls, courier_type):
        if courier_type not in ['FOOT', 'BIKE', 'AUTO']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return courier_type

    @validator('regions')
    @classmethod
    def regions_validator(cls, regions):
        regions = set(regions)
        for region in regions:
            if region <= 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        return regions

    @validator('working_hours')
    @classmethod
    def working_hours_validator(cls, working_hours):
        working_hours = set(working_hours)
        for cur_wh in working_hours:
            data = cur_wh.split('-')
            if cur_wh.count('-') != 1:
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
        return working_hours


class PostCouriersModel(BaseModel):
    couriers: List[PostCourierModel]

    @validator('couriers')
    @classmethod
    def couriers_validator(cls, couriers):
        for courier in couriers:
            PostCourierModel.validate(courier)
        return couriers


class GetCourierModel(BaseModel):
    courier_id: int
    courier_type: str
    regions: List[int]
    working_hours: List[str]


class GetCouriersModel(BaseModel):
    couriers: List[GetCourierModel]


class GetMetaInfoModel(BaseModel):
    courier_id: int
    courier_type: str
    regions: List[int]
    working_hours: List[str]
    rating: float
    earnings: float
