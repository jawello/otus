from locust import HttpUser, task, TaskSet, SequentialTaskSet
from random import randint
from faker import Faker
import json

fake = Faker('ru_RU')


class UserBehavior(SequentialTaskSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_strings = fake.words(nb=randint(1, 20))
        self.prev_response = []
        self.i = 0

    @task
    def search_product(self):
        if self.i >= len(self.search_strings):
            self.interrupt()
        with self.client.get(f"""/products_search?name={self.search_strings[self.i]}""",
                             headers={"Host": "arch.homework"}, catch_response=True, name="/product_search") \
                as response:
            if response.status_code == 200:
                if response.text:
                    self.prev_response = json.loads(response.text)
            elif response.status_code != 200:
                response.failure("Got wrong response")
            elif response.elapsed.total_seconds() > 2:
                response.failure("Request took too long")

    def get_random_word_from_response(self):
        words_list = self.prev_response[randint(0, len(self.prev_response) - 1)]['name'].split(' ')
        return words_list[randint(0, len(words_list)-1)]

    @task
    def search_specific_product(self):
        if self.prev_response:
            self.client.get(
                f"""/products_search?name={self.search_strings[self.i]} {self.get_random_word_from_response()}""",
                headers={"Host": "arch.homework"}, name="/product_search/specific")
        self.i += 1


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    min_wait = 1000
    max_wait = 6000
