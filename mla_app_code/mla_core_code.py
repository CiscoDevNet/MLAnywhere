from flask import Flask, render_template, request
from flask import jsonify
from flask import json
from helper import CCP
import os
import requests

GITHUB_TOKEN = '9a2c8254bbb5807ddd14d29babe4ccf8b5bd0acb'
PLATFORM = 'darwin'
KS_VERSION = '0.13.1'
KF_VERSION = '0.5.0'
KFAPP = 'kfapp'
# url = ''
# username = ''
# password = ''
cookie = ''
headers = {
			'content-type': 'application/json',
		}
app = Flask(__name__)
ccp=CCP("","","")

@app.route("/stage1")
def run_stage1():
	 return render_template('stage1.html',)


@app.route("/stage2", methods = ['POST', 'GET'])
def run_stage2():
		#print (request.method)


		if request.method == 'POST':
			global ccp
			# global username
			# global password
			# ipadd = request.form['IP Address']
			# username=request.form['Username']
			# password=request.form['Password']
			# url = "https://" + ipadd
			ccp = CCP("https://" + request.form['IP Address'],request.form['Username'],request.form['Password'])
			# print(ccp)
			#url = "https://10.10.20.110"
			#username = 'admin'
			#password = 'Cisco123'
			login = ccp.login()
			# if not login:
			# 	print ("There was an issue with login: " + login.text)
			# 	return render_template('stage1.html')
			# response = requests.request("POST", ccp.url + "/2/system/login?username=" + ccp.username + "&password=" + ccp.password,  headers=headers, verify=False)
			ccp.cookie = login.cookies
			print(ccp.cookie)
			print(login.text)
		return render_template('stage2.html',cookies=cookie)


@app.route("/stage3", methods = ['POST', 'GET'])
def run_stage3():
	# response = requests.request("POST", ccp.url + "/2/system/login?username=" + ccp.username + "&password=" + ccp.password,  headers=headers, verify=False)
	# ccp.cookie = response.cookies

	if request.method == 'POST':
		clusterName = request.form['Cluster Name']
		# workerNodes = 1
		# workerVcpus = 2
		# workerMemory = 16384
		# masterMemory = 16384
		data = {
				  "is_harbor_enabled": False,
				  "provider_client_config_uuid": "65339e0e-0fa6-491e-af4b-67f252524c1e",
				  "name": clusterName,
				  "kubernetes_version": "1.11.5",
				  "ssh_key": "ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBJ7vpe5839wACR0n7e/FQ4DEzf9SeV533qjxY5kp97AXE7Ge9wmBYqIDttj7CGmyeYqKrwhdsKvfWWEWO7xP9MQ= conmurph@CONMURPH-M-P0GM",
				  "description": "",
				  "datacenter": "LK02HX",
				  "cluster": "HX",
				  "resource_pool": "HX/Resources",
				  "networks": [
				    "vm-network-140",
				    "k8-priv-iscsivm-network"
				  ],
				  "datastore": "CCP-Tenant",
				  "storage_class": "vsphere",
				  "workers": 2,
				  "ssh_user": "ccpuser",
				  "type": 1,
				  "masters": 1,
				  "deployer_type": "kubeadm",
				  "ingress_vip_pool_id": "d3d326ad-147b-4b3c-ad95-cc0e8911a795",
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
				    "template": "ccp-tenant-image-1.11.5-ubuntu18-2.2.2"
				  },
				  "master_node_pool": {
				    "vcpus": 2,
				    "memory": 16384,
				    "template": "ccp-tenant-image-1.11.5-ubuntu18-2.2.2"
				  },
				  "network_plugin": {
				    "name": "calico",
				    "status": "",
				    "details": "{\"pod_cidr\":\"192.168.0.0/16\"}"
				  },
				  "deployer": {
				    "proxy_cmd": "StrictHostKeyChecking no\nHost 15.29.3?.* !15.29.30.* !15.29.31.*\n ProxyCommand nc --proxy 10.193.231.10:8111 --proxy-type socks4 %h %p",
				    "provider_type": "vsphere",
				    "provider": {
				      "vsphere_datacenter": "LK02HX",
				      "vsphere_datastore": "CCP-Tenant",
				      "vsphere_client_config_uuid": "65339e0e-0fa6-491e-af4b-67f252524c1e",
				      "vsphere_working_dir": "/LK02HX/vm"
				    }
				  }
				}
	print(ccp.username)
	# cluster = ccp.getClusters()
	# if cluster:
	# 	for eachCluster in cluster.json():
	# 		print(eachCluster)
	# 	else:
	# 		print(cluster.text)
	response = requests.request("POST", ccp.url + "/2/clusters", json=data, cookies=ccp.cookie, headers=headers, verify=False)
	print(response.text)
	# uuid = response.json()["uuid"]
	# response = requests.request("GET", ccp.url + "/2/clusters/" + uuid + "/env", cookies=ccp.cookie, headers=headers, verify=False)

	# create .kube directory to use kubectl
	# saveConfig = open("kubeconfig.yaml","w+")
	# saveConfig = open("config","w+")
	# os.system('mkdir ~/.kube')
	# os.system('mv config ~/.kube')
	# saveConfig.write(response.text)

	return render_template('stage3.html',)


@app.route("/stage4")
def run_stage4():
	os.system("./kfinstall.sh {} {} {} {} {}".format(GITHUB_TOKEN, PLATFORM, KS_VERSION, KF_VERSION, KFAPP))
	return render_template('stage4.html',)


if __name__ == "__main__":
	 app.run()



# @app.route("/download")
# def run_installation_script():
#	os.system("./bash_scripts/testinstall.sh")
#	os.system("./bash_scripts/kfinstallv1.sh")
#	os.system("./bash_scripts/kfinstallv2.sh {} {} {} {} {}".format(GITHUB_TOKEN, PLATFORM, KS_VERSION, KF_VERSION, KFAPP))
#	return render_template('download.html')


# @app.route('/result')
# def stage1Data():
#   return render_template('stage1.html')


# @app.route('/result',methods = ['POST', 'GET'])
# def result():
#   if request.method == 'POST':
#     result = request.form
#     return render_template("result.html",result = result)


# if __name__ == '__main__':

#   app.run(port=5000)

#example to save it in a file
# def f_add_vlan(form_vlan,form_room):
#   rooms_data = json.loads(open('js/rooms.js').read())
#   for room in rooms_data['rooms']:
#     if room['id'] == form_room and form_vlan != room['vlan']:
#       room['vlan'] = form_vlan
#       update_room_vlan_dnac(room,ports_data)
#       with open('js/rooms.js', 'w') as jsonfile:
#         json.dump(rooms_data,jsonfile,indent=4)
