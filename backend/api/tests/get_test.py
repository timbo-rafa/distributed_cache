import os
import requests
from cache_api import app
from flask_api import status

class Get_Test():
    def __init__(self):
        self.key = "get-key"
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

        self.value = "get-value"
        data = {
            "value" : self.value
        }

        url = self.url.format(key=self.key)
        self.api.post(url, headers=self.headers, json=data)

    def cache_get_should_return_correct_value_test(self):
        key = "get-key"

        url = self.url.format(key=key)
        response = self.api.get(url, headers=self.headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json["value"] == self.value

    def cache_get_should_return_cas_test(self):
        key = "get-key"

        url = self.url.format(key=key)
        response = self.api.get(url, headers=self.headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json['cas'] > 0

    ####################################
    ############ ERRORS ################
    ####################################

    def cache_get_should_fail_for_invalid_key_test(self):
        key = "invalid"

        url = self.url.format(key=key)
        response = self.api.get(url, headers=self.headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND