from geo_cache_client import Cache
import os
import subprocess
import time
import datetime

def get_docker_ip(container_name):
    ip = None
    try:
        ip = subprocess.check_output(["docker","inspect", "-f", '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}', container_name])
        ip = ip.strip().decode('utf-8')
    except Exception as e:
        return None
    return ip if ip else None

def main():
    """Example that sets a simple item in the cache
    and prints the replica from an external cluster possibly
    in another data center in another location.

    For demo purposes, all these nodes are assumed to run in the same machine,
    and there is an attempt to get these nodes ip using docker's cli.
    """    
    cache = Cache(name="example")
    montreal = {
        'lat': 45.5017,
        'lon':-73.5673
    }
    cache.set_closest_server(montreal["lat"], montreal["lon"])

    item = {
        'time' : str(datetime.datetime.now())
    }

    print('Saving "my_item":', item)
    response = cache.set("my_item", item).json()
    print(response)

    retrieved_item = cache.get("my_item").json()
    print("Retrieved Item:")
    print(retrieved_item)

    xdcr_ip = os.environ.get('XDCR_IP', get_docker_ip('br-cluster'))
    if not xdcr_ip:
        return
    xdcr_cache = Cache(name="example", db_host=xdcr_ip)
    xdcr_replica = xdcr_cache.get("my_item").json()
    print("Retrieved XDCR replica from {xdcrip}:".format(xdcrip=xdcr_ip))
    print(xdcr_replica)

if __name__ == "__main__":
    main()