from cache_couchbase2 import CacheCouchbase2

class CacheSingleton:
    """Singleton to avoid creating couchbase objects and database connections
    multiple times.
    """
    __cacheInstances = {}
    @staticmethod
    def get(name, host, port, ttl, xdcr_hosts):    
        key = "{name}@{host}:{port}"
        cache = CacheSingleton.__cacheInstances.get(key)

        if cache == None:
            CacheSingleton.__cacheInstances[key] = CacheCouchbase2(name=name,
                host=host, 
                port=port,
                ttl=ttl,
                xdcr_hosts=xdcr_hosts)
            cache = CacheSingleton.__cacheInstances[key]
        return  cache
