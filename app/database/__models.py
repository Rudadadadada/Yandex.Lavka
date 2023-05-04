from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Time
from sqlalchemy_serializer import SerializerMixin

from app.database.db_session import Base


class Courier(Base, SerializerMixin):
    __tablename__ = 'couriers'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    courier_type = Column(String, nullable=False)

    def __init__(self, courier_type):
        self.courier_type = courier_type


class Region(Base, SerializerMixin):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    region = Column(Integer, nullable=False)

    def __init__(self, region):
        self.region = region


class CourierWorkingHour(Base, SerializerMixin):
    __tablename__ = 'couriers_working_hours'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    courier_id = Column(Integer, ForeignKey('couriers.id'), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    def __init__(self, courier_id, start_time, end_time):
        self.courier_id = courier_id
        self.start_time = start_time
        self.end_time = end_time


class CourierRegion(Base, SerializerMixin):
    __tablename__ = 'couriers_regions'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    courier_id = Column(Integer, ForeignKey('couriers.id'), nullable=False)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)

    def __init__(self, courier_id, region_id):
        self.courier_id = courier_id
        self.region_id = region_id


class OrderDeliveryHour(Base, SerializerMixin):
    __tablename__ = 'orders_delivery_hours'

    id: int = Column(Integer, primary_key=True, autoincrement=True, index=True)
    order_id: int = Column(Integer, ForeignKey('orders.id'), nullable=False)
    start_time: Time = Column(Time, nullable=False)
    end_time: Time = Column(Time, nullable=False)

    def __init__(self, order_id, start_time, end_time):
        self.order_id = order_id
        self.start_time = start_time
        self.end_time = end_time


class Order(Base, SerializerMixin):
    __tablename__ = 'orders'

    id: int = Column(Integer, primary_key=True, autoincrement=True, index=True)
    weight: int = Column(Integer, nullable=False)
    region: int = Column(Integer, nullable=False)
    cost: int = Column(Integer, nullable=False)

    def __init__(self, weight, region, cost):
        self.weight = weight
        self.region = region
        self.cost = cost
