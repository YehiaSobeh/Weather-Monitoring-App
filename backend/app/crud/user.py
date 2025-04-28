from models.user import User
from sqlalchemy.orm import Session


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter_by(id=user_id).first()


def check_if_user_with_email_exists(db: Session, email: str) -> bool:
    return db.query(User).filter_by(email=email).first() is not None
