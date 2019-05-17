
'''
Copyright (c) 2019 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
'''

from flask import Flask, render_template, request
from flask import jsonify
from flask import json
from helper import CCP
import os
import requests

GITHUB_TOKEN = '9a2c8254bbb5807ddd14d29babe4ccf8b5bd0acb'
PLATFORM = 'linux'
KS_VERSION = '0.13.1'
KF_VERSION = '0.5.0'
KFAPP = 'kfapp'
cookie = ''
headers = {
			'content-type': 'application/json',
		}
app = Flask(__name__)
ccp=CCP("","","")

@app.route("/stage1")
def run_stage1():
		return render_template('stage1.html')


@app.route("/stage2", methods = ['POST', 'GET'])
def run_stage2():

		if request.method == 'POST':
			global ccp

			ccp = CCP("https://" + request.form['IP Address'],request.form['Username'],request.form['Password'])
			login = ccp.login()
			if not login:
				print ("There was an issue with login: " + login.text)
				return render_template('stage1.html')
			ccp.cookie = login.cookies
			print(login.text)
		return render_template('stage2.html',cookies=cookie)


@app.route("/stage3", methods = ['POST', 'GET'])
def run_stage3():

	if request.method == 'POST':
		clusterName = request.form['Cluster Name']
		# workerNodes = 1
		# workerVcpus = 2
		# workerMemory = 16384
		# masterMemory = 16384
		data = {
				  "is_harbor_enabled": False,
				  "provider_client_config_uuid": "3a27de53-d215-4462-86d1-f3235734fbdc",
				  "name": clusterName,
				  "kubernetes_version": "1.12.3",
				  "ssh_key": "ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBLqTOk9POe1pIvVkETUmcnvY+Dn9zvshqq0DbALF+map0VPUO1309yf8aTqyI28BzGwIfqjvCKSApnsLnyLSpI8= mimaurer@MIMAURER-M-30BX",
				  "description": "Cluster via api/ testing KF",
				  "datacenter": "Datacenter",
				  "cluster": "VNA-A-30",
				  "resource_pool": "VNA-A-30/Resources",
				  "networks": [
				    "Cisco 10.51.71.0_24"
				  ],
				  "datastore": "esxi3-ssd-raid1",
				  "storage_class": "vsphere",
				  "workers": 2,
				  "ssh_user": "ahmed",
				  "type": 1,
				  "masters": 1,
				  "deployer_type": "kubeadm",
				  "ingress_vip_pool_id": "081c4a1e-35c6-4fc1-b5a8-6859ac343be6",
				  "load_balancer_ip_num": 1,
				  "is_istio_enabled": False,
				  "registries_root_ca": [
				    ""
				  ],
				  "aws_iam_enabled": False,
				  "aws_iam_role_arn": "",
				  "worker_node_pool": {
				    "vcpus": 2,
				    "memory": 16384,
				    "template": "ccp-tenant-image-1.12.3-ubuntu18-3.1.0"
				  },
				  "master_node_pool": {
				    "vcpus": 2,
				    "memory": 16384,
				    "template": "ccp-tenant-image-1.12.3-ubuntu18-3.1.0"
				  },
				  "node_ip_pool_uuid": "081c4a1e-35c6-4fc1-b5a8-6859ac343be6",
				  "network_plugin": {
				    "name": "calico",
				    "status": "",
				    "details": "{\"pod_cidr\":\"192.168.0.0/16\"}"
				  },
				  "deployer": {
				    "proxy_cmd": "StrictHostKeyChecking no\nHost 15.29.3?.* !15.29.30.* !15.29.31.*\n ProxyCommand nc --proxy 10.193.231.10:8111 --proxy-type socks4 %h %p",
				    "provider_type": "vsphere",
				    "provider": {
				      "vsphere_datacenter": "Datacenter",
				      "vsphere_datastore": "esxi3-ssd-raid1",
				      "vsphere_client_config_uuid": "3a27de53-d215-4462-86d1-f3235734fbdc",
				      "vsphere_working_dir": "/Datacenter/vm"
				    }
				  }
				}
	# oldCluster = ccp.getClusters()


	newCluster = ccp.deployNewClusterFromFile(data)

	uuid = newCluster.json()["uuid"]
	# uuid = "b925e0ba-733b-4d5b-a7f5-ff807fc5b82c"
	getYaml = ccp.getConfig(uuid)
	print("getYaml text  =  " + getYaml.text)
	# create .kube directory to use kubectl
	saveConfig = open("kubeconfig.yaml","w+")
	saveConfig = open("config","w+")
	os.system('mkdir ~/.kube')
	os.system('mv config ~/.kube')
	saveConfig.write(getYaml.text)

	return render_template('stage3.html',)


@app.route("/stage4")
def run_stage4():
	os.system("./kfinstallv2.sh {} {} {} {} {}".format(GITHUB_TOKEN, PLATFORM, KS_VERSION, KF_VERSION, KFAPP))
	return render_template('stage4.html',)


if __name__ == "__main__":
	 app.run(host='0.0.0.0', port=5000)



# @app.route("/download")
# def run_installation_script():
#	os.system("./bash_scripts/testinstall.sh")
#	os.system("./bash_scripts/kfinstallv1.sh")
#	os.system("./bash_scripts/kfinstallv2.sh {} {} {} {} {}".format(GITHUB_TOKEN, PLATFORM, KS_VERSION, KF_VERSION, KFAPP))
#	return render_template('download.html')



# if __name__ == '__main__':
