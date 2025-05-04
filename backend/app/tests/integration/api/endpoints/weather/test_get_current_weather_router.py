from unittest.mock import patch
import pytest


@pytest.mark.asyncio
async def test_get_current_weather(client):
    city = "malaysia"
    fake_weather_data = {"temp": 15}

    with patch(
        "services.weather.fetch_current_weather",
        return_value=fake_weather_data
    ):
        response = client.get(f"/api/v1/weather/current/{city}")

        assert response.status_code == 200
        assert response.json() == fake_weather_data
