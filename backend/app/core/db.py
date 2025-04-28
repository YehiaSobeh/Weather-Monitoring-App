from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import db_settings

engine = create_engine(
    db_settings.SQLITE_DATABASE_URL,
    # Allow the same database connection to be shared across multiple threads.
    connect_args={"check_same_thread": False},
)

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()
