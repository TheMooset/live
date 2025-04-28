from fastapi import APIRouter
from fastapi.responses import JSONResponse
from services.health_check.read_health_check import ReadHealthCheckService
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK

router = APIRouter()


@router.get("/health-check")
def get_health_check():
    result = ReadHealthCheckService().execute()
    status_code = HTTP_500_INTERNAL_SERVER_ERROR
    if result and result['result']:
        status_code = HTTP_200_OK
    return JSONResponse(content=result, status_code=status_code)
