#!/bin/bash
# Bash script for CSAP KubeFlow/ML-Anywhere project
# Downloads and installes ksonnet and kubeflow

GITHUB_TOKEN=$1
PLATFORM=$2
KS_VERSION=$3
KF_VERSION=$4
KFAPP=$5

# step 0: set GitHub token
echo '*** step 0 ***'
export GITHUB_TOKEN=$GITHUB_TOKEN

# step 1: install Nvidia device plugin
echo '*** installing Nvidia device plugin ***'
#kubectl get nodes
kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v1.11/nvidia-device-plugin.yml

# step 2: install ksonnet
echo '*** installing ksonnet ***'
if [[ -e /usr/local/bin/ks ]] && [[ -x /usr/local/bin/ks ]]
then
    echo '*** a version of ksonnet already exists ***'
    ks version
else
    wget https://github.com/ksonnet/ksonnet/releases/download/v${KS_VERSION}/ks_${KS_VERSION}_${PLATFORM}_amd64.tar.gz
    tar -xvf ks_${KS_VERSION}_${PLATFORM}_amd64.tar.gz
    rm ks_${KS_VERSION}_${PLATFORM}_amd64.tar.gz
    chmod +x ks_${KS_VERSION}_${PLATFORM}_amd64/ks
    mv ks_${KS_VERSION}_${PLATFORM}_amd64/ks /usr/local/bin/
    rm -rf ks_${KS_VERSION}_${PLATFORM}_amd64/
fi

# step 3: install kfctl
echo '*** installing kfctl ***'
if [[ -e /usr/local/bin/kfctl ]] && [[ -x /usr/local/bin/kfctl ]]
then
    echo '*** a version of kfctl already exists ***'
    kfctl version
else
    wget https://github.com/kubeflow/kubeflow/releases/download/v${KF_VERSION}/kfctl_v${KF_VERSION}_${PLATFORM}.tar.gz
    tar -xvf kfctl_v${KF_VERSION}_${PLATFORM}.tar.gz
    rm kfctl_v${KF_VERSION}_${PLATFORM}.tar.gz
    mv kfctl /usr/local/bin/
fi

# step 4: prepare kubeflow using kfctl
echo '*** preparing KubeFlow ***'
export KFAPP=${KFAPP}
kfctl init ${KFAPP}
cd ${KFAPP}
kfctl generate all -V
kfctl apply all -V

kubectl -n kubeflow get  all