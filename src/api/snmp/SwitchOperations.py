#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

import ipaddress
import threading

import beaker.cache
from beaker.cache import cache_region, cache_regions

import snmp_cmds
from models import *

from src.api.models import Interface, Vlan, CdpNeighbor, Config
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
        # defining beaker cache regions
        cache_regions.update(
            {
                'api_data': {
                    'type': 'memory',
                    'expire': 60 * 10,  # 10mn
                    'key_length': 250
                }
            }
        )
        self.rebuild_cache_background()

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

    # This needs to be cached
    @cache_region('api_data')
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

        # We need to put that in cache, so we can use it later

        return interfaces

    # This needs to be cached
    @cache_region('api_data')
    def get_cdp_neighbors(self):
        """Return a list of cdp neighbors
        using those oids :
        cdp_neighbors:
            ip: 1.3.6.1.4.1.9.9.23.1.2.1.1.4.15
            fqdn: 1.3.6.1.4.1.9.9.23.1.2.1.1.6.15
            interface: 1.3.6.1.4.1.9.9.23.1.2.1.1.7.15
            model: 1.3.6.1.4.1.9.9.23.1.2.1.1.8.15
         """
        utils = SnmpUtils(self.ip, self.port, self.community)
        cdp_ips = list(utils.bulk(self.config['cdp_neighbors']['ip']).values())
        cdp_fqdns = list(utils.bulk(self.config['cdp_neighbors']['fqdn']).values())
        cdp_interfaces = list(utils.bulk(self.config['cdp_neighbors']['interface']).values())
        cdp_models = list(utils.bulk(self.config['cdp_neighbors']['model']).values())

        cdp_neighbors = []
        for i in range(len(cdp_ips)):
            try:
                cdp_neighbors.append(CdpNeighbor(
                    # convert ip from hex to human readable
                    ip=str(ipaddress.IPv4Address(int(cdp_ips[i], 16))),
                    fqdn=cdp_fqdns[i],
                    interface=cdp_interfaces[i],
                    model=cdp_models[i]
                ))
            except ValueError:
                cdp_neighbors.append(CdpNeighbor(
                    # convert ip from hex to human readable
                    ip="0.0.0.0",
                    fqdn=cdp_fqdns[i],
                    interface=cdp_interfaces[i],
                    model=cdp_models[i]
                ))
        return cdp_neighbors

    def set_interface_vlan(self, dot1q_id, interface_id):
        """Set the vlan of an interface"""
        snmp_cmds.snmpset(ipaddress=self.ip, port=self.port, community=self.community,
                          oid=self.config['interfaces']['oids']['sets']['vlan'] + '.' + str(interface_id),
                          value=str(dot1q_id),
                          value_type='i')
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

    def add_vlan(self, vlan):
        """Add a vlan to the switch"""
        snmp_cmds.snmpset(ipaddress=self.ip, port=self.port, community=self.community,
                          oid=self.config['vlans']['oids']['add'],
                          value=str(vlan.dot1q_id),
                          value_type='i')
        snmp_cmds.snmpset(ipaddress=self.ip, port=self.port, community=self.community,
                          oid=self.config['vlans']['oids']['name'] + '.' + str(vlan.dot1q_id),
                          value=vlan.name,
                          value_type='s')
        self.rebuild_cache_background()

    def translate_config_and_set_to_switch(self, config: Config, switch: str, port: int, community: str):
        """Translate a config and set it to a switch
        :param config: the config to translate
        :param switch: the switch to set the config
        :param port: the port of the switch
        :param community: the community of the switch
        """
        vlans = self.get_vlannames_and_ids()
        for interface in config.interfaces:
            self.set_interface_vlan(interface.vlan.dot1q_id, interface.port_id)
        for vlan in config.vlans:
            if vlan not in vlans:
                self.add_vlan(vlan)
        # rebuild the cache
        self.rebuild_cache_background()
        return

    def invalidate_cache(self):
        """Invalidate the beaker cache"""
        beaker.cache.region_invalidate(self.get_vlannames_and_ids, "api_data")
        beaker.cache.region_invalidate(self.get_cdp_neighbors, "api_data")
        beaker.cache.region_invalidate(self.get_interfaces, "api_data")

    def rebuild_cache(self):
        """Rebuild the beaker cache"""
        self.invalidate_cache()
        self.get_vlannames_and_ids()
        self.get_cdp_neighbors()
        self.get_interfaces()
        # print("cache rebuilt")

    def rebuild_cache_background(self):
        """Rebuild the beaker cache in the background"""
        threading.Thread(target=self.rebuild_cache).start()

    def get_vlan_by_id(self, vlan_id):
        """Return a vlan by its id"""
        vlans = self.get_vlannames_and_ids()
        self.rebuild_cache_background()
        for vlan in vlans:
            if vlan.dot1q_id == vlan_id:
                return vlan
        return None

    def get_hostname(self):
        """Return the hostname of the switch"""
        return snmp_cmds.snmpwalk(ipaddress=self.ip, port=self.port, community=self.community,
                                  oid=self.config['systemName'])[0][1]

    def get_uptime(self):
        """Return the uptime of the switch"""
        return snmp_cmds.snmpwalk(ipaddress=self.ip, port=self.port, community=self.community,
                                  oid=self.config['uptime'])[0][1]
