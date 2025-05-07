from sqlalchemy.orm import Session
from passlib.context import CryptContext

from core.security import generate_tokens
from models import User
from schemas import user as schemas


pwd_context = CryptContext(schemes=["bcrypt"])  # pragma: no mutate


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def compare_password_with_hash(
    input_password: str,
    stored_password_hash: str
) -> bool:
    return pwd_context.verify(input_password, stored_password_hash)


def create_user(db: Session, user_data: schemas.UserCreate):
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
        surname=user_data.surname,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return generate_tokens(str(db_user.id))
