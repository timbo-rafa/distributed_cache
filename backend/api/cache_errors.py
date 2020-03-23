from flask import Blueprint, jsonify
from flask_api import status
from werkzeug.exceptions import HTTPException
from couchbase.exceptions import CouchbaseError, AuthError, NetworkError, TemporaryFailError
from cache_exceptions import *

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(AuthError)
def auth_error(e):
    return jsonify(
        error=str(e),
        message=e.message,
        rc=e.rc
    ), status.HTTP_401_UNAUTHORIZED

@errors.app_errorhandler(NetworkError)
def network_error(e):
    return jsonify(
        error=str(e),
        message=e.message,
        rc=e.rc
    ), status.HTTP_500_INTERNAL_SERVER_ERROR

@errors.app_errorhandler(TemporaryFailError)
def temporary_error(e):
    # Operational couchbase error
    return jsonify(
        error=str(e),
        message=e.message
    ), status.HTTP_503_SERVICE_UNAVAILABLE

@errors.app_errorhandler(CouchbaseError)
def database_error(e):
    return jsonify(
        error=str(e),
        message=e.message,
        rc=e.rc
    ), status.HTTP_400_BAD_REQUEST

@errors.app_errorhandler(HTTPException)
def http_error(e):
    return jsonify(error=str(e)), e.code

@errors.app_errorhandler(ApiError)
def http_error(e):
    return jsonify(
        error=str(e),
        message=e.message
    ), status.HTTP_400_BAD_REQUEST

@errors.app_errorhandler(Exception)
def error_handler(e):
    print(e)
    return jsonify(error=str(e)), status.HTTP_500_INTERNAL_SERVER_ERROR