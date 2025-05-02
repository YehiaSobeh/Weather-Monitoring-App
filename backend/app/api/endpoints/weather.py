from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_cache_redis, get_db, rate_limit, get_user_id_from_token
from services import weather as weather_service
from crud import weather as weather_crud
from schemas.weather import WeatherHistoryItem

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


@router.get(
    "/history/{city}",
    summary="Get Weather History",
    description="Fetches the weather history for a given city.",
    response_model=list[WeatherHistoryItem],
)
async def get_weather_history(
    city: str,
    db: Session = Depends(get_db),
    user_id=Depends(get_user_id_from_token),
) -> list[WeatherHistoryItem]:
 
    records = weather_crud.get_weather_history(db, city)
    if not records:
        raise HTTPException(404, f"No weather history for city: {city}")
    return records