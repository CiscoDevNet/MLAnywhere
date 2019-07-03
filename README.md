# MLAnywhere

This is a project to simplify the process of deploying Kubeflow + Tensorflow onto any underlying Kubernetes platform


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
      * [Troubleshooting](#troubleshooting)
      * [License](#license)

Created by [gh-md-toc](https://github.com/ekalinin/github-markdown-toc)

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

## MLAnywhere Deployment Options

### Standalone

There are two parts to the MLAnywhere installation wizard, the core scripts and the Kubeflow deployment tools. Both of these need to be available in order to using MLAnywhere in a standalone environment.

1. Clone the MLAnywhere repository to your local machine

   ```git clone https://github.com/CiscoDevNet/MLAnywhere.git```

2. Ensure the following tools are available on your local machine. See the script, `mlanywhere-bootstrap.sh` ,for an installation example 

* kubectl - 1.14.0
* ksonnet - 0.13.1
* kfctl - 0.5.1

3. From the `mla_app_code` folder run `python mla_core_code.py`. This will start MLAnywhere on port 5000 by default

4. Navigate to the IP address of your local machine using port 5000. e.g. http://localhost:5000

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

   `docker build -t conmurphy/mlanywhere:mlanywhere-beta-v1-app . --no-cache`

6. Push image into repository

   `docker push conmurphy/mlanywhere:mlanywhere-beta-v1-app`

7. Deploy new container on machine

   `docker run -p 5000:5000 conmurphy/mlanywhere:mlanywhere-beta-v1-app`

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


### Vagrant

1. Install Vagrant on your local machine

   [Vagrant installation instructions](https://www.vagrantup.com/docs/installation/)

2. Clone the MLAnywhere repository to your local machine

   `git clone https://github.com/CiscoDevNet/MLAnywhere.git`

3. Change directory to newly cloned MLAnywhere folder

   `cd MlAnywhere`

4. Run `vagrant up` from the MlAnywhere folder

5. Open browser and navigate to the IP address of your local machine using port 5000. e.g. http://localhost:5000

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

* Configure the host on which the MLAnywhere wizard is running with the `http_proxy`, `https_proxy`, and `no_proxy settings`

   For example
   
   ```
   export http_proxy = http://proxy.mycompany.com:80
   export https_proxy = http://proxy.mycompany.com:80
   export no_proxy = localhost, 127.0.0.1
   ```
   
* If running the installation wizard in a Docker or Kubernetes environment behind a corporate proxy you will also need to configure the Docker service to use the proxy. IF this is not enabled you may not be able to pull down the required images.

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


* When using the wizard to create a new cluster in stage 2, leave the proxy field disabled

### MLAnywhere Installation Wizard - Proxy, Kubeflow - Proxy




## Troubleshooting

## License

This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
