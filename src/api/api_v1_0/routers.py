from fastapi import APIRouter
from starlette.status import HTTP_404_NOT_FOUND
from api.api_v1_0.endpoints.room import router as room_router
from api.api_v1_0.endpoints.comment import router as comment_router
from api.api_v1_0.endpoints.health_check import router as health_check_router

router = APIRouter()

router.include_router(room_router, responses={HTTP_404_NOT_FOUND: {"description": "Not found"}}, prefix="/room",
                      tags=["room"])

router.include_router(health_check_router, responses={HTTP_404_NOT_FOUND: {"description": "Not found"}},
                      tags=["health-check"])

router.include_router(comment_router, responses={HTTP_404_NOT_FOUND: {"description": "Not found"}}, prefix="/comment",
                      tags=["comment"])
