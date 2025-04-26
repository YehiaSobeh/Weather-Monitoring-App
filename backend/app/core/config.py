from decouple import config


class DBSettings:
    SQLITE_DATABASE_URL: str = config("SQLITE_DATABASE_URL", default="sqlite:///./test.db")


db_settings = DBSettings()
