#!/bin/bash
# Bash script for CSAP KubeFlow/ML-Anywhere project
# Downloads and deploys and installs ksonnet and kubeflow

GITHUB_TOKEN=$1
KFAPP=$2

# step 0: set GitHub token
export GITHUB_TOKEN=$GITHUB_TOKEN

# step 1: install Nvidia device plugin
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v1.11/nvidia-device-plugin.yml

# step 4: prepare kubeflow using kfctl
export KFAPP=${KFAPP}
kfctl init ${KFAPP}
cd ${KFAPP}
kfctl generate all -V
kfctl apply all -V

kubectl -n kubeflow get  all