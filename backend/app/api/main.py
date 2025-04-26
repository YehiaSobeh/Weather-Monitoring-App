from fastapi import APIRouter

from schemas.api_tags import ApiTags
from .endpoints import user

api_router = APIRouter()

api_router.include_router(
    user.router,
    tags=[ApiTags.USER],
    prefix="/user",
)
