
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

from flask import Flask, json, render_template, request, session, Response, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from kubernetes import client, utils
import kubernetes.utils
from kubernetes.client.rest import ApiException

from kubernetes  import config as kubeConfig
from ccp import CCP
from mlaConfig import config
import proxy 

import os,sys
import requests
from flask_socketio import SocketIO, emit
import subprocess
from datetime import timedelta

import time

import uuid
import secrets

import re

import logging

from pprint import pprint

import time

#logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)
socketio = SocketIO(app)

ALLOWED_EXTENSIONS = set(['py'])

API_VERSION = 3

@app.route("/")
def index():
    if request.method == 'GET':
        return render_template('splashScreen.html')


##################################
# Overview of existing Clusters
##################################
@app.route("/clusterOverview", methods = ['GET'])
def clusterOverview():
    session['sessionUUID'] =  uuid.UUID(bytes=secrets.token_bytes(16))
    
    kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
    
    files = [f for f in os.listdir(kubeConfigDir) if os.path.isfile(os.path.join(kubeConfigDir, f))]
    
    kubeConfigs = []
    for file in files:
        kubeConfigs.append(file[4:])
    
    return render_template('clusterOverview.html', clusters=kubeConfigs)
    

##################################
# REGISTER EXISTING CLUSTER
##################################

@app.route("/existingClusterUpload", methods = ['POST', 'GET'])
def existingClusterUpload():
    if request.method == 'GET':
        return render_template('existingClusterUpload.html')
    else:
        session['sessionUUID'] =  uuid.UUID(bytes=secrets.token_bytes(16))
        session['customCluster'] = True

        if 'file' not in request.files:
            return 'No file provided', 400
        
        #if 'clusterName' not in request.form:
            #return 'Cluster name not defined', 400

        file = request.files['file']
        #clusterName = request.form['clusterName']
        clusterName = str(session['sessionUUID'])

        if file.filename == '':
            return 'No file provided', 400
        
        if clusterName == '':
            return 'Cluster name not defined', 400

        if file:
            kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
            
            clusterName = clusterName.replace(' ', '_')
            filename = 'k8s_' + clusterName
            
            file.save(os.path.join(kubeConfigDir, filename))
            return jsonify(dict(redirectURL='/deployKubeflow?cluster=' + filename))


##################################
# LOGIN TO CCP
##################################

@app.route("/ccpLogin")
def run_ccpLogin():

    if request.method == 'POST':

        ccp = CCP("https://" + request.form['IP Address'],request.form['Username'],request.form['Password'])
                
        loginV2 = ccp.loginV2()
        loginV3 = ccp.loginV3()

        if not loginV2 and not loginV3:
            print ("There was an issue with login: " + login.text)
            return render_template('ccpLogin.html')
        else:
            session['ccpURL'] = "https://" + request.form['IP Address']
            session['ccpToken'] = loginV2.cookies.get_dict()
            session['x-auth-token'] = loginV3

            return render_template('ccpClusterCreation.html')

    return render_template('ccpLogin.html')


@app.route("/testConnection", methods = ['POST', 'GET'])
def run_testConnection():
    
    if request.method == 'POST':

        jsonData = request.get_json()
        
        ccp = CCP("https://" + jsonData['ipAddress'],jsonData['username'],jsonData['password'])

        
        # vip pools UUID still requires the v2 API so you need to login for both the v2 and v3 API until the vip pools has been moved to v3
               
        loginV2 = ccp.loginV2()
        loginV3 = ccp.loginV3()

        if not loginV2 and not loginV3:
            socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': config.ERROR_CCP_LOGIN })
            return json.dumps({'success':False}), 401, {'ContentType':'application/json'} 
        else:
            session['ccpURL'] = "https://" + jsonData['ipAddress']
            session['ccpToken'] = loginV2.cookies.get_dict()
            session['sessionUUID'] =  uuid.UUID(bytes=secrets.token_bytes(16))
            session['x-auth-token'] = loginV3

            socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_CCP_LOGIN })
            return jsonify(dict(redirectURL='/ccpClusterCreation'))
    
    return render_template('ccpLogin.html')


##################################
# CREATE CCP CLUSTER
##################################

@app.route('/checkClusterAlreadyExists', methods=['GET', 'POST'])
def checkClusterAlreadyExists():

    if request.method == 'GET':

        if "ccpToken" in session and "x-auth-token" in session:

            ccp = CCP(session['ccpURL'],"","",session['ccpToken'],session['x-auth-token'])
        
            jsonData = request.args.to_dict()

            clusterName = jsonData["clusterName"]

            if not ccp.checkClusterAlreadyExists(clusterName):
                return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
            else:
                return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 


@app.route("/ccpClusterCreation", methods = ['POST', 'GET'])
def run_ccpClusterCreation():

        if request.method == 'POST':

            uuid = ""

            if "ccpToken" not in session or "x-auth-token" not in session:
                return render_template('ccpLogin.html')

            ccp = CCP(session['ccpURL'],"","",session['ccpToken'],session['x-auth-token'])

            formData = request.get_json()
            
            try:
                if API_VERSION == 2:
                    with open("ccpRequestV2.json") as json_data:
                        clusterData = json.load(json_data)
                        print(clusterData)
                else:
                    with open("ccpRequestV3.json") as json_data:
                        clusterData = json.load(json_data)
            except IOError as e:
                
                socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': config.ERROR_DEPLOY_CLUSTER_FAILED})
                return json.dumps({'success':False,"errorCode":"ERROR_DEPLOY_CLUSTER_FAILED","errorMessage":config.ERROR_DEPLOY_CLUSTER_FAILED,"errorMessageExtended":e}), 400, {'ContentType':'application/json'}

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
                        socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_PROXY_CREATING_TEMP_DIR })
                        os.makedirs("./tmp-keys/")
                    except OSError as e:
                        if e.errno != errno.EEXIST:
                            socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': config.ERROR_CONFIGURING_PROXY })
                            return json.dumps({'success':False,"errorCode":"ERROR_CONFIGURING_PROXY","errorMessage":config.ERROR_CONFIGURING_PROXY,"errorMessageExtended":e}), 400, {'ContentType':'application/json'}


                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_PROXY_GENERATING_KEYS })

                keyName = "{}-{}".format(session["sessionUUID"],formData["clusterName"])    

                proxy.generateTemporaryKeys(keyName,"./tmp-keys")
                
                with open("./tmp-keys/{}.pub".format(keyName)) as f:
                    publicKey = f.read().splitlines() 
                
                sshKey = str(publicKey[0])
                clusterData["ssh_key"] = sshKey
                
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_PROXY_GENERATING_KEYS_COMPLETE })

            else:
                clusterData["ssh_key"] = formData["sshKey"] 
            
            if "vsphereResourcePools" not in formData:
                formData["vsphereResourcePools"] = ""

            if API_VERSION == 2:
                clusterData["name"] = formData["clusterName"]
                clusterData["datacenter"] = formData["vsphereDatacenters"]
                clusterData["cluster"] = formData["vsphereClusters"]
                clusterData["resource_pool"] = formData["vsphereClusters"] + "/" + formData["vsphereResourcePools"]
                clusterData["datastore"] = formData["vsphereDatastores"] 
                clusterData["ingress_vip_pool_id"] = formData["vipPools"] 
                clusterData["master_node_pool"]["template"] = formData["tenantImageTemplate"] 
                clusterData["worker_node_pool"]["template"] = formData["tenantImageTemplate"] 
                clusterData["node_ip_pool_uuid"] = formData["vipPools"] 
                clusterData["networks"] = [formData["vsphereNetworks"] ]
                clusterData["provider_client_config_uuid"] = formData["vsphereProviders"]
                clusterData["deployer"]["provider"]["vsphere_client_config_uuid"] = formData["vsphereProviders"] 
                clusterData["deployer"]["provider"]["vsphere_datacenter"] = formData["vsphereDatacenters"] 
                clusterData["deployer"]["provider"]["vsphere_datastore"] = formData["vsphereDatastores"] 
                clusterData["deployer"]["provider"]["vsphere_working_dir"] = "/" + formData["vsphereDatacenters"] + "/vm"
            else:
                clusterData["name"] = formData["clusterName"]
                clusterData["subnet_id"] = formData["vipPools"] 
                clusterData["master_group"]["template"] = formData["tenantImageTemplate"] 
                clusterData["node_groups"][0]["template"] = formData["tenantImageTemplate"] 
                clusterData["provider"] = formData["vsphereProviders"]
                clusterData["vsphere_infra"]["datacenter"] = formData["vsphereDatacenters"] 
                clusterData["vsphere_infra"]["datastore"] = formData["vsphereDatastores"] 
                clusterData["vsphere_infra"]["networks"] = [ formData["vsphereNetworks"] ]
                clusterData["vsphere_infra"]["cluster"] = formData["vsphereClusters"] 
                clusterData["vsphere_infra"]["resource_pool"] = formData["vsphereResourcePools"]
                clusterData["node_groups"][0]["ssh_key"] = clusterData["ssh_key"]
                clusterData["master_group"]["ssh_key"] = clusterData["ssh_key"]
                clusterData.pop('ssh_key', None)

            socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_DEPLOY_CLUSTER })

            response = ccp.deployCluster(clusterData)

            if API_VERSION == 2 :

                if (response.status_code == 200) or (response.status_code == 201) :
                    socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_DEPLOY_CLUSTER_COMPLETE })
            
                if "uuid" not in response.json():
                    socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': config.ERROR_DEPLOY_CLUSTER_FAILED })
                    return json.dumps({'success':False,"errorCode":"ERROR_DEPLOY_CLUSTER_FAILED","errorMessage":config.ERROR_DEPLOY_CLUSTER_FAILED,"errorMessageExtended":response.text}), 400, {'ContentType':'application/json'}

                uuid = response.json()["uuid"]
            else:
                if "id" not in response.json():
                    socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': config.ERROR_DEPLOY_CLUSTER_FAILED })
                    return json.dumps({'success':False,"errorCode":"ERROR_DEPLOY_CLUSTER_FAILED","errorMessage":config.ERROR_DEPLOY_CLUSTER_FAILED,"errorMessageExtended":response.text}), 400, {'ContentType':'application/json'}

                uuid = response.json()["id"]

            kubeConfig = ccp.getConfig(uuid)

            if API_VERSION == 2 :

                if "apiVersion" in kubeConfig.text:

                    socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_CREATING_KUBE_CONFIG })

                    kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
                    if not os.path.exists(kubeConfigDir):
                        try:
                            os.makedirs(kubeConfigDir)
                        except OSError as e:
                            if e.errno != errno.EEXIST:
                                raise

                    
                    with open("{}/{}".format(kubeConfigDir,'k8s_' + str(session["sessionUUID"])), "w") as f:
                        f.write(kubeConfig.text)
                else:
                    socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': config.ERROR_KUBECONFIG_MISSING})
                    return json.dumps({'success':False,"errorCode":"ERROR_KUBECONFIG_MISSING","errorMessage":config.ERROR_KUBECONFIG_MISSING}), 400, {'ContentType':'application/json'}

            else:

                # it looks like the CCP V3 API has made the cluster creation async so we get back a response straight away however
                # theres a status field which shows "CREATING". Will need to wait until this is "READY"

                if "status" in kubeConfig.text:
                    while kubeConfig.json()["status"] == "CREATING":
                        kubeConfig = ccp.getConfig(uuid)
                        socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_DEPLOY_CLUSTER })
                        time.sleep(30)

                    if kubeConfig.json()["status"] != "READY":
                        socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': config.ERROR_DEPLOY_CLUSTER_FAILED })
                        return json.dumps({'success':False,"errorCode":"ERROR_DEPLOY_CLUSTER_FAILED","errorMessage":config.ERROR_DEPLOY_CLUSTER_FAILED,"errorMessageExtended":response.text}), 400, {'ContentType':'application/json'}

                    socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_DEPLOY_CLUSTER_COMPLETE })

                    if "kubeconfig" in kubeConfig.text:

                        kubeConfig = kubeConfig.json()["kubeconfig"]

                        socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_CREATING_KUBE_CONFIG })

                        kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
                        if not os.path.exists(kubeConfigDir):
                            try:
                                os.makedirs(kubeConfigDir)
                            except OSError as e:
                                if e.errno != errno.EEXIST:
                                    raise

                        
                        with open("{}/{}".format(kubeConfigDir,session["sessionUUID"]), "w") as f:
                            f.write(kubeConfig)
                    else:
                        socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': config.ERROR_KUBECONFIG_MISSING})
                        return json.dumps({'success':False,"errorCode":"ERROR_KUBECONFIG_MISSING","errorMessage":config.ERROR_KUBECONFIG_MISSING}), 400, {'ContentType':'application/json'}

            # if a proxy is required then we need to insert his once the worker nodes have been deployed

            if "proxyInput" in formData:
                cluster = ccp.getCluster(clusterData["name"])
                if "uuid" in cluster.text:
                    cluster = cluster.json()
                    nodes = cluster["nodes"]
                    privateKey = "{}-{}".format(session["sessionUUID"],clusterData["name"])
                    publicKey = "{}-{}.pub".format(session["sessionUUID"],clusterData["name"])
                    
                    if os.path.isfile('./tmp-keys/{}'.format(privateKey)) and os.path.isfile('./tmp-keys/{}'.format(publicKey)) :
                        for node in nodes:

                            socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_DEPLOYING_PROXY + " " + node["public_ip"] })
                            proxy.sendCommand(node["public_ip"],'ccpuser','./tmp-keys/{}'.format(privateKey),formData["sshKey"],'configure_proxy.sh',proxyInput )
                    else:
                        socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': config.ERROR_PROXY_CONFIGURATION})
                    
                    socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_PROXY_SSH_CLEANUP})

                    proxy.deleteTemporaryKeys(privateKey,publicKey,"./tmp-keys")

                else:
                    socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': config.ERROR_DEPLOY_CLUSTER_FAILED})
                    return json.dumps({'success':False,"errorCode":"ERROR_DEPLOY_CLUSTER_FAILED","errorMessage":config.ERROR_DEPLOY_CLUSTER_FAILED,"errorMessageExtended":cluster.text}), 400, {'ContentType':'application/json'}

            socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_DEPLOY_CLUSTER_COMPLETE})

            return jsonify(dict(redirectURL='/deployKubeflow'))

        elif request.method == 'GET':

            if "ccpToken" in session:
                return render_template('ccpClusterCreation.html')
            else:
                return render_template('ccpLogin.html')

            
##################################
# DEPLOY KUBEFLOW
##################################

@app.route("/deploy", methods = ['POST'])
def deploy():
    deploy_mla('asdf')

def deploy_mla(kubeconfig_name):
    kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
    kubeSessionEnv = {**os.environ, 'KUBECONFIG': "{}/{}".format(kubeConfigDir, kubeconfig_name)}
    
    socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_KUBECTL_STARTING_INSTALL)})
    
    proc = subprocess.Popen(["kubectl","apply","-f","mla_tenant.yaml"],stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=kubeSessionEnv)
    proc.wait()
    (stdout, stderr) = proc.communicate()
    
    if proc.returncode != 0:
        socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_MLA_YAML,stderr.decode("utf-8") )})
        return json.dumps({'success':False,"errorCode": "ERROR_KUBEFLOW_YAML","errorMessage":config.ERROR_MLA_YAML}), 400, {'ContentType':'application/json'}
    else:
        socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_MLA_YAML)})
    
    return


@app.route("/deployKubeflow", methods = ['POST', 'GET'])
def run_deployKubeflow():
    
    if request.method == 'POST':
        if "customCluster" in session or ("ccpToken" in session and "x-auth-token" in session):

            deploy_mla('k8s_' + str(session["sessionUUID"]))
            
            return jsonify(dict(redirectURL='/postInstallTasks'))
        else:
            return jsonify(dict(redirectURL='/clusterOverview'))
    
    elif request.method == 'GET':

            if "customCluster" in session or ("ccpToken" in session and "x-auth-token" in session):
                return render_template('deployKubeflow.html')
            else:
                return render_template('clusterOverview.html')


##################################
# POST INSTALL VIEW
##################################
            
@app.route("/postInstallTasks", methods = ['GET'])
def run_postInstallTasks():
    cluster = request.args.get('cluster')
    if "customCluster" in session or ("ccpToken" in session and "x-auth-token" in session):
        if cluster != '' and cluster != None:
            return render_template('postInstallTasks.html')
        else:
            return render_template('postInstallTasks.html')
    else:
        return render_template('clusterOverview.html')
        

@app.route("/mladeploymentstatus", methods = ['GET'])
def mladeploymentstatus():
    cluster = request.args.get('cluster')

    if cluster == '' or cluster == None:
        cluster = 'k8s_' + str(session["sessionUUID"])

    kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
    kubeSessionEnv = {**os.environ, 'KUBECONFIG': "{}/{}".format(kubeConfigDir,session["sessionUUID"])}
    kubeConfig.load_kube_config(config_file="{}/{}".format(kubeConfigDir,cluster))

    api_instance = kubernetes.client.CoreV1Api()

    nodes = api_instance.list_node(watch=False)
    for node in nodes.items:
        for address in node.status.addresses:
            if address.type == 'ExternalIP':
                node_ip = address.address

    services = api_instance.list_namespaced_service('default')
    for service in services.items:
        if service.metadata.name == 'mla-svc':
            node_port = service.spec.ports[0].node_port

    session["mla_endpoint"] = str(node_ip) + ':' + str(node_port)
    
    try:
        status = requests.get("http://{}/status".format(session["mla_endpoint"]))
    except:
        return 'Pod not reachable yet', 200
    
    if status.status_code == 200:
        return status.text, 200
    else:
        return 'Pod not reachable yet', 200


@app.route("/vsphereProviders", methods = ['POST', 'GET'])
def run_vsphereProviders():
    
    if request.method == 'GET':
        
        if "ccpToken" in session and "x-auth-token" in session:

            ccp = CCP(session['ccpURL'],"","",session['ccpToken'],session['x-auth-token'])
            response = ccp.getProviderClientConfigs()
            
            if response:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_VSPHERE_PROVIDERS })
                return jsonify(response)
            else:
                return config.ERROR_VSPHERE_PROVIDERS, 400

@app.route("/vsphereDatacenters", methods = ['POST', 'GET'])
def run_vsphereDatacenters():
    
    
    if request.method == 'GET':

        if "ccpToken" in session and "x-auth-token" in session:
            ccp = CCP(session['ccpURL'],"","",session['ccpToken'],session['x-auth-token'])
        
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

        if "ccpToken" in session and "x-auth-token" in session:
            ccp = CCP(session['ccpURL'],"","",session['ccpToken'],session['x-auth-token'])
        
            jsonData = request.args.to_dict()

            response = ccp.getProviderVsphereClusters(jsonData["vsphereProviderUUID"],jsonData["vsphereProviderDatacenter"])

            if response:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_VSPHERE_CLUSTERS })
                return jsonify(response)
            else:
                return jsonify("[]")

@app.route("/vsphereResourcePools", methods = ['POST', 'GET'])
def run_vsphereResourcePools():
    
    
    if request.method == 'GET':

        if "ccpToken" in session and "x-auth-token" in session:
            ccp = CCP(session['ccpURL'],"","",session['ccpToken'],session['x-auth-token'])
        
            jsonData = request.args.to_dict()

            response = ccp.getProviderVsphereResourcePools(jsonData["vsphereProviderUUID"],jsonData["vsphereProviderDatacenter"],jsonData["vsphereProviderCluster"])

            if response:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_VSPHERE_RESOURCE_POOLS })
                
                return jsonify(response)
            else:
                return jsonify("[]")

@app.route("/vsphereNetworks", methods = ['POST', 'GET'])
def run_vsphereNetworks():
    
    
    if request.method == 'GET':

        if "ccpToken" in session and "x-auth-token" in session:
            ccp = CCP(session['ccpURL'],"","",session['ccpToken'],session['x-auth-token'])
        
            jsonData = request.args.to_dict()

            response = ccp.getProviderVsphereNetworks(jsonData["vsphereProviderUUID"],jsonData["vsphereProviderDatacenter"])

            if response:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_VSPHERE_NETWORKS })
                return jsonify(response)
            else:
                return jsonify("[]")

@app.route("/vsphereDatastores", methods = ['POST', 'GET'])
def run_vsphereDatastores():
    
    
    if request.method == 'GET':

        if "ccpToken" in session and "x-auth-token" in session:
            ccp = CCP(session['ccpURL'],"","",session['ccpToken'],session['x-auth-token'])
        
            jsonData = request.args.to_dict()

            response = ccp.getProviderVsphereDatastores(jsonData["vsphereProviderUUID"],jsonData["vsphereProviderDatacenter"])

            if response:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_VSPHERE_DATASTORES })
                return jsonify(response)
            else:
                return jsonify("[]")

@app.route("/vsphereVMs", methods = ['POST', 'GET'])
def run_vsphereVMs():
    
    
    if request.method == 'GET':

        if "ccpToken" in session and "x-auth-token" in session:
            ccp = CCP(session['ccpURL'],"","",session['ccpToken'],session['x-auth-token'])
        
            jsonData = request.args.to_dict()

            response = ccp.getProviderVsphereVMs(jsonData["vsphereProviderUUID"],jsonData["vsphereProviderDatacenter"])

            if response:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_VSPHERE_VMS })
                return jsonify(response)
            else:
                return jsonify("[]")

@app.route("/vipPools", methods = ['POST', 'GET'])
def run_vipPools():
    
    if request.method == 'GET':

        if "ccpToken" in session and "x-auth-token" in session:
            ccp = CCP(session['ccpURL'],"","",session['ccpToken'],session['x-auth-token'])
        
            jsonData = request.args.to_dict()

            response = ccp.getVIPPools()

            if response:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_VIP_POOLS })
                return jsonify(response)
            else:
                return jsonify("[]")

@app.route("/clusterConfigTemplate", methods = ['POST', 'GET'])
def run_clusterConfigTemplate():
    
    if request.method == 'GET':

        if "ccpToken" in session and "x-auth-token" in session:
            ccp = CCP(session['ccpURL'],"","",session['ccpToken'],session['x-auth-token'])
        
            try:
                
                if API_VERSION == 2:
                    with open("ccpRequestV2.json") as json_data:
                        clusterData = json.load(json_data)
                        return jsonify(clusterData)
                else:
                    with open("ccpRequestV3.json") as json_data:
                        clusterData = json.load(json_data)
                        return jsonify(clusterData)


            except IOError as e:
                return "I/O error({0}): {1}".format(e.errno, e.strerror)

@app.route("/viewPods", methods = ['POST', 'GET'])
def run_viewPods():
    if request.method == 'GET':
        if "customCluster" in session or ("ccpToken" in session and "x-auth-token" in session):

            kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
            kubeSessionEnv = {**os.environ, 'KUBECONFIG': "{}/{}".format(kubeConfigDir,'k8s_' + str(session["sessionUUID"])),"KFAPP":config.KFAPP}
                
            kubeConfig.load_kube_config(config_file="{}/{}".format(kubeConfigDir,'k8s_' + str(session["sessionUUID"])))   
            
            api_instance = kubernetes.client.CoreV1Api()
            api_response = api_instance.list_pod_for_all_namespaces( watch=False)
            
            podsToReturn = []
            for i in api_response.items:
                podsToReturn.append({"NAMESPACE":  i.metadata.namespace, "NAME":i.metadata.name, "STATUS":i.status.phase})
            
            return jsonify(podsToReturn)

@app.route("/toggleIngress", methods = ['POST', 'GET'])
def run_toggleIngress():
    
    if request.method == 'POST':
        if "ccpToken" in session and "x-auth-token" in session:
            

            kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
            kubeSessionEnv = {**os.environ, 'KUBECONFIG': "{}/{}".format(kubeConfigDir,'k8s_' + str(session["sessionUUID"])),"KFAPP":config.KFAPP}
            #kubeSessionEnv = {**os.environ, 'KUBECONFIG': "kubeconfig.yaml","KFAPP":config.KFAPP}

            socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_KUBECTL_DEPLOY_INGRESS)})
        
            ingress = getIngressDetails()
            
            if ingress == None:
                socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_CONFIGURING_INGRESS,stderr.decode("utf-8") )})
            else:
                ingress = ingress.json

            if ingress["ACCESSTYPE"] == "NodePort":
                proc = subprocess.Popen(["kubectl","apply","-f","ingress.yaml"],stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=kubeSessionEnv)
                proc.wait()
                (stdout, stderr) = proc.communicate()

                if proc.returncode != 0:
                    socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_CONFIGURING_INGRESS,stderr.decode("utf-8") )})
                else:
                    socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_CONFIGURING_INGRESS)})
            elif ingress["ACCESSTYPE"] == "Ingress":
                proc = subprocess.Popen(["kubectl","delete","-f","ingress.yaml"],stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=kubeSessionEnv)
                proc.wait()
                (stdout, stderr) = proc.communicate()

                if proc.returncode != 0:
                    socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_CONFIGURING_NODEPORT,stderr.decode("utf-8") )})
                else:
                    socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_CONFIGURING_NODEPORT)})

        return getIngressDetails()


@app.route("/checkIngress", methods = ['POST', 'GET'])
def run_checkIngress():

    if request.method == 'GET':
        if "ccpToken" in session and "x-auth-token" in session:
            return getIngressDetails()

@app.route("/checkKubeflowDashboardReachability", methods = ['POST', 'GET'])
def run_checkKubeflowDashboardReachability():
    
    if request.method == 'GET':
        if "ccpToken" in session and "x-auth-token" in session:
            ingress = getIngressDetails()

            if ingress == None:
                return json.dumps({'success':False,"errorCode":"ERROR_KUBEFLOW_DASHBOARD_REACHABILITY","errorMessage":config.ERROR_KUBEFLOW_DASHBOARD_REACHABILITY}), 400, {'ContentType':'application/json'}
            else:
                ingress = ingress.json

            if ingress["IP"]:
                url = "http://{}".format(ingress["IP"])
                response = requests.request("GET", url , verify=False)
                if response.status_code == 200:
                    return jsonify({"STATUS": response.status_code , "URL":url})
                else:
                    return json.dumps({'success':False,"errorCode":"ERROR_KUBEFLOW_DASHBOARD_REACHABILITY","errorMessage":config.ERROR_KUBEFLOW_DASHBOARD_REACHABILITY}), 400, {'ContentType':'application/json'}


    return json.dumps({'success':False,"errorCode":"ERROR_KUBEFLOW_DASHBOARD_REACHABILITY","errorMessage":config.ERROR_KUBEFLOW_DASHBOARD_REACHABILITY}), 400, {'ContentType':'application/json'}

def getIngressDetails():
    
    if "ccpToken" in session and "x-auth-token" in session:

        kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
        kubeSessionEnv = {**os.environ, 'KUBECONFIG': "{}/{}".format(kubeConfigDir,'k8s_' + str(session["sessionUUID"])),"KFAPP":config.KFAPP}

        socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_KUBECTL_DEPLOY_INGRESS)})
        
        kubeConfig.load_kube_config(config_file="{}/{}".format(kubeConfigDir,'k8s_' + str(session["sessionUUID"])))
        #kubeConfig.load_kube_config(config_file="kubeconfig.yaml")

        api_instance = kubernetes.client.ExtensionsV1beta1Api()
        
        api_response = api_instance.list_namespaced_ingress(namespace="kubeflow",field_selector="metadata.name=kubeflow-ingress",watch=False)

        # check whether an ingress has been deployed and if not then return the nodeport for the ambassador service, otherwise return the loadbalancer
        # ip of the nginx controller - will probably needto update when deploying other non CCP instances in the future
        if api_response.items:
            for i in api_response.items:
                if "kubeflow-ingress" in i.metadata.name and "kubeflow" in i.metadata.namespace:
                    api_instance = kubernetes.client.CoreV1Api()
                    service = api_instance.list_namespaced_service(namespace="ccp",field_selector="metadata.name=nginx-ingress-controller",watch=False)
                    for j in service.items:
                        if (j.spec.load_balancer_ip):
                            return jsonify({"ACCESSTYPE":  "Ingress", "IP":j.spec.load_balancer_ip})
        else:
            workerAddress = ""
            workerPort = ""
            api_instance = kubernetes.client.CoreV1Api()
            nodes = api_instance.list_node( watch=False)
            for n in nodes.items:
                if "worker" in n.metadata.name:
                    for address in n.status.addresses:
                        if address.type == "ExternalIP" :
                            workerAddress = address.address

            api_instance = kubernetes.client.CoreV1Api()
            service = api_instance.list_namespaced_service(namespace="kubeflow",field_selector="metadata.name=ambassador",watch=False)
            for j in service.items:
                for port in j.spec.ports:
                    if port.node_port:
                        workerPort = str(port.node_port)

            if workerAddress and workerPort:
                return jsonify({"ACCESSTYPE":  "NodePort", "IP":"{}:{}".format(workerAddress,workerPort)})


@app.route('/downloadKubeconfig/<filename>', defaults={'filename': None}, methods=['GET'])
def downloadKubeconfig(filename):
    if "customCluster" in session or ("ccpToken" in session and "x-auth-token" in session):
        socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_DOWNLOAD_KUBECONFIG })
        kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
        return send_file("{}/{}".format(kubeConfigDir,'k8s_' + str(session["sessionUUID"])))
    else:
        return "Not found", 400


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	

@socketio.on('connect')
def test_connect():
    print("Connected to socketIO")

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)

if __name__ == "__main__":
    app.secret_key = "4qDID0dZoQfZOdVh5BzG"
    
    kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
    if not os.path.exists(kubeConfigDir):
        os.mkdir(kubeConfigDir)
    
    app.run(host='0.0.0.0', port=5000)
    socketio.run(app)
