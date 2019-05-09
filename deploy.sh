#!/usr/bin/env bash

# Description:
#   Upload the server application to the server
#   To be more exact, copies the 'nyanko-rover-server' directory to the user's home directory on the RPi (server).

#
# 1. Load configuration parameters (server IP address, ssh key path, etc.) from nyanko-rover-config.json
#

if [ ! -f nyanko-rover-config.json ]; then
    cp nyanko-rover-config.json.example nyanko-rover-config.json
    echo "Set the IP address of your RPi, and other properties to nyanko-rover-config.json and run this script again."
    exit 0
fi

# Read the first line of the text file and store it to a variable
server_ip_address=$(cat nyanko-rover-config.json | python3 -c "import sys, json; print(json.load(sys.stdin)['server_ip_address'])")

# SSH port
ssh_port=$(cat nyanko-rover-config.json | python3 -c "import sys, json; print(json.load(sys.stdin)['ssh_port'])")

# Read the pathname of the SSH key file
ssh_key=$(cat nyanko-rover-config.json | python3 -c "import sys, json; print(json.load(sys.stdin)['ssh_key'])")

# RPi login user
user=$(cat nyanko-rover-config.json | python3 -c "import sys, json; print(json.load(sys.stdin)['login_user'])")

echo $server_ip_address, $ssh_port, $ssh_key, $user

#
# 2. If the user specified '--clean' option, delete the current application on the server
#

# Note that we need to double quote the commands so that the bash shell will
# interpolate the $user before sending the command string to the remote host.
if [ "$1" = "--clean" ]; then
  ssh -i $ssh_key -o IdentitiesOnly=yes $user@$server_ip_address -p $ssh_port "rm -rf /home/$user/nyanko-rover-server"
fi

#
# 3. Upload the application in this directory to the server
#

# Make sure no trash will be sent to the server.
rm -f nyanko-rover-server/nyankoroverserver.log

# Copy the RPi-specific modules
# Replace the stub motor control functions (motor_control.py) with real ones (motor_control-rpi.py)
cp -f rpi/motor_control-rpi-queue.py nyanko-rover-server/motor_control.py
cp -f rpi/vcgencmd-rpi.py            nyanko-rover-server/vcgencmd.py
cp -f rpi/RPiCamera-rpi.py           nyanko-rover-server/camera/RPiCamera.py
cp -f rpi/server_params-rpi.json     nyanko-rover-server/server_params.json

# Send the package to the server
rsync -Parvz -e "ssh -i $ssh_key -o IdentitiesOnly=yes" nyanko-rover-server $user@$server_ip_address:/home/$user/

# Uncomment the RPi.GPIO dependency in Pipfile, i.e. replace '#RPi.GIPO' to 'RPi.GPIO'
# Note that backslashes are necessary to escape double quotes because sed command is double quoted.
# When you execute sed from terminal, they do not have to be escaped.
ssh -i $ssh_key -o IdentitiesOnly=yes $user@$server_ip_address -p $ssh_port "sed -i 's/^#\"RPi\.GPIO\"/\"RPi\.GPIO\"/' /home/$user/nyanko-rover-server/Pipfile"

# Similarly, uncomment the #picamera to picamera
ssh -i $ssh_key -o IdentitiesOnly=yes $user@$server_ip_address -p $ssh_port "sed -i 's/^#picamera/picamera/' /home/$user/nyanko-rover-server/Pipfile"

# Delete the old log file if there is one so that new log entries will not be appended to it.
ssh -i $ssh_key -o IdentitiesOnly=yes $user@$server_ip_address -p $ssh_port "rm -f /home/$user/nyanko-rover-server/nyankoroverserver.log"
