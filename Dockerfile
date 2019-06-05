# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Set ENV VARS
ENV FLASK_ENV=development

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN pwd

WORKDIR /app/mla_app_code

RUN pwd

# Run amla_core_code.py when the container launches
CMD python "./mla_core_code.py" 
