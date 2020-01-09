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

# Copy the current directory contents into the container at /app
COPY . /app


# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt


# Run amla_core_code.py when the container launches
CMD python "./mla_core_code.py" 

