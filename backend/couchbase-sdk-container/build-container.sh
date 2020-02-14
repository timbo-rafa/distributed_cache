apt-get update
apt-get install -y curl gnupg2 python3-dev python3-pip

### Couchbase's C SDK
##  from ubuntu repository
curl -L http://packages.couchbase.com/ubuntu/couchbase.key | apt-key add -
echo "deb http://packages.couchbase.com/ubuntu bionic bionic/main" > /etc/apt/sources.list.d/couchbase.list

apt-get update
apt-get install -y libcouchbase-dbg libcouchbase-dev libcouchbase2* #python3-setuptools libev4 libev-dev libevent-dev libuv1-dev openssl libssl-dev

### Couchbase's Python SDK
##  from pip package
pip3 install couchbase==2.5.10
#pip3 install couchbase==3.0.0b3

#apt-get autoremove -y
