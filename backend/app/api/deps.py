import time

from typing import Annotated
import jwt

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.db import session_local
from core.security import decode_access_token
from crud.user import get_user_by_id
from redis_client import r
from core.config import weather_settings

http_bearer_dependency = HTTPBearer()


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def get_user_id_from_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials, Depends(http_bearer_dependency)
    ],
    db: Session = Depends(get_db),
) -> int:
    user_id = _get_user_id_from_jwt_token(credentials.credentials)
    print(f"User ID from token: {user_id}")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(detail="Invalid token", status_code=401)
    return user_id


def _get_user_id_from_jwt_token(token: str) -> int:
    try:
        token_data = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(detail="Token has expired", status_code=401)
    except jwt.InvalidTokenError:
        raise HTTPException(detail="Invalid token", status_code=401)
    print(type(token_data["user_id"]))
    return token_data["user_id"]


async def get_cache_redis():
    return await r.get_cache_redis()


async def get_rate_limit_redis():
    return await r.get_rate_limit_redis()


async def rate_limit(
    request: Request,
    user_id: Annotated[int, Depends(get_user_id_from_token)],
    r=Depends(get_rate_limit_redis),
) -> None:
    """
    Allows up to 60 requests per minute user.
    Uses Redis to count requests in the current minute and raises
    HTTP 429 if the limit is exceeded.
    """
    current_window = int(time.time() // weather_settings.rate_limit_window)

    # each endpoint has its own rate limit
    endpoint_url = request.url.path

    # Key format: rate_limit:<current_window>
    key = f"rate_limit:{user_id}:{endpoint_url}:{current_window}"

    # Increment the counter for the current minute
    count = await r.incr(key)

    # Set the key to expire after the window (first request only)
    if count == 1:
        await r.expire(key, weather_settings.rate_limit_window)

    if count > weather_settings.rate_limit_count:
        raise HTTPException(
            status_code=429, detail="Too Many Requests. Please try again later."
        )
