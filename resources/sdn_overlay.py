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
        'vlan', 'dataplane_ip', 'dataplane_subnet', 'dataplane_gateway'
    )

    _vswitch_schema = {
        DATAPATH: properties.Schema(
            properties.Schema.STRING,
            _('Openflow datapath ID of the virtual switch.'),
            required=True
        ),
        CONTROLLER_IP: properties.Schema(
            properties.Schema.STRING,
            _('Openflow controller IP address.'),
            required=True
        ),
        CONTROLLER_PORT: properties.Schema(
            properties.Schema.STRING,
            _('Openflow controller TCP port.'),
            required=True
        ),
        OPENFLOW_VERSION: properties.Schema(
            properties.Schema.STRING,
            _('Openflow version.'),
            required=True
        ),
        PHYSICAL_DEVICE: properties.Schema(
            properties.Schema.STRING,
            _('Physical device name.'),
            required=True
        )
    }

    _vport_schema = {
        DATAPATH: properties.Schema(
            properties.Schema.STRING,
            _('Openflow datapath ID of the virtual switch.'),
            required=True
        ),
        VIRTUAL_PORT_NUMBER: properties.Schema(
            properties.Schema.STRING,
            _('Openflow virtual port number.'),
            required=True
        ),
        PHYSICAL_PORT_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Physical port name.'),
            required=True
        ),
        BINDING_TYPE: properties.Schema(
            properties.Schema.STRING,
            _('Binding type between virtual and physical ports.'),
            required=True
        ),
        VLAN: properties.Schema(
            properties.Schema.STRING,
            _('VLAN identifier for VLAN binding type.')
        )
    }

    _vlink_schema = {
        DATAPATH_SRC: properties.Schema(
            properties.Schema.STRING,
            _('Openflow datapath ID of the source virtual switch.'),
            required=True
        ),
        DATAPATH_DST: properties.Schema(
            properties.Schema.STRING,
            _('Openflow datapath ID of the destination virtual switch.'),
            required=True
        ),
        VIRTUAL_PORT_NUMBER_SRC: properties.Schema(
            properties.Schema.STRING,
            _('Openflow source virtual port number.'),
            required=True
        ),
        VIRTUAL_PORT_NUMBER_DST: properties.Schema(
            properties.Schema.STRING,
            _('Openflow destination virtual port number.'),
            required=True
        ),
        PHYSICAL_PORT_NAME_SRC: properties.Schema(
            properties.Schema.STRING,
            _('Source physical port name.'),
            required=True
        ),
        PHYSICAL_PORT_NAME_DST: properties.Schema(
            properties.Schema.STRING,
            _('Destination physical port name.'),
            required=True
        ),
        LINK_TYPE: properties.Schema(
            properties.Schema.STRING,
            _('Link tunnel type.'),
            required=True
        ),
        VLAN: properties.Schema(
            properties.Schema.STRING,
            _('VLAN identifier for STATIC_VLAN link type.')
        ),
        NSI_BANDWIDTH: properties.Schema(
            properties.Schema.STRING,
            _('Bandwidth value for NSI link type.')
        )
    }

    _vhost_schema = {
        HOSTNAME: properties.Schema(
            properties.Schema.STRING,
            _('Virtual host name.'),
            required=True
        ),
        ENDPOINT_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Endpoint type name.'),
            required=True
        ),
        TEMPLATE_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Template image name.'),
            required=True
        ),
        DATAPATH: properties.Schema(
            properties.Schema.STRING,
            _('Openflow datapath ID of the virtual switch.'),
            required=True
        ),
        VIRTUAL_PORT_NUMBER: properties.Schema(
            properties.Schema.STRING,
            _('Virtual port number to connect with the virtual switch.'),
            required=True
        ),
        VLAN: properties.Schema(
            properties.Schema.STRING,
            _('VLAN identifier for binding the virtual host and switch.'),
            required=True
        ),
        DATAPLANE_IP: properties.Schema(
            properties.Schema.STRING,
            _('Dataplane IP address.'),
            required=True
        ),
        DATAPLANE_SUBNET: properties.Schema(
            properties.Schema.STRING,
            _('Dataplane subnet address.'),
            required=True
        ),
        DATAPLANE_GATEWAY: properties.Schema(
            properties.Schema.STRING,
            _('Dataplane gateway address.'),
            required=True
        )
    }

    properties_schema = {
        REST_ADDRESS: properties.Schema(
            properties.Schema.STRING,
            _('The REST API IP address and TCP port used to send requests '
              'to the SDNOverlay service.'
              'Ex.: http://172.25.0.2:8181'),
            required=True
        ),
        REST_USER: properties.Schema(
            properties.Schema.STRING,
            _('The REST API user used to send requests '
              'to the SDNOverlay service.'
              'Ex.: karaf'),
            default='karaf'
        ),
        REST_PASSWORD: properties.Schema(
            properties.Schema.STRING,
            _('The REST API password used to send requests '
              'to the SDNOverlay service.'
              'Ex.: karaf'),
            default='karaf'
        ),
        NETWORK_NAME: properties.Schema(
            properties.Schema.STRING,
            _('The Virtual Network name.'
              'Ex.: vnet'),
            required=True
        ),
        SWITCHES: properties.Schema(
            properties.Schema.LIST,
            _('List with 0 or more map elements containing virtual switch details.'),
            schema=properties.Schema(
                properties.Schema.MAP,
                schema=_vswitch_schema
            ),
            update_allowed=True,
        ),
        PORTS: properties.Schema(
            properties.Schema.LIST,
            _('List with 0 or more map elements containing virtual port details.'),
            schema=properties.Schema(
                properties.Schema.MAP,
                schema=_vport_schema
            ),
            update_allowed=True,
        ),
        LINKS: properties.Schema(
            properties.Schema.LIST,
            _('List with 0 or more map elements containing virtual link details.'),
            schema=properties.Schema(
                properties.Schema.MAP,
                schema=_vlink_schema
            ),
            update_allowed=True,
        ),
        HOSTS: properties.Schema(
            properties.Schema.LIST,
            _('List with 0 or more map elements containing virtual host details.'),
            schema=properties.Schema(
                properties.Schema.MAP,
                schema=_vhost_schema
            ),
            update_allowed=True,
        )
    }

    def getClient(self):
        rest_api = self.properties[self.REST_ADDRESS]
        user = self.properties[self.REST_USER]
        pw = self.properties[self.REST_PASSWORD]
        return SoloClient(endpoint=rest_api, user=user, password=pw)

    def handle_create(self):
        
        client = self.getClient()
        
        vnets = JsonVNet(self.properties[self.NETWORK_NAME])

        vswitches = self.properties[self.SWITCHES] or []
        self._addVSwitches(vnets, vswitches)

        vports = self.properties[self.PORTS] or []
        self._addVPorts(vnets, vports)

        vlinks = self.properties[self.LINKS] or []
        self._addVLinks(vnets, vlinks)

        vhosts = self.properties[self.HOSTS] or []
        self._addVHosts(vnets, vhosts)

        networkName = client.createVNet(vnets.getJson())

        if (networkName is False) or (networkName is None):
            raise exception.ResourceInError(resource_status=self.FAILED,
                                            status_reason="REST server error")

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
            raise exception.Error("REST server error")

        return self.resource_id

    def check_delete_complete(self, networkName):

        client = self.getClient()
        return (client.getVNetName(networkName) is None)

    def _addVSwitches(self, vnets, vswitches):
        #iterate over a list of maps
        for vswitch in vswitches:
            datapath = vswitch[self.DATAPATH]
            controller_ip = vswitch[self.CONTROLLER_IP]
            controller_port = vswitch[self.CONTROLLER_PORT]
            of_version = vswitch[self.OPENFLOW_VERSION]
            phy_device = vswitch[self.PHYSICAL_DEVICE]
            vnets.addVSwitch(datapath, controller_ip, controller_port, of_version, phy_device)

    def _addVPorts(self, vnets, vports):
        for vport in vports:
            datapath = vport[self.DATAPATH]
            vport_number = vport[self.VIRTUAL_PORT_NUMBER]
            pport_name = vport[self.PHYSICAL_PORT_NAME]
            binding = vport[self.BINDING_TYPE]
            vlan = vport[self.VLAN] or None
            vnets.addVPort(datapath, vport_number, pport_name, binding, vlan)

    def _addVLinks(self, vnets, vlinks):
        for vlink in vlinks:
            dpid_src = vlink[self.DATAPATH_SRC]
            dpid_dst = vlink[self.DATAPATH_DST]
            vport_src = vlink[self.VIRTUAL_PORT_NUMBER_SRC]
            vport_dst = vlink[self.VIRTUAL_PORT_NUMBER_DST]
            pport_src = vlink[self.PHYSICAL_PORT_NAME_SRC]
            pport_dst = vlink[self.PHYSICAL_PORT_NAME_DST]
            link_type = vlink[self.LINK_TYPE]
            vlan = vlink[self.VLAN] or None
            nsi_bw = vlink[self.NSI_BANDWIDTH] or None
            vnets.addVLink(dpid_src, dpid_dst, vport_src, vport_dst, pport_src, pport_dst, link_type, vlan, nsi_bw)

    def _addVHosts(self, vnets, vhosts):
        for vhost in vhosts:
            hostname = vhost[self.HOSTNAME]
            endpoint = vhost[self.ENDPOINT_NAME]
            template = vhost[self.TEMPLATE_NAME]
            datapath = vhost[self.DATAPATH]
            vport = vhost[self.VIRTUAL_PORT_NUMBER]
            vlan = vhost[self.VLAN]
            dp_ip = vhost[self.DATAPLANE_IP]
            dp_sub = vhost[self.DATAPLANE_SUBNET]
            dp_gw = vhost[self.DATAPLANE_GATEWAY]
            vnets.addVHost(hostname, endpoint, template, datapath, vport, vlan, dp_ip, dp_sub, dp_gw)

def resource_mapping():
    return {
        'RNP::SOLO::VirtualNetwork': SDNOverlay,
    }
