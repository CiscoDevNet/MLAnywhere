
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
import proxy 
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

    return render_template('stage1.html')

@app.route("/stage2", methods = ['POST', 'GET'])
def run_stage2():

        if request.method == 'POST':

            uuid = ""

            ccp = CCP(session['ccpURL'],"","",session['ccpToken'])

            formData = request.get_json()
            
            try:
                with open("ccpRequest.json") as json_data:
                    
                    clusterData = json.load(json_data)

                    # if a proxy is required then we need to insert this once the worker nodes have been deployed
                    # we will generate new SSH keys which will be provided to CCP as the initial keys
                    # once the proxy has been updated we will insert the 

                    if "proxyInput" in formData:
                        # create a  directory to add temporary keys - will be deleted once the proxy has been configured
                        if not os.path.exists("./tmp-keys/"):
                            try:
                                os.makedirs("./tmp-keys/")
                            except OSError as e:
                                if e.errno != errno.EEXIST:
                                    raise

                        proxy.generateTemporaryKeys("./tmp-keys/")
                        
                        with open("./tmp-keys/id_ed25519.pub") as f:
                            publicKey = f.readlines()
                        clusterData["ssh_key"] = publicKey[0]
                        
                    else:
                        clusterData["ssh_key"] = formData["sshKey"] 
                    
                    clusterData["name"] = formData["clusterName"]
                    clusterData["provider_client_config_uuid"] = formData["vsphereProviders"]
                    clusterData["name"] = formData["clusterName"]
                    clusterData["datacenter"] = formData["vsphereDatacenters"]
                    clusterData["cluster"] = formData["vsphereClusters"]
                    clusterData["resource_pool"] = formData["vsphereClusters"] + "/" + formData["vsphereResourcePools"]
                    clusterData["datastore"] = formData["vsphereDatastores"] 
                    clusterData["deployer"]["provider"]["vsphere_client_config_uuid"] = formData["vsphereProviders"] 
                    clusterData["deployer"]["provider"]["vsphere_datacenter"] = formData["vsphereDatacenters"] 
                    clusterData["deployer"]["provider"]["vsphere_datastore"] = formData["vsphereDatastores"] 
                    clusterData["deployer"]["provider"]["vsphere_working_dir"] = "/" + formData["vsphereDatacenters"] + "/vm"
                    clusterData["ingress_vip_pool_id"] = formData["vipPools"] 
                    clusterData["master_node_pool"]["template"] = formData["tenantImageTemplate"] 
                    clusterData["worker_node_pool"]["template"] = formData["tenantImageTemplate"] 
                    clusterData["node_ip_pool_uuid"] = formData["vipPools"] 
                    
                    clusterData["networks"] = [formData["vsphereNetworks"] ]

                    print (clusterData)
                    response = ccp.deployCluster(clusterData)

                    #print(response.text)
                    
                    uuid = response.json()["uuid"]

                    #uuid = "51a0390c-5a9b-408a-8258-acc803cef4d5"

                    kubeConfig = ccp.getConfig(uuid)

                    if "apiVersion" in kubeConfig.text:

                        if not os.path.exists(config.KUBE_CONFIG_DIR):
                            try:
                                os.makedirs(config.KUBE_CONFIG_DIR)
                            except OSError as e:
                                if e.errno != errno.EEXIST:
                                    raise

                        with open(config.KUBE_CONFIG_DIR + "/config", "w") as f:
                            f.write(kubeConfig.text)
                    else:
                        #TODO SEND ERROR MESSAGE TO LOGGING
                        print("UUID NOT FOUND")

                    # if a proxy is required then we need to insert his once the worker nodes have been deployed

                    if "proxyInput" in formData:
                        cluster = ccp.getCluster(clusterData["name"])
                        if "uuid" in cluster.text:
                            cluster = cluster.json()
                            nodes = cluster["nodes"]
                            privateKey = "./tmp-keys/id_ed25519"
                            publicKey = "./tmp-keys/id_ed25519.pub"
                            
                            if os.path.isfile(privateKey) and os.path.isfile(publicKey):
                                for node in nodes:
                                    proxy.sendCommand(node["public_ip"],'ccpuser','./tmp-keys/id_ed25519',formData["sshKey"],'configure_proxy.sh',formData["proxyInput"] )
                            else:
                                #TODO SEND ERROR MESSAGE TO LOGGING
                                print("ERROR CONFIGURING PROXY")
                            
                            proxy.deleteTemporaryKeys("./tmp-keys/")
                        else:
                            #TODO SEND ERROR MESSAGE TO LOGGING
                            print("WRONG NAME")

                    return json.dumps({'success':True,'redirectURL':'/stage3'}), 200, {'ContentType':'application/json'} 

            except IOError as e:
                return "I/O error({0}): {1}".format(e.errno, e.strerror)

        elif request.method == 'GET':
            if session['ccpToken']:
                return render_template('stage2.html')
            else:
                return render_template('stage1.html')

@app.route("/stage3", methods = ['POST', 'GET'])
def run_stage3():

    
    if request.method == 'GET':
        if session['ccpToken']:
            return render_template('stage3.html')
        else:
            return render_template('stage1.html')
    

    
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



@app.route("/vsphereProviders", methods = ['POST', 'GET'])
def run_vsphereProviders():
    
    if request.method == 'GET':

        ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
    
        response = ccp.getProviderClientConfigs()

        if response:
            return response.text
        else:
            return []

@app.route("/vsphereDatacenters", methods = ['POST', 'GET'])
def run_vsphereDatacenters():
    
    
    if request.method == 'GET':

        ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
    
        jsonData = request.args.to_dict()
        print(jsonData)
        response = ccp.getProviderVsphereDatacenters(jsonData["vsphereProviderUUID"])

        if response:
            return jsonify(response)
        else:
            return []

@app.route("/vsphereClusters", methods = ['POST', 'GET'])
def run_vsphereClusters():
    
    
    if request.method == 'GET':

        ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
    
        jsonData = request.args.to_dict()
        print(jsonData)
        response = ccp.getProviderVsphereClusters(jsonData["vsphereProviderUUID"],jsonData["vsphereProviderDatacenter"])

        if response:
            return jsonify(response)
        else:
            return []

@app.route("/vsphereResourcePools", methods = ['POST', 'GET'])
def run_vsphereResourcePools():
    
    
    if request.method == 'GET':

        ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
    
        jsonData = request.args.to_dict()
        print(jsonData)
        response = ccp.getProviderVsphereResourcePools(jsonData["vsphereProviderUUID"],jsonData["vsphereProviderDatacenter"],jsonData["vsphereProviderCluster"])

        if response:
            return jsonify(response)
        else:
            return []

@app.route("/vsphereNetworks", methods = ['POST', 'GET'])
def run_vsphereNetworks():
    
    
    if request.method == 'GET':

        ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
    
        jsonData = request.args.to_dict()
        print(jsonData)
        response = ccp.getProviderVsphereNetworks(jsonData["vsphereProviderUUID"],jsonData["vsphereProviderDatacenter"])

        if response:
            return jsonify(response)
        else:
            return []

@app.route("/vsphereDatastores", methods = ['POST', 'GET'])
def run_vsphereDatastores():
    
    
    if request.method == 'GET':

        ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
    
        jsonData = request.args.to_dict()
        print(jsonData)
        response = ccp.getProviderVsphereDatastores(jsonData["vsphereProviderUUID"],jsonData["vsphereProviderDatacenter"])

        if response:
            return jsonify(response)
        else:
            return []

@app.route("/vsphereVMs", methods = ['POST', 'GET'])
def run_vsphereVMs():
    
    
    if request.method == 'GET':

        ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
    
        jsonData = request.args.to_dict()
        print(jsonData)
        response = ccp.getProviderVsphereVMs(jsonData["vsphereProviderUUID"],jsonData["vsphereProviderDatacenter"])

        if response:
            return jsonify(response)
        else:
            return []

@app.route("/vipPools", methods = ['POST', 'GET'])
def run_vipPools():
    
    
    if request.method == 'GET':

        ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
    
        jsonData = request.args.to_dict()
        print(jsonData)
        response = ccp.getVIPPools()

        if response:
            return jsonify(response)
        else:
            return []

@app.route("/clusterConfigTemplate", methods = ['POST', 'GET'])
def run_clusterConfigTemplate():
    
    if request.method == 'GET':

        ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
    
        try:
            with open("ccpRequest.json") as json_data:
                clusterData = json.load(json_data)
                return jsonify(clusterData)

        except IOError as e:
            return "I/O error({0}): {1}".format(e.errno, e.strerror)



if __name__ == "__main__":
    app.secret_key = "4qDID0dZoQfZOdVh5BzG"
    app.run(host='0.0.0.0', port=5000)

