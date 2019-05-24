
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

from flask import Flask, json, render_template, request, session, Response, jsonify

from ccp import CCP
import os
import requests

from mlaConfig import config

app = Flask(__name__)

@app.route("/testConnection", methods = ['POST', 'GET'])
def run_testConnection():
    
    if request.method == 'POST':

        jsonData = request.get_json()
        
        ccp = CCP("https://" + jsonData['ipAddress'],jsonData['username'],jsonData['password'])
                
        login = ccp.login()

        if not login:
            return json.dumps({'success':False}), 401, {'ContentType':'application/json'} 
        else:
            session['ccpURL'] = "https://" + jsonData['ipAddress']
            session['ccpToken'] = login.cookies.get_dict()
            return json.dumps({'success':True,'redirectURL':'/stage2'}), 200, {'ContentType':'application/json'} 
    
    return render_template('stage1.html')
        
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

        elif request.method == 'GET':
            if session['ccpToken']:
                    return render_template('stage2.html')
            else:
                return render_template('stage1.html')
@app.route("/stage3", methods = ['POST', 'GET'])
def run_stage3():

    uuid = ""

    if request.method == 'POST':

        ccp = CCP(session['ccpURL'],"","",session['ccpToken'])

        clusterName = request.form['Cluster Name']
        
        try:
            with open("ccpRequest.json") as json_data:
                clusterData = json.load(json_data)
                clusterData["name"] = clusterName

                #response = ccp.deployCluster(clusterData)

                #uuid = response.json()["uuid"]

                print(uuid)

                uuid ="6de40233-738e-4e7f-bbf8-b6ca99a7d53c"
                kubeConfig = ccp.getConfig(uuid)

                print (kubeConfig.text)

                if not os.path.exists(config.KUBE_CONFIG_DIR):
                    try:
                        os.makedirs(config.KUBE_CONFIG_DIR)
                    except OSError as e:
                        if e.errno != errno.EEXIST:
                            raise
                
                with open(config.KUBE_CONFIG_DIR + "/config", "w") as f:
                    f.write(kubeConfig.text)

        except IOError as e:
            return "I/O error({0}): {1}".format(e.errno, e.strerror)

    return render_template('stage3.html')


@app.route("/stage4")
def run_stage4():

    # Alex: I tried to put the commands from the bash script kfapply into the python code directly. If this doesn't work, use the below line instead
    #os.system("./kfapply.sh {} {}".format(config.GITHUB_TOKEN, config.KFAPP))
    os.system("export GITHUBTOKEN={}".format(GITHUB_TOKEN))
	os.system("kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v1.11/nvidia-device-plugin.yml")
    os.system("export KFAPP={}".format(KFAPP))
	os.system("mkdir {}".format(KFAPP))
	os.system("kfctl init {}".format(KFAPP))
	os.system("cd {}".format(KFAPP))
	os.system("kfctl generate all -V")
	os.system("kfctl generate apply -V")

    return render_template('stage4.html')


if __name__ == "__main__":
    app.secret_key = "4qDID0dZoQfZOdVh5BzG"
    app.run(port=5000)

