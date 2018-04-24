# Controlling RC Car via WiFi

## Overview

I've been trying to convert an affordable store-bought RC car into something more versatile and fun.
So far I installed an SBC (RPi 3) and can now drive the car forward and backward.
I'll see how this goes.

## Setup Guide

Follow the steps below to set up a few things. These are necessary to upload all the files to the server.


1. Create a key pair, with the private key unencrypted (hit the return key without typing anything else when they ask you a password saying 'Enter passphrase (empty for no passphrase):').

```
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa-rpi_ssh_server -C user@mymail.com
```

2. Copy the public key to the server.
Replace '192.168.10.100' with your local RPi server's IP address.

```
ssh-copy-id -i ~/.ssh/id_rsa-rpi_ssh_server user@192.168.10.100
```

3. Try logging in to the server via key-based authentication

```
ssh user@192.168.10.100 -i ~/.ssh/id_rsa-rpi_ssh_server
```

Make sure no one else gets their hands on your computer (remember your private key is not encrypted)


