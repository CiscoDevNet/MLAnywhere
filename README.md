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

### Docker

### Kubernetes

### Vagrant

## Using a Corporate Proxy

## Troubleshooting

## License

This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
