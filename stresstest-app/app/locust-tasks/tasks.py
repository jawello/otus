from locust import HttpUser, task, between, TaskSet, TaskSet
from faker import Faker
import json

fake = Faker()


class UserBehavior(TaskSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = fake.simple_profile(sex=None)
        self.login = self.profile['username']

    def on_start(self):
        self.client.post("/users", json.dumps({
            "first_name": self.profile['name'].split(' ')[0],
            "last_name": self.profile['name'].split(' ')[1],
            "login": self.profile['username'],
            "email": self.profile['mail'],
            "phone": fake.phone_number()
        }), headers={"Host": "arch.homework"})

    def on_stop(self):
        self.client.delete(f"/users/{self.login}", headers={"Host": "arch.homework"})

    @task(5)
    def get_all_users(self):
        self.client.get("/users", headers={"Host": "arch.homework"})

    @task(10)
    def get_current_user_info(self):
        self.client.get(f"/users/{self.login}", headers={"Host": "arch.homework"})

    @task(2)
    def change_current_user_info(self):
        new_profile = fake.simple_profile(sex=None)
        self.client.put(f"/users/{self.login}", json.dumps({
            "first_name": new_profile['name'].split(' ')[0],
            "last_name": new_profile['name'].split(' ')[1],
            "email": new_profile['mail'],
            "phone": fake.phone_number()
        }), headers={"Host": "arch.homework"})


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    min_wait = 1000
    max_wait = 6000