from decouple import config


class DBSettings:
    POSTGRES_DATABASE_URL: str = config("POSTGRES_DATABASE_URL")
    POSTGRES_DATABASE: str = config("POSTGRES_DATABASE")
    POSTGRES_USER: str = config("POSTGRES_USER")
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD")
    POSTGRES_PORT: str | int = config("POSTGRES_PORT", default=5432)
    POSTGRES_HOST: str = config("POSTGRES_HOST", default="postgresql")


db_settings = DBSettings()
