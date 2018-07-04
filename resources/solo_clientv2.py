#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import requests

from requests.auth import HTTPBasicAuth
from requests.status_codes import codes

HTTP_OK = codes.ok                        #200
HTTP_ACCEPTED = codes.accepted            #202
HTTP_NO_CONTENT = codes.no_content        #204
HTTP_BAD_REQUEST = codes.bad_request      #400
HTTP_NOT_FOUND = codes.not_found          #404
HTTP_SERVER_ERROR = codes.server_error    #500

ENDPOINT="http://172.25.0.2:8181"
USER="karaf"
PASSWORD="karaf"

class SoloClient:
    
    def __init__(self, endpoint=ENDPOINT, user=USER, password=PASSWORD):
        self.authentication = HTTPBasicAuth(user, password)
        self.url_post_vnet = endpoint + "/overlay/orchestrator/v1/vnet"
        self.url_get_vnets = endpoint + "/overlay/orchestrator/v1/vnet"
        self.url_get_vnet = endpoint + "/overlay/orchestrator/v1/vnet/network/"
        self.url_get_state = endpoint + "/overlay/orchestrator/v1/vnet/state/network/"
        self.url_get_backup = endpoint + "/overlay/orchestrator/v1/vnet/backup"
        self.url_delete_vnet = endpoint + "/overlay/orchestrator/v1/vnet/network/"

    def createVNet(self, jsonVnet):
    	if jsonVnet is not None:
            response = requests.post(self.url_post_vnet, data=json.dumps(jsonVnet), auth=self.authentication)
            if (response.status_code == HTTP_ACCEPTED):
                return jsonVnet["vNets"][0]["vNetworkName"]
            else:
                return False

    def removeVNet(self, networkName):
        if networkName is not None:
            response = requests.delete(self.url_delete_vnet+networkName, auth=self.authentication)
            if (response.status_code == HTTP_NO_CONTENT):
                return True
            else:
                return False

    def inspectVNet(self, networkName):
        response = requests.get(self.url_get_state+networkName, auth=self.authentication)
        if (response.status_code == HTTP_SERVER_ERROR):
            raise RuntimeError("Error getting a response from the REST server")
        if (response.status_code == HTTP_NOT_FOUND):
        	return False
      
        state = json.loads(response.text)

        if (state["State"] == "CREATED"):
            return True
        else:
            return False

    def _getVnets(self):
        response = requests.get(self.url_get_vnets, auth=self.authentication)
        if (response.status_code != HTTP_OK):
            return json.loads(response.text)
        else:
            return None

    def getVNetId(self, networkName):
        vnets = self._getVnets()
        if vnets is not None:
            for vnet in vnets["vNets"]:
                if vnet["vNetworkName"] == networkName:
                    return vnet["vNetworkId"]
        return None

    def getVNetName(self, networkId):
        vnets = self._getVnets()
        if vnets is not None:
            for vnet in vnets["vNets"]:
                if vnet["vNetworkId"] == networkId:
                    return vnet["vNetworkName"]
        return None

class JsonVNet:
    def __init__(self, networkName):
        self.obj = {"vNetworkName": networkName, "vSwitches": [], "vPorts": [], "vLinks": [], "vHosts": []}

    def addVSwitch(self, dpid, controllerIp, controllerPort, of_version, phyDevice):
        vswitch = {}
        vswitch["datapathId"] = dpid
        vswitch["controllerIp"] = controllerIp
        vswitch["controllerPort"] = controllerPort
        vswitch["openflowVersion"] = of_version
        vswitch["physicalDevice"] = phyDevice

        vswitch["vNetworkName"] = self.obj["vNetworkName"]

        self.obj["vSwitches"].append(vswitch)

    def addVPort(self, dpid, virtualPort, physicalPort, binding, vlan=None):
        vport = {}
        vport["datapathId"] = dpid
        vport["virtualPortNumber"] = virtualPort
        vport["physicalPortName"] = physicalPort
        vport["bindingType"] = binding
        if (vlan != None):
            vport["vlanId"] = vlan

        vport["vNetworkName"] = self.obj["vNetworkName"]

        self.obj["vPorts"].append(vport)

    def addVLink(self, srcDpid, dstDpid, srcVirtualPort, dstVirtualPort, srcPhysicalPort, dstPhysicalPort, linkType, vlan=None, bandwidth=None):
        vlink = {}
        vlink["srcDatapathId"] = srcDpid
        vlink["dstDatapathId"] = dstDpid
        vlink["srcVirtualPortNumber"] = srcVirtualPort
        vlink["dstVirtualPortNumber"] = dstVirtualPort
        vlink["srcPhysicalPort"] = srcPhysicalPort
        vlink["dstPhysicalPort"] = dstPhysicalPort
        vlink["linkType"] = linkType
        if (vlan != None):
            vlink["vlanId"] = vlan
        if (bandwidth != None):
            vlink["nsiBandwidth"] = bandwidth

        vlink["vNetworkName"] = self.obj["vNetworkName"]

        self.obj["vLinks"].append(vlink)

    def addVHost(self, hostname, endpoint, template, dpid, virtualPort, vlan, ip, subnet, gateway):
        vhost = {}
        vhost["hostname"] = hostname
        vhost["endpointName"] = endpoint
        vhost["templateName"] = template
        vhost["datapathId"] = dpid
        vhost["virtualPortNumber"] = virtualPort
        vhost["vlanId"] = vlan
        vhost["dataplaneIp"] = ip
        vhost["dataplaneSubnet"] = subnet
        vhost["dataplaneGateway"] = gateway

        vhost["vNetworkName"] = self.obj["vNetworkName"]

        self.obj["vHosts"].append(vhost)

    def getJson(self):
        out = {"vNets":[self.obj]}
        return out