from app.database.db_session import global_init
from routers.orders import order
from routers.courier import courier

from config import DATABASE

from fastapi import FastAPI


def get_application() -> FastAPI:
    application = FastAPI(title="Yandex Lavka")
    application.include_router(order)
    application.include_router(courier)

    return application


app = get_application()

# global_init(DATABASE)
