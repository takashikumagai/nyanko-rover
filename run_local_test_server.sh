#!/usr/bin/env bash

cp -f stub/motor_control-stub.py nyanko-rover-server/motor_control.py
cp -f stub/VideoStream-stub.py nyanko-rover-server/VideoStream.py
cd nyanko-rover-server
rm nyankoroverserver.log
./myserver.py
