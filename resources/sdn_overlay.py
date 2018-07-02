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

from oslo_log import log as logging
import six

from heat.common import exception
from heat.common.i18n import _
from heat.engine import attributes
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource
from heat.engine import support

LOG = logging.getLogger(__name__)

from solo_clientv2 import SoloClient, JsonVNet

class SDNOverlay(resource.Resource):

    support_status = support.SupportStatus(
        status=support.UNSUPPORTED,
        message=_('This resource is not supported, use at your own risk.'))

    PROPERTIES = (
        REST_ADDRESS, REST_USER, REST_PASSWORD, NETWORK_NAME, 
        SWITCHES, PORTS, LINKS, HOSTS
    ) = (
        'rest_address', 'rest_user', 'rest_password', 'network_name', 
        'switches', 'ports', 'links', 'hosts'
    )

    _VSWITH_KEYS = (
        DATAPATH, CONTROLLER_IP, CONTROLLER_PORT, OPENFLOW_VERSION, PHYSICAL_DEVICE
    ) = (
        'datapath', 'controller_ip', 'controller_port', 'openflow_version', 'physical_device'
    )

    _VPORT_KEYS = (
        DATAPATH, VIRTUAL_PORT_NUMBER, PHYSICAL_PORT_NAME, BINDING_TYPE, VLAN
    ) = (
        'datapath', 'virtual_port_number', 'physical_port_name', 'binding_type', 'vlan'
    )

    _VLINK_KEYS = (
        DATAPATH_SRC, DATAPATH_DST, VIRTUAL_PORT_NUMBER_SRC, VIRTUAL_PORT_NUMBER_DST, 
        PHYSICAL_PORT_NAME_SRC, PHYSICAL_PORT_NAME_DST, LINK_TYPE, VLAN, NSI_BANDWIDTH
    ) = (
        'datapath_src', 'datapath_dst', 'virtual_port_number_src', 'virtual_port_number_dst', 
        'physical_port_name_src', 'physical_port_name_dst', 'link_type', 'vlan', 'nsi_bandwidth'
    )

    _VHOST_KEYS = (
        HOSTNAME, ENDPOINT_NAME, TEMPLATE_NAME, DATAPATH, VIRTUAL_PORT_NUMBER, 
        VLAN, DATAPLANE_IP, DATAPLANE_SUBNET, DATAPLANE_GATEWAY
    ) = (
        'hostname', 'endpoint_name', 'template_name', 'datapath', 'virtual_port_number',  
        'vlan', 'DATAPLANE_IP', 'dataplane_subnet', 'dataplane_gateway'
    )

    properties_schema = {
        REST_ADDRESS: properties.Schema(
            properties.Schema.STRING,
            _('The REST API IP address and TCP port used to send requests '
              'to the SDNOverlay service.'
              'Ex.: http://172.25.0.2:8181')
        ),
        NETWORK_NAME: properties.Schema(
            properties.Schema.STRING,
            _('The Virtual Network name.'
              'Ex.: vnet')
        )
    }

    def getClient(self):
        rest_api = self.properties[self.REST_ADDRESS]
        user = "karaf"
        pw = "karaf"
        return SoloClient(endpoint=rest_api, user=user, password=pw)

    def handle_create(self):
        
        client = self.getClient()
        
        vnets = JsonVNet(self.properties[self.NETWORK_NAME])
        #vnets.addVSwitch("1000000000000011", "192.168.1.1", "6633", "OF_13", "whx-rj")
        #vnets.addVSwitch("2000000000000022", "192.168.1.1", "6633", "OF_13", "whx-sp")
        networkName = client.createVNet(vnets.getJson())

        if (networkName is False) or (networkName is None):
            #throw exception
            return False

        self.resource_id_set(networkName)
        return networkName

    def check_create_complete(self, networkName):

        client = self.getClient()
        return client.inspectVNet(networkName)

    def handle_delete(self):

        if self.resource_id is None:
            return

        client = self.getClient()
        ok = client.removeVNet(self.resource_id)

        if not ok:
            #throw error
            return False

        return self.resource_id

    def check_delete_complete(self, networkName):

        client = self.getClient()
        return (client.getVNetName() is None)

    def validate(self):
        ##oq?!
        return

def resource_mapping():
    return {
        'RNP::SOLO::VirtualNetwork': SDNOverlay,
    }
