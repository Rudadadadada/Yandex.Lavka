from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, DateTime, Float
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

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    def __init__(self, order_id, start_time, end_time):
        self.order_id = order_id
        self.start_time = start_time
        self.end_time = end_time


class Order(Base, SerializerMixin):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    weight = Column(Integer, nullable=False)
    region = Column(Integer, nullable=False)
    cost = Column(Integer, nullable=False)
    completed_time = Column(DateTime)

    def __init__(self, weight, region, cost, completed_time):
        self.weight = weight
        self.region = region
        self.cost = cost
        self.completed_time = completed_time


class DistributedOrders(Base, SerializerMixin):
    __tablename__ = 'distributed_orders'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    courier_id = Column(Integer, ForeignKey('couriers.id'), nullable=False)
    group_order_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    predictable_time = Column(Time, nullable=False)
    after_fact_time = Column(DateTime)
    earnings = Column(Float)

    def __init__(self, order_id, courier_id, group_order_id, date, start_time, end_time, predictable_time,
                 after_fact_time, earnings):
        self.order_id = order_id
        self.courier_id = courier_id
        self.group_order_id = group_order_id
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.predictable_time = predictable_time
        self.after_fact_time = after_fact_time
        self.earnings = earnings
