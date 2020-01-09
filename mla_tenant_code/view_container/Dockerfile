# Use an official Python runtime as a parent image
FROM ubuntu:18.04

###########################################################################################
# BUILD TIME
###########################################################################################

#####################################
# INSTALL DEPENDENCIES
#####################################
RUN apt-get update
RUN apt-get upgrade
RUN apt-get -y install curl
RUN apt-get -y install tar
RUN apt-get -y install python3-pip
RUN pip3 install kubernetes
RUN pip3 install flask

#####################################
# SETUP KUBECTL
#####################################
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

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
# COPY SETUP FILE TO CONTAINER
#####################################
COPY ./webserver ./webserver

###########################################################################################
# RUN TIME
###########################################################################################
ENTRYPOINT ["python3", "./webserver/main.py"]
