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

    rsa_public_key = _raw_pub.replace("\\n", "\n")
    rsa_private_key = _raw_priv.replace("\\n", "\n")
    access_token_expires_minutes: int = config("ACCESS_TOKEN_EXPIRES_MINUTES")
    refresh_token_expires_days: int = config("REFRESH_TOKEN_EXPIRES_DAYS")


db_settings = DBSettings()
authorization_settings = AuthorizationSettings()
