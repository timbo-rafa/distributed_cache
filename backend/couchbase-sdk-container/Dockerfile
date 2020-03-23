FROM python:3.7-alpine

RUN apk add --no-cache --virtual .build-deps \
        cmake alpine-sdk \
    && apk add --no-cache libcouchbase libcouchbase-dev \
    && pip install couchbase==2.5.10 \
    && apk del .build-deps

EXPOSE 8091-8096 11210-11211