
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

from flask import Flask, json, render_template, request, session, Response, jsonify, send_file


from ccp import CCP
from mlaConfig import config
import proxy 

import os,sys
import requests
from flask_socketio import SocketIO, emit
import subprocess
from datetime import timedelta

import uuid
import secrets

import re


app = Flask(__name__)
socketio = SocketIO(app)


@app.route("/testConnection", methods = ['POST', 'GET'])
def run_testConnection():
    
    if request.method == 'POST':

        jsonData = request.get_json()
        
        ccp = CCP("https://" + jsonData['ipAddress'],jsonData['username'],jsonData['password'])
                
        login = ccp.login()

        if not login:
            socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': config.ERROR_CCP_LOGIN })
            return json.dumps({'success':False}), 401, {'ContentType':'application/json'} 
        else:
            session['ccpURL'] = "https://" + jsonData['ipAddress']
            session['ccpToken'] = login.cookies.get_dict()
            session['sessionUUID'] =  uuid.UUID(bytes=secrets.token_bytes(16))

            socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_CCP_LOGIN })
            return jsonify(dict(redirectURL='/stage2'))
    
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
                        socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_SETTING_PROXY })

                        proxyInput = formData["proxyInput"]

                        regex = re.compile(
                                r'^((?:http)s?://)?' # http:// or https://
                                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                                r'localhost|' #localhost...
                                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                                r'(?::\d+)?' # optional port
                                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

                        if re.match(regex, proxyInput) is None:
                            
                            return json.dumps({'success':False,"errorCode":"ERROR_INVALID_PROXY","errorMessage":config.ERROR_INVALID_PROXY}), 400, {'ContentType':'application/json'}


                        # create a  directory to add temporary keys - will be deleted once the proxy has been configured
                        if not os.path.exists("./tmp-keys/"):
                            try:
                                os.makedirs("./tmp-keys/")
                            except OSError as e:
                                if e.errno != errno.EEXIST:
                                    socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': e })
                                    raise

                        socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_PROXY_GENERATING_KEYS })

                        proxy.generateTemporaryKeys("./tmp-keys/")
                        
                        with open("./tmp-keys/id_ed25519.pub") as f:
                            publicKey = f.readlines()
                        clusterData["ssh_key"] = publicKey[0]

                        socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_PROXY_GENERATING_KEYS_COMPLETE })

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

                    socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_DEPLOY_CLUSTER })
                    
                    response = ccp.deployCluster(clusterData)

                    if response.status_code == 200:
                        socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_DEPLOY_CLUSTER_COMPLETE })
                    

                    uuid = response.json()["uuid"]
                    
                    kubeConfig = ccp.getConfig(uuid)

                    if "apiVersion" in kubeConfig.text:

                        socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_CREATING_KUBE_CONFIG })

                        kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
                        if not os.path.exists(kubeConfigDir):
                            try:
                                os.makedirs(kubeConfigDir)
                            except OSError as e:
                                if e.errno != errno.EEXIST:
                                    raise

                        #print ("{}/config".format(kubeConfigDir))
                        #with open("{}/config".format(kubeConfigDir), "w") as f:
                        with open("{}/{}".format(kubeConfigDir,session["sessionUUID"]), "w") as f:
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

                                    socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_DEPLOYING_PROXY + " " + node["public_ip"] })

                                    proxy.sendCommand(node["public_ip"],'ccpuser','./tmp-keys/id_ed25519',formData["sshKey"],'configure_proxy.sh',proxyInput )
                            else:
                                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.ERROR_PROXY_CONFIGURATION})
                            
                            socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_PROXY_SSH_CLEANUP})

                            proxy.deleteTemporaryKeys("./tmp-keys/")

                        else:
                            #TODO SEND ERROR MESSAGE TO LOGGING
                            print("WRONG NAME")

                    socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_DEPLOY_CLUSTER_COMPLETE})

                    return jsonify(dict(redirectURL='/stage3'))

            except IOError as e:
                return "I/O error({0}): {1}".format(e.errno, e.strerror)

        elif request.method == 'GET':

            if "ccpToken" in session:
                return render_template('stage2.html')
            else:
                return render_template('stage1.html')

@app.route("/stage3", methods = ['POST', 'GET'])
def run_stage3():

    
    if request.method == 'POST':
        if "ccpToken" in session:

            kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
            kubeSessionEnv = {**os.environ, 'KUBECONFIG': "{}/{}".format(kubeConfigDir,session["sessionUUID"]),"KFAPP":config.KFAPP}

            print(kubeSessionEnv)

            socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_KUBECTL_STARTING_INSTALL)})

            proc = subprocess.Popen(["kubectl","create","-f","https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v1.11/nvidia-device-plugin.yml"],stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=kubeSessionEnv)
            proc.wait()
            (stdout, stderr) = proc.communicate()

            if proc.returncode != 0:
                socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_KUBECTL_NVIDIA_YAML,stderr.decode("utf-8") )})
            else:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_KUBECTL_NVIDIA_YAML)})



            proc = subprocess.Popen(["export","KFAPP=","{}".format(config.KFAPP)],stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True, env=kubeSessionEnv)

            proc.wait()
            (stdout, stderr) = proc.communicate()

            if proc.returncode != 0:
                socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_EXPORT_KFAPP,stderr.decode("utf-8") )})
            else:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_EXPORT_KFAPP)})



            proc = subprocess.Popen(["mkdir {}".format(config.KFAPP)],stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=kubeSessionEnv)
            proc.wait()
            (stdout, stderr) = proc.communicate()

            if proc.returncode != 0:
                socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_MKDIR_KFAPP,stderr.decode("utf-8") )})
            else:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_MKDIR_KFAPP)})



            proc = subprocess.Popen(["kfctl","init", "{}".format(config.KFAPP)],stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=kubeSessionEnv)
            proc.wait()
            (stdout, stderr) = proc.communicate()

            if proc.returncode != 0:
                socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_KFCTL_INIT,stderr.decode("utf-8") )})
            else:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_KFCTL_INIT)})



            proc = subprocess.Popen(["kfctl","generate","all", "-V"],stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd="{}".format(config.KFAPP), env=kubeSessionEnv)
            proc.wait()
            (stdout, stderr) = proc.communicate()

            if proc.returncode != 0:
                socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_KFCTL_GENERATE_ALL,stderr.decode("utf-8") )})
            else:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_KFCTL_GENERATE_ALL)})



            proc = subprocess.Popen(["kfctl","apply","all", "-V"],stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd="{}".format(config.KFAPP), env=kubeSessionEnv)
            proc.wait()
            (stdout, stderr) = proc.communicate()

            if proc.returncode != 0:
                socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_KFCTL_APPLY_ALL,stderr.decode("utf-8") )})
            else:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_KFCTL_APPLY_ALL)})
            

            
            return jsonify(dict(redirectURL='/stage4'))
        else:
            return jsonify(dict(redirectURL='/stage1'))
    
    elif request.method == 'GET':

            if "ccpToken" in session:
                return render_template('stage3.html')
            else:
                return render_template('stage1.html')

    
@app.route("/stage4")
def run_stage4():

    if request.method == 'GET':

        if "ccpToken" in session:
            return render_template('stage4.html')
        else:
            return render_template('stage1.html')



@app.route("/vsphereProviders", methods = ['POST', 'GET'])
def run_vsphereProviders():
    
    if request.method == 'GET':

        if "ccpToken" in session:

            ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
            response = ccp.getProviderClientConfigs()
            
            #if "access denied" in response.text:
            #    return render_template('stage1.html')

            if response:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_VSPHERE_PROVIDERS })
                return response.text
            else:
                return [config.ERROR_VSPHERE_PROVIDERS]

@app.route("/vsphereDatacenters", methods = ['POST', 'GET'])
def run_vsphereDatacenters():
    
    
    if request.method == 'GET':

        if "ccpToken" in session:
            ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
        
            jsonData = request.args.to_dict()
    
            response = ccp.getProviderVsphereDatacenters(jsonData["vsphereProviderUUID"])

            if response:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_VSPHERE_DATACENTERS })
                return jsonify(response)
            else:
                return [config.ERROR_VSPHERE_DATACENTERS]

@app.route("/vsphereClusters", methods = ['POST', 'GET'])
def run_vsphereClusters():
    
    
    if request.method == 'GET':

        if "ccpToken" in session:
            ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
        
            jsonData = request.args.to_dict()

            response = ccp.getProviderVsphereClusters(jsonData["vsphereProviderUUID"],jsonData["vsphereProviderDatacenter"])

            if response:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_VSPHERE_CLUSTERS })
                return jsonify(response)
            else:
                return []

@app.route("/vsphereResourcePools", methods = ['POST', 'GET'])
def run_vsphereResourcePools():
    
    
    if request.method == 'GET':

        if "ccpToken" in session:

            ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
        
            jsonData = request.args.to_dict()

            response = ccp.getProviderVsphereResourcePools(jsonData["vsphereProviderUUID"],jsonData["vsphereProviderDatacenter"],jsonData["vsphereProviderCluster"])

            if response:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_VSPHERE_RESOURCE_POOLS })
                return jsonify(response)
            else:
                return []

@app.route("/vsphereNetworks", methods = ['POST', 'GET'])
def run_vsphereNetworks():
    
    
    if request.method == 'GET':

        if "ccpToken" in session:

            ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
        
            jsonData = request.args.to_dict()

            response = ccp.getProviderVsphereNetworks(jsonData["vsphereProviderUUID"],jsonData["vsphereProviderDatacenter"])

            if response:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_VSPHERE_NETWORKS })
                return jsonify(response)
            else:
                return []

@app.route("/vsphereDatastores", methods = ['POST', 'GET'])
def run_vsphereDatastores():
    
    
    if request.method == 'GET':

        if "ccpToken" in session:

            ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
        
            jsonData = request.args.to_dict()

            response = ccp.getProviderVsphereDatastores(jsonData["vsphereProviderUUID"],jsonData["vsphereProviderDatacenter"])

            if response:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_VSPHERE_DATASTORES })
                return jsonify(response)
            else:
                return []

@app.route("/vsphereVMs", methods = ['POST', 'GET'])
def run_vsphereVMs():
    
    
    if request.method == 'GET':

        if "ccpToken" in session:

            ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
        
            jsonData = request.args.to_dict()

            response = ccp.getProviderVsphereVMs(jsonData["vsphereProviderUUID"],jsonData["vsphereProviderDatacenter"])

            if response:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_VSPHERE_VMS })
                return jsonify(response)
            else:
                return []

@app.route("/vipPools", methods = ['POST', 'GET'])
def run_vipPools():
    
    
    if request.method == 'GET':

        if "ccpToken" in session:

            ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
        
            jsonData = request.args.to_dict()

            response = ccp.getVIPPools()

            if response:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_VIP_POOLS })
                return jsonify(response)
            else:
                return []

@app.route("/clusterConfigTemplate", methods = ['POST', 'GET'])
def run_clusterConfigTemplate():
    
    if request.method == 'GET':

        if "ccpToken" in session:

            ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
        
            try:
                with open("ccpRequest.json") as json_data:
                    clusterData = json.load(json_data)
                    return jsonify(clusterData)

            except IOError as e:
                return "I/O error({0}): {1}".format(e.errno, e.strerror)

@app.route('/downloadKubeconfig', methods=['GET', 'POST'])
def downloadKubeconfig():

    if request.method == 'GET':

        if "ccpToken" in session:
            socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_DOWNLOAD_KUBECONFIG })
            kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
            return send_file("{}/{}".format(kubeConfigDir,session['sessionUUID']))
        else:
            return render_template('stage1.html')


@socketio.on('connect')
def test_connect():
    print("Connected to socketIO")

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)

if __name__ == "__main__":
    app.secret_key = "4qDID0dZoQfZOdVh5BzG"
    app.run(host='0.0.0.0', port=5000)
    socketio.run(app)

