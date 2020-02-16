# !/bin/bash
#

# UNSAFE!!
# TODO: ERASE LATER
CB_REST_USERNAME="Administrator"
CB_REST_PASSWORD="password"

set -e

echo "Deploying first cluster: ca-cluster"
# Run cluster container
docker run --name ca-cluster -d \
           -e CB_REST_USERNAME="$CB_REST_USERNAME" -e CB_REST_PASSWORD="$CB_REST_PASSWORD" \
           -p 8091-8094:8091-8094 -p 11210:11210 couchbase:6.5.0

# Run node container
echo "Deploying one extra node: ca-node1"
docker run --name ca-node1 -d \
           -e CB_REST_USERNAME="$CB_REST_USERNAME" -e CB_REST_PASSWORD="$CB_REST_PASSWORD" \
           -p 8081-8084:8091-8094 -p 11200:11210 couchbase:6.5.0

# Get IPS
CA_CLUSTER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ca-cluster)
CA_NODE1_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ca-node1)

echo -n "Waiting for ca-cluster to be ready."
until curl $CA_CLUSTER_IP:8091 >/dev/null 2>&1
do
  echo -n "."
  sleep 1s
done
echo -e "\nca-cluster ready!"

echo -n "Waiting for ca-node1 to be ready."
until curl $CA_NODE1_IP:8091 >/dev/null 2>&1
do
  echo -n "."
  sleep 1s
done
echo -e "\nca-node1 ready!"

echo "Starting ca-cluster's database"
docker exec ca-cluster \
  couchbase-cli cluster-init --cluster $CA_CLUSTER_IP \
                             --cluster-username $CB_REST_USERNAME \
                             --cluster-password $CB_REST_PASSWORD \
                             --services data,index \
                             --cluster-ramsize 512 --cluster-index-ramsize 256

echo "Adding ca-node1 to ca-cluster's database"
docker exec ca-cluster \
  couchbase-cli server-add -c localhost --server-add $CA_NODE1_IP \
                           --server-add-username $CB_REST_USERNAME \
                           --server-add-password $CB_REST_PASSWORD

echo "Rebalancing ca-cluster"
docker exec ca-cluster \
  couchbase-cli rebalance -c localhost

################################################################
# Repeat for second cluster
################################################################

echo "Deploying second cluster: br-cluster"
docker run --name br-cluster -d \
           -e CB_REST_USERNAME="$CB_REST_USERNAME" -e CB_REST_PASSWORD="$CB_REST_PASSWORD" \
           -p 8191-8194:8091-8094 -p 11310:11210 couchbase:6.5.0

echo "Deploying one extra node: br-node1"
docker run --name br-node1 -d \
           -e CB_REST_USERNAME="$CB_REST_USERNAME" -e CB_REST_PASSWORD="$CB_REST_PASSWORD" \
           -p 8181-8184:8091-8094 -p 11300:11210 couchbase:6.5.0

BR_CLUSTER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' br-cluster)
BR_NODE1_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' br-node1)

echo -n "Waiting for br-cluster to be ready."
until curl $BR_CLUSTER_IP:8091 >/dev/null 2>&1
do
  echo -n "."
  sleep 1s
done
echo -e "\nbr-cluster ready!"

echo -n "Waiting for br-node1 to be ready."
until curl $BR_NODE1_IP:8091 >/dev/null 2>&1
do
  echo -n "."
  sleep 1s
done
echo -e "\nbr-node1 ready!"

echo "Starting br-cluster's database"
docker exec br-cluster \
  couchbase-cli cluster-init --cluster $BR_CLUSTER_IP \
                             --cluster-username $CB_REST_USERNAME \
                             --cluster-password $CB_REST_PASSWORD \
                             --services data,index \
                             --cluster-ramsize 512 --cluster-index-ramsize 256

echo "Adding br-node1 to br-cluster's database"
docker exec br-cluster \
  couchbase-cli server-add -c localhost --server-add $BR_NODE1_IP \
                           --server-add-username $CB_REST_USERNAME \
                           --server-add-password $CB_REST_PASSWORD


echo "Rebalancing br-cluster"
docker exec br-cluster \
  couchbase-cli rebalance -c localhost

#################################################
# Bucket creation
#################################################

# docker exec ca-cluster \
#   couchbase-cli bucket-create -c $CA_CLUSTER_IP \
#                               --bucket $CACHE_DEFAULT_BUCKET \
#                               --bucket-type "couchbase" \
#                               --bucket-replica 1 \
#                               --max-ttl $CACHE_DEFAULT_TTL \
#                               --wait


#################################################
# XDCR
#################################################

echo "Setting br-cluster as a replication target in ca-cluster"
# Replication is actually set after bucket creation, 
docker exec ca-cluster \
  couchbase-cli xdcr-setup -c $CA_CLUSTER_IP --create \
                           --xdcr-cluster-name $BR_CLUSTER_IP --xdcr-hostname $BR_CLUSTER_IP \
                           --xdcr-username $CB_REST_USERNAME --xdcr-password $CB_REST_PASSWORD

echo "Setting ca-cluster as a replication target in br-cluster"
docker exec br-cluster \
  couchbase-cli xdcr-setup -c $BR_CLUSTER_IP --create \
                           --xdcr-cluster-name $CA_CLUSTER_IP --xdcr-hostname $CA_CLUSTER_IP \
                           --xdcr-username $CB_REST_USERNAME --xdcr-password $CB_REST_PASSWORD

echo "Demo database configuration done"
echo "Success!"