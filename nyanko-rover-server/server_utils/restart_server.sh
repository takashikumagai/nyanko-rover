#!/usr/bin/env bash

dirpath=$(dirname $0)

# Stop if the server is running
sudo ${dirpath}/stop_server.sh

cd ${dirpath}/..

rm -f nyankoroverserver.log

./myserver.py &
