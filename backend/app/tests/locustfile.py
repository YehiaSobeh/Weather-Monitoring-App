from locust import HttpUser, task, between
from random import randint
import string

class FastAPIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.email = f"user{randint(1000, 9999)}@example.com"
        self.password = "testpassword"
        self.name = "Test"
        self.surname = "User"

        register_payload = {
            "name": self.name,
            "surname": self.surname,
            "email": self.email,
            "password": self.password
        }
        with self.client.post("/api/v1/user/register", json=register_payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Registration failed: {response.text}")
                return

        login_payload = {
            "email": self.email,
            "password": self.password
        }
        with self.client.post("/api/v1/user/login", json=login_payload, catch_response=True) as response:
            if response.status_code == 200:
                token = response.json().get("access_token")
                if token:
                    self.client.headers.update({"Authorization": f"Bearer {token}"})
                else:
                    response.failure("Login succeeded but no token received.")
            else:
                response.failure(f"Login failed: {response.text}")

    @task
    def load_dashboard(self):
        city = "Kazan"
        params = {"units": "metric"}  
        
        with self.client.get(f"/api/v1/weather/current/{city}", params=params, catch_response=True) as response:
            if response.status_code == 200:
                # Check if the request was completed within 3 seconds
                if response.elapsed.total_seconds() > 3:
                    response.failure(f"Fetching current weather took too long: {response.elapsed.total_seconds()} seconds")
                else:
                    pass
            else:
                response.failure(f"Failed to fetch current weather for {city}. Status code: {response.status_code}")
        with self.client.get(f"/api/v1/weather/history/{city}", catch_response=True) as response:
            if response.status_code == 200:
                if len(response.json()) == 0:
                    response.failure("No historical data received")
                else:
                    # Check if the request was completed within 3 seconds
                    if response.elapsed.total_seconds() > 3:
                        response.failure(f"Fetching weather history took too long: {response.elapsed.total_seconds()} seconds")
                    else:
                        pass  # Successful response
            else:
                response.failure(f"Failed to fetch weather history for {city}. Status code: {response.status_code}")
    @task
    def subscribe_to_alerts(self):
        with self.client.get("/api/v1/subscribe/create", catch_response=True) as response:
            if response.status_code == 200:
                pass
            else:
                response.failure(f"Failed to load subscribe page. Status code: {response.status_code}")
