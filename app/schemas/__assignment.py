from typing import List, Optional

from pydantic import BaseModel

import datetime


class AssignmentOrderModel(BaseModel):
    order_id: int
    weight: int
    region: int
    delivery_hours: List[str]
    cost: int
    completed_time: Optional[datetime.datetime] = None


class AssignmentOrdersModel(BaseModel):
    group_order_id: int
    orders: List[AssignmentOrderModel]


class AssignmentCourierModel(BaseModel):
    courier_id: int
    orders: List[AssignmentOrdersModel]


class AssignmentInfoModel(BaseModel):
    date: datetime.date
    couriers: List[AssignmentCourierModel]
