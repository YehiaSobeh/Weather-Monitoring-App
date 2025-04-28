from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_cache_redis, get_db, rate_limit, get_user_id_from_token
from services import weather as weather_service

router = APIRouter()


@router.get(
    "/current/{city}",
    summary="Get Current Weather",
    description="Fetches the current weather for a given city.",
    response_model=dict[str, Any],
)
async def get_current_weather(
    city: str,
    db: Session = Depends(get_db),
    r=Depends(get_cache_redis),
    _=Depends(rate_limit),
    user_id=Depends(get_user_id_from_token),
) -> dict[str, Any]:
    """
    - db: Database session (dependency).
    - r: Redis cache session (dependency).
    - rate_limit: Rate limiter (dependency).
    """
    return await weather_service.fetch_current_weather(db, r, city)
