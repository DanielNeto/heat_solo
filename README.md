# SDN Overlay Orchestrator plugin for Openstack Heat

This plugin enables the use of SDN OverLay Orchestrator (SOLO) resources in a Heat template. These resources are Virtual Networks with associated Virtual Switches, Virtual Ports, Virtual Links and Virtual Hosts.

## 1 - Install SOLO

To install the SDN Overlay Orchestrator follow the instructions in [SOLO wiki](https://git.rnp.br/sdn-overlay/sdn-overlay-orchestrator/wikis/Home)


## 2 - Install Heat (Devstack)

To enable the Heat Orchestrator plugin in a Devstack install, add the following lines to the *local.conf* file

```
#Enable heat plugin
enable_plugin heat https://git.openstack.org/openstack/heat stable/queens

IMAGE_URL_SITE="https://download.fedoraproject.org"
IMAGE_URL_PATH="/pub/fedora/linux/releases/25/CloudImages/x86_64/images/"
IMAGE_URL_FILE="Fedora-Cloud-Base-25-1.3.x86_64.qcow2"
IMAGE_URLS+=","$IMAGE_URL_SITE$IMAGE_URL_PATH$IMAGE_URL_FILE
```

Modify **stable/queens** to the desired release.

For more details and configurations go to [Heat and Devstack](https://docs.openstack.org/heat/queens/getting_started/on_devstack.html)

## 3 - Install Plugin

To install the *heat_solo* plugin run:

```
git clone https://github.com/DanielNeto/heat_solo.git
cd heat_solo
sudo ./install.sh
```

These instructions assume the value of *heat.conf* `plugin_dirs` includes the default directory `/usr/local/lib/heat`. If that is not the case, edit this line in the file */etc/heat/heat.conf*

```
[DEFAULT]
...
plugin_dirs = /usr/lib64/heat,/usr/lib/heat,/usr/local/lib/heat,/usr/local/lib64/heat
```

## 4 - Restart Heat

After that restart the **heat-engine** process.

```
sudo systemctl restart devstack@h-eng.service
```

## 5 - Test

This repository includes some examples of heat templates (HOT) to test the installation. These templates are inside the directory */tests*. Each template has an specific topology.

```
vnet_template.yaml - 1 Virtual Network only
vswitch_template.yaml - 1 Virtual Network with 2 Virtual Switches
vport_template.yaml - 1 Virtual Network with 2 Virtual Switches and each one has a Virtual Port
vlink_template.yaml - 1 Virtual Network with 2 Virtual Switches and 3 different Virtual Links between them
vhost_template.yaml - 1 Virtual Network with 1 Virtual Switch and 1 Virtual Host associated
```

To create a stack with one of the above templates run:

```
openstack stack create -t TEMPLATE_NAME STACK_NAME
```

Replace **TEMPLATE_NAME** and **STACK_NAME** accordingly.

Other useful commands:

```
openstack stack list
openstack stack show STACK_NAME
openstack stack resource list STACK_NAME
openstack stack event list STACK_NAME
openstack stack template show STACK_NAME
openstack stack delete STACK_NAME
```
