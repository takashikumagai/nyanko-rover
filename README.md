# WiFi RC Car Project

## Overview

An experimental platform for controlling an RC car via WiFi using a raspberry pi. Intended for RC cars which are relatively small and have motors that are not overly powerful. It works like this:

1. Buy an RC car (cheap one recommended)
2. Convert RC car; rip off the stock ciruit board on the car and rewire motors and batteries with the PCB (I've somehow lost the URL of the instructable article my board is based on. Need to find it and put the URL here)
3. Install this project on RPi

## Components

### Hardware

- An RC car
- RPi 3 Model B
- A breadboard
- L293D motor driver
- jumper wires
- USB charger

### Software

- RPi 3 Model B
  - OS: Ubuntu 16.04 LTS Mate
  - Python version 3.x.x


## Setup Guide

Follow the steps below to set up a few things. These are necessary to upload all the files to the server.


#### 1. Create a key pair, with the private key unencrypted (hit the return key without typing anything else when they ask you a password saying 'Enter passphrase (empty for no passphrase):').

```
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa-rpi_ssh_server -C user@mymail.com
```

#### 2. Copy the public key to the server.
Replace '192.168.10.100' with your local RPi server's IP address.

```
ssh-copy-id -i ~/.ssh/id_rsa-rpi_ssh_server user@192.168.10.100
```

#### 3. Try logging in to the server via key-based authentication

```
ssh user@192.168.10.100 -i ~/.ssh/id_rsa-rpi_ssh_server
```

Make sure no one else gets their hands on your computer (remember your private key is not encrypted)

#### 4. Edit the sudoers file to enable password-less executions of reboot and shutdown commands.

Run

```
sudo visudo
```

from terminal to launch the editor, then add these lines:

```
# Need this to power off the device from web app GUI
username ALL=(ALL) NOPASSWD: /sbin/reboot, /sbin/shutdown

```

Replace username above with your user name.


