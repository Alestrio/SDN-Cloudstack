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

    def bulk(self, *oids_list):
        """
        That function overrides the one in the library to provide only values
        """
        result = super(SnmpGateway, self).bulk(*oids_list)
        return list(result.values())

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

        vlan_names = self.bulk(self.OIDS['vlans']['name'])
        vlan_ids = self.bulk(self.OIDS['vlans']['dot1q_id'])
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

        if_descriptions = self.bulk(self.OIDS['interfaces']['description'])
        if_port_ids = self.bulk(self.OIDS['interfaces']['index'])
        if_statuses = self.bulk(self.OIDS['interfaces']['status'])
        if_op_modes = self.bulk(self.OIDS['interfaces']['op_mode'])
        if_vlans = super(SnmpGateway, self).bulk(self.OIDS['interfaces']['vlan'])  # Using the library method
        if_speeds = self.bulk(self.OIDS['interfaces']['speed'])
        if_macs = self.bulk(self.OIDS['interfaces']['mac_address'])
        return parse_interface_list(if_descriptions, if_port_ids, if_statuses, if_op_modes, if_vlans, if_speeds,
                                    if_macs)

    def get_vlan_by_id(self, vlan_id):
        if vlan_id:
            if vlan_id is not int:
                vlan_id = int(vlan_id)
            vlan_name = self.findById((self.OIDS['vlans']['name']), vlan_id)
            vlan_dot1q_id = int(self.findById(self.OIDS['vlans']['dot1q_id'], vlan_id), 16)-100000
            if vlan_dot1q_id == vlan_id:
                return Vlan(dot1q_id=vlan_dot1q_id, description=vlan_name)
        return None

    def get_interface_by_id(self, interface_id):
        if_description = self.findById(self.OIDS['interfaces']['description'], interface_id)
        if_port_id = self.findById(self.OIDS['interfaces']['index'], interface_id)
        if_status = self.findById(self.OIDS['interfaces']['status'], interface_id)
        if_op_mode = self.findById(self.OIDS['interfaces']['op_mode'], interface_id)
        if_vlan = self.findById(self.OIDS['interfaces']['vlan'], interface_id)
        if_speed = self.findById(self.OIDS['interfaces']['speed'], interface_id)
        if_mac = self.findById(self.OIDS['interfaces']['mac_address'], interface_id)
        if str(interface_id) == if_port_id:
            return Interface(description=if_description,
                            port_id=int(if_port_id),
                            status=if_status,
                            operational_mode=if_op_mode,
                            vlan=(self.get_vlan_by_id(int(if_vlan)) if if_vlan else None),
                            speed=(int(if_speed)/1000000 if if_speed else 0))
        else:
            return None

    def set_interface_vlan(self, interface_id, vlan_id):
        pass

    def get_cdp_neighbors(self):
        pass

