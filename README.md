
# Geo Distributed LRU Cache

## Dependencies (server)
This application heavily relies on
[Docker](https://docs.docker.com/install/)
for speedy installation and deployment. All the dependencies are already met if you use the provided docker containers.

However, if you are unable to use Docker, the server has the following dependencies:

1. Database
   
    1. [Couchbase Server](https://www.couchbase.com/downloads) 6.5.0 Enterprise
2. API
   
   1. [Python](https://www.python.org/downloads/) v3.7
   
   2. [Couchbase C Client](https://docs.couchbase.com/c-sdk/2.10/start-using-sdk.html) v2.10.5

   3. [Couchbase Python Client](https://docs.couchbase.com/python-sdk/current/start-using-sdk.html) v.2.9.5

You can also check the Dockerfile scripts under `backend/` for installation steps.

## Dependencies (client)

```python
pip install geo-cache-client
```
Alternatively, you can make http requests as described in `geo_cache_client/cache_client.py`

## Installation (demo)

In an enterprise production environment, the different components of this application are likely to be deployed in different nodes and possibly different machines. The final deployment is therefore dependant on the back-end architecture and DevOps of such company. For demo purposes, we provide a sample application in which all components run under the same machine, as a starting point for developers.

To keep things simple, credentials are the same for all clusters and nodes, geolocations are stored in the settings, and we use docker to get the proper IPs. In a real environment, this kind of information could be processed differently.

To setup the demo back-end cluster, run:

```bash
    git clone https://github.com/timbo-rafa/geo-cache
    cd geo-cache
    # set credentials
    export CB_REST_USERNAME="Administrator"
    export CB_REST_PASSWORD="password"
    bash scripts/deploy-database.sh
    bash scripts/deploy-api.sh
```
If you'd like to see the database dashboard, couchbase provides one at http://localhost:8091/ui/index.html

Next, to install the client:

```
pip install geo-cache-client
```

The programs under the folder `examples` provides some sample usage:

```bash
python examples/concurrency.py
python examples/replication.py
```

# Solution 

In order to quickly come up with a scalable enterprise-level library, the optimal approach is to delegate as much features as we can to an already existing software package and use it as an underlying architecture.

Upon researching current technologies available, an ideal software seems to be the [Couchbase Server](https://docs.couchbase.com/server/6.5/introduction/intro.html), a distributed multi-model NoSQL document-oriented database. Amongst the key features we have high availability, scale-out architecture, and a memory-first architecture, the ideal scenario for our cache. Essential requirements for our application are detailed below on the section [Features](#Features).

Couchbase stores data through a concept
[Buckets](https://docs.couchbase.com/server/6.5/learn/buckets-memory-and-storage/buckets-memory-and-storage.html),

>Couchbase Server keeps items in Buckets. Before an item can be saved, a bucket must exist for it. Each bucket is assigned a name at its creation: this name is referenced by the application or user wishing to save or access items within it.

This is how we store data in our application. We access couchbase through its Python SDK and expose our API using Flask.

## Features

### 1 - Simple integration

```
pip install geo-cache-client
```

### 2 - Resilient to network failures and crashes

Resiliency is achieved through 4 properties:

##### Data replication (within a cluster)

>Replicas provide protection against data loss by keeping copies of a bucket’s data on multiple servers.

On bucket creation (or editing), it is possible to set the number of replicas.
For our demo, we set `--bucket-replica 1`.

For more information, please see
[bucket-create](https://docs.couchbase.com/server/6.5/cli/cbcli/couchbase-cli-bucket-create.html)
or
[bucket-edit](https://docs.couchbase.com/server/6.5/cli/cbcli/couchbase-cli-bucket-edit.html).

##### Data persistence
Couchbase buckets are written to disk by setting `--bucket-type couchbase`.
For more information, please see [bucket-create](https://docs.couchbase.com/server/6.5/cli/cbcli/couchbase-cli-bucket-create.html).

Data replication and persistence prevents our system from losing data in case of node crashes or failures.

##### Automatic failover

>Failover is a process whereby a failed node can be taken out of a cluster with speed.

For more information, please see
[Failover](https://docs.couchbase.com/server/current/learn/clusters-and-availability/failover.html)
and
[auto-failover command](https://docs.couchbase.com/server/4.5/cli/cbcli/setting-autofailover.html).

##### Cross Data Center Replication (XDCR)

[Cross Data Center Replication (XDCR)](https://docs.couchbase.com/server/6.5/manage/manage-xdcr/xdcr-management-overview.html)
allows us to continuously replicate data from a bucket on one cluster to another bucket in another cluster, possibly located in another geolocation.
This makes our system still able to deliver and even more fault-tolerant, should a data center become unavailable.

### 3 - Near real time replication of data across Geolocation. Writes need to be in real time.

This requirement is achieved through [XDCR](https://docs.couchbase.com/server/6.5/manage/manage-xdcr/xdcr-management-overview.html).

### 4 - Data consistency across regions

Achieved through
[XDCR](https://docs.couchbase.com/server/6.5/manage/manage-xdcr/xdcr-management-overview.html).
You can assure consistency by passing the 
[CAS](https://docs.couchbase.com/server/4.1/developer-guide/cas-concurrency.html)
value from a previous operation to a `cache.set` operation.

### 5 - Locality of reference, data should almost always be available from the closest region

Supported with
[XDCR](https://docs.couchbase.com/server/6.5/manage/manage-xdcr/xdcr-management-overview.html).
You can connect to the closest server by using  `GET /closest/<lat>/<long>`. This ensures that data will first be written to and read from the closest region.

### 6 - Flexible Schema

The cache stores a key-value pair of strings and it is agnostic to the actual data value. We can therefore "stringify" any object in a JSON-like manner, achieving a flexible schema.

Additionally, couchbase is a NoSQL document-oriented database and also has flexible schema, if needed be in further development.

### 7 - Cache can expire
On bucket creation or editing, we can specify the maximum TTL (time-to-live) for all documents in a bucket in seconds.

You can set the environment variable `CB_TTL` on the cache api to set the TTL of data.

For more information, please see
[bucket-create](https://docs.couchbase.com/server/6.5/cli/cbcli/couchbase-cli-bucket-create.html).
### 8 - LRU

Couchbase default ejection policy for persistent storage is `valueOnly`, which keeps only keys in memory. With that in mind, memory eviction uses a simplified version of LRU,
[not recently used (NRU)](https://docs.couchbase.com/server/4.1/architecture/db-engine-architecture.html#not-recently-used-nru-items).

## Future Improvements

1. Fine-grained credentials
2. Geolocation processing
3. Non-default cb port
4. `settings.py` for cache_couchbase
5. Check if node is up before returning closest
6. Select fastest ping db cluster instead of closest (?)
7. [Choose threading strategy](https://docs.couchbase.com/python-sdk/2.0/threads.html)