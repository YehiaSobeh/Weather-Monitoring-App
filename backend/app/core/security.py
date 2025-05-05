from datetime import datetime, timedelta, timezone
import jwt

from core.config import authorization_settings


def generate_jwt_token(token_data: dict) -> str:
    return jwt.encode(
        payload=token_data,
        key=authorization_settings.rsa_private_key,
        algorithm=authorization_settings.token_algorithm,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        jwt=token,
        key=authorization_settings.rsa_public_key,
        algorithms=[authorization_settings.token_algorithm],
        issuer=authorization_settings.access_token_issuer,
    )


def decode_refresh_token(token: str) -> dict:
    return jwt.decode(
        jwt=token,
        key=authorization_settings.rsa_public_key,
        algorithms=[authorization_settings.token_algorithm],
        issuer=authorization_settings.refresh_token_issuer,
    )


def check_refresh_token_issuer(token: str) -> None:
    jwt.decode(
        jwt=token,
        key=authorization_settings.rsa_public_key,
        algorithms=[authorization_settings.token_algorithm],
        issuer=authorization_settings.refresh_token_issuer,
        options={"verify_exp": False},
    )


def regenerate_access_token(refresh_token: str) -> dict:
    token_data = decode_refresh_token(refresh_token)
    current_datetime = datetime.now(tz=timezone.utc)
    access_token_expires_in = (
        current_datetime
        + timedelta(
            minutes=authorization_settings.access_token_expires_minutes
        )
    ).timestamp()
    access_token = generate_jwt_token(
        {
            "user_id": token_data["user_id"],
            "exp": access_token_expires_in,
            "iss": authorization_settings.access_token_issuer,
        }
    )
    return {
        "access_token": access_token,
        "expires_in": int(access_token_expires_in)
    }


def generate_tokens(user_id: str) -> dict:
    current_datetime = datetime.now(tz=timezone.utc)

    access_token_expires_in = (
        current_datetime
        + timedelta(
            minutes=int(
                authorization_settings.access_token_expires_minutes
            )
        )
    ).timestamp()

    refresh_token_expires_in = (
        current_datetime
        + timedelta(
            days=int(
                authorization_settings.refresh_token_expires_days
            )
        )
    ).timestamp()

    access_token = generate_jwt_token(
        {
            "user_id": user_id,
            "exp": access_token_expires_in,
            "iss": authorization_settings.access_token_issuer
        }
    )
    refresh_token = generate_jwt_token(
        {
            "user_id": user_id,
            "exp": refresh_token_expires_in,
            "iss": authorization_settings.refresh_token_issuer,
        }
    )

    return {
        "access_token": access_token,
        "expires_in": int(access_token_expires_in),
        "refresh_token": refresh_token,
        "refresh_token_expires_in": int(refresh_token_expires_in),
    }
