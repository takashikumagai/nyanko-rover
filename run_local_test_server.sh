#!/usr/bin/env bash

rm -rf __pycache__
cp -f stub/motor_control-stub.py   nyanko-rover-server/motor_control.py
cp -f stub/vcgencmd-stub.py        nyanko-rover-server/vcgencmd.py
cp -f stub/RPiCamera-stub.py       nyanko-rover-server/camera/RPiCamera.py
cp -f stub/server_params-stub.json nyanko-rover-server/server_params.json

cd nyanko-rover-server
rm -rf __pycache__
rm -f nyankoroverserver.log

# Start the local Flask server
pipenv run flask run --host=0.0.0.0
