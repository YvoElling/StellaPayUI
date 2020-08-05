#!/bin/bash

# Ping google DNS until connection is made upon startup
while ! timeout 0.2 ping -c 1 -n 8.8.8.8 &> /dev/null
do
    printf "Connecting..."
done
printf "Connected!"

# Change to the StellaPayUI directory
cd /home/pi/StellaPayUI || cd /home/yvoelling/Repositories/Python/StellaPayUI || exit

# Launch git pull to update the running StellaPay version to the latest available on the master
sudo git pull

# Start the StellaPay program
python3 StellaPay.py
exec bash



