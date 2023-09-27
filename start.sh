#!/bin/bash

# Use default user in the Dockerfile
user=$(grep '^ARG username' Dockerfile | awk -F'[ =]' '{print $3}')

# Set the working directory and name of the Docker container
workdir="/home/$user/lab"
image_name="trng"
container_name="test_${image_name}"

# Build the Docker image
docker build -t "$image_name" .

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

# Run the Docker in detached mode
docker run                          \
    --detach                        \
    --name "$container_name"        \
    --hostname "$container_name"    \
    --device "$device"              \
    --network host                  \
    --volume "$PWD:$workdir"        \
    --workdir "$workdir"            \
    -it                             \
    --rm                            \
    "$image_name"

# If the Docker run failed, exit with an error
if [ $? -ne 0 ]; then
    echo "Docker run failed" >&2
    exit 3
fi
