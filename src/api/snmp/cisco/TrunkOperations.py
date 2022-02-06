#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
from typing import Optional

import beaker.cache
import snmp_cmds
from beaker.cache import cache_region

from src.api.models import TrunkBrief, Trunk
from src.api.snmp.AbstractOperations import AbstractOperations
from src.api.snmp.SnmpUtils import SnmpUtils
from src.api.snmp.cisco.InterfaceOperations import InterfaceOperations
from src.api.snmp.cisco.VlanOperations import VlanOperations


class TrunkOperations(AbstractOperations):
    def invalidate_cache(self):
        beaker.cache.region_invalidate(self.get_trunks, 'api_data')

    def rebuild_cache(self):
        """rebuilds cache"""
        self.invalidate_cache()
        self.get_trunks()

    def __init__(self, ip, port, community, config, interface_operations: InterfaceOperations,
                 vlan_operations: VlanOperations):
        super().__init__(ip, port, community, config)
        self.interface_operations = interface_operations
        self.vlan_operations = vlan_operations

    @cache_region('api_data')
    def get_trunks(self):
        """returns trunks table as json"""
        trunks = []
        interfaces = self.interface_operations.get_interfaces()
        vlans = self.vlan_operations.get_vlannames_and_ids()
        utils = SnmpUtils(self.ip, self.port, self.community)
        domains = utils.bulk(self.config['trunks']['oids']['domain'])
        # last item in oid of domains
        indexes = [int(i.split('.')[-1]) for i in domains.keys()]
        domains = list(domains.values())
        tagged_vlans = utils.bulk(self.config['trunks']['oids']['vlans'])
        native_vlan = list(utils.bulk(self.config['trunks']['oids']['native']).values())
        statuses = list(utils.bulk(self.config['trunks']['oids']['status']).values())
        encapsulations = list(utils.bulk(self.config['trunks']['oids']['encapsulation']).values())
        for i in range(len(indexes)):
            interface = None
            for j in interfaces:
                if j.port_id == indexes[i]:
                    interface = j
            tr_native_vlan = None
            for j in vlans:
                if j.dot1q_id == int(native_vlan[i]):
                    tr_native_vlan = j
            if tr_native_vlan is None and native_vlan[i] != '1':
                tr_native_vlan = native_vlan[i]
            # Parsing binary value as vlans
            tr_tagged_vlans = []
            # https://www.perlmonks.org/?node_id=719096
            # https://github.com/nocproject/noc/blob/10815c0a376ebf76325d154ef65609e03a41112d/sa/profiles/Cisco/IOS/get_switchport.py
            # https://github.com/datagutten/switchinfo/blob/c354e542d4b72eea3992a3f92494329d9083756a/switchinfo/SwitchSNMP/Cisco.py
            # Get tagged vlans for a trunk
            # we need to compress the byte-string to get the vlans
            if tagged_vlans.get(self.config['trunks']['oids']['vlans'] + '.' + str(indexes[i])) and \
                    str(tagged_vlans.get(
                        self.config['trunks']['oids']['vlans'] + '.' + str(indexes[i]))) != '0x7' + 'f' * 255:
                tg_vls = str(tagged_vlans.get(self.config['trunks']['oids']['vlans'] + '.' + str(indexes[i])))[2:]
                tg_vls_bin = format(int(tg_vls, 16), '0512b')
                for j in range(len(tg_vls_bin)):
                    if tg_vls_bin[j] == '1':
                        # append the id of the vlan, the index of the bin string
                        tr_tagged_vlans.append(j)

            trunks.append(Trunk(
                interface=interface,
                domain=domains[i],
                native_vlan=tr_native_vlan,
                tagged_vlans=tr_tagged_vlans,
                status=statuses[i]
            )) if encapsulations[i] == '4' else None

        return trunks

    def get_trunks_brief(self):
        trunks = self.get_trunks()
        trunks_brief = []
        for trunk in trunks:
            vlans = ""
            for vl in trunk.tagged_vlans:
                vlans += str(vl.dot1q_id) + ", "
            vlans = vlans[:-2]
            trunks_brief.append(TrunkBrief(
                interface_id=trunk.interface.port_id,
                native_vlan=trunk.native_vlan,
                tagged_vlans=vlans,
            ))
        return trunks_brief

    def get_trunk(self, interface_id) -> Optional[Trunk]:
        """returns trunk table as json"""
        trunks = self.get_trunks()
        for trunk in trunks:
            if trunk.interface.port_id == int(interface_id):
                return trunk
        return None

    def get_trunk_by_native_vlan(self, native_vlan):
        """returns trunk table as json"""
        trunks = self.get_trunks()
        for trunk in trunks:
            if trunk.native_vlan.dot1q_id == int(native_vlan):
                return trunk
        return None

    def push_tagged_vlans(self, trunk):
        bit_string = trunk.get_tagged_vlans_bit_string()
        print(len(bit_string))
        octet_string = format(int(bit_string, 2), '0256x')
        print(len(octet_string))
        snmp_cmds.snmpset(ipaddress=self.ip,
                          oid=self.config['trunks']['oids']['vlans'] + '.' + str(trunk.interface.port_id),
                          value=octet_string, community=self.community, value_type='x')

    def set_tagged_vlan_2k_4k_0(self, interface_id):
        octet_string = '0x' + '0' * 256
        snmp_cmds.snmpset(ipaddress=self.ip, oid=self.config['trunks']['oids']['vlans2k'] + '.' + str(interface_id),
                          value=octet_string, community=self.community, value_type='x')
        snmp_cmds.snmpset(ipaddress=self.ip, oid=self.config['trunks']['oids']['vlans3k'] + '.' + str(interface_id),
                          value=octet_string, community=self.community, value_type='x')
        snmp_cmds.snmpset(ipaddress=self.ip, oid=self.config['trunks']['oids']['vlans4k'] + '.' + str(interface_id),
                          value=octet_string, community=self.community, value_type='x')

    def set_trunk_native_vlan(self, interface_id, native_vlan):
        """sets trunk native vlan"""
        snmp_cmds.snmpset(ipaddress=self.ip, oid=self.config['trunks']['oids']['native'] + '.' + str(interface_id),
                          value=str(native_vlan), community=self.community, value_type='i')

    def create_trunk(self, interface_id, native_vlan, tagged_vlans):
        """creates trunk"""
        # set interface mode to trunk
        snmp_cmds.snmpset(ipaddress=self.ip, oid=self.config['interfaces']['oids']['sets']['trunk_mode'] +
                                                 '.' + str(interface_id),
                          value='2', community=self.community, value_type='i')  # Set as trunk on (2 = off)
        # set encapsulation to dot1q
        snmp_cmds.snmpset(ipaddress=self.ip, oid=self.config['trunks']['oids']['encapsulation'] +
                                                 '.' + str(interface_id),
                          value='4', community=self.community, value_type='i')  # Set encapsulation to dot1q (4 = dot1q)
        # Add trunk to the list of trunks
        self.get_trunks()
        trunk = Trunk(interface_id=interface_id, native_vlan=native_vlan, tagged_vlans=tagged_vlans)
        # set native vlan
        self.set_trunk_native_vlan(interface_id, native_vlan)
        trunk.native_vlan = native_vlan
        # set tagged vlans
        for vlan in tagged_vlans:
            # self.add_tagged_vlan(trunk, vlan)
            trunk.tagged_vlans.append(vlan)
        self.set_tagged_vlan_2k_4k_0(interface_id)

        self.push_tagged_vlans(trunk)
        self.rebuild_cache_background()

    def set_trunk(self, interface_id, tagged_vlans, native_vlan):
        """sets trunk"""
        # get the trunk
        if self.get_trunk(interface_id):
            # update the trunk
            self.update_trunk(interface_id, native_vlan, tagged_vlans)
        else:
            # create the trunk
            self.create_trunk(interface_id, native_vlan, tagged_vlans)

    def update_trunk(self, interface_id, native_vlan, tagged_vlans):
        """updates trunk"""
        # set native vlan
        trunk = self.get_trunk(interface_id)
        self.set_trunk_native_vlan(interface_id, native_vlan)
        # set tagged vlans
        for vlan in tagged_vlans:
            # self.add_tagged_vlan(trunk, vlan)
            trunk.tagged_vlans.append(vlan)
        self.set_tagged_vlan_2k_4k_0(interface_id)

        self.push_tagged_vlans(trunk)
        self.rebuild_cache_background()
