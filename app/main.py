import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.limiter import limiter
from app.routers import orders, couriers


def get_application() -> FastAPI:
    application = FastAPI(title="Yandex Lavka")
    application.include_router(orders.order)
    application.include_router(couriers.courier)

    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    return application


app = get_application()


def custom_openapi():
    if not app.openapi_schema:
        app.openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            terms_of_service=app.terms_of_service,
            contact=app.contact,
            license_info=app.license_info,
            routes=app.routes,
            tags=app.openapi_tags,
            servers=app.servers,
        )
        for _, method_item in app.openapi_schema.get('paths').items():
            for _, param in method_item.items():
                responses = param.get('responses')
                if '422' in responses:
                    del responses['422']
                elif '200' in responses:
                    del responses['200']
    return app.openapi_schema


app.openapi = custom_openapi

# if __name__ == '__main__':
#     uvicorn.run("main:app", host="localhost", port=8080)
