import pytest
import requests
from unittest.mock import Mock
from frontend import auth


class DotDict(dict):
    """Dict with attribute access and key membership compatibility."""
    __getattr__ = dict.get

    def __setattr__(self, name, value):
        self[name] = value


@pytest.fixture
def mock_st(mocker):
    mock_st = mocker.MagicMock()
    mock_st.session_state = DotDict()
    mocker.patch.object(auth, "st", mock_st)
    return mock_st


def test_login_success(mocker, mock_st):
    mock_post = mocker.patch("frontend.auth.requests.post")
    mock_post.return_value.raise_for_status.return_value = None
    mock_post.return_value.json.return_value = {"access_token": "test_token"}

    mock_st.form_submit_button.return_value = True
    mock_st.text_input.side_effect = ["test@example.com", "password123"]
    mock_st.rerun = Mock()

    auth.login_page()

    mock_post.assert_called_once_with(
        f"{auth.API_URL}/user/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert mock_st.session_state.access_token == "test_token"
    assert mock_st.session_state.authenticated is True
    assert mock_st.session_state.email == "test@example.com"
    mock_st.rerun.assert_called_once()


def test_login_http_error(mocker, mock_st):
    mock_post = mocker.patch("frontend.auth.requests.post")
    mock_post.side_effect = requests.exceptions.HTTPError()

    mock_st.form_submit_button.return_value = True
    mock_st.text_input.side_effect = ["test@example.com", "wrongpass"]
    mock_st.error = Mock()

    auth.login_page()

    mock_st.error.assert_called_once_with("Invalid credentials")


def test_register_password_mismatch(mocker, mock_st):
    mock_st.form_submit_button.return_value = True
    mock_st.text_input.side_effect = [
        "John", "Doe", "test@ex.com", "pass", "nopass"
    ]
    mock_st.error = Mock()

    auth.register_page()

    mock_st.error.assert_called_once_with("Passwords don't match")


def test_register_success(mocker, mock_st):
    mock_post = mocker.patch("frontend.auth.requests.post")
    mock_post.return_value.raise_for_status.return_value = None

    mock_st.form_submit_button.return_value = True
    mock_st.text_input.side_effect = [
        "John", "Doe", "test@ex.com", "pass", "pass"
    ]
    mock_st.success = Mock()

    auth.register_page()

    mock_post.assert_called_once_with(
        f"{auth.API_URL}/user/register",
        json={
            "name": "John",
            "surname": "Doe",
            "email": "test@ex.com",
            "password": "pass"
        },
    )
    mock_st.success.assert_called_once_with(
        "Registration successful! Redirecting to login..."
    )
    assert mock_st.session_state.show_login is True


def test_register_api_error(mocker, mock_st):
    mock_post = mocker.patch("frontend.auth.requests.post")
    mock_resp = Mock()
    mock_resp.json.return_value = {"detail": "Email already exists"}
    mock_post.side_effect = requests.exceptions.HTTPError(response=mock_resp)

    mock_st.form_submit_button.return_value = True
    mock_st.text_input.side_effect = [
        "John", "Doe", "test@ex.com", "pass", "pass"
    ]
    mock_st.error = Mock()

    auth.register_page()

    mock_st.error.assert_called_once_with("Error: Email already exists")
