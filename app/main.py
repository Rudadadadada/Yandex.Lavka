import uvicorn
from fastapi import FastAPI

from app.config import DATABASE
from app.database.db_session import global_init, create_session
from app.routers import orders, couriers


def get_application() -> FastAPI:
    application = FastAPI(title="Yandex Lavka")
    application.include_router(orders.order)
    application.include_router(couriers.courier)

    return application


app = get_application()

global_init(DATABASE)

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000)