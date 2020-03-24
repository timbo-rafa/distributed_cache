import flask
import json
import os
from flask import request, jsonify
from flask_api import status
from cache_singleton import CacheSingleton
from argparse import ArgumentParser
from cache_errors import errors
from cache_exceptions import *

import haversine
import settings

app = flask.Flask(__name__)
app.register_blueprint(errors)
app.config["DEBUG"] = True

# app cache key prefix
# so we can store some metadata as well
# with other prefixes
app_prefix = "bucket."
key_prefix = "data."
#geo_prefix = "geo."

@app.route('/')
def ping():
    return json.dumps({'success':True}), 200, {'Content-type':'application/json'}

@app.route('/api/<name>/<key>', methods=['GET'])
def get(name, key):
    """Cache get operation.
    
    :param name: name of the app, used to partition the cache memory space.
    :param key: key of the cache item to be retrieved.
    :return: the item with its cas, or an error.
    """
    cb_host = request.args.get('databaseHost')

    cache = CacheSingleton.get(name=app_prefix + name,
                        host=cb_host if cb_host != None else app.config["CB_HOST"],
                        port=app.config["PORT"],
                        ttl=app.config["TTL"],
                        xdcr_hosts=app.config["XDCR_HOSTS"])

    result = cache.get(key_prefix + key)

    if result.rc is 13:
        response = {
            'key': key,
            'rc': result.rc
        }
        return response, status.HTTP_404_NOT_FOUND

    response = {
        'key': key,
        'value': result.value,
        'cas': result.cas,
        'rc': result.rc
    }

    return response

@app.route('/api/<name>/<key>', methods=['POST'])
def set(name, key):
    """Cache set operation.
    
    :param name: name of the app, used to partition the cache memory space.
    :param key: key of the cache item to be set.
    :return: the item with its cas, or an error.
    """

    cb_host = request.args.get('databaseHost')
    
    req = request.get_json()

    value = req.get("value")
    cas = req["cas"] if 'cas' in req else 0

    if  value == None:
        raise MissingParameterError('"value" parameter not found')

    cache = CacheSingleton.get(name=app_prefix + name,
                            host=cb_host if cb_host != None else app.config["CB_HOST"],
                            port=app.config["PORT"],
                            ttl=app.config["TTL"],
                            xdcr_hosts=app.config["XDCR_HOSTS"])
    
    result = cache.set(key_prefix + key, value, cas)
    response = {
        'cas': result.cas,
        'key': key,
        'value': value,
        'rc': result.rc
    }
        
    return response, status.HTTP_201_CREATED

@app.route('/api/closest/<lat>/<lon>', methods=['GET'])
def closest(lat, lon):
    """Returns the API IP that is closest to the given location.
    
    :param lat: latitude of the client.
    :param lon: longitude of the client.
    :return: the closest API IP.
    """
    
    client_point = {
        'lat': float(lat),
        'lon': float(lon)
    }

    closest_ip = haversine.closest(settings.HOST_GEOLOCATION, client_point)
    closest_api_ip = settings.API_BY_DB[closest_ip]
    
    return {
        'ip': closest_api_ip
    }

def read_args(_args=None):
    parser = ArgumentParser()
    parser.add_argument('--couchbase-host')
    parser.add_argument('--couchbase-port')
    parser.add_argument('--ttl')
    args, unknown = parser.parse_known_args(_args)
    app.config["CB_HOST"] = args.couchbase_host if args.couchbase_host else os.environ.get('CB_HOST', settings.CB_HOST)
    app.config["PORT"] = args.couchbase_port if args.couchbase_port else os.environ.get('CB_PORT', settings.CB_PORT)
    app.config["TTL"] = args.ttl if args.ttl != None else os.environ.get('CB_TTL', settings.CB_TTL)
    app.config["XDCR_HOSTS"] = settings.CB_XDCR_HOSTS

read_args()
if __name__ == "__main__":
    app.run(host='0.0.0.0')