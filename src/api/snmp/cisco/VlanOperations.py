#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
import beaker
import snmp_cmds
from beaker.cache import cache_region
from pysnmp.error import PySnmpError

from src.api.models import Vlan
from src.api.snmp.AbstractOperations import AbstractOperations
from src.api.snmp.SnmpUtils import SnmpUtils


class VlanOperations(AbstractOperations):
    """
    Class that implements the VlanOperations interface.
    """

    def __init__(self, ip, port, community, config):
        super().__init__(ip, port, community, config)

    # This needs to be cached
    @cache_region('api_data')
    def get_vlannames_and_ids(self):
        vlans = []
        switch = SnmpUtils(self.ip, self.port, self.community)
        for k, v in switch.bulk('1.3.6.1.4.1.9.9.46.1.3.1.1.4').items():
            vlans.append(Vlan(description=v, dot1q_id=int(k.split('.')[-1])))
        return vlans

    # This needs to be cached
    @cache_region('api_data')
    def get_vlan_linked_interfaces(self):
        utils = SnmpUtils(self.ip, self.port, self.community)
        if_vlans = utils.bulk(self.config['interfaces']['oids']['vlan'])
        vlans = {}
        for k, v in if_vlans.items():
            vlans[k.split('.')[-1]] = v
        return vlans

    def add_vlan(self, vlan):
        """Add a vlan to the switch"""
        # destroy the row
        snmp_cmds.snmpset(ipaddress=self.ip, port=self.port, community=self.community,
                          oid=self.config['vlans']['set']['row_status'] + '.' + str(vlan.dot1q_id),
                          value='6', value_type='i')
        # Set vtpVlaneditOperation to copy
        snmp_cmds.snmpset(ipaddress=self.ip, port=self.port, community=self.community,
                          oid=self.config['vlans']['set']['operation'],
                          value='2', value_type='i')
        # set vtpVlaneditRowStatus to createAndGo
        snmp_cmds.snmpset(ipaddress=self.ip, port=self.port, community=self.community,
                          oid=self.config['vlans']['set']['row_status'] + '.' + str(vlan.dot1q_id),
                          value='4', value_type='i')
        # set vtpVlaneditType to ethernetCsmacd
        snmp_cmds.snmpset(ipaddress=self.ip, port=self.port, community=self.community,
                          oid=self.config['vlans']['set']['type'] + '.' + str(vlan.dot1q_id),
                          value='1', value_type='i')
        # set vtpVlaneditVlanName
        snmp_cmds.snmpset(ipaddress=self.ip, port=self.port, community=self.community,
                          oid=self.config['vlans']['set']['name'] + '.' + str(vlan.dot1q_id),
                          value=vlan.description, value_type='s')
        # set vtpVlanEditDot1qSaid to vlan id
        snmp_cmds.snmpset(ipaddress=self.ip, port=self.port, community=self.community,
                          oid=self.config['vlans']['set']['said'] + '.' + str(vlan.dot1q_id),
                          value=str(hex(vlan.dot1q_id+100000)), value_type='x')
        # set vtpVlanEditOperation to apply
        snmp_cmds.snmpset(ipaddress=self.ip, port=self.port, community=self.community,
                          oid=self.config['vlans']['oids']['operation'] + '.' + str(vlan.dot1q_id),
                          value='2', value_type='i')
        self.rebuild_cache_background()

    def get_vlan_by_id(self, vlan_id):
        """Return a vlan by its id"""
        vlans = self.get_vlannames_and_ids()
        self.rebuild_cache_background()
        for vlan in vlans:
            if vlan.dot1q_id == vlan_id:
                return vlan
        return None

    def create_vlan(self, vlan_id, vlan_name):
        """Create a vlan on the switch"""
        self.add_vlan(Vlan(dot1q_id=vlan_id, description=vlan_name))

    def invalidate_cache(self):
        beaker.cache.region_invalidate(self.get_vlannames_and_ids, "api_data")
        beaker.cache.region_invalidate(self.get_vlan_linked_interfaces, "api_data")

    def rebuild_cache(self):
        try:
            self.invalidate_cache()
            self.get_vlannames_and_ids()
            self.get_vlan_linked_interfaces()
        except snmp_cmds.exceptions.SNMPTimeout as e:
            print('SNMPTimeout')
        # except error from pysnmp
        except PySnmpError as e:
            print('SNMPTimeout')
        except Exception as e:
            print(e)
