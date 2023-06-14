# Use Debian Bookworm as base image
FROM debian:bookworm

# Set the shell to bash
SHELL ["/bin/bash", "-c"]

# Update the package list
RUN apt-get update -y

# Install system packages
RUN apt-get install -y python3 python3-pip python3-venv \
        ffmpeg sox rtl-sdr

# Create a new user 'tester'
RUN useradd -ms /bin/bash tester

# Switch to the new user
USER tester

# Set the working directory to the user's home directory
WORKDIR /home/tester

# Create a Python virtual environment
RUN python3 -m venv .venv

# Add the virtual environment activation to .bashrc
RUN echo $'\n\
# Virtual environment activation\n\
source ~/.venv/bin/activate\n' >> .bashrc

# Install the python packages with the virtual environment activated
COPY requirements.txt .
RUN source .venv/bin/activate && pip3 install --no-cache-dir -r requirements.txt
