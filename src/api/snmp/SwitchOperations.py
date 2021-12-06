import asyncio

import snmp_cmds
from models import *

from src.api.models import Interface, Vlan
from src.api.snmp.SnmpUtils import SnmpUtils


class SwitchOperations:
    """Class exposing all kinds of operations on a cisco switch like :
    - get_interfaces,
    - get_interface_by_id,
    - get_interface_by_name,
    - get_vlans,
    - get_vlan_by_id,
    - get_vlan_by_name,
    - get_cdp_neighbors,
    - set_interface_vlan,
    - set_interface_shutdown,
    - set_interface_trunk"""

    def __init__(self, ip, port, community, config):
        self.ip = ip
        self.port = port
        self.community = community
        self.config = config

    def get_vlannames_and_ids(self):
        vlans = []
        switch = SnmpUtils('10.59.10.68')
        for k, v in switch.bulk('1.3.6.1.4.1.9.9.46.1.3.1.1.4').items():
            vlans.append(Vlan(description=v, dot1q_id=int(k.split('.')[-1])))
        return vlans

    def get_vlan_linked_interfaces(self):
        utils = SnmpUtils(self.ip, self.port, self.community)
        if_vlans = utils.bulk(self.config['interfaces']['oids']['vlan'])
        vlans = {}
        for k, v in if_vlans.items():
            vlans[k.split('.')[-1]] = v
        return vlans


    def get_interfaces(self):
        """Return a list of interfaces"""
        interfaces = []
        vlans = self.get_vlannames_and_ids()
        if_vlans = self.get_vlan_linked_interfaces()
        # We need to gather all interfaces
        for interface in snmp_cmds.snmptable(ipaddress=self.ip, port=self.port, community=self.community,
                                             oid=self.config['interfaces']['table']):
            # Here, we have an array of dictionnaries
            # We need to extract every information to put it in Interface object
            # We need to extract the interface name, the interface id, the interface description, the interface status
            # the interface operstatus, the interface speed, the interface trunk status, the interface vlan
            try:
                interfaces.append(Interface(
                    vlan=int(if_vlans[interface['ifIndex']]),
                    name=interface['ifDescr'],
                    port_id=interface['ifIndex'],
                    description=interface['ifDescr'],
                    status=interface['ifOperStatus'],
                    operstatus=interface['ifOperStatus'],
                    speed=interface['ifSpeed'],
                ))
            except KeyError:
                interfaces.append(Interface(
                    vlan=None,
                    name=interface['ifDescr'],
                    port_id=interface['ifIndex'],
                    description=interface['ifDescr'],
                    status=interface['ifOperStatus'],
                    operstatus=interface['ifOperStatus'],
                    speed=interface['ifSpeed'],
                ))
        # We wait for the gather_vlans to finish
        # We need to add the vlans to the interfaces
        for interface in interfaces:
            for vlan in vlans:
                if vlan.dot1q_id == interface.vlan:
                    interface.vlan = vlan
        return interfaces
