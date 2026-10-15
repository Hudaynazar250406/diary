from locust import HttpUser, task, between


class DiaryUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def view_groups(self):
        self.client.get("/groups")

    @task(1)
    def health(self):
        self.client.get("/health")