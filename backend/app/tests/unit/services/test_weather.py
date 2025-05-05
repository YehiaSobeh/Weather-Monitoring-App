import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import respx
from sqlalchemy.orm import Session

from services.weather import fetch_current_weather
from core.config import weather_settings
from utils.weather import send_request

from fastapi import HTTPException
from unittest.mock import Mock
from app.api.endpoints.weather import get_weather_history


@pytest.mark.asyncio
async def test_send_request_success():
    url = "https://api.example.com"
    params = {"param": "value"}
    expected_json = {"key": "value"}

    # Use respx to mock the GET request.
    with respx.mock:
        route = respx.get(url, params=params).mock(
            return_value=httpx.Response(200, json=expected_json)
        )

        response = await send_request(url, params)

        assert response == expected_json
        assert route.called


@pytest.mark.asyncio
async def test_fetch_current_weather_cached_data(db_session: Session):
    city = "malaysia"
    fake_weather_data = {"temp": 15}

    """ Mock the Redis client to return cached data
        use AsyncMock because fetch_current_weather is an async function
        and redis operations not awaitable .
    """
    mock_r = AsyncMock()
    mock_r.get = AsyncMock(return_value=json.dumps(fake_weather_data))

    _ = await fetch_current_weather(db_session, mock_r, city)

    # Verify that the cached data is returned
    mock_r.get.assert_called_once_with(f"weather:current:{city.lower()}")

    # Ensure we didn't store anything in cache
    mock_r.set.assert_not_called()


@pytest.mark.asyncio
async def test_fetch_current_weather_no_cache(db_session):
    city = "malaysia"
    fake_weather_data = {
        "main": {"temp": 15, "humidity": 50, "pressure": 1012},
        "wind": {"speed": 3.2},
    }

    cache_key = f"weather:current:{city.lower()}"

    mock_r = AsyncMock()

    # No cached data
    mock_r.get.return_value = None

    # Mock send_request to return fake weather data
    with patch(
        "services.weather.send_request", new_callable=AsyncMock
    ) as mock_send_request, patch(
        "services.weather.store_weather_data"
    ) as mock_store_weather_data:

        mock_send_request.return_value = fake_weather_data

        _ = await fetch_current_weather(db_session, mock_r, city)

        mock_send_request.assert_awaited_once()
        # Verify that the weather data was stored in the database.
        mock_store_weather_data.assert_called_once_with(
            db_session, fake_weather_data, city
        )
        # Verify that the data was cached.
        mock_r.set.assert_awaited_once_with(
            cache_key,
            json.dumps(fake_weather_data),
            ex=weather_settings.current_weather_cache_ttl,
        )


@pytest.mark.asyncio
async def test_get_weather_history_with_records():
    # Mock the CRUD function to return dummy data
    mock_records = [
        {"city": "Kazan", "temperature": -30.0, "fetched_at": "2025-05-01"}
    ]
    mock_crud = Mock(return_value=mock_records)

    # Mock dependencies (db, user_id)
    mock_db = Mock()
    mock_user_id = "user123"

    with patch("app.api.endpoints.weather.weather_crud.get_weather_history",
               mock_crud):
        response = await get_weather_history("Kazan", db=mock_db,
                                             user_id=mock_user_id)

        # Assert the response matches the mock data
        assert len(response) == 1
        assert response[0]["city"] == "Kazan"


@pytest.mark.asyncio
async def test_get_weather_history_no_records():
    # Mock CRUD to return empty list
    mock_crud = Mock(return_value=[])
    mock_db = Mock()
    mock_user_id = "user123"

    with patch("app.api.endpoints.weather.weather_crud.get_weather_history",
               mock_crud):
        # Expect HTTP 404 when no records exist
        with pytest.raises(HTTPException) as exc_info:
            await get_weather_history("InvalidCity", db=mock_db,
                                      user_id=mock_user_id)
        assert exc_info.value.status_code == 404
