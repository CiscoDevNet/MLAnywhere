# Use an official Python runtime as a parent image
FROM python:2.7-alpine

# Set ENV VARS
ENV FLASK_ENV=development

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Run app.py when the container launches
CMD python "./mla_app_code/mla_app.py" runserver -h 0.0.0.0
