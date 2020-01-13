# Use an official Python runtime as a parent image
FROM ubuntu:18.04

###########################################################################################
# BUILD TIME
###########################################################################################

#####################################
# INSTALL DEPENDENCIES
#####################################
RUN apt-get upgrade
RUN apt-get update
RUN apt-get -y install curl
RUN apt-get -y install tar
RUN apt-get -y install python3-pip
RUN pip3 install kubernetes

#####################################
# SETUP KUBECTL
#####################################
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

#####################################
# SETUP KUBEFLOW
#####################################
RUN curl -L https://github.com/kubeflow/kubeflow/releases/download/v0.7.1/kfctl_v0.7.1-2-g55f9b2a_linux.tar.gz > kfctl.tar.gz
RUN tar xvf kfctl.tar.gz
RUN rm kfctl.tar.gz
RUN chmod +x ./kfctl
RUN mv ./kfctl /usr/local/bin/kfctl

#####################################
# SETUP HELM
#####################################
RUN curl -L  https://get.helm.sh/helm-v3.0.0-linux-amd64.tar.gz > helm.tar.gz
RUN tar zxvf helm.tar.gz
RUN mv linux-amd64/helm ./
RUN rm -r linux-amd64
RUN chmod +x ./helm
RUN mv ./helm /usr/local/bin/helm

#####################################
# PRE-SETUP CHECKS
#####################################
#RUN kubectl version > ../install.log

#####################################
# COPY SETUP FILE TO CONTAINER
#####################################
COPY ./setup ./setup

#####################################
# KUBEFLOW SETUP PART 1
#####################################
RUN mkdir kfapp
WORKDIR "/kfapp"
RUN kfctl build -V -f "../setup/kfctl_k8s_istio.0.7.1.yaml"
WORKDIR "/"

###########################################################################################
# RUN TIME
###########################################################################################
ENTRYPOINT exec sh ./setup/setup.sh 2>&1 | tee /usr/mnt/log.txt