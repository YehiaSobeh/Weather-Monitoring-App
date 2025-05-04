import pytest
import jwt
import jwt.api_jwt
from types import SimpleNamespace
import datetime as real_datetime

import core.security as security
from core.config import authorization_settings

# 1) Configure a deterministic secret key & algorithm
@pytest.fixture(autouse=True)
def dummy_config(monkeypatch):
    monkeypatch.setattr(authorization_settings, "rsa_private_key", "my-secret")
    monkeypatch.setattr(authorization_settings, "rsa_public_key",  "my-secret")
    monkeypatch.setattr(authorization_settings, "token_algorithm", "HS256")
    # short expiries so we can compute them by hand
    monkeypatch.setattr(authorization_settings, "access_token_expires_minutes", 5)
    monkeypatch.setattr(authorization_settings, "refresh_token_expires_days",    1)
    yield

# 2) Freeze "now" (for both our code and PyJWT) to 2020-01-01T00:00:00Z
@pytest.fixture(autouse=True)
def freeze_time(monkeypatch):
    # Subclass the real datetime.datetime so we can override now() and utcnow()
    class FixedDateTime(real_datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            # 2020-01-01T00:00:00 in whatever tz
            return cls(2020, 1, 1, tzinfo=tz)
        @classmethod
        def utcnow(cls):
            # naive UTC 2020-01-01T00:00:00
            return cls(2020, 1, 1)

    # Patch your module to use FixedDateTime
    monkeypatch.setattr(security, "datetime", FixedDateTime)
    # Patch PyJWT’s internal datetime for exp checks
    monkeypatch.setattr(jwt.api_jwt, "datetime", FixedDateTime)

    yield


def test_generate_and_decode_access_token_roundtrip():
    payload = {"foo": "bar", "iss": security.ACCESS_TOKEN_ISSUER}
    token = security.generate_jwt_token(payload)
    # decode_access_token also checks issuer and exp against our fake clock
    decoded = security.decode_access_token(token)
    assert decoded["foo"] == "bar"
    assert decoded["iss"] == security.ACCESS_TOKEN_ISSUER


def test_decode_access_token_wrong_issuer_raises():
    # craft a token with the wrong "iss"
    bad = jwt.encode(
        {"foo": "bar", "iss": "not-valid-issuer"},
        key="my-secret", algorithm="HS256"
    )
    with pytest.raises(jwt.InvalidIssuerError):
        security.decode_access_token(bad)


def test_decode_refresh_token_and_check_issuer():
    # generate a valid refresh token
    rt = jwt.encode(
        {"user_id": "u1", "iss": security.REFRESH_TOKEN_ISSUER},
        key="my-secret", algorithm="HS256"
    )
    data = security.decode_refresh_token(rt)
    assert data["user_id"] == "u1"

    # simulate an expired refresh token (exp in the past)
    expired = jwt.encode(
        {"user_id": "u2", "iss": security.REFRESH_TOKEN_ISSUER, "exp": 1},
        key="my-secret", algorithm="HS256"
    )
    # Should not raise, because check_refresh_token_issuer sets verify_exp=False
    security.check_refresh_token_issuer(expired)


def test_decode_refresh_token_wrong_issuer_raises():
    bad_rt = jwt.encode(
        {"user_id": "x", "iss": "wrong"},
        key="my-secret", algorithm="HS256"
    )
    with pytest.raises(jwt.InvalidIssuerError):
        security.decode_refresh_token(bad_rt)


def test_generate_tokens_structure_and_expiry():
    result = security.generate_tokens(user_id="user42")
    assert set(result) == {
        "access_token", "refresh_token", "expires_in", "refresh_token_expires_in"
    }

    # Access-token payload checks
    at_data = security.decode_access_token(result["access_token"])
    assert at_data["user_id"] == "user42"
    assert at_data["iss"]     == security.ACCESS_TOKEN_ISSUER
    # now=1577836800 + 5 minutes → 1577837100
    assert result["expires_in"] == 1577837100

    # Refresh-token payload checks
    rt_data = security.decode_refresh_token(result["refresh_token"])
    assert rt_data["user_id"] == "user42"
    assert rt_data["iss"]     == security.REFRESH_TOKEN_ISSUER
    # now=1577836800 + 1 day → 1577923200
    assert result["refresh_token_expires_in"] == 1577923200


def test_regenerate_access_token_from_refresh():
    # build a refresh token that won't expire immediately
    exp_ts = security.datetime.now(tz=security.timezone.utc).timestamp() + 1000
    rt = jwt.encode(
        {"user_id": "abc", "iss": security.REFRESH_TOKEN_ISSUER, "exp": exp_ts},
        key="my-secret", algorithm="HS256"
    )

    out = security.regenerate_access_token(rt)
    assert "access_token" in out and "expires_in" in out

    new_data = security.decode_access_token(out["access_token"])
    assert new_data["user_id"] == "abc"
    assert new_data["iss"]     == security.ACCESS_TOKEN_ISSUER
    # expires_in = now (1577836800) + 5m → 1577837100
    assert out["expires_in"] == 1577837100
