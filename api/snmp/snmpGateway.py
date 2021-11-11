#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
from models import Vlan, Interface
from snmp.snmp_utils import SnmpUtils


class SnmpGateway(SnmpUtils):
    """
    Wrapper for @HakkaOfDev's library
    """
    def __init__(self, config, oids):
        super().__init__(config['host'], port=config['port'], community=config['community'])
        self.OIDS = oids

    def get_all_vlans(self):
        """
        Allows to query and get all vlans
        :return: A list of vlans
        """
        def parse_vlan_list(ids, names):
            vlans = list[Vlan]()
            for i in range(len(ids) - 1):
                vl_id = int(ids[i], 16) - 100000
                vlans.append(Vlan(dot1q_id=vl_id, description=names[i]))
            return vlans

        vlan_names = list(self.bulk(self.OIDS['vlans']['name']).values())
        vlan_ids = list(self.bulk(self.OIDS['vlans']['dot1q_id']).values())
        return parse_vlan_list(vlan_ids, vlan_names)

    def get_all_interfaces(self):
        """
        Allows to query and get all interfaces
        :return: A list of interfaces
        """
        def parse_interface_list(descriptions, port_ids, statuses, op_modes, vlans, speeds, macs):
            ifaces = list[Interface]()
            for i in range(len(descriptions)-1):
                try:
                    ifaces.append(Interface(description=descriptions[i],
                                            port_id=int(port_ids[i]),
                                            status=statuses[i],
                                            operational_mode=op_modes[i],
                                            vlan=self.get_vlan_by_id(int(vlans[self.OIDS['interfaces']['vlan']+f'.{port_ids[i]}'])),
                                            speed=int(speeds[i])/1000000))
                except KeyError:
                    ifaces.append(Interface(description=descriptions[i],
                                            port_id=int(port_ids[i]),
                                            status=statuses[i],
                                            operational_mode=op_modes[i],
                                            speed=int(speeds[i])/1000000))
            return ifaces

        if_descriptions = list(self.bulk(self.OIDS['interfaces']['description']).values())
        if_port_ids = list(self.bulk(self.OIDS['interfaces']['index']).values())
        if_statuses = list(self.bulk(self.OIDS['interfaces']['status']).values())
        if_op_modes = list(self.bulk(self.OIDS['interfaces']['op_mode']).values())
        if_vlans = self.bulk(self.OIDS['interfaces']['vlan'])
        if_speeds = list(self.bulk(self.OIDS['interfaces']['speed']).values())
        if_macs = list(self.bulk(self.OIDS['interfaces']['mac_address']).values())
        return parse_interface_list(if_descriptions, if_port_ids, if_statuses, if_op_modes, if_vlans, if_speeds,
                                    if_macs)

    def get_vlan_by_id(self, vlan_id):
        vlan_name = list(self.findById((self.OIDS['vlans']['name']), vlan_id).values())[-1]
        vlan_dot1q_id = int(list(self.findById((self.OIDS['vlans']['dot1q_id']), vlan_id).values())[-1], 16)-100001
        if vlan_dot1q_id == vlan_id:
            return Vlan(dot1q_id=vlan_dot1q_id, description=vlan_name)
        else:
            return None

    def get_interface_by_id(self, interface_id):
        pass

    def set_interface_vlan(self, interface_id, vlan_id):
        pass

    def get_cdp_neighbors(self):
        pass

