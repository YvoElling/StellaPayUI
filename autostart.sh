#!/bin/bash

# Ping google DNS until connection is made upon startup
#while ! timeout 0.2 ping -c 1 -n 8.8.8.8 &> /dev/null
#do
#    printf "Connecting..."
#    sleep 1
#done
#printf "Connected!"

# CD to the current directory of the script
cd "${0%/*}"

# Launch git pull to update the running StellaPay version to the latest available on the master
sudo git pull

# Start the StellaPay program
python3 StellaPay.py
exec bash



