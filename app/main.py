import uvicorn
from fastapi import FastAPI

from limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.config import DATABASE
from app.database.db_session import global_init
from app.routers import orders, couriers


def get_application() -> FastAPI:
    application = FastAPI(title="Yandex Lavka")
    application.include_router(orders.order)
    application.include_router(couriers.courier)

    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    return application


app = get_application()

global_init(DATABASE)

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
