from locust import HttpUser, task, between
from random import randint
import time


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
        with self.client.post(
            "/api/v1/user/register",
            json=register_payload,
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Registration failed: {response.text}")
                return

        login_payload = {
            "email": self.email,
            "password": self.password
        }
        with self.client.post(
            "/api/v1/user/login",
            json=login_payload,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                token = response.json().get("access_token")
                if token:
                    self.client.headers.update(
                        {"Authorization": f"Bearer {token}"})
                else:
                    response.failure("Login succeeded but no token received.")
            else:
                response.failure(f"Login failed: {response.text}")

    @task
    def load_dashboard(self):
        city = "kazan"
        params = {"units": "metric"}

        # Fetch current weather
        with self.client.get(
            f"/api/v1/weather/current/{city}",
            params=params,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                if response.elapsed.total_seconds() > 3:
                    response.failure(
                        f"Fetching current weather took too long: "
                        f"{response.elapsed.total_seconds()} seconds"
                    )
            else:
                response.failure(
                    f"Failed to fetch current weather for {city}. "
                    f"Status code: {response.status_code}"
                )

        # Fetch weather history
        with self.client.get(
            f"/api/v1/weather/history/{city}",
            headers={
                "Authorization":
                f"Bearer {self.client.headers['Authorization'].split()[1]}",
                "Accept": "application/json"
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if len(data) == 0:
                        response.failure("No historical data received")
                    elif response.elapsed.total_seconds() > 3:
                        response.failure(
                            f"Fetching weather history took too long: "
                            f"{response.elapsed.total_seconds()} seconds"
                        )
                    else:
                        required_keys = {
                            "city", "temperature", "humidity",
                            "wind_speed", "pressure",
                            "fetched_at", "updated_at"
                        }
                        for record in data:
                            if not required_keys.issubset(record):
                                response.failure(
                                    "Incomplete weather data structure")
                                break
                        else:
                            response.success()
                except Exception as e:
                    response.failure(f"Error parsing JSON: {e}")
            else:
                response.failure(
                    f"Failed to fetch weather history for {city}. "
                    f"Status code: {response.status_code}"
                )

    @task
    def subscribe_to_alerts(self):
        time.sleep(1)  # simulate user thinking before subscribing
        payload = {
            "city": "kazan",
            "temperature_threshold": 0
        }

        with self.client.post(
            "/api/v1/subscribe/create",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"Subscription failed. Status code: "
                    f"{response.status_code}, Response: {response.text}"
                )
            else:
                time.sleep(1)
