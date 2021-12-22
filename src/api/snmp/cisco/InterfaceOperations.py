#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
import beaker
import snmp_cmds
from beaker.cache import cache_region

from src.api.models import Interface, Vlan
from src.api.snmp.AbstractOperations import AbstractOperations
from src.api.snmp.SnmpUtils import SnmpUtils
from src.api.snmp.cisco.VlanOperations import VlanOperations


class InterfaceOperations(AbstractOperations):

    def invalidate_cache(self):
        beaker.cache.region_invalidate(self.get_interfaces, "api_data")

    def rebuild_cache(self):
        """Rebuild the cache"""
        self.invalidate_cache()
        self.get_interfaces()

    def __init__(self, ip, port, community, config, vlan_operations: VlanOperations):
        super().__init__(ip, port, community, config)
        self.vlan_operations = vlan_operations

    # This needs to be cached
    @cache_region('api_data')
    def get_interfaces(self):
        """Return a list of interfaces"""
        interfaces = []
        vlans = self.vlan_operations.get_vlannames_and_ids()
        if_vlans = self.vlan_operations.get_vlan_linked_interfaces()
        # We need to gather all interfaces
        for interface in snmp_cmds.snmptable(ipaddress=self.ip, port=self.port, community=self.community,
                                             oid=self.config['interfaces']['table']):
            # Here, we have an array of dictionnaries
            # We need to extract every information to put it in Interface object
            # We need to extract the interface name, the interface id, the interface description, the interface status
            # the interface operstatus, the interface speed, the interface trunk status, the interface vlan
            interfaces.append(Interface(
                vlan=int(if_vlans.get(interface['ifIndex'])) if if_vlans.get(interface['ifIndex']) else None,
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

        # We need to put that in cache, so we can use it later

        return interfaces

    def set_interface_vlan(self, dot1q_id, interface_id):
        """Set the vlan of an interface"""
        snmp_cmds.snmpset(ipaddress=self.ip, port=self.port, community=self.community,
                          oid=self.config['interfaces']['oids']['sets']['vlan'] + '.' + str(interface_id),
                          value=str(dot1q_id),
                          value_type='x')
        self.rebuild_cache_background()

    def get_interface_by_id(self, interface_id):
        """Return an interface by its id"""
        utils = SnmpUtils(self.ip, self.port, self.community)
        if_name = utils.findById(self.config['interfaces']['oids']['description'], interface_id)
        if_status = utils.findById(self.config['interfaces']['oids']['status'], interface_id)
        if_operstatus = utils.findById(self.config['interfaces']['oids']['operstatus'], interface_id)
        if_speed = utils.findById(self.config['interfaces']['oids']['speed'], interface_id)
        if_vlan = utils.findById(self.config['interfaces']['oids']['vlan'], interface_id)
        if_port_id = utils.findById(self.config['interfaces']['oids']['index'], interface_id)

        vlan_name = utils.findById(self.config['vlans']['name'], if_vlan)

        self.rebuild_cache_background()
        return Interface(
            vlan=Vlan(
                dot1q_id=if_vlan,
                name=vlan_name
            ),
            name=if_name,
            port_id=if_port_id,
            description=if_name,
            status=if_status,
            operstatus=if_operstatus,
            speed=if_speed,
        )

    def get_interfaces_by_vlan(self, vlan_id):
        # We need to get the interfaces from the cache using the vlan_id
        interfaces = []
        for interface in self.get_interfaces():
            if interface.vlan:
                if interface.vlan.dot1q_id == vlan_id:
                    interfaces.append(interface)
        return interfaces

