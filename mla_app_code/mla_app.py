from flask import Flask, render_template, request
from flask import jsonify
from flask import json
import os
import requests

GITHUB_TOKEN = '9a2c8254bbb5807ddd14d29babe4ccf8b5bd0acb'
PLATFORM = 'darwin'
KS_VERSION = '0.13.1'
KF_VERSION = '0.5.0'
KFAPP = 'kfapp'
url = ''
username = ''
password = ''
cookie = ''
headers = ''
app = Flask(__name__)


@app.route("/stage1")
def run_stage1():
	 return render_template('stage1.html',)


@app.route("/stage2", methods = ['POST', 'GET'])
def run_stage2():
		print (request.method)
		if request.method == 'POST':
			global url
			global username
			global password
			ipadd = request.form['IP Address']
			username=request.form['Username']
			password=request.form['Password']
			url = "https://" + ipadd
			#url = "https://10.10.20.110"
			#username =
			headers = {
				'content-type': 'application/json',
			}

		response = requests.request("POST", url + "/2/system/login?username=" + username + "&password=" + password,  headers=headers, verify=False)
		cookie = response.cookies
		return render_template('stage2.html',cookies=cookie)


@app.route("/stage3", methods = ['POST', 'GET'])
def run_stage3():
	global url
	#url="https://10.10.20.110"
	headers = {
		'content-type': 'application/json',
	}

	response = requests.request("POST", url + "/2/system/login?username=" + "admin" + "&password=" + "Cisco123",  headers=headers, verify=False)
	cookie = response.cookies

	if request.method == 'POST':
		clusterName = request.form['Cluster Name']
		workerNodes = 1
		workerVcpus = 2
		workerMemory = 16384
		masterMemory = 16384
		data = {
			"is_harbor_enabled": False,
			"provider_client_config_uuid": "49af8434-a0cf-4951-873f-a04512c67c98",
			"name": clusterName,
			"kubernetes_version": "1.11.5",
			"ssh_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDIyJZfCNzDNJ+RupHpY8HhpvEq4YCz58FZONMxZCXY0RZB0uSTqu2fJ4KNDdOGggKPxaVkHam6GZoI8bBbclnViuI3yuo3rmeJoOlInGKXjAJ2KfnHHAXvmPj2UE4ritvdEOK+fJ0dGLKXCDFrolLKc8n4S1ck7cVmv1ruJ3+4iHJXhlp2Ea4irvIuwndgnZeKs4Zem5BZJh2trk6Cq7ctS1MgrjNy8fpFYIttjHuvWPSZ772IBI4jcjioEKJZYnayG9eVBBVuiLWHTuF8ZcaKvySlgrif0PG2Dj7zTsgOZtnJXhD36h2wOXJdUqsy1V7oHVPW1S16wantBN534QMz sandbox@CCP_SANDBOX_KEY",
			"description": "Cluster created via API",
			"datacenter": "CCP",
			"cluster": "CCP",
			"resource_pool": "CCP/Resources",
			"networks": [
				"VMNetwork"
			],
			"datastore": "CCPDatastore",
			"storage_class": "vsphere",
			"workers": workerNodes,
			"ssh_user": "ccpuser",
			"type": 1,
			"masters": 1,
			"deployer_type": "kubeadm",
			"ingress_vip_pool_id": "855f8eb6-a399-4052-8ad0-80adc3127f50",
			"load_balancer_ip_num": 5,
			"is_istio_enabled": False,
			"registries_root_ca": [
				""
			],
			"aws_iam_enabled": False,
			"aws_iam_role_arn": "",
			"worker_node_pool": {
				"vcpus": 2,
				"memory": workerMemory,
				"template": "ccp-tenant-image-1.11.5-ubuntu18-2.2.2"
			},
			"master_node_pool": {
				"vcpus": 2,
				"memory": masterMemory,
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
				"vsphere_datacenter": "CCP",
				"vsphere_datastore": "CCPDatastore",
				"vsphere_client_config_uuid": "49af8434-a0cf-4951-873f-a04512c67c98",
				"vsphere_working_dir": "/CCP/vm"
				}
			}
		}

	response = requests.request("POST", url + "/2/clusters", json=data, cookies=cookie, headers=headers, verify=False)
	uuid = response.json()["uuid"]
	response = requests.request("GET", url + "/2/clusters/" + uuid + "/env", cookies=cookie, headers=headers, verify=False)

	# create .kube directory to use kubectl
	#saveConfig = open("kubeconfig.yaml","w+")
	saveConfig = open("config","w+")
	os.system('mkdir ~/.kube')
	os.system('mv config ~/.kube')
	saveConfig.write(response.text)

	return render_template('stage3.html',)


@app.route("/stage4")
def run_stage4():
	os.system("./kfinstall.sh {} {} {} {} {}".format(GITHUB_TOKEN, PLATFORM, KS_VERSION, KF_VERSION, KFAPP))
	return render_template('stage4.html',)


if __name__ == "__main__":
	 app.run(host='0.0.0.0', port=5000)



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
