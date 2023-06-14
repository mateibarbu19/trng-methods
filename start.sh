#!/bin/bash

# Set the working directory and name of the Docker container
workdir="/home/tester/app"
name="test_trng"

# Build the Docker image
docker build -t trng .

# If the build failed, exit with an error
if [ $? -ne 0 ]; then
    echo "Docker build failed" >&2
    exit 2
fi

# Get the device file for the RTL-SDR dongle
device=$(lsusb | grep RTL2838 | awk '{print "/dev/bus/usb/" $2 "/" $4}' | tr -d ':')

# Check if the device file exists
if [ ! -e "$device" ]; then
    echo "Device not found, running without device" >&2
    device="/dev/null"
fi

# Run the Docker
docker run                      \
    --detach                    \
    --name "$name"              \
    --hostname "$name"          \
    --device "$device"          \
    --volume "$PWD:$workdir"    \
    --workdir "$workdir"        \
    -it                         \
    --rm                        \
    trng