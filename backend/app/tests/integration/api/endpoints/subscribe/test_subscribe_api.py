import pytest
from unittest.mock import patch, MagicMock, create_autospec
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from main import app
from api.deps import get_user_id_from_token, get_db

client = TestClient(app)

# Dependency overrides
@pytest.fixture(autouse=True)
def override_dependencies():
    def mock_get_user_id():
        return 1

    def mock_get_db():
        db = create_autospec(Session)
        db.add = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()
        return db

    app.dependency_overrides[get_user_id_from_token] = mock_get_user_id
    app.dependency_overrides[get_db] = mock_get_db
    yield
    app.dependency_overrides.clear()

def test_create_subscription_success():
    with patch('services.subscribe.is_subscribed', return_value=False), \
         patch('services.subscribe.send_subscription_email.delay'), \
         patch('crud.user.get_email_by_user_id', return_value="test@example.com"):
        
        response = client.post(
            "/api/v1/subscribe/create",
            json={"city": "Paris", "temperature_threshold": 20.5},
            headers={"Authorization": "Bearer mock-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "Paris"

def test_duplicate_subscription():
    with patch('services.subscribe.is_subscribed', side_effect=[False, True]), \
         patch('services.subscribe.send_subscription_email.delay'), \
         patch('crud.user.get_email_by_user_id', return_value="test@example.com"):
        
        response1 = client.post(
            "/api/v1/subscribe/create",
            json={"city": "London", "temperature_threshold": 15.0},
            headers={"Authorization": "Bearer mock-token"}
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            "/api/v1/subscribe/create",
            json={"city": "London", "temperature_threshold": 15.0},
            headers={"Authorization": "Bearer mock-token"}
        )
        
        assert response2.status_code == 400
        assert "already has a subscription" in response2.json()["detail"]
