
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
    def __init__(self, url=None, username=None,password=None,cookie=None, token=None, apiVersion = 3):
        self.url = url
        self.username = username
        self.password = password
        self.cookie = cookie
        self.token = token
        self.apiVersion = apiVersion

    def loginV2(self):

        headers = {
            'content-type': 'application/json',
        }

        # vip pools UUID still requires the v2 API so you need to login for both the v2 and v3 API

        response = requests.request("POST", self.url + "/2/system/login?username=" + self.username + "&password=" + self.password,  headers=headers, verify=False)

        if response:
            self.cookie = response.cookies

        return response


    def loginV3(self):

        headers = {
            'content-type': 'application/json',
        }

        # vip pools UUID still requires the v2 API so you need to login for both the v2 and v3 API

        data = {"username":self.username,"password":self.password}
            
        response = requests.request("POST", self.url + "/v3/system/login",data=json.dumps(data),  headers=headers, verify=False)
            
        if "X-Auth-Token" in response.headers:
            self.token = response.headers["X-Auth-Token"]
            return response.headers["X-Auth-Token"]
    
        return None


    def getConfig(self, uuid):

        headers = {
            'content-type': 'application/json',
            'x-auth-token': self.token,
        }

        if self.apiVersion == 2:
            response = requests.request("GET", self.url + "/2/clusters/" + uuid + "/env", cookies=self.cookie, verify=False)
        else:
            response = requests.request("GET", self.url + "/v3/clusters/" + uuid + "/env",headers=headers, verify=False)

        return response


    def getClusters(self):

        headers = {
            'content-type': 'application/json',
            'x-auth-token': self.token,
        }

        if self.apiVersion == 2:
            response = requests.request("GET", self.url + "/2/clusters",cookies=self.cookie, verify=False)
        else:
            response = requests.request("GET", self.url + "/v3/clusters",headers=headers,  verify=False)

        return response
    
    def getCluster(self,name):

        headers = {
            'content-type': 'application/json',
            'x-auth-token': self.token,
        }

        if self.apiVersion == 2:
            response = requests.request("GET", self.url + "/2/clusters/"+name,cookies=self.cookie, verify=False)
        else:
            response = requests.request("GET", self.url + "/v3/clusters/"+name,headers=headers, verify=False)

        return response

    
    def getProviderClientConfigs(self):

        headers = {
            'content-type': 'application/json',
            'x-auth-token': self.token,
        }

        # the v2 API had a "uuid" attribute while the v3 API has renamed this to "id". for the v3 API I'm adding a "uuid" key to the response (newProvidersList)
        # so that we don't have to update the front end calls as it's expecting "uuid", not "id"

        if self.apiVersion == 2:
            response = requests.request("GET", self.url + "/2/providerclientconfigs",cookies=self.cookie, verify=False)
        else:
            response = requests.request("GET", self.url + "/v3/providers",headers=headers, verify=False)
            if response:
                newProviderList = []
                for provider in response.json():
                    provider["uuid"] = provider["id"]
                    newProviderList.append(provider)
                return newProviderList

        return response.text
    
    def getProviderVsphereDatacenters(self,providerClientUUID):

        headers = {
            'content-type': 'application/json',
            'x-auth-token': self.token,
        }

        if self.apiVersion == 2:
            response = requests.request("GET", self.url + "/2/providerclientconfigs/" + providerClientUUID + "/vsphere/datacenter",cookies=self.cookie, verify=False)
        else:
            response = requests.request("GET", self.url + "/v3/providers/" + providerClientUUID + "/datacenters",headers=headers, verify=False)

        response = response.json()

        if "Datacenters" in response:
            return response["Datacenters"]
        else:
            return response

    def getProviderVsphereClusters(self,providerClientUUID,datacenterName):

        headers = {
            'content-type': 'application/json',
            'x-auth-token': self.token,
        }

        if self.apiVersion == 2:
            response = requests.request("GET", self.url + "/2/providerclientconfigs/" + providerClientUUID + "/vsphere/datacenter/" + datacenterName + "/cluster",cookies=self.cookie, verify=False)
        else:
            response = requests.request("GET", self.url + "/v3/providers/" + providerClientUUID + "/clusters?datacenter="+datacenterName,headers=headers, verify=False)

        
        response = response.json()

        if "Clusters" in response:
            return response["Clusters"]
        else:
            return response
    
    def getProviderVsphereNetworks(self,providerClientUUID,datacenterName):

        headers = {
            'content-type': 'application/json',
            'x-auth-token': self.token,
        }

        if self.apiVersion == 2:
            response = requests.request("GET", self.url + "/2/providerclientconfigs/" + providerClientUUID + "/vsphere/datacenter/" + datacenterName + "/network",cookies=self.cookie, verify=False)
        else:
            response = requests.request("GET", self.url + "/v3/providers/" + providerClientUUID + "/networks?datacenter="+datacenterName,headers=headers, verify=False)

        response = response.json()

        if "Networks" in response:
            return response["Networks"]
        else:
            return response
    
    def getProviderVsphereVMs(self,providerClientUUID,datacenterName):

        headers = {
            'content-type': 'application/json',
            'x-auth-token': self.token,
        }

        if self.apiVersion == 2:
            response = requests.request("GET", self.url + "/2/providerclientconfigs/" + providerClientUUID + "/vsphere/datacenter/" + datacenterName + "/vm",cookies=self.cookie, verify=False)
        else:
            response = requests.request("GET", self.url + "/v3/providers/" + providerClientUUID + "/vms?datacenter="+datacenterName,headers=headers, verify=False)

        response = response.json()

        if "VMs" in response:
            return response["VMs"]
        else:
            return response

    def getProviderVsphereDatastores(self,providerClientUUID,datacenterName):

        headers = {
            'content-type': 'application/json',
            'x-auth-token': self.token,
        }

        if self.apiVersion == 2:
            response = requests.request("GET", self.url + "/2/providerclientconfigs/" + providerClientUUID + "/vsphere/datacenter/" + datacenterName + "/datastore",cookies=self.cookie, verify=False)
        else:
            response = requests.request("GET", self.url + "/v3/providers/" + providerClientUUID + "/datastores?datacenter="+datacenterName,headers=headers, verify=False)

        response = response.json()

        if "Datastores" in response:
            return response["Datastores"]
        else:
            return response

    def getProviderVsphereResourcePools(self,providerClientUUID,datacenterName,clusterName):

        headers = {
            'content-type': 'application/json',
            'x-auth-token': self.token,
        }

        if self.apiVersion == 2:
            response = requests.request("GET", self.url + "/2/providerclientconfigs/" + providerClientUUID + "/vsphere/datacenter/" + datacenterName + "/cluster/" + clusterName + "/pool",cookies=self.cookie, verify=False)
        else:
            response = requests.request("GET", self.url + "/v3/providers/" + providerClientUUID + "/resource-pools?datacenter="+datacenterName,headers=headers, verify=False)

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
            'x-auth-token': self.token,
        }

        if self.apiVersion == 2:
            headers = {
                'content-type': 'application/json',
            }
            response = requests.request("POST", self.url + "/2/clusters", json=newClusterDetails,cookies=self.cookie, headers=headers, verify=False)
        else:
            headers = {
                'content-type': 'application/json',
                'x-auth-token': self.token,
            }
            response = requests.request("POST", self.url + "/v3/clusters/", json=newClusterDetails, headers=headers, verify=False)

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