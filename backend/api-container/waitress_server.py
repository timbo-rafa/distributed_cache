import waitress
from cache_api import app

waitress.serve(app, host="0.0.0.0", port=5000)