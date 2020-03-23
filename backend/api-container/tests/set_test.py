import os
import requests
from cache_api import app
from flask_api import status

class Set_Test():
    def __init__(self):
        self.key = "set-key"
        self.name = "test"
        self.api_host = os.environ.get("API_IP", "172.17.0.1")
        self.port = os.environ.get("PORT", 5000)
        
        self.headers = {
            'content-type': 'application/json'
        }

        self.url = "http://{host}:{port}/api/{name}/{key}".format(
            host=self.api_host,
            port=self.port,
            name=self.name,
            key="{key}")

    def setUp(self):
        self.api = app.test_client()

    def cache_should_set_value_test(self):
        key = "set-key"
        value = "value"
        data = {
            "value" : value
        }

        url = self.url.format(key=key)
        response = self.api.post(url, headers=self.headers, json=data)

        assert response.status_code == status.HTTP_201_CREATED

    def cache_set_should_return_cas_test(self):
        key = "set-key"
        value = "value"
        data = {
            "value" : value
        }

        url = self.url.format(key=key)
        response = self.api.post(url, headers=self.headers, json=data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json['cas'] > 0

    ####################################
    ############ ERRORS ################
    ####################################

    def cache_set_should_fail_without_value_test(self):
        key = "set-key"
        data = {}

        url = self.url.format(key=key)
        response = self.api.post(url, headers=self.headers, json=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def cache_should_not_set_when_cas_differs_test(self):
        key = "set-key"
        value = "value"
        data = {
            "value" : value,
            "cas": 1
        }

        url = self.url.format(key=key)
        response = self.api.post(url, headers=self.headers, json=data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST