#!/usr/bin/env bash

dirpath=$(dirname $0)

# Stop if the server is running
sudo ${dirpath}/stop_server.sh

cd ${dirpath}/..

rm -f nyankoroverserver.log

pipenv run flask run --host='0.0.0.0'
