#!/usr/bin/env bash

ps -aux | grep -E -m 1 nyanko-rover-server.+flask.+run

p=$(ps -aux | grep -E -m 1 nyanko-rover-server.+flask.+run)

# Convert the string into an array
q=($p)

echo "Terminating the process"
sudo pkill -f ${q[1]}

ps -aux | grep -E -m 1 nyanko-rover-server.+flask.+run

