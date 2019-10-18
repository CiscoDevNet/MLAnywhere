# MLAnywhere (mla) 

![MLA Stage 2](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_dark_final_transparent_small.png)

This is a project to simplify the process of deploying Kubeflow (along with the associated technologies like Tensorflow) onto underlying Kubernetes platforms.


Table of Contents
=================

  * [MLAnywhere](#mlanywhere)
      * [Kubeflow Resource Requirements](#kubeflow-resource-requirements)
      * [Compatibility](#compatibility)
      * [Installation](#installation)
      * [MLAnywhere Deployment Options](#mlanywhere-deployment-options)
      	  * [Standalone](#standalone)
         * [Docker](#docker)
         * [Kubernetes](#kubernetes)
         * [Vagrant](#vagrant)
      * [Using a Corporate Proxy](#using-a-corporate-proxy)
      * [Demo Scripts](#demo-scripts)
      * [Using MLAnywhere](#using-mlanywhere)
         * [stage1](#stage-1)
         * [stage2](#stage-2)
         * [stage3](#stage-3)
         * [stage4](#stage-4)
      * [Troubleshooting](#troubleshooting)
      * [License](#license)

Created by [gh-md-toc](https://github.com/ekalinin/github-markdown-toc)

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/CiscoDevNet/MLAnywhere)

## Kubeflow Resource Requirements

In order to provide the best experience, MLAnywhere will provision three worker nodes to run the Kubeflow pods. Each worker node will use two vCPUS and 16GB memory.

## Compatibility

## Installation

#### High Level Steps

* Deploy the MLAnywhere installation wizard (see below for deployment options)
* Login to the CCP deployment where the new Kubeflow cluster will be created
* Fill in the cluster form and wait for it to be deployed
* Deploy Kubeflow in the newly created cluster
* Download the Kubeconfig for the cluster
* Start developing!

## MLAnywhere Deployment Technique

### Docker

If you don't currently have a Docker image built, use the following steps to build and push your image to Docker hub or the repository of your choice. If the image has already been built you can skip steps 3,4,5, and 6. The installation instructions assume you are running Docker on your local machine.

1. Login to Docker hub or the repository of your choice

    [Docker hub login instruction](https://docs.docker.com/engine/reference/commandline/login/)

2. Create repository if not already existing

   [Creating a Dockerhub repository](https://docs.docker.com/docker-hub/repos/)

3. Clone the MLAnywhere repository to your local machine

   `git clone https://github.com/CiscoDevNet/MLAnywhere.git`
   
4. Change directory to newly created MLAnywhere repository

   `cd MLAnywhere`

5. Build Docker image and tag appropriately

   `docker build -t <your_repo>/mlanywhere:mlanywhere-beta-v1-app . --no-cache`

6. Push image into repository

   `docker push <your_repo>/mlanywhere:mlanywhere-beta-v1-app`

7. Deploy new container on machine

   `docker run -p 5000:5000 <your_repo>/mlanywhere:mlanywhere-beta-v1-app`

8. Open browser and navigate to the IP address of your local machine using port 5000. e.g. http://localhost:5000

### Kubernetes

The following assumes you already have a Kubernetes cluster running in which to deploy the MLAnywhere Installation Wizard. 

The MLAnywhere Installation Wizard is deployed to Kubernetes with a `service` and a `deployment`. These files have been created separately, or alternatively you can use the all in one file, `mlanywhere-all-in-one.yml`. 

By default MLAnywhere uses a Kubernetes Nodeport for access running on port 30003. This service can be changed if required.


1. Install Kubectl and configure KUBECONFIG access to the Kubernetes cluster if not already configured.

   [Install and setup Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
   
2. Clone the MLAnywhere repository to your local machine

   `git clone https://github.com/CiscoDevNet/MLAnywhere.git`

3. Change directory to newly cloned MLAnywhere folder

   `cd MlAnywhere`
 
4. Deploy the MLAnywhere Installation Wizard

   `kubectl apply -f mlanywhere-all-in-one.yml 
   
5. Check the pod has been deployed correctly

   `kubectl get pods`

6. Determine the IP address of the worker nodes to which the pod has been deployed

   `kubectl get nodes -o wide`

7. Open a browser and navigate to the IP Address of one of the nodes, remembing to include the port. e.g. http://10.1.1.21:30003


## Using a Corporate Proxy

When using the MLAnywhere Installation Wizard behind a corporate proxy, you may need to configure proxy settings on the MLAnywhere or Kubeflow hosts. 

The following scenarios outline these configurations.

### MLAnywhere Installation Wizard - No Proxy, Kubeflow - No Proxy

* No additional configuration required for either the wizard or Kubeflow hosts

### MLAnywhere Installation Wizard - No Proxy, Kubeflow - Proxy

In this scenario you have deployed the MLAnywhere wizard to an environment which does not require a proxy, however you are connecting to a CCP cluster which does require a proxy. For example, you are running the wizard on your laptop and connecting to your CCP lab behind a proxy.

* No additional configuration required for the MLAnywhere Wizard host
* When using the wizard to create a new cluster in stage 2, enable the proxy field and add the required proxy address

### MLAnywhere Installation Wizard - Proxy, Kubeflow - No Proxy

* When using the wizard to create a new cluster in stage 2, leave the proxy field disabled

* Configure the host on which the MLAnywhere wizard is running with the `http_proxy`, `https_proxy`, and `no_proxy settings`

   For example
   
   ```
   export http_proxy = http://proxy.mycompany.com:80
   export https_proxy = http://proxy.mycompany.com:80
   export no_proxy = localhost, 127.0.0.1
   ```
   
* If running the installation wizard in a Docker or Kubernetes environment behind a corporate proxy you will also need to configure the Docker service to use the proxy. If this is not enabled you may not be able to pull down the required images.

   On each of the worker nodes where the installation wizard is running:
   
   1. Update `/etc/systemd/system/docker.service.d/https-proxy.conf` with the appropriate proxy settings. 
   
   ```
    [Service]
    Environment="HTTPS_PROXY=http://proxy.mycompany.com:80" "NO_PROXY=localhost,127.0.0.1"
    ```
  
  2. Update `/etc/systemd/system/docker.service.d/http-proxy.conf` with the appropriate proxy settings. 
    
    ```
    [Service]
    Environment="HTTP_PROXY=http://proxy.mycompany.com:80" "NO_PROXY=localhost,127.0.0.1"
    ```
   
  3. Restart docker
  
    ```
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    ```

* If running the installation wizard in a Docker or Kubernetes environment behind a corporate proxy you will also need to include the proxy configuration in the containers themselves. This can be achieved by setting the correct environmental variables. Samples have been provided in the Kubernetes `yml` files.

NOTE: You will need to include the Kubernetes API server, 10.96.0.1, as part of the `no_proxy` configuration. See below for example. 

   Sample deployment file
   
   ```
   apiVersion: extensions/v1beta1
   kind: Deployment
   metadata:
     name: mlanywhere
   spec:
     strategy:
       rollingUpdate:
         maxSurge: 1
         maxUnavailable: 1
       type: RollingUpdate
     replicas: 1
     template:
       metadata:
         labels:
           app: mlanywhere
       spec:
         containers:
         - name: mlanywhere
           image: mlanywhere:mlanywhere-beta-v1-app

           imagePullPolicy: "IfNotPresent"

           # Uncomment if using a proxy
           env:
           - name: https_proxy
             value: "http://proxy.mycompany.com:80"
           - name: http_proxy
             value: "http://proxy.mycompany.com:80"
           - name: no_proxy
             value: "localhost,127.0.0.1,10.96.0.1"

           ports:
             - containerPort: 5000
   ```

### MLAnywhere Installation Wizard - Proxy, Kubeflow - Proxy

* When using the wizard to create a new cluster in stage 2, enable the proxy field and add the required proxy address

* Configure the host on which the MLAnywhere wizard is running with the `http_proxy`, `https_proxy`, and `no_proxy settings`

   For example
   
   ```
   export http_proxy = http://proxy.mycompany.com:80
   export https_proxy = http://proxy.mycompany.com:80
   export no_proxy = localhost, 127.0.0.1
   ```
   
* If running the installation wizard in a Docker or Kubernetes environment behind a corporate proxy you will also need to configure the Docker service to use the proxy. If this is not enabled you may not be able to pull down the required images.

   On each of the worker nodes where the installation wizard is running:
   
   1. Update `/etc/systemd/system/docker.service.d/https-proxy.conf` with the appropriate proxy settings. 
   
   ```
    [Service]
    Environment="HTTPS_PROXY=http://proxy.mycompany.com:80" "NO_PROXY=localhost,127.0.0.1"
    ```
  
  2. Update `/etc/systemd/system/docker.service.d/http-proxy.conf` with the appropriate proxy settings. 
    
    ```
    [Service]
    Environment="HTTP_PROXY=http://proxy.mycompany.com:80" "NO_PROXY=localhost,127.0.0.1"
    ```
   
  3. Restart docker
  
    ```
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    ```

* If running the installation wizard in a Docker or Kubernetes environment behind a corporate proxy you will also need to include the proxy configuration in the containers themselves. This can be achieved by setting the correct environmental variables. Samples have been provided in the Kubernetes `yml` files.

NOTE: You will need to include the Kubernetes API server, 10.96.0.1, as part of the `no_proxy` configuration. See below for example. 

   Sample deployment file
   
   ```
   apiVersion: extensions/v1beta1
   kind: Deployment
   metadata:
     name: mlanywhere
   spec:
     strategy:
       rollingUpdate:
         maxSurge: 1
         maxUnavailable: 1
       type: RollingUpdate
     replicas: 1
     template:
       metadata:
         labels:
           app: mlanywhere
       spec:
         containers:
         - name: mlanywhere
           image: mlanywhere:mlanywhere-beta-v1-app

           imagePullPolicy: "IfNotPresent"

           # Uncomment if using a proxy
           env:
           - name: https_proxy
             value: "http://proxy.mycompany.com:80"
           - name: http_proxy
             value: "http://proxy.mycompany.com:80"
           - name: no_proxy
             value: "localhost,127.0.0.1,10.96.0.1"

           ports:
             - containerPort: 5000
   ```

## Using MLAnywhere

There are currently 4 simple stages to MLAnywhere which are all built into the tool which lead to the creation of a kubeflow environment.

### Stage 1 

Access the IP address hosting K8s worker node VM as we are using a NodePort ServiceType, and port that has been defined in the K8s manifest file mlanywhere-svc.yml.

In this example it is port 30003 as per the service description: -
```
apiVersion: v1
kind: Service
metadata:
  name: mlanywhere-svc
  labels:
    app: mlanywhere-svc
spec:
  type: NodePort
  ports:
  - port: 5000
    nodePort: 30003
    protocol: TCP
  selector:
    app: mlanywhere
```

So with the example of http://1x.9x.8x.2x:30003/stage1 you should get the following web page presented to you: -

![MLA Stage 1](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage1.png)

In this stage you add the connection details of the underlying container management platform which in this case is the Cisco Container Platform <a href="https://www.cisco.com/c/en/us/products/cloud-systems-management/container-platform/index.html" target="target">Details Here</a> as mla needs to create K8s cluster dynamically to host the subsequent Kubeflow envs.

### Stage 2

As the contianer management tool is hosted upon vmware vSphere, we get the opportunity in stage 2 to define the following aspects of this supporting infrastructure so we can control exactly how the VMs get created as mla intetacts with the vSphere API to apply these configuration choices: -

- Cluster Name 
- vSphere Provider 
- vSphere DataCenter 
- vSphere Cluster
- vSphere Resource Pool 
- vSphere Network
- vSphere DataStore
- CCP Tenant Image Name 
- VIP Pool 
- SSH Key 


Most of these aspects are obvious but I will expand on a few elements here.

The **vSphere Provider** is a concept with CCP which we are exposing but this should be left as the default "vSphere" 

The **CCP Tenant Image Name** is the OVA image that is loaded into vSphere as part of the CCP process but effectively you are chosing the revision of the K8s cluster so in this example it is 1.13.5.

The **VIP Pool** is again a feature within CCP which is a pool of IP addresses pre entered into CCP from which VIPs will be allocated from.

The **SSH Key** is a public key that you select which will get injected into the supporting VMs in the maintenance or troubleshoot operations so thie key will normally come from your local laptop, or jump host.



![MLA Stage 2](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage2.png)


Another key value aspect of MLA is it's ability to configure the various **proxy** settings which are needed if your K8s environment is behind a corportate proxy. This is especially key in cloud native and open-source soluitons which need to dynamically contact services such as Docker Hub, GitHub and OS repositories as part of the automated build prcoesses include in tooling around contianer environments.

So it's simply a case of inserting your appropriate proxy address into the provided area and let MLA configure all of the various configuration files that need updated throughout the underlying operating system.


![MLA Stage 2](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage2_proxy.png)

Furthermore, once you hit the **Deploy** button, you have the ability to view what is happening under the skin of MLA via the **Logging**.
We have added this due to aid the process of troubleshooting in case of underlying problems in the infrastruccture etc.


![MLA Stage 2](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage2_logging.png)


It's worth noting that MLA will build out automatically the supporting Kubernetes cluster via the targeted container cluster manager

![MLA Stage 2_Cluster Build](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage2_cluster_build.png)


### Stage 3

Well this stage is very easy indeed.....simply press the **Install Kubeflow** button and it does exactly that!


![MLA Stage 3_Deploy_Kubeflow](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage3.png)


Again there is the option to see what is happening under the skin with the **Logging** button if required.






### Stage 4

From the final screen you can download the **KUBECONFIG** file to be able to connect to you Kubernetes cluster using **kubectl**.

*NOTE*: In the next release we will have the links to the Kubeflow Dashboard included in this final page.


Done.......it was that easy!


## Troubleshooting

## License

This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
