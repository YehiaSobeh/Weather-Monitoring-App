from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import db_settings

engine = create_engine(db_settings.POSTGRES_DATABASE_URL)

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()
