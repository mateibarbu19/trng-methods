# Use Debian Bookworm as base image
FROM debian:bookworm

# Define the username as a build argument with a default value of 'tester'
ARG username=tester

# Set the shell to bash
SHELL ["/bin/bash", "-c"]

# Update the package list
RUN apt-get update -y

# Install system packages
RUN apt-get install -y python3 python3-pip python3-venv \
        ffmpeg sox rtl-sdr

# Create a new user with the username from the build argument
RUN useradd -ms /bin/bash $username

# Switch to the new user
USER $username

# Set the working directory to the user's home directory
WORKDIR /home/$username

# Create a Python virtual environment
RUN python3 -m venv venv

# Add the virtual environment activation to .bashrc
RUN echo $'\n\
# Virtual environment activation\n\
source ~/venv/bin/activate\n' >> .bashrc

# Install the python packages with the virtual environment activated
COPY requirements.txt .
RUN source venv/bin/activate && pip3 install --no-cache-dir -r requirements.txt
