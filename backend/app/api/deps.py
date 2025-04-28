from typing import Annotated
import jwt

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.db import session_local
from core.security import decode_access_token
from crud.user import get_user_by_id


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
    user_id = get_user_id_from_jwt_token(credentials.credentials)
    user = get_user_by_id(db, user_id, allow_invisible=False)
    if not user:
        raise HTTPException(detail="Invalid token", status_code=401)
    return user_id


def get_user_id_from_jwt_token(token: str) -> int:
    try:
        token_data = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(detail="Token has expired", status_code=401)
    except jwt.InvalidTokenError:
        raise HTTPException(detail="Invalid token", status_code=401)
    return token_data["user_id"]
