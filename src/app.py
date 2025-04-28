from config import config
from services.base_service import UnauthorizedError, ServiceValidationError

if not config.debug:
    import sentry_sdk

    sentry_sdk.init(config.sentry_dsn)

from fastapi import FastAPI
from api.api_v1_0.routers import router as api_router_v1_0
from fastapi.exceptions import RequestValidationError
import logging
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.status import HTTP_400_BAD_REQUEST

app = FastAPI(title=config.app_title)

app.include_router(api_router_v1_0, prefix='/api_v1.0')


@app.get('/robots.txt', response_class=PlainTextResponse)
def robots():
    data = """User-agent: *\nDisallow: /"""
    return data

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc: RequestValidationError):
    errors = []
    for e in exc.errors():
        loc = '>'.join([str(item) for item in e['loc'] if item != "body"])
        errors.append({"message": e['msg'], "error_code": 0, "fields": [loc]})
    return JSONResponse(content=errors, status_code=HTTP_400_BAD_REQUEST)


@app.exception_handler(ServiceValidationError)
def validation_exception_handler(request, exc: ServiceValidationError):
    return JSONResponse(content=exc.to_json(), status_code=exc.http_error_code)


@app.exception_handler(UnauthorizedError)
def validation_exception_handler(request, exc: UnauthorizedError):
    return JSONResponse(content=exc.to_json(), status_code=exc.http_error_code)


logging.basicConfig(level=config.log_level)
logging.info("application starts...")

if config.debug and __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, debug=True)
