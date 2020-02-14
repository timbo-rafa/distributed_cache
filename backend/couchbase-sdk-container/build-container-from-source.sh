ROOT="$PWD"

apt-get update

# Build dependencies
BUILD_DEPENDENCIES="build-essential cmake git openjdk-11-jdk"
apt-get install -y $BUILD_DEPENDENCIES

# Couchbase dependencies
apt-get install -y python3-dev python3-pip python3-setuptools libev4 libev-dev libevent-dev libuv1-dev openssl libssl-dev

pip3 install scikit-build

### Couchbase's C SDK
## from source
cd "$ROOT"
git clone https://github.com/couchbase/libcouchbase
cd libcouchbase
git checkout tags/2.9.5
mkdir build
cd build
../cmake/configure
make
make install
make clean

pip3 install couchbase==3.0.0b3
### Couchbase's Python SDK
# from source
#cd "$ROOT"
#git clone https://github.com/couchbase/couchbase-python-client
#cd couchbase-python-client
#git checkout tags/2.5.10
#python3 setup.py build_ext --inplace
#pip3 install .

cd "$ROOT"
rm -Rf libcouchbase #couchbase-python-client

apt-get remove -y $BUILD_DEPENDENCIES
apt-get autoremove -y
