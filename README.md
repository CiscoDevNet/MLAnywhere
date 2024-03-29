# MLAnywhere (mla)

![MLA Stage 2](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_dark_final_transparent_small.png)

This is a project to simplify the process of deploying Kubeflow (along with the associated technologies like Tensorflow) onto underlying Kubernetes platforms whilst assisting with the educational jump from traditional DC skills into the cloud native world!


Table of Contents
=================

  * [MLAnywhere](#mlanywhere)
      * [Important Notice](#important-notice)
      * [Kubeflow Resource Requirements](#kubeflow-resource-requirements)
      * [Compatibility](#compatibility)
      * [Installation](#installation)
      * [MLAnywhere Deployment Options](#mlanywhere-deployment-options)
         * [Docker Image Preparation](#Docker-Image-Preparation)
         * [Kubernetes](#kubernetes)
      * [Using a Corporate Proxy](#using-a-corporate-proxy)
      * [Demo Scripts](#demo-scripts)
      * [Using MLAnywhere](#using-mlanywhere)
         * [stage1](#stage-1)
         * [stage2](#stage-2)
         * [stage3](#stage-3)
      * [Additional Information](#additional-information)
         * [Using a Corporate Proxy](#when-using-a-corporate-proxy)
      * [Troubleshooting](#troubleshooting)
      * [License](#license)

Created by [gh-md-toc](https://github.com/ekalinin/github-markdown-toc)

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/CiscoDevNet/MLAnywhere)

## Important Notice

This code is based on the Cisco Container Platform v6.0 and no further development will be done as our focus will now be on the Cisco Kubeflow Starter Pack https://developer.cisco.com/kubeflow/


## Kubeflow Resource Requirements

In order to provide the an acceptable experience, MLAnywhere will provision two nodes to run the Kubeflow pods. Each worker node will use two vCPUS and 16GB memory (though more worker nodes would be even better!).


## Compatibility

Cisco Container Platform version 5.x - 6.00



## Installation

#### High Level Steps

* Deploy the MLAnywhere installation wizard (see below for deployment options)
* Login to the CCP deployment where the new Kubernetes cluster will be created to support the Kubeflow env
* Fill in the cluster definition form and wait for it to be deployed
* Deploy Kubeflow in a fully automated way into the newly created cluster
* Run the included real world based demo and build out your ML skills!



## MLAnywhere Deployment Technique

At a high level the installation flow is as follows: -


![MLA_Installatin_Flow](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_flow_diagram.png)



### Downloading code and Docker Image Preparation (steps 1 + 2)

If you don't currently have a Docker image built for MLAnywhere, use the following steps to build and push your image to Docker hub or the repository of your choice. If the image has already been built you go directly to **Installing MLAnywhere into a Kubernetes cluster Step 3**. The installation instructions assume you are running Docker on your local machine.

1. Clone the MLAnywhere repository to your local machine

   `git clone https://github.com/CiscoDevNet/MLAnywhere.git`

2. Change directory to newly created MLAnywhere repository

   `cd MLAnywhere`

3. Build Docker image and tag appropriately

   `docker build -t <your_repo>/mlanywhere:mlanywhere-app . --no-cache`

4. Login to Docker hub or the repository of your choice

    [Docker hub login instruction](https://docs.docker.com/engine/reference/commandline/login/)

   Or....create repository if not already existing

   [Creating a Dockerhub repository](https://docs.docker.com/docker-hub/repos/)

5. Push image into repository

   `docker push <your_repo>/mlanywhere:mlanywhere-app`



### Installing MLAnywhere into a Kubernetes cluster (step 3)  

The following assumes you now have a Kubernetes cluster available to you in which to deploy the MLAnywhere Installation Wizard.

The MLAnywhere Installation Wizard by default is deployed into Kubernetes cluster with a `service` and a `deployment` construction. These files are created as 2 separate yaml manifests. Alternatively you can use the all in one file, `mlanywhere-all-in-one.yml`.

Also by default, MLAnywhere uses a Kubernetes Nodeport for access running on port 30003. This service port can be changed if required.


1. Install Kubectl and configure KUBECONFIG access to the Kubernetes cluster if not already configured.

   [Install and setup Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

2. Clone the MLAnywhere repository to your local machine if it has not already been done so.

   `git clone https://github.com/CiscoDevNet/MLAnywhere.git`

3. Change directory to newly cloned MLAnywhere folder

   `cd MlAnywhere`

4. Deploy the MLAnywhere Installation Wizard

   `kubectl apply -f mlanywhere-all-in-one.yml`

   Note: Make sure you update the location of the image that will be used to the one you created in the earlier stage

5. Check the pod has been deployed correctly

   `kubectl get pods`

6. Determine the IP address of the worker nodes to which the pod has been deployed and make a note of these.

   `kubectl get nodes -o wide`

7. Open a browser and navigate to the IP Address of one of the worker nodes, remembering to include the port. e.g. http://10.1.1.21:30003



## Using MLAnywhere (mla)

Now MLAnywhere is installed, we can start to understand that there are 3 simple stages included which are all built into the tool which lead to the creation of a kubeflow environment and a valuable real world demo.


### Stage 1

Access the IP address hosting K8s worker node VM (as guided above) as we are using a NodePort ServiceType, and port that has been defined in the K8s manifest file mlanywhere-svc.yml.

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

So with the example of http://1x.9x.8x.2x:30003 you should get the following web page presented to you: -

![MLA Stage 1](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage1.png)

In this 1st stage please input the connection details of the underlying container management platform which in this case is the Cisco Container Platform (CCP) <a href="https://www.cisco.com/c/en/us/products/cloud-systems-management/container-platform/index.html" target="target">Details Here</a> as mla needs to create K8s clusters dynamically to host the subsequent Kubeflow env.

### Stage 2

As the container management tool is hosted upon vmware vSphere in this example, we get the opportunity to define the following aspects of this supporting infrastructure so we can control exactly how the VMs get created as mla interacts with the vSphere API to apply these configuration choices: -

- Cluster Name
- vSphere Provider
- vSphere DataCenter
- vSphere Cluster
- vSphere Resource Pool
- vSphere Network
- vSphere DataStore
- GPU
- CCP Tenant Image Name
- VIP Pool
- SSH Key


Most of these aspects are obvious but we will expand on a few elements here.

The **vSphere Provider** is a concept with CCP which we are exposing but this should be left as the default "vSphere"

The **CCP Tenant Image Name** is the OVA image that is loaded into vSphere as part of the CCP process but effectively you are choosing the revision of the K8s cluster so in this example it is 1.13.5.

The **VIP Pool** is again a feature within CCP which is a pool of IP addresses pre entered into CCP from which VIPs will be allocated from.

The **SSH Key** is a public key that you select which will get injected into the supporting VMs in the maintenance or troubleshoot operations so this key will normally come from your local laptop, or jump host.



![MLA Stage 2](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage2.png)


Another key value aspect of MLA is it's ability to configure the various **proxy** settings which are needed if your K8s environment is behind a corportate proxy. This is especially important in cloud native and open-source solutions which need to dynamically contact services such as Docker Hub, GitHub and OS repositories as part of the automated build processes included in tooling around container environments.

So it's simply a case of inserting your appropriate proxy address into the provided area and let MLA configure all of the various configuration files that need updated throughout the underlying operating system.



![MLA Stage 2](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage2_proxy.png)


Furthermore, once you hit the **Deploy** button, you have the ability to view what is happening under the skin of MLA via the **Logging**.
We have added this due to aid the process of troubleshooting in case of underlying problems in the infrastructure and to also aid the education process!



![MLA Stage 2](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage2_logging.png)



It's worth noting that MLA will build out automatically the supporting Kubernetes cluster via the targeted container cluster manager



![MLA Stage 2_Cluster Build](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage2_cluster_build.png)




### Stage 3

Well this stage is very easy indeed.....simply click on the **Install Kubeflow** button and it does exactly that!


![MLA Stage 3_Deploy_Kubeflow](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage3.png)


Again there is the option to see what is happening under the skin with the **Logging** button if required.

Once the process has built out (in a very visually descriptive fashion), you can access the Kubeflow dashboard via the provided link.

![MLA Stage 3_Kubeflow_Dashboard](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage3_dashboard.png)

You will have probably noticed that MLAnywhere actually injects a real world ML demo into the environment for you to examine and learn from so let's have a look at that via clicking the **Go to KubeFlow** button.





### The Bolts Demo


If we look at the Kubeflow dashboard, we can see at the top of the page we get to choose the **ciscodemo** namespace.....so let's do that to build out the supporting pipelines!



![MLA Stage 3_Kubeflow_Namespace](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage3_namespace.png)




Once this is chosen, select the **bolts demo** from the available **Jupyter NoteBooks**.

![MLA Stage 3_Kubeflow_Bolts_Demo](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage3_bolts_demo.png)




Once this opens, you should see something like the following graphic

![MLA Stage 3_Kubeflow_Bolts_Details](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage3_run_bolts_details.png)




From here, select **Run All Below**



![MLA Stage 3_Kubeflow_Run_Bolts_Notebook](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage3_run_bolts_notebook.png)




Once run, go to the bottom of the Notebook and select **Run link here** as per the following graphic.

![MLA Stage 3_Kubeflow_Run_Bolts_Pipeline](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage3_run_bolts_pipeline.png)




It should start to build out the **Pipeline** from which we can run ML workloads upon.

When the Pipeline is built, it should look like the following.......

![MLA Stage 3_Kubeflow_Run_Pipeline_Complete](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage3_bolts_pipeline_complete.png)


So let's start to use our fresh kubeflow pipeline!

The demo scenario which we have included is an industrial use case which compares images of bolts on a production line to make sure the wrong components do not end up on the wrong production lines!

So as we have seen thus far, the Kubeflow environment is built out with a **model** defined and placed in 'production' (deploy-on-prem) with supporting components via the constructed pipeline (such as tensorboard etc).

Typically in production, an application would be pointed at the created model for it to consume in order to bring an actual usable outcome, but for the sake of simplicity, we will use another Jupyter NoteBook as a **client** (rather than a custom built application).

In fact, this client will use some of the images of bolts which were imported, stored and served out during the pipeline configuration stage which we have already done.

The client will compare these images to what the model has been designed and tuned to do, which effectively is to determine if the bolts are 'imperial' or 'metric' thread based.


So let's run the next notebook to do this!


Go back to the Kubeflow Dashboard page and now select the **Demo Client** notebook.


![MLA Stage 3_Demo_Client](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage3_bolts_demo_client.png)



Once it loads, it should look like the following, so go ahead and run it: -


![MLA Stage 3_Demo_Client_Loaded](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage3_bolts_demo_client_loaded.png)


Well, congratulations as we have got to the end as you will be able to see that the experiment has given un an accuracy score on the likelihood of the bolt being of a metric type (in my e.g. its 97% and 82% 'certain')!

![MLA Stage 3_Demo_Client_Complete](https://github.com/CiscoDevNet/MLAnywhere/blob/master/images/mla_stage3_bolts_demo_client_complete.png)





## Additional Information


## When Using a Corporate Proxy

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


## Troubleshooting

## License

This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
