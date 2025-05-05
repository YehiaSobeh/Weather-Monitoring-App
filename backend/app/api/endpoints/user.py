from api.deps import get_db
from core.security import generate_tokens
from crud import user as crud_user
from fastapi import APIRouter, Depends, HTTPException
from schemas import AuthorizationTokens, LoginRequest, UserCreate
from services import user as users_service
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> dict:
    if crud_user.check_if_user_with_email_exists(db, user_data.email):
        raise HTTPException(detail="Email already in use", status_code=400)
    tokens = users_service.create_user(db, user_data)
    return tokens


@router.post("/login")
def login(
    login_data: LoginRequest, db: Session = Depends(get_db)
) -> AuthorizationTokens:
    invalid_credentials_error = HTTPException(
        detail="Invalid credentials.", status_code=401
    )

    user = crud_user.get_user_by_email(db, login_data.email)
    if not user:
        raise invalid_credentials_error

    if not users_service.compare_password_with_hash(
        login_data.password, user.password
    ):
        raise invalid_credentials_error

    return generate_tokens(str(user.id))
