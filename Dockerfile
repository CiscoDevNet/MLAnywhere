# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Set ENV VARS
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=0
ENV PLATFORM=linux
ENV K8SVERSION=1.14.0
ENV KS_VERSION=0.13.1
ENV KF_VERSION=0.5.0

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Install for ssh-keygen
RUN apt-get update
RUN apt-get -y install openssh-client

# Install needed executables
RUN wget https://storage.googleapis.com/kubernetes-release/release/v${K8SVERSION}/bin/${PLATFORM}/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/

RUN wget https://github.com/ksonnet/ksonnet/releases/download/v${KS_VERSION}/ks_${KS_VERSION}_${PLATFORM}_amd64.tar.gz
RUN tar -xvf ks_${KS_VERSION}_${PLATFORM}_amd64.tar.gz
RUN rm ks_${KS_VERSION}_${PLATFORM}_amd64.tar.gz
RUN chmod +x ks_${KS_VERSION}_${PLATFORM}_amd64/ks
RUN mv ks_${KS_VERSION}_${PLATFORM}_amd64/ks /usr/local/bin/
RUN rm -rf ks_${KS_VERSION}_${PLATFORM}_amd64/

RUN wget https://github.com/kubeflow/kubeflow/releases/download/v${KF_VERSION}/kfctl_v${KF_VERSION}_${PLATFORM}.tar.gz
RUN tar -xvf kfctl_v${KF_VERSION}_${PLATFORM}.tar.gz
RUN rm kfctl_v${KF_VERSION}_${PLATFORM}.tar.gz
RUN chmod +x ./kfctl
RUN mv ./kfctl /usr/local/bin/

WORKDIR /app/mla_app_code


# Run amla_core_code.py when the container launches
CMD python "./mla_core_code.py" 

