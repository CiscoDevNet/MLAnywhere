from flask import Flask, render_template, request, session
from flask import jsonify
from flask import json
from ccp import CCP
import os
import requests

from mlaConfig import config

app = Flask(__name__)

@app.route("/stage1")
def run_stage1():
	return render_template('stage1.html')

@app.route("/stage2", methods = ['POST', 'GET'])
def run_stage2():

		if request.method == 'POST':
		
			ccp = CCP("https://" + request.form['IP Address'],request.form['Username'],request.form['Password'])
			
			login = ccp.login()

			if not login:
				print ("There was an issue with login: " + login.text)
				return render_template('stage1.html')
			else:
				session['ccpURL'] = "https://" + request.form['IP Address']
				session['ccpToken'] = login.cookies.get_dict()

		return render_template('stage2.html')

@app.route("/stage3", methods = ['POST', 'GET'])
def run_stage3():

	if request.method == 'POST':

		ccp = CCP(session['ccpURL'],"","",session['ccpToken'])

		clusterName = request.form['Cluster Name']

		try:
			with open("ccpRequest.json") as json_data:
				clusterData = json.load(json_data)
				clusterData["name"] = clusterName

				response = ccp.deployCluster(clusterData)

				print(response.text)

		except IOError as e:
			return "I/O error({0}): {1}".format(e.errno, e.strerror)

		uuid = newCluster.json()["uuid"]
		
		getYaml = ccp.getConfig(uuid)
		print("getYaml text  =  " + getYaml.text)
		# create .kube directory to use kubectl
		#saveConfig = open("kubeconfig.yaml","w+")
		saveConfig = open("config","w+")
		os.system('mkdir ~/.kube')
		os.system('mv config ~/.kube')
		saveConfig.write(getYaml.text)

	return render_template('stage3.html')


@app.route("/stage4")
def run_stage4():
	os.system("./kfinstall.sh {} {} {} {} {}".format(config.GITHUB_TOKEN, config.PLATFORM, config.KS_VERSION, config.KF_VERSION, config.KFAPP))
	return render_template('stage4.html')


if __name__ == "__main__":
	print (config.DEBUG_VERIFY)
	app.secret_key = "4qDID0dZoQfZOdVh5BzG"
	app.run(port=5000)

