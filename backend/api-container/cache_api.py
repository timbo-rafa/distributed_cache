import flask
import json
import os
from flask import request
from flask_api import status
from cache_singleton import CacheSingleton
from argparse import ArgumentParser
import haversine
import settings

app = flask.Flask(__name__)
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
    cb_host = request.args.get('databaseHost')

    cache = CacheSingleton.get(name=app_prefix + name,
                            host=cb_host if cb_host != None else app.config["CB_HOST"],
                            port=app.config["PORT"],
                            ttl=app.config["TTL"],
                            xdcr_hosts=app.config["XDCR_HOSTS"])

    try:
        result = cache.get(key_prefix + key)
        response = {
            'key': key,
            'value': result.value,
            'cas': result.cas,
            'rc': result.rc
        }

        return response

    except Exception as e:
        return {
            'error': str(e),
            'message': e.message,
            'rc' : e.rc
        }, status.HTTP_400_BAD_REQUEST

@app.route('/api/<name>/<key>', methods=['POST'])
def set(name, key):
    cb_host = request.args.get('databaseHost')
    
    req = request.get_json()

    value = req.get("value")
    cas = req.get("cas")

    if  value == None:
        return {
            'error': '"value" parameter is missing'
        }, status.HTTP_400_BAD_REQUEST
    cas = cas if cas != None else 0

    cache = CacheSingleton.get(name=app_prefix + name,
                            host=cb_host if cb_host != None else app.config["CB_HOST"],
                            port=app.config["PORT"],
                            ttl=app.config["TTL"],
                            xdcr_hosts=app.config["XDCR_HOSTS"])
    
    try:
        result = cache.set(key_prefix + key, value, cas)
        response = {
            'cas': result.cas,
            'key': key,
            'value': value,
            'rc': result.rc
        }
        
        return response, status.HTTP_201_CREATED

    except Exception as e:
        return {
            'error': str(e),
            'message': e.message,
            'rc' : e.rc
        }, status.HTTP_400_BAD_REQUEST

@app.route('/api/closest/<lat>/<lon>', methods=['GET'])
def closest(lat, lon):
    client_point = {
        'lat': float(lat),
        'lon': float(lon)
    }

    closest_ip = haversine.closest(settings.HOST_GEOLOCATION, client_point)
    closest_api_ip = settings.API_BY_DB[closest_ip]
    return {
        'ip': closest_api_ip
    }

def read_args():
    parser = ArgumentParser()
    parser.add_argument('--couchbase-host')
    parser.add_argument('--couchbase-port')
    parser.add_argument('--ttl')
    args, unknown = parser.parse_known_args()
    app.config["CB_HOST"] = args.couchbase_host if args.couchbase_host else os.environ.get('CB_HOST', settings.CB_HOST)
    app.config["PORT"] = args.couchbase_port if args.couchbase_port else os.environ.get('CB_PORT', settings.CB_PORT)
    app.config["TTL"] = args.ttl if args.ttl != None else os.environ.get('CB_TTL', settings.CB_TTL)
    app.config["XDCR_HOSTS"] = settings.CB_XDCR_HOSTS

read_args()
if __name__ == "__main__":
    app.run(host='0.0.0.0')