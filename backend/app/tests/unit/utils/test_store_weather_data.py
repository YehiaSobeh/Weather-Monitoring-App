from unittest.mock import Mock
from app.utils.weather import store_weather_data
from models.weather import Weather
from sqlalchemy.orm import Session


def test_store_weather_data_valid():
    # Mock DB session
    mock_db = Mock(spec=Session)

    # Valid weather data
    weather_data = {
        "main": {"temp": 7.0, "pressure": 900, "humidity": 50},
        "wind": {"speed": 10.0},
    }
    store_weather_data(mock_db, weather_data, "Innopolis")
    # Assert Weather object was created and added to DB
    mock_db.add.assert_called_once()
    added_weather = mock_db.add.call_args[0][0]
    assert isinstance(added_weather, Weather)
    assert added_weather.city == "innopolis"
    assert added_weather.temperature == 7.0
    assert added_weather.humidity == 50
    assert added_weather.pressure == 900
    assert added_weather.wind_speed == 10.0


def test_store_weather_data_missing_keys():
    mock_db = Mock(spec=Session)

    # Missing 'wind' key
    weather_data = {"main": {"temp": 15.0}}

    store_weather_data(mock_db, weather_data, "Aleppo")

    # Assert Weather object was still created (graceful handling)
    added_weather = mock_db.add.call_args[0][0]
    assert added_weather.wind_speed is None
