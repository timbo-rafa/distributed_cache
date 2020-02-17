import requests

class Cache:
    def __init__(self,
            name,
            api_host="localhost",
            db_host=None,
            port=5000):
        """Cache constructor.
        
        :param name: the name as a string of the cache you want to connect to.
        :param api_host: the IP address of the cache API. Defaults to "localhost".
        :param db_host: the IP address of the actual cache. If not set, it is handled by API.
        :param port: the port of the cache API, defaults to 5000
        """

        self.name = name
        self.api_host = api_host
        self.db_host = db_host
        self.port = port

        self.headers = {
            'content-type': 'application/json'
        }

    def set_closest_server(self, lat, lon):
        """Connects the cache to the closest server.
        
        :param lat: Latitude of your location.
        :param lon: Longitude of your location.
        """
        url = "http://{host}:{port}/api/closest/{lat}/{lon}".format(
            host=self.api_host,
            port=self.port,
            lat=lat,
            lon=lon)

        response = requests.get(url, headers=self.headers)
        if response.ok:
            ip = response.json().get("ip")
            if ip is not None:
                self.api_host = ip
                self.db_host = None

    def get(self, key):
        """Retrieves an item of the specified key.
        
        :param key: The identifier string for the cache item to be retrieved.
        :return: The http request of the retrieved item as a dictionary,
        containing 'cas', 'value' keys if successful.
        The response needs to be parsed as a JSON.
        """
        url = "http://{host}:{port}/api/{name}/{key}".format(
            host=self.api_host,
            port=self.port,
            name=self.name,
            key=key)
        params = {}

        if self.db_host:
            params["databaseHost"] = self.db_host

        response = requests.get(url, headers=self.headers, params=params)
        return response
    
    def set(self, key, value, cas=None):
        """Sets an item of the specified key.
        
        :param key: The identifier string for the cache item to be set.
        :param value: The new value of the item.
        :param cas: The cas obtained from a previous operation.
        The set operation will only succeed if the cas has NOT changed
        since the last operation in which you retrieved the cas.
        :return: The http request of the updated item as a dictionary,
        containing 'cas', 'value' keys if successful.
        The response needs to be parsed as a JSON.
        """
        data = {
            "value": value
        }
        if cas is not None:
            data["cas"] = cas


        url = "http://{host}:{port}/api/{name}/{key}".format(
            host=self.api_host,
            port=self.port,
            name=self.name,
            key=key)
        params = {}

        if self.db_host:
            params["databaseHost"] = self.db_host
        
        response = requests.post(url, headers=self.headers, params=params, json=data)
        return response