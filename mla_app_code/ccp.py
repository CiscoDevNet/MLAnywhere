
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

import configparser
import json
import os
import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CCP:
    def __init__(self, url=None, username=None,password=None,cookie=None):
        self.url = url
        self.username = username
        self.password = password
        self.cookie = cookie

    def login(self):

        headers = {
            'content-type': 'application/json',
        }

        response = requests.request("POST", self.url + "/2/system/login?username=" + self.username + "&password=" + self.password,  headers=headers, verify=False)

        if response:
            self.cookie = response.cookies

        return response
    
    def getConfig(self, uuid):

        response = requests.request("GET", self.url + "/2/clusters/" + uuid + "/env", cookies=self.cookie, verify=False)
        
        return response


    def getClusters(self):

        response = requests.request("GET", self.url + "/2/clusters",cookies=self.cookie, verify=False)
        return response
    
    def getCluster(self,name):

        response = requests.request("GET", self.url + "/2/clusters/"+name,cookies=self.cookie, verify=False)

        return response

    
    def getProviderClientConfigs(self):

        response = requests.request("GET", self.url + "/2/providerclientconfigs",cookies=self.cookie, verify=False)

        return response
    
    def getProviderVsphereDatacenters(self,providerClientUUID):

        response = requests.request("GET", self.url + "/2/providerclientconfigs/" + providerClientUUID + "/vsphere/datacenter",cookies=self.cookie, verify=False)

        response = response.json()

        if "Datacenters" in response:
            return response["Datacenters"]
        else:
            return response

    def getProviderVsphereClusters(self,providerClientUUID,datacenterName):

        response = requests.request("GET", self.url + "/2/providerclientconfigs/" + providerClientUUID + "/vsphere/datacenter/" + datacenterName + "/cluster",cookies=self.cookie, verify=False)

        response = response.json()

        if "Clusters" in response:
            return response["Clusters"]
        else:
            return response
    
    def getProviderVsphereNetworks(self,providerClientUUID,datacenterName):

        response = requests.request("GET", self.url + "/2/providerclientconfigs/" + providerClientUUID + "/vsphere/datacenter/" + datacenterName + "/network",cookies=self.cookie, verify=False)

        response = response.json()

        if "Networks" in response:
            return response["Networks"]
        else:
            return response
    
    def getProviderVsphereVMs(self,providerClientUUID,datacenterName):

        response = requests.request("GET", self.url + "/2/providerclientconfigs/" + providerClientUUID + "/vsphere/datacenter/" + datacenterName + "/vm",cookies=self.cookie, verify=False)

        response = response.json()

        if "VMs" in response:
            return response["VMs"]
        else:
            return response

    def getProviderVsphereDatastores(self,providerClientUUID,datacenterName):

        response = requests.request("GET", self.url + "/2/providerclientconfigs/" + providerClientUUID + "/vsphere/datacenter/" + datacenterName + "/datastore",cookies=self.cookie, verify=False)

        response = response.json()

        if "Datastores" in response:
            return response["Datastores"]
        else:
            return response

    def getProviderVsphereResourcePools(self,providerClientUUID,datacenterName,clusterName):

        response = requests.request("GET", self.url + "/2/providerclientconfigs/" + providerClientUUID + "/vsphere/datacenter/" + datacenterName + "/cluster/" + clusterName + "/pool",cookies=self.cookie, verify=False)

        response = response.json()

        if "Pools" in response:
            return response["Pools"]
        else:
            return response
    
    def getVIPPools(self):

        response = requests.request("GET", self.url + "/2/network_service/subnets",cookies=self.cookie, verify=False)

        response = response.json()

        if "Pools" in response:
            return response["Pools"]
        else:
            return response
    
    def deployCluster(self, newClusterDetails):

        headers = {
            'content-type': 'application/json',
        }

        response = requests.request("POST", self.url + "/2/clusters", json=newClusterDetails,cookies=self.cookie, headers=headers, verify=False)

        return response


    def deployClusterFromFile(self, newClusterDetails):

        try:
            with open(newClusterDetails) as json_data:
                data = json.load(json_data) 

            headers = {
                'content-type': 'application/json',
            }

            response = requests.request("POST", self.url + "/2/clusters", json=data,cookies=self.cookie, headers=headers, verify=False)

            return response

        except IOError as e:
            return "I/O error({0}): {1}".format(e.errno, e.strerror)


    def checkClusterAlreadyExists(self,clusterName):

        clusters = self.getClusters()

        clusters = clusters.json()

        for cluster in clusters:
            if clusterName in cluster.values():
                return True
        
        return False