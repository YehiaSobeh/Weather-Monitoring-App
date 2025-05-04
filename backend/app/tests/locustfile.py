from locust import HttpUser, task, between
import random
import string

class APIUser(HttpUser):
    # simulate a real user waiting 1–3 seconds between actions
    wait_time = between(1, 3)

    @task(10)
    def create_user_burst(self):
        # high-volume user creation
        name = ''.join(random.choices(string.ascii_letters, k=8))
        email = f"{name.lower()}@example.com"
        self.client.post("/users/", json={"name": name, "email": email})

    @task(5)
    def list_users_steady(self):
        # steady stream of listing
        self.client.get("/users/")

    @task(5)
    def get_random_user(self):
        # mix of reads at random IDs
        user_id = random.randint(1, 1000)
        self.client.get(f"/users/{user_id}")

    @task(3)
    def login_load(self):
        # simulate login load
        self.client.post("/login", json={
            "email": "loaduser@example.com",
            "password": "password123"
        })

    @task(1)
    def delete_user(self):
        # occasional delete
        user_id = random.randint(1, 1000)
        self.client.delete(f"/users/{user_id}")
