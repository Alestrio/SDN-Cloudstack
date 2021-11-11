#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
from api.models import Vlan
from api.snmp.snmp_utils import SnmpUtils


class SnmpGateway(SnmpUtils):
    """
    Wrapper for @HakkaOfDev's library
    """
    def __init__(self, config, oids):
        super().__init__(config['host'], port=config['port'], community=config['community'])
        self.OIDS = oids

    def check_if_id_exists(self, oid):
        pass

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
        pass

    def get_vlan_by_id(self, vlan_id):
        pass

    def get_interface_by_id(self, interface_id):
        pass

    def set_interface_vlan(self, interface_id, vlan_id):
        pass

    def get_cdp_neighbors(self):
        pass

