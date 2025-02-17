from locust import HttpUser, task, between

class ApiUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def send_coin(self):
        self.client.post(
            "/api/sendCoin",
            json={"toUser": "user2", "amount": 1},
            headers={"Authorization": "Bearer <TOKEN>"}
        )