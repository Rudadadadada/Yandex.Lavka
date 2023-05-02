from sqlalchemy import create_engine, URL, Engine, orm
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session


Base = declarative_base()

__factory = None


def global_init(db_params: dict):
    global __factory

    if __factory:
        return

    if not db_params:
        raise Exception("Database params should be specified.")

    url_object = URL.create(**db_params)
    engine: Engine = create_engine(url_object, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from app.database.__models import Courier, Order, OrderDeliveryHour, CourierWorkingHour, Region

    Base.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
