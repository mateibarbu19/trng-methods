# True Random Number Generators - Methods

This repository is a testbench for my bachelor's degree project. Do not regard
it as anything more than a work in progess.

## Setup

This project was tested only with the Docker image I provided. You will find a
Bash script for setting up and running a Docker container that can interact with
a RTL-SDR device.

### Provided usage steps

1. Make sure Docker is installed on your host machine.
2. Clone this repository to your host machine.
3. Run start script and attach to the container.
4. Do whatever data acquisition and signal processing you like.

```bash
$ git https://github.com/mateibarbu19/trng-methods
$ cd trng-methods
$ ./start.sh
$ docker attach test_trng
(.venv) tester@test_trng:~/app$ python3 src/vlf.py --download --duration 5 --plot
```

### Troubleshooting

By default, Docker containers are run with limited permissions for security
reasons. You can use the `--privileged` flag to give the Docker container full
access to the host's devices, but this can be a security risk.

I used a more targeted approach, which uses the `--device` flag to give the
Docker container access to a specific device on the host.

If you're experiencing issues, it could be a permissions problem on the host
side. When Docker tries to pass through the USB device, the current user might
not have the necessary permissions to access it.

Here are some steps you can take to resolve this issue on a Linux host:

1. Find the vendor and product ID of your RTL-SDR dongle:

    ```bash
    $ lsusb | grep RTL2838 # query for the device
    Bus 001 Device 003: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T
    ```

    In this case, the vendor ID is `0bda` and the product ID is `2838`.

2. Create a new `udev` rule for the device. This will set the permissions for
   the device so that all users can read from and write to it. Create a file in
   `/etc/udev/rules.d/` and put the following line in it:

    ```
    SUBSYSTEM=="usb", ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="2838", MODE:="0666"
    ```

    Replace `0bda` and `2838` with the vendor and product ID of your device. The
    `MODE="0666"` sets the permissions so that all users can read from and write
    to the device.

3. Reload the udev rules with the following command:

    ```bash
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    ```

You can read more about this issue
[here](https://gitea.osmocom.org/sdr/rtl-sdr/src/branch/master/debian).
