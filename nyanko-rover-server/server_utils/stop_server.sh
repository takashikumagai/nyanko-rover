#!/usr/bin/env bash

p=$(ps -aux | grep -E -m 1 nyanko-rover-server.+flask.+run)
q={$p}

echo "Terminating the process"
sudo pkill -f ${q[1]}

ps -aux | grep -E -m 1 nyanko-rover-server.+flask.+run
