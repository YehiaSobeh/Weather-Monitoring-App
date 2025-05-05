import datetime as real_datetime

import jwt
import jwt.api_jwt
import pytest

import core.security as security
from core.config import authorization_settings


@pytest.fixture(autouse=True)
def dummy_config(monkeypatch):
    monkeypatch.setattr(
        authorization_settings, "rsa_private_key", "my-secret"
    )
    monkeypatch.setattr(
        authorization_settings, "rsa_public_key", "my-secret"
    )
    monkeypatch.setattr(
        authorization_settings, "token_algorithm", "HS256"
    )
    monkeypatch.setattr(
        authorization_settings, "access_token_expires_minutes", 5
    )
    monkeypatch.setattr(
        authorization_settings, "refresh_token_expires_days", 1
    )
    yield


@pytest.fixture(autouse=True)
def freeze_time(monkeypatch):

    class FixedDateTime(real_datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2020, 1, 1, tzinfo=tz)

        @classmethod
        def utcnow(cls):
            return cls(2020, 1, 1)

    monkeypatch.setattr(security, "datetime", FixedDateTime)
    monkeypatch.setattr(jwt.api_jwt, "datetime", FixedDateTime)

    yield


def test_generate_and_decode_access_token_roundtrip():
    payload = {
        "foo": "bar",
        "iss": authorization_settings.access_token_issuer,
    }
    token = security.generate_jwt_token(payload)
    decoded = security.decode_access_token(token)
    assert decoded["foo"] == "bar"
    assert decoded["iss"] == authorization_settings.access_token_issuer


def test_decode_access_token_wrong_issuer_raises():
    bad = jwt.encode(
        {"foo": "bar", "iss": "not-valid-issuer"},
        key="my-secret",
        algorithm="HS256",
    )
    with pytest.raises(jwt.InvalidIssuerError):
        security.decode_access_token(bad)


def test_decode_refresh_token_and_check_issuer():
    rt = jwt.encode(
        {"user_id": "u1", "iss": authorization_settings.refresh_token_issuer},
        key="my-secret",
        algorithm="HS256",
    )
    data = security.decode_refresh_token(rt)
    assert data["user_id"] == "u1"

    expired = jwt.encode(
        {
            "user_id": "u2",
            "iss": authorization_settings.refresh_token_issuer,
            "exp": 1,
        },
        key="my-secret",
        algorithm="HS256",
    )
    security.check_refresh_token_issuer(expired)


def test_decode_refresh_token_wrong_issuer_raises():
    bad_rt = jwt.encode(
        {"user_id": "x", "iss": "wrong"},
        key="my-secret",
        algorithm="HS256",
    )
    with pytest.raises(jwt.InvalidIssuerError):
        security.decode_refresh_token(bad_rt)


def test_generate_tokens_structure_and_expiry():
    result = security.generate_tokens(user_id="user42")
    assert set(result) == {
        "access_token",
        "refresh_token",
        "expires_in",
        "refresh_token_expires_in",
    }

    at_data = security.decode_access_token(result["access_token"])
    assert at_data["user_id"] == "user42"
    assert at_data["iss"] == authorization_settings.access_token_issuer
    assert result["expires_in"] == 1577837100

    rt_data = security.decode_refresh_token(result["refresh_token"])
    assert rt_data["user_id"] == "user42"
    assert rt_data["iss"] == authorization_settings.refresh_token_issuer
    assert result["refresh_token_expires_in"] == 1577923200


def test_regenerate_access_token_from_refresh():
    exp_ts = (
        security.datetime.now(tz=security.timezone.utc).timestamp() + 1000
    )
    rt = jwt.encode(
        {
            "user_id": "abc",
            "iss": authorization_settings.refresh_token_issuer,
            "exp": exp_ts,
        },
        key="my-secret",
        algorithm="HS256",
    )

    out = security.regenerate_access_token(rt)
    assert "access_token" in out and "expires_in" in out

    new_data = security.decode_access_token(out["access_token"])
    assert new_data["user_id"] == "abc"
    assert new_data["iss"] == authorization_settings.access_token_issuer
    assert out["expires_in"] == 1577837100
