
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

from flask import Flask, json, render_template, request, session, Response, jsonify, send_file, redirect
import kubernetes.client
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

import uuid
import secrets

import re

import logging

from pprint import pprint

import base64

#logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)
socketio = SocketIO(app)

ALLOWED_EXTENSIONS = set(['py'])


@app.route("/")
def index():
    if request.method == 'GET':
        return render_template('stage1.html')


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

            if "ccpToken" not in session:
                return render_template('stage1.html')

            ccp = CCP(session['ccpURL'],"","",session['ccpToken'])

            formData = request.get_json()
            
            try:
                with open("ccpRequest.json") as json_data:
                    
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

            if (response.status_code == 200) or (response.status_code == 201) :
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_DEPLOY_CLUSTER_COMPLETE })
            
            if "uuid" not in response.json():
                socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': config.ERROR_DEPLOY_CLUSTER_FAILED })
                return json.dumps({'success':False,"errorCode":"ERROR_DEPLOY_CLUSTER_FAILED","errorMessage":config.ERROR_DEPLOY_CLUSTER_FAILED,"errorMessageExtended":response.text}), 400, {'ContentType':'application/json'}

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

                
                with open("{}/{}".format(kubeConfigDir,session["sessionUUID"]), "w") as f:
                    f.write(kubeConfig.text)
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

            return jsonify(dict(redirectURL='/stage3'))

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
           
            socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_KUBECTL_STARTING_INSTALL)})

            proc = subprocess.Popen(["kubectl","apply","-f","https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v1.11/nvidia-device-plugin.yml"],stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=kubeSessionEnv)
            proc.wait()
            (stdout, stderr) = proc.communicate()

            if proc.returncode != 0:
                socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_KUBECTL_NVIDIA_YAML,stderr.decode("utf-8") )})
                return json.dumps({'success':False,"errorCode":"ERROR_KUBECTL_NVIDIA_YAML","errorMessage":config.ERROR_KUBECTL_NVIDIA_YAML}), 400, {'ContentType':'application/json'}
            else:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_KUBECTL_NVIDIA_YAML)})



            proc = subprocess.Popen(["export","KFAPP=","{}".format(config.KFAPP)],stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True, env=kubeSessionEnv)

            proc.wait()
            (stdout, stderr) = proc.communicate()

            if proc.returncode != 0:
                socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_EXPORT_KFAPP,stderr.decode("utf-8") )})
                return json.dumps({'success':False,"errorCode":"ERROR_EXPORT_KFAPP","errorMessage":config.ERROR_EXPORT_KFAPP}), 400, {'ContentType':'application/json'}
            else:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_EXPORT_KFAPP)})


            if not os.path.isdir("{}".format(config.KFAPP)):
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
                return json.dumps({'success':False,"errorCode":"ERROR_KFCTL_INIT","errorMessage":config.ERROR_KFCTL_INIT}), 400, {'ContentType':'application/json'}
            else:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_KFCTL_INIT)})



            proc = subprocess.Popen(["kfctl","generate","all", "-V"],stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd="{}".format(config.KFAPP), env=kubeSessionEnv)
            proc.wait()
            (stdout, stderr) = proc.communicate()

            if proc.returncode != 0:
                socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_KFCTL_GENERATE_ALL,stderr.decode("utf-8") )})
                return json.dumps({'success':False,"errorCode":"ERROR_KFCTL_GENERATE_ALL","errorMessage":config.ERROR_KFCTL_GENERATE_ALL}), 400, {'ContentType':'application/json'}
            else:
                socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_KFCTL_GENERATE_ALL)})



            proc = subprocess.Popen(["kfctl","apply","all", "-V"],stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd="{}".format(config.KFAPP), env=kubeSessionEnv)
            proc.wait()
            (stdout, stderr) = proc.communicate()

            if proc.returncode != 0:
                socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_KFCTL_APPLY_ALL,stderr.decode("utf-8") )})
                return json.dumps({'success':False,"errorCode":"ERROR_KFCTL_APPLY_ALL","errorMessage":config.ERROR_KFCTL_APPLY_ALL}), 400, {'ContentType':'application/json'}
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

@app.route("/stage5", methods = ['POST', 'GET'])
def run_stage5():

    if request.method == 'GET':

        if "ccpToken" in session:
            return render_template('stage5.html')
        else:
            return render_template('stage1.html')


@app.route("/vsphereProviders", methods = ['POST', 'GET'])
def run_vsphereProviders():
    
    if request.method == 'GET':

        if "ccpToken" in session:

            ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
            response = ccp.getProviderClientConfigs()
            
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

@app.route("/viewPods", methods = ['POST', 'GET'])
def run_viewPods():
    
    if request.method == 'GET':

        if "ccpToken" in session:

            ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
        

            kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
            kubeSessionEnv = {**os.environ, 'KUBECONFIG': "{}/{}".format(kubeConfigDir,session["sessionUUID"]),"KFAPP":config.KFAPP}
            #kubeSessionEnv = {**os.environ, 'KUBECONFIG': "kubeconfig.yaml","KFAPP":config.KFAPP}

            kubeConfig.load_kube_config(config_file="{}/{}".format(kubeConfigDir,session["sessionUUID"]))
            #kubeConfig.load_kube_config(config_file="kubeconfig.yaml")

            api_instance = kubernetes.client.CoreV1Api()


            api_response = api_instance.list_pod_for_all_namespaces( watch=False)
            
            podsToReturn = []
            for i in api_response.items:
                podsToReturn.append({"NAMESPACE":  i.metadata.namespace, "NAME":i.metadata.name, "STATUS":i.status.phase})
            
            return jsonify(podsToReturn)

@app.route("/toggleIngress", methods = ['POST', 'GET'])
def run_toggleIngress():
    
    if request.method == 'POST':
        if "ccpToken" in session:

            kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
            kubeSessionEnv = {**os.environ, 'KUBECONFIG': "{}/{}".format(kubeConfigDir,session["sessionUUID"]),"KFAPP":config.KFAPP}

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
        if "ccpToken" in session:
            return getIngressDetails()

@app.route("/checkKubeflowDashboardReachability", methods = ['POST', 'GET'])
def run_checkKubeflowDashboardReachability():
    
    if request.method == 'GET':
        if "ccpToken" in session:
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
    
    if "ccpToken" in session:

        kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
        kubeSessionEnv = {**os.environ, 'KUBECONFIG': "{}/{}".format(kubeConfigDir,session["sessionUUID"]),"KFAPP":config.KFAPP}

        socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': "{}".format(config.INFO_KUBECTL_DEPLOY_INGRESS)})
        
        kubeConfig.load_kube_config(config_file="{}/{}".format(kubeConfigDir,session["sessionUUID"]))
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


                

@app.route('/downloadKubeconfig', methods=['GET', 'POST'])
def downloadKubeconfig_redirect():

    return redirect('/downloadKubeconfig/kubeconfig.yaml')

@app.route('/downloadKubeconfig/<filename>', methods=['GET', 'POST'])
def downloadKubeconfig(filename):

    if request.method == 'GET':

        if "ccpToken" in session:
            socketio.emit('consoleLog', {'loggingType': 'INFO','loggingMessage': config.INFO_DOWNLOAD_KUBECONFIG })
            kubeConfigDir = os.path.expanduser(config.KUBE_CONFIG_DIR)
            return send_file("{}/{}".format(kubeConfigDir,session['sessionUUID']))
        else:
            return render_template('stage1.html')

@app.route('/checkClusterAlreadyExists', methods=['GET', 'POST'])
def checkClusterAlreadyExists():

    if request.method == 'GET':

        if "ccpToken" in session:

            ccp = CCP(session['ccpURL'],"","",session['ccpToken'])
        
            jsonData = request.args.to_dict()

            clusterName = jsonData["clusterName"]

            if not ccp.checkClusterAlreadyExists(clusterName):
                return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
            else:
                return json.dumps({'success':False}), 400, {'ContentType':'application/json'} 

@app.route('/createNotebookServer', methods=['GET', 'POST'])
def run_createNotebookServer():

    if request.method == 'POST':

        if "ccpToken" in session:

            ingress = getIngressDetails()

            if ingress == None:
                socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_CONFIGURING_INGRESS,stderr.decode("utf-8") )})
            else:
                ingress = ingress.json

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }

            new_notebooks = [
                {
                    'name': config.NOTEBOOK_NAME,
                    'cpu': config.NOTEBOOK_CPU,
                    'memory': config.NOTEBOOK_MEMORY 
                }
            ]
            
            for new_nb in new_notebooks:
                data = 'nm=' + new_nb['name'] + '&ns=kubeflow&imageType=standard&standardImages=gcr.io%2Fkubeflow-images-public%2Ftensorflow-1.13.1-notebook-cpu%3Av0.5.0&customImage=&cpu=' + new_nb['cpu'] + '&memory=' + new_nb['memory'] + '&ws_type=Existing&ws_name=' + new_nb['name'] + '&ws_mount_path=%2Fhome%2Fjovyan&extraResources=%7B%7D'

                response = requests.post('http://' + ingress["IP"] + '/jupyter/api/namespaces/kubeflow/notebooks', data, headers=headers)

            ready = False
            timeout = False
            counter = 0

            while ready != True or timeout != True:
                counter += 1
                nblist = get_notebooks(ingress["IP"])
                loop_ready = True
                for nb in nblist:
                    if 'running' not in nb['status'].keys():
                        loop_Ready = False
                
                if loop_ready == True:
                    ready = True
                
                if counter > 1000 and ready == False:
                    timeout = True     
                
            if response.status_code == 200:
                return json.dumps({'success':True,"errorCode":"INFO_JUPYTER_NOTEBOOK","message":config.INFO_JUPYTER_NOTEBOOK}), 200, {'ContentType':'application/json'}
            else:
                return json.dumps({'success':False,"errorCode":"ERROR_JUPYTER_NOTEBOOK","message":config.ERROR_JUPYTER_NOTEBOOK}), 400, {'ContentType':'application/json'}


        else:
            return render_template('stage1.html')

@app.route('/uploadFiletoJupyter', methods=['GET', 'POST'])
def run_uploadFiletoJupyter():

    if request.method == 'POST':

        if "ccpToken" in session:

            file = request.files.to_dict()

            filename = next(iter( file.keys() ))

            if file and allowed_file(file.filename):
                encoded = base64.b64encode(file.read())
                data = {'name':file.filename,'path':file.filename,'type':'file','format':'base64','content': str(encoded)}
                print(data)
            else:
                return json.dumps({'success':False,"errorCode":"ERROR_JUPYTER_NOTEBOOK","message":config.ERROR_JUPYTER_NOTEBOOK}), 400, {'ContentType':'application/json'}

            ingress = getIngressDetails()

            if ingress == None:
                socketio.emit('consoleLog', {'loggingType': 'ERROR','loggingMessage': "{} - {}".format(config.ERROR_CONFIGURING_INGRESS,stderr.decode("utf-8") )})
            else:
                ingress = ingress.json

            xsrf = get_jupyter_cookie(ingress["IP"])
            
            headers = {
                'Content-Type': 'application/json',
                'X-XSRFToken': xsrf
            }
            
            data = json.dumps(data)
            
            response = requests.put('http://' + ingress["IP"] + '/notebook/kubeflow/'+ config.NOTEBOOK_NAME +'/api/contents/' + file_name, cookies=dict(_xsrf=xsrf), headers=headers, data=data)

            if response.status_code == 200:
                return json.dumps({'success':True,"errorCode":"INFO_JUPYTER_NOTEBOOK","message":config.INFO_JUPYTER_NOTEBOOK}), 200, {'ContentType':'application/json'}
            else:
                return json.dumps({'success':False,"errorCode":"ERROR_JUPYTER_NOTEBOOK","message":config.ERROR_JUPYTER_NOTEBOOK}), 400, {'ContentType':'application/json'}

        else:
            return render_template('stage1.html')


def get_notebooks(ip):
    nblist = requests.get('http://' + ip + '/jupyter/api/namespaces/kubeflow/notebooks')
    nblist = json.loads(nblist.content)
    return nblist['notebooks']


def get_jupyter_cookie(ip):
    req = requests.get('http://' + ip + '/notebook/kubeflow/bolts-server/tree?')
    return req.cookies['_xsrf']


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
    app.run(host='0.0.0.0', port=5000)
    socketio.run(app)

