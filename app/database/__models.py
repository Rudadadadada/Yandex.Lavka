from sqlalchemy import Column, Integer, String, ForeignKey, Time, orm
from sqlalchemy_serializer import SerializerMixin

from app.database.db_session import Base


class Courier(Base, SerializerMixin):
    __tablename__ = 'couriers'

    courier_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    type = Column(String, nullable=False)

    regions = Column(Integer, ForeignKey('regions.id'), nullable=False)
    working_hours = Column(Integer, ForeignKey('working_hours.id'), nullable=False)

    region = orm.relationship('Region')
    time = orm.relationship('WorkingHours')


class DeliveryHours(Base, SerializerMixin):
    __tablename__ = 'delivery_hours'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    start_time = Column(Time, nullable=False)
    finished_time = Column(Time, nullable=False)

    couriers = orm.relationship('Order', back_populates='working_time')


class Order(Base, SerializerMixin):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    weight = Column(Integer, nullable=False)
    region = Column(Integer, nullable=False)
    delivery_hours = Column(Time, nullable=False)
    cost = Column(Integer, nullable=False)

    time = orm.relationship('DeliveryHours')


class Region(Base, SerializerMixin):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    region = Column(Integer, nullable=False)

    couriers = orm.relationship('Courier', back_populates='regions')


class WorkingHours(Base, SerializerMixin):
    __tablename__ = 'working_hours'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    start_time = Column(Time, nullable=False)
    finished_time = Column(Time, nullable=False)

    couriers = orm.relationship('Courier', back_populates='working_hours')
