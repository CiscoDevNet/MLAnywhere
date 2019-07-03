# MLAnywhere

This is a project to simplify the process of deploying Kubeflow + Tensorflow onto any underlying Kubernetes platform


Table of Contents
=================

  * [MLAnywhere](#mlanywhere)
      * [Kubeflow Resource Requirements](#kubeflow-resource-requirements)
      * [Compatibility](#compatibility)
      * [Installation](#installation)
      * [MLAnywhere Deployment Options](#mlanywhere-deployment-options)
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

If you don't currently have a Docker image built, use the following steps to build and push your image to Docker hub or the repository of your choice.

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

## Troubleshooting

## License

This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
