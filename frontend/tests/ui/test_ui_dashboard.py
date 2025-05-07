import pytest
import requests
import datetime as _dt
from unittest.mock import Mock
from frontend import dashboard
import pandas as pd


class DotDict(dict):
    __getattr__ = dict.get

    def __setattr__(self, name, value):
        self[name] = value


@pytest.fixture
def mock_st(mocker):
    mock_st = mocker.MagicMock()
    mock_st.session_state = DotDict()
    mocker.patch.object(dashboard, "st", mock_st)
    return mock_st


def test_get_auth_headers(mock_st):
    mock_st.session_state.access_token = "test_token"
    assert dashboard.get_auth_headers() == {
        "Authorization": "Bearer test_token"}


def test_display_historical_no_data(mock_st):
    dashboard.display_historical([], 7)
    mock_st.warning.assert_called_once_with("No historical data available")


def test_display_historical_filter_dates(mocker, mock_st):
    # Fake datetime on dashboard to control utcnow
    class FakeDateTime:
        @classmethod
        def utcnow(cls):
            # Midday ensures 2-day window excludes the older 00:00 entry
            return _dt.datetime(2023, 1, 1, 12, 0, 0)

        @classmethod
        def fromisoformat(cls, s):
            return _dt.datetime.fromisoformat(s)

    mocker.patch.object(dashboard, "datetime", FakeDateTime)

    history = [
        {"fetched_at": "2022-12-30T00:00:00", "temperature": 10},
        {"fetched_at": "2023-01-01T00:00:00", "temperature": 20},
    ]

    mock_px = mocker.patch.object(dashboard, "px")

    dashboard.display_historical(history, days_back=2)

    args, kwargs = mock_px.line.call_args
    df: pd.DataFrame = kwargs.get("data_frame") or args[0]
    assert len(df) == 1
    assert df.iloc[0]["temperature"] == 20


def test_render_dashboard_no_city(mock_st):
    mock_st.button.return_value = True
    mock_st.text_input.return_value = ""
    mock_st.error = Mock()

    dashboard.render_current_weather()

    mock_st.error.assert_called_once_with("Please enter a city")


def test_render_dashboard_success(mocker, mock_st):
    # Arrange: put a valid token in session and simulate sidebar inputs
    mock_st.session_state = DotDict(access_token="test_token")
    mock_st.button.return_value = True
    mock_st.text_input.side_effect = ["Paris"]
    mock_st.radio.return_value = "Metric (°C)"
    mock_st.slider.return_value = 7

    # Stub out requests.get() to return a fake “current” response
    mock_get = mocker.patch("frontend.dashboard.requests.get")
    current_resp = Mock()
    current_resp.json.return_value = {
        "name": "Paris",
        "main": {"temp": 15, "humidity": 70, "pressure": 1015},
        "wind": {"speed": 5},
    }
    mock_get.return_value = current_resp

    # Act
    dashboard.render_current_weather()

    # Assert: session_state.current was set correctly
    assert mock_st.session_state.current["city"] == "Paris"
    assert mock_st.session_state.current["temperature"] == 15
    assert mock_st.session_state.current["humidity"] == 70
    assert mock_st.session_state.current["wind_speed"] == 5
    assert mock_st.session_state.current["pressure"] == 1015

    # Assert: exactly one GET call, to the
    # current-weather endpoint with timeout=5
    mock_get.assert_called_once_with(
        f"{dashboard.API_URL}/weather/current/Paris",
        headers={"Authorization": "Bearer test_token"},
        params={"units": "metric"},
        timeout=5
    )


def test_subscribe_success(mocker, mock_st):
    mock_st.session_state = DotDict(access_token="test_token")
    mock_st.form_submit_button.return_value = True
    mock_st.text_input.return_value = "London"
    mock_st.number_input.return_value = 25.0

    mock_post = mocker.patch("frontend.dashboard.requests.post")
    mock_post.return_value = Mock()
    mock_st.success = Mock()

    dashboard.subscribe_page()

    mock_post.assert_called_once_with(
        f"{dashboard.API_URL}/subscribe/create",
        headers={"Authorization": "Bearer test_token"},
        json={"city": "London", "temperature_threshold": 25.0},
        timeout=10,
    )
    mock_st.success.assert_called_once_with("Subscribed successfully!")


def test_subscribe_http_error(mocker, mock_st):
    mock_st.session_state = DotDict(access_token="test_token")
    mock_st.form_submit_button.return_value = True
    mock_st.text_input.return_value = "London"
    mock_st.number_input.return_value = 25.0

    mock_post = mocker.patch("frontend.dashboard.requests.post")
    mock_resp = Mock()
    mock_resp.text = "Server error"
    mock_post.side_effect = requests.exceptions.HTTPError(response=mock_resp)
    mock_st.error = Mock()

    dashboard.subscribe_page()

    mock_st.error.assert_called_once_with("Subscription failed: Server error")
