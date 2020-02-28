#!/bin/bash

#####################################
# HELM UPGRADE
#####################################
echo -------------- Upgrading Helm --------------
helm repo add stable  https://kubernetes-charts.storage.googleapis.com/
helm repo update

#####################################
# NFS SERVER SETUP
#####################################
echo -------------- Setting up NFS server --------------
kubectl get pods --all-namespaces
helm install stable/nfs-server-provisioner --generate-name --set=persistence.enabled=true --set=persistence.storageClass=standard --set=persistence.size=200Gi

#####################################
# KUBEFLOW SETUP PART 2
#####################################
echo -------------- Setting up Kubeflow --------------
kfctl apply -V -f /kfapp/kfctl_k8s_istio.0.7.1.yaml

#####################################
# ASSURE PODS ARE READY
#####################################
echo -------------- Waiting for all Pods to be ready --------------
python3 ./setup/ready_check_pod.py
kubectl get pods --all-namespaces

#####################################
# KUBEFLOW POST INSTALL
#####################################
echo -------------- Executing Kubeflow post-install --------------
kubectl -n kubeflow get all

#####################################
# CHANGE DEFAULT STORAGE CLASS
#####################################
echo -------------- Changing the default Storage Class --------------
DEFAULT_STORAGECLASS=$(kubectl get storageclass | grep 'default' | awk '{print $1}')
echo Default Storageclass: $DEFAULT_STORAGECLASS

kubectl patch storageclass $DEFAULT_STORAGECLASS -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'
kubectl patch storageclass $DEFAULT_STORAGECLASS -p '{"metadata": {"annotations":{"storageclass.beta.kubernetes.io/is-default-class":"false"}}}'
kubectl patch storageclass nfs -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

#####################################
# CREATE PVC
#####################################
echo -------------- Creating PVC --------------
kubectl apply -f ./setup/pvc/
kubectl get pvc

#####################################
# GET IP AND PORT FOR DASHBOARD
#####################################
echo -------------- Getting IP and port for Kubeflow dashboard --------------
INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}')
SECURE_INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="https")].nodePort}')
INGRESS_HOST=$(kubectl get po -l istio=ingressgateway -n istio-system -o jsonpath='{.items[0].status.hostIP}')

export INGRESS_PORT
export SECURE_INGRESS
export INGRESS_HOST

echo Kubeflow running at:
echo $INGRESS_HOST:$INGRESS_PORT

#####################################
# CREATE DEMO NAMESPACE
#####################################
echo -------------- Creating the demo namespace --------------
kubectl get pods --all-namespaces

NS_URL="http://${INGRESS_HOST}:${INGRESS_PORT}/api/workgroup/create"

echo $NS_URL

curl -X POST "$NS_URL" -H 'content-type: application/json' --data '{"namespace":"ciscodemo"}' --max-time 25 --connect-timeout 25 --retry 400 --retry-delay 5
echo 

#####################################
# CREATE NOTEBOOK SERVER
#####################################
echo -------------- Creating notebook server --------------
NB_URL="${INGRESS_HOST}:${INGRESS_PORT}/jupyter/api/namespaces/ciscodemo/notebooks"

curl "$NB_URL" -H 'Accept: application/json, text/plain, */*' -H 'Content-Type: application/json' --data '{"name":"ciscodemo","namespace":"ciscodemo","image":"gcr.io/kubeflow-images-public/tensorflow-1.14.0-notebook-cpu:v-base-ef41372-1177829795472347138","customImage":"","customImageCheck":false,"cpu":"0.1","memory":"1.0Gi","noWorkspace":false,"workspace":{"type":"New","name":"workspace-ciscodemo","templatedName":"workspace-{notebook-name}","size":"10Gi","mode":"ReadWriteMany","class":"{none}","extraFields":{}},"datavols":[],"extra":"{}","shm":true,"configurations":[]}' --max-time 25 --connect-timeout 25 --retry 400 --retry-delay 5
echo 

#####################################
# CHECK THAT NOTEBOOK SERVER IS READY
#####################################
echo -------------- Waiting for notebook server to be ready --------------
python3 ./setup/ready_check_nb.py

#####################################
# UPLOAD DEMOS TO NOTEBOOK SERVER
#####################################
echo -------------- Uploading demos to notebook server --------------

kubectl -n ciscodemo exec ciscodemo-0 --container ciscodemo -- wget --retry-connrefused --tries=400 --waitretry=5 --read-timeout=25 --timeout=25 mla-svc.default.svc.cluster.local:5000/examples/bolts_demo.zip
kubectl -n ciscodemo exec ciscodemo-0 --container ciscodemo unzip bolts_demo.zip
kubectl -n ciscodemo exec ciscodemo-0 --container ciscodemo rm bolts_demo.zip

echo

#####################################
# INSTALL ADDITONAL MODULES FOR NB
#####################################
echo -------------- Installing additional modules for notebook server --------------

kubectl -n ciscodemo exec ciscodemo-0 --container ciscodemo -- python -m pip install --user --upgrade pip
kubectl -n ciscodemo exec ciscodemo-0 --container ciscodemo -- python -m pip install --user numpy==1.16.0
kubectl -n ciscodemo exec ciscodemo-0 --container ciscodemo -- python -m pip install --user grpcio==1.16.1
kubectl -n ciscodemo exec ciscodemo-0 --container ciscodemo -- python -m pip install --user imageio==2.4.1
kubectl -n ciscodemo exec ciscodemo-0 --container ciscodemo -- python -m pip install --user matplotlib==3.0.2
kubectl -n ciscodemo exec ciscodemo-0 --container ciscodemo -- python -m pip install --user Pillow==5.3.0
kubectl -n ciscodemo exec ciscodemo-0 --container ciscodemo -- python -m pip install --user tensorflow-serving-api==1.15.0

#####################################
# GIVE FULL PERMISSIONS TO NAMESPACE
#####################################
echo -------------- Giving full permissions to namespace --------------

kubectl apply -f ./setup/rb_ciscodemo.yaml

echo

#####################################
# KEEP CONTAINER ALIVE
#####################################
echo -------------- Done --------------
echo $INGRESS_HOST:$INGRESS_PORT
sleep infinity