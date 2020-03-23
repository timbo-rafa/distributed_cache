# Python wrapper for some API functions
# missing on the couchbase-python-client SDK
import requests
import sys

class CouchbaseException(Exception):
    pass

# Couchbase Python API is missing max_ttl
# https://docs.couchbase.com/server/current/rest-api/rest-bucket-create.html
def createBucket(
    host,
    username,
    password,
    name,
    bucketType,
    ramQuotaMB,
    replicaNumber,
    maxTTL,
    port=8091):
    
    data = {
        'name': name,
        'bucketType': bucketType,
        'ramQuotaMB': ramQuotaMB,
        'replicaNumber': replicaNumber,
        'maxTTL': maxTTL
    }

    url = "{host}:{port}".format(host=host, port=port)

    response = requests.post(
        "http://{url}/pools/default/buckets".format(url=url),
        auth=(username, password),
        data=data)

    if not response.ok:
            raise CouchbaseException(response.text)
    return response

# https://docs.couchbase.com/server/current/rest-api/rest-xdcr-create-replication.html
def createXDCR(
        host,
        username,
        password,
        fromBucket,
        toCluster,
        toBucket,
        port=8091):
    """Creates a replication between two data centers.
    
    :param host: IP address of source cluster
    :param port: port of source cluster
    :param username: username of source cluster
    :param password: password of source cluster
    :param fromBucket: source bucket to replicate
    :param toCluster: IP address of target cluster
    :param toBucket: target bucket for replicas
    """                                        
    
    data = {
        'replicationType': "continuous",
        'toCluster': toCluster,
        'fromBucket': fromBucket,
        'toBucket': toBucket
    }

    url = "{host}:{port}".format(host=host, port=port)
    response = requests.post(
        "http://{url}/controller/createReplication".format(url=url),
        auth=(username, password),
        data=data)

    if not response.ok:
        print(response.text, file=sys.stderr)
        #raise CouchbaseException(response.text)

    return response

# def listXDCRReferecences(
#         host,
#         username,
#         password,
#         port=8091):
#     """List replications of a cluster.
    
#     :param host: IP address of cluster
#     :param port: port of cluster
#     :param username: username of source cluster
#     :param password: password of source cluster
#     """                                        

#     url = "{host}:{port}".format(host=host, port=port)
#     response = requests.get(
#         "http://{url}/pools/default/remoteClusters".format(url=url),
#         auth=(username, password))

#     if not response.ok:
#         raise CouchbaseException(response.text)

#     return response.json()