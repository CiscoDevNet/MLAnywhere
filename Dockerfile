# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Set ENV VARS
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=0
ENV PLATFORM=linux
ENV K8SVERSION=1.14.0

# Set the working directory to /app
WORKDIR /app


# Install for ssh-keygen
RUN apt-get update && apt-get install -y \
curl \
wget


# Install kubectl
RUN wget https://storage.googleapis.com/kubernetes-release/release/v${K8SVERSION}/bin/${PLATFORM}/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/


#Upgrade pip
RUN pip install --no-cache-dir --upgrade pip


# Copy the current directory contents into the container at /app
COPY . /app


# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt


WORKDIR /app/mla_app_code


# Run amla_core_code.py when the container launches

ENTRYPOINT ["python", "-u","./mla_core_code.py" ]
