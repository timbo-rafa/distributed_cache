FROM timborafa/couchbase-python-sdk:2

WORKDIR /api
COPY . .
RUN pip3 install -r requirements.txt && rm requirements.txt

ENTRYPOINT [ "python3", "waitress_server.py"]
EXPOSE 5000 8091