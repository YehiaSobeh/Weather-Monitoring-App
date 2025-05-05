from unittest.mock import patch


def test_create_subscription_success(client):
    with patch('services.subscribe.is_subscribed', return_value=False), \
         patch('services.subscribe.send_subscription_email.delay'), \
         patch('crud.user.get_email_by_user_id',
               return_value="test@example.com"):
        response = client.post(
            "/api/v1/subscribe/create",
            json={"city": "Paris", "temperature_threshold": 20.5},
            headers={"Authorization": "Bearer mock-token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "Paris"


def test_duplicate_subscription(client):
    with patch('services.subscribe.is_subscribed',
               side_effect=[False, True]), \
         patch('services.subscribe.send_subscription_email.delay'), \
         patch('crud.user.get_email_by_user_id',
               return_value="test@example.com"):
        # first request succeeds
        response1 = client.post(
            "/api/v1/subscribe/create",
            json={"city": "London", "temperature_threshold": 15.0},
            headers={"Authorization": "Bearer mock-token"}
        )
        assert response1.status_code == 200

        # second request (same user+city) fails
        response2 = client.post(
            "/api/v1/subscribe/create",
            json={"city": "London", "temperature_threshold": 15.0},
            headers={"Authorization": "Bearer mock-token"}
        )
        assert response2.status_code == 400
        assert "already has a subscription" in response2.json()["detail"]
