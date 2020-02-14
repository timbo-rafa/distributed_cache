# Demo couchbase server for playground purposes
# deploy and go to http://localhost:8091
docker run -t --name db -p 8091-8094:8091-8094 -p 11210:11210 couchbase/server-sandbox:6.5.0