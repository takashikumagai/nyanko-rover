#!/usr/bin/env bash

ps -aux | grep python3

echo "Terminating the process"
sudo pkill -f "python3 ./myserver.py"

ps -aux | grep python3
