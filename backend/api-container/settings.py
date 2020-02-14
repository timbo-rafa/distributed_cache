import subprocess
import socket
import os

BR_CLUSTER_IP=os.environ.get('BR_CLUSTER_IP')
CA_CLUSTER_IP=os.environ.get('CA_CLUSTER_IP')

CB_HOST=BR_CLUSTER_IP
CB_PORT=8091
CB_TTL=60*60*4 # 4 hrs

CB_XDCR_HOSTS = {}
CB_XDCR_HOSTS[BR_CLUSTER_IP] = [CA_CLUSTER_IP]
CB_XDCR_HOSTS[CA_CLUSTER_IP] = [BR_CLUSTER_IP]

HOST_GEOLOCATION = {}
HOST_GEOLOCATION[BR_CLUSTER_IP] = {
        "lat": -23.5505,
        "lon": -46.6333
}
HOST_GEOLOCATION[CA_CLUSTER_IP] = {
        "lat": 43.6532,
        "lon": -79.3832
}

API_IP = socket.gethostbyname(socket.gethostname())
API_BY_DB = {}
API_BY_DB[BR_CLUSTER_IP] = API_IP
API_BY_DB[CA_CLUSTER_IP] = API_IP