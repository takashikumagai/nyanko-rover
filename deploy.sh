#!/usr/bin/env bash

# Description:
#   Upload the server application to the server
#   To be more exact, copies the 'nyanko-rover-server' directory to the user's home directory on the RPi (server).

#
# 1. Load configuration parameters (server IP address, ssh key path, etc.) from nyanko-rover-config.json
#

ssh_remote_host=$1

if [ -z "${ssh_remote_host}" ]; then
    echo "Specify an ssh host defined in ~/.ssh/config as the first argument"
    exit 1
fi

# First user_env_var_on_remote_host will get a value like USER=someuser
user_env_var_on_remote_host=$(ssh ${ssh_remote_host} printenv | grep USER=)
user=${user_env_var_on_remote_host:5}

if [ ! -f nyanko-rover-config.json ]; then
    cp nyanko-rover-config.json.example nyanko-rover-config.json
    echo "Set the IP address of your RPi, and other properties to nyanko-rover-config.json and run this script again."
    exit 0
fi

#
# 2. If the user specified '--clean' option, delete the current application on the server
#

# Note that we need to double quote the commands so that the bash shell will
# interpolate the $user before sending the command string to the remote host.
if [ "$1" = "--clean" ]; then
  ssh ${ssh_remote_host} "rm -rf /home/${user}/nyanko-rover-server"
fi

#
# 3. Upload the application in this directory to the server
#

# Make sure no trash will be sent to the server.
rm -f nyanko-rover-server/nyankoroverserver.log

# Send the package to the server
rsync -Parvzz nyanko-rover-server ${ssh_remote_host}:/home/${user}/

remote_host_dir=/home/${user}/nyanko-rover-server

# Copy the RPi-specific modules
# Replace the stub motor control functions (motor_control.py) with real ones (motor_control-rpi.py)
rsync -Parvzz rpi/motor_control-rpi-queue.py    ${ssh_remote_host}:${remote_host_dir}/motor_control.py
rsync -Parvzz rpi/vcgencmd-rpi.py               ${ssh_remote_host}:${remote_host_dir}/vcgencmd.py
rsync -Parvzz rpi/RPiCamera-rpi.py              ${ssh_remote_host}:${remote_host_dir}/camera/RPiCamera.py
rsync -Parvzz rpi/server_params-rpi.json        ${ssh_remote_host}:${remote_host_dir}/server_params.json
# rsync these files the same way but no name changes with them
rsync -Parvzz rpi/motor_controller_TEU_105BK.py ${ssh_remote_host}:${remote_host_dir}/
rsync -Parvzz rpi/motor_controller_L293D.py     ${ssh_remote_host}:${remote_host_dir}/
rsync -Parvzz rpi/esc_tester.py                 ${ssh_remote_host}:${remote_host_dir}/

# Uncomment the RPi.GPIO dependency in Pipfile, i.e. replace '#RPi.GIPO' to 'RPi.GPIO'
# Note that backslashes are necessary to escape double quotes because sed command is double quoted.
# When you execute sed from terminal, they do not have to be escaped.
ssh ${ssh_remote_host} "sed -i 's/^#\"RPi\.GPIO\"/\"RPi\.GPIO\"/' ${remote_host_dir}/Pipfile"

# Similarly, uncomment the #picamera to picamera
ssh ${ssh_remote_host} "sed -i 's/^#picamera/picamera/' ${remote_host_dir}/Pipfile"

# Delete the old log file if there is one so that new log entries will not be appended to it.
ssh ${ssh_remote_host} "rm -f ${remote_host_dir}/nyankoroverserver.log"
