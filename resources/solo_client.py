#Fake SOLO Client

import json
import requests

from requests.auth import HTTPDigestAuth

import requests.status_codes.codes.ok as HTTP_OK						#200
import requests.status_codes.codes.accepted as HTTP_ACCEPTED			#202
import requests.status_codes.codes.no_content as HTTP_NO_CONTENT		#204
import requests.status_codes.codes.bad_request as HTTP_BAD_REQUEST		#400
import requests.status_codes.codes.not_found as HTTP_NOT_FOUND			#404
import requests.status_codes.codes.server_error as HTTP_SERVER_ERROR	#500

USER="karaf"
PASSWORD="karaf"

class SoloClient:
	
	def __init__(self, endpoint):
		endpoint = "http://172.25.0.2:8181"
		self.url_post_vnet = endpoint + "/overlay/orchestrator/v1/vnet"
		self.url_get_vnets = endpoint + "/overlay/orchestrator/v1/vnet"
		self.url_get_vnet = endpoint + "/overlay/orchestrator/v1/vnet/network/"
		self.url_get_backup = endpoint + "/overlay/orchestrator/v1/vnet/backup"
		self.url_get_vswitches = endpoint + "/overlay/orchestrator/v1/vswitch/network/"
		self.url_get_vports = endpoint + "/overlay/orchestrator/v1/vport/network/"
		self.url_get_vlinks = endpoint + "/overlay/orchestrator/v1/vlink/network/"
		self.url_get_vhosts = endpoint + "/overlay/orchestrator/v1/vhost/network/"

	def createVNet(self, networkName, *kwargs):
		#parsear json
		vnets={}
		response = requests.post(self.url_post_vnet, data=json.dumps(vnets), auth=HTTPBasicAuth(USER, PASSWORD))
		if (response.status_code == HTTP_ACCEPTED):
			return True
		else:
			return False

	def inspectVNet(self, networkId):
		
		response = requests.get(self.url_get_vnets, auth=HTTPBasicAuth(USER, PASSWORD))
		if (response.status_code != HTTP_OK):
			#error
			return False
		
		##############
		## VNETWORK ##
		##############

		vnets = json.loads(response.text)
		
		vnetFound = False
		networkName = ""
		for vnet in vnets["vNets"]:
			if (vnet["vNetworkId"] == networkId):
				vnetFound = True
				networkName = vnet["vNetworkName"]
				break
		if (not vnetFound):
			#vnet nao existe
			return False

		###############
		## VSWTICHES ##
		###############

		response = requests.get(self.url_get_vswitches+networkNamem, auth=HTTPBasicAuth(USER, PASSWORD))
		if (response.status_code != HTTP_OK):
			#error
			return False

		vswitches = json.loads(response.text)

		for vswitch in vswitches["vSwitches"]:
			if (vswitch["status"] != "CREATED"):
				#tem um switch pendente
				return False

		############
		## VPORTS ##
		############

		response = requests.get(self.url_get_vports+networkNamem, auth=HTTPBasicAuth(USER, PASSWORD))
		if (response.status_code != HTTP_OK):
			#error
			return False

		vports = json.loads(response.text)

		for vport in vports["vPorts"]:
			if (vport["status"] != "CREATED"):
				#tem uma porta pendente
				return False

		############
		## VLINKS ##
		############

		response = requests.get(self.url_get_vlinks+networkNamem, auth=HTTPBasicAuth(USER, PASSWORD))
		if (response.status_code != HTTP_OK):
			#error
			return False

		vlinks = json.loads(response.text)

		for vlink in vlinks["vLinks"]:
			if (vlink["status"] != "CREATED"):
				#tem um link pendente
				return False

		############
		## VHOSTS ##
		############

		response = requests.get(self.url_get_vlinks+networkNamem, auth=HTTPBasicAuth(USER, PASSWORD))
		if (response.status_code != HTTP_OK):
			#error
			return False

		vhosts = json.loads(response.text)

		for vhost in vhosts["vHosts"]:
			if (vhost["status"] != "CREATED"):
				#tem um link pendente
				return False

		#allright
		return True

	def getVNetId(self, networkName):
		return 1