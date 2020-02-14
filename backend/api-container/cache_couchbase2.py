import os
import socket
import time
from itertools import repeat
from couchbase.cluster import Cluster
from couchbase.cluster import PasswordAuthenticator
from couchbase.admin import Admin
from couchbase_wrapper import createXDCR
from couchbase_wrapper import createBucket

class CacheCouchbase2:
    """Geo distributed cache based on Couchbase Server 2"""
    def __init__(self,
            name=None,
            host=None,
            port=None,
            username=None,
            password=None,
            ttl=None,
            ram_quota_mb=None,
            xdcr_hosts=None):
        """Cache Constructor.
        
        :param name: name of couchbase bucket to use. Defaults to env var "CB_BUCKET", else "cache"
        :param host: IP address of couchbase server. Defaults to env var "CB_HOST", else attempts to socket.gethostbyname.
        :param port: port of couchbase server. Defaults to env var "CB_PORT", else "8091"
        :param username: username of couchbase server. Defaults to env var CB_REST_USERNAME, else "Administrator"
        :param password: password of couchbase server. Defaults to env var CB_DEFAULT_BUCKET, else "password"
        :param ram_quota_mb: memory quota of buckets, in mb. Defaults to env var CB_BUCKET_RAM_QUOTA_MB, else 256
        :param bucket_ttl: max time-to-live of items. Defaults to env var CB_TTL, else 4hrs
        :param xdcr_hosts: dict of key-value pairs, where key is the source IP and value is a list of target IPs
        """        
        self.host = host if host else os.environ.get('CB_HOST', socket.gethostbyname(socket.gethostname()))
        self.port = port if port else os.environ.get('CB_PORT', '8091')
        self.username = username if username else os.environ.get('CB_REST_USERNAME', 'Administrator')
        self.password = password if password else os.environ.get('CB_REST_PASSWORD', 'password')
        self.name = name if name else os.environ.get('CB_BUCKET', 'cache')
        self.ram_quota = ram_quota_mb if ram_quota_mb else os.environ.get('CB__RAM_QUOTA_MB', 256)
        self.ttl = ttl if ttl != None else os.environ.get('CB_TTL', 60*60*4)
        self.xdcr_hosts = xdcr_hosts

        self.cluster = Cluster('couchbase://{host}:{port}'.format(host=host,port=port))
        self.cluster.authenticate(PasswordAuthenticator(self.username, self.password))

        self.__bucket_create(self.cluster, self.host, sync=True)
        self.__xdcr_create()
        self.bucket = self.cluster.open_bucket(self.name)

    def __bucketExists(self, cluster, bucket_name):
        buckets = [b.name() for b in cluster.cluster_manager().buckets_list()]
        return bucket_name in buckets

    def __bucket_create(self, cluster, host, sync=False):
        # At time of development, python api was missing max_ttl parameter
        # self.cluster.cluster_manager().bucket_create(
        #     self.name,
        #     bucket_type="couchbase",
        #     replicas=1, ram_quota=256)
        
        if self.__bucketExists(cluster, self.name):
            return

        res = createBucket(
            host=host,
            port=self.port,
            username=self.username,
            password=self.password,
            name=self.name,
            bucketType="couchbase",
            replicaNumber=1,
            maxTTL=self.ttl,
            ramQuotaMB=self.ram_quota)

        if sync:
            cluster.cluster_manager().wait_ready(self.name, timeout=60, sleep_interval=0.8)
        
    def __xdcr_create(self):
        """Creates replications between host and xdcr_hosts.
        """        
        if not self.xdcr_hosts:
            return
        if not isinstance(self.xdcr_hosts, dict):
            print("xdcr_hosts not a dictionary. Ignoring")
            return

        for xdcr_host in self.xdcr_hosts[self.host]:
            xdcr_cluster = Cluster('couchbase://' + xdcr_host)
            xdcr_cluster.authenticate(PasswordAuthenticator(self.username, self.password))

            # Create bucket in External Cluster
            self.__bucket_create(xdcr_cluster, xdcr_host, sync=True)

            # host > external
            createXDCR(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                fromBucket=self.name,
                toCluster=xdcr_host,
                toBucket=self.name)

            # external > host
            if self.host in self.xdcr_hosts[xdcr_host]:
                createXDCR(
                    host=xdcr_host,
                    username=self.username,
                    password=self.password,
                    fromBucket=self.name,
                    toCluster=self.host,
                    toBucket=self.name)

    def get(self, key):
        """Get item from cache.
        
        :param key: item key
        :return: the value and cas of the item as a tuple.
        """

        result = self.bucket.get(key, replica=True, quiet=True)
        return result

    def set(self, key, value, cas=0):
        """Set an item.
        
        :param key: item key.
        :param value: value of the item.
        :param cas: (optional) cas (Check and Set)
        """

        result = self.bucket.upsert(key, value, cas)
        return result