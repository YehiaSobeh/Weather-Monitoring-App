from decouple import config


class DBSettings:
    SQLITE_DATABASE_URL: str = config(
        "SQLITE_DATABASE_URL", default="sqlite:///./test.db"
    )


class AuthorizationSettings:
    jwt_secret_key: str = config("JWT_SECRET_KEY")
    token_algorithm: str = config("TOKEN_ALGORITHM", default="RS256")
    _raw_pub = config("RSA_PUBLIC_KEY")
    _raw_priv = config("RSA_PRIVATE_KEY")
    access_token_issuer = config("ACCESS_TOKEN_ISSUER", 
                                 default="backend:access-token")
    refresh_token_issuer = config("REFRESH_TOKEN_ISSUER",
                                  default="backend:refresh-token")

    rsa_public_key = _raw_pub.replace("\\n", "\n")
    rsa_private_key = _raw_priv.replace("\\n", "\n")
    access_token_expires_minutes: int = config("ACCESS_TOKEN_EXPIRES_MINUTES")
    refresh_token_expires_days: int = config("REFRESH_TOKEN_EXPIRES_DAYS")


class WeatherSettings:
    weather_api_key: str = config("WEATHER_API_KEY")
    weather_url: str = "https://api.openweathermap.org/data/2.5"
    redis_host: str = "localhost"
    redis_port: int = "6379"
    current_weather_cache_ttl: int = 600
    forecast_cache_ttl: int = 3600
    rate_limit_count: int = 10
    rate_limit_window: int = 10


class MailSettings:
    mail_host: str = config("MAIL_HOST")
    mail_port: int = config("MAIL_PORT")
    mail_username: str = config("MAIL_USERNAME")
    mail_password: str = config("MAIL_PASSWORD")


db_settings = DBSettings()
authorization_settings = AuthorizationSettings()
weather_settings = WeatherSettings()
mail_settings = MailSettings()
