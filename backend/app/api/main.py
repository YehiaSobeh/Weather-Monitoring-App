from fastapi import APIRouter

from schemas.api_tags import ApiTags
from .endpoints import user, weather, subscribe

api_router = APIRouter()

api_router.include_router(
    user.router,
    tags=[ApiTags.USER],
    prefix="/user",
)
api_router.include_router(
    weather.router,
    tags=[ApiTags.WEATHER],
    prefix="/weather",
)
api_router.include_router(
    subscribe.router,
    tags=[ApiTags.SUBSCRIBE],
    prefix="/subscribe",
)
