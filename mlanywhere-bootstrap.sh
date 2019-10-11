#!/bin/bash

# Set ENV VARS
export FLASK_ENV=development
export PYTHONUNBUFFERED=0
export PLATFORM=linux
export K8SVERSION=1.14.0
export KS_VERSION=0.13.1
export KF_VERSION=0.5.1

cd /app

# Install for ssh-keygen
apt-get update
apt-get -y install openssh-client

apt-get install -y wget

# Install needed executables
wget https://storage.googleapis.com/kubernetes-release/release/v${K8SVERSION}/bin/${PLATFORM}/amd64/kubectl
chmod +x ./kubectl
mv ./kubectl /usr/local/bin/


wget https://github.com/ksonnet/ksonnet/releases/download/v${KS_VERSION}/ks_${KS_VERSION}_${PLATFORM}_amd64.tar.gz
tar -xvf ks_${KS_VERSION}_${PLATFORM}_amd64.tar.gz
rm ks_${KS_VERSION}_${PLATFORM}_amd64.tar.gz
chmod +x ks_${KS_VERSION}_${PLATFORM}_amd64/ks
mv ks_${KS_VERSION}_${PLATFORM}_amd64/ks /usr/local/bin/
rm -rf ks_${KS_VERSION}_${PLATFORM}_amd64/

wget https://github.com/kubeflow/kubeflow/releases/download/v${KF_VERSION}/kfctl_v${KF_VERSION}_${PLATFORM}.tar.gz
tar -xvf kfctl_v${KF_VERSION}_${PLATFORM}.tar.gz
rm kfctl_v${KF_VERSION}_${PLATFORM}.tar.gz
chmod +x ./kfctl
mv ./kfctl /usr/local/bin/

sudo apt -y install python3-pip
sudo apt -y install git

# Uncomment for when using private git repo
#sudo git clone https://<username>:<PersonalAccessToken>@github.com/CiscoDevNet/MLAnywhere.git /app

sudo git clone -b https://github.com/CiscoDevNet/MLAnywhere.git /app

pip3 install  -r /app/requirements.txt

cd /app/mla_app_code

python3 -u ./mla_core_code.py
