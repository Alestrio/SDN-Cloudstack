#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
from models import Vlan, Interface
from snmp.snmp_utils import SnmpUtils
from time import time
import asyncio

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
                vlans += [Vlan(dot1q_id=vl_id, description=names[i])]
            return vlans

        vlan_names = self.bulk(self.OIDS['vlans']['name'])
        vlan_ids = self.bulk(self.OIDS['vlans']['dot1q_id'])
        return parse_vlan_list(vlan_ids, vlan_names)

    async def get_all_interfaces(self):
        """
        Allows to query and get all interfaces
        :return: A list of interfaces
        """
        async def get_all_vlans_trunkmodes_coro():
            t0 = time()
            special_keys = {
                self.OIDS['vlans']['name']:[],
                self.OIDS['vlans']['dot1q_id']:[],
                #self.OIDS['interfaces']['trunk_mode']:[]
            }
            print(time() - t0)

            vlan_infos = super(SnmpGateway, self).bulk(
                self.OIDS['interfaces']['trunk_mode'],
                self.OIDS['vlans']['name'],
                self.OIDS['vlans']['dot1q_id'])
            print(time() - t0)

            for vl_key, vl_value in vlan_infos.items():
                vlan_key_without_id = '.'.join(key.split('.')[:-1])
                try:
                    arrays[key_without_id] += [value]
                except KeyError:
                    pass
            print(time() - t0)

            list_vlans = list[Vlan]()
            for j in range(len(special_keys[self.OIDS['vlans']['dot1q_id']]) - 1):
                vl_id = int(special_keys[self.OIDS['vlans']['dot1q_id']][j], 16) - 100000
                vl_name = special_keys[self.OIDS['vlans']['name']][j]
                list_vlans += [Vlan(dot1q_id=vl_id, description=vl_name)]
            print(time() - t0)

            vlans_by_id = {}
            for vl in list_vlans:
                vlans_by_id[vl.dot1q_id] = vl

            print(time() - t0)
            return vlans_by_id

        t0 = time()
        vlans_task = asyncio.create_task(get_all_vlans_trunkmodes_coro())
        if_infos = super(SnmpGateway, self).bulk(self.OIDS['interfaces']['description'],
                                    self.OIDS['interfaces']['index'],
                                    self.OIDS['interfaces']['status'],
                                    self.OIDS['interfaces']['op_mode'],
                                    self.OIDS['interfaces']['mac_address'],
                                    self.OIDS['interfaces']['speed'],
                                    self.OIDS['interfaces']['vlan'])
        arrays = {
            self.OIDS['interfaces']['description']: [],
            self.OIDS['interfaces']['index']: [],
            self.OIDS['interfaces']['status']: [],
            self.OIDS['interfaces']['op_mode']: [],
            self.OIDS['interfaces']['mac_address']: [],
            self.OIDS['interfaces']['speed']: [],
            self.OIDS['interfaces']['vlan']: [],
            self.OIDS['interfaces']['trunk_mode']: []
        }
        for key, value in if_infos.items():
            key_without_id = '.'.join(key.split('.')[:-1])
            try:
                arrays[key_without_id] += [value]
            except KeyError:
                pass

        await vlans_task
        vlans_by_id = vlans_task.result()
        print(time()-t0)
        ifaces = []
        for i in range(len(arrays[self.OIDS['interfaces']['description']]) - 1):
            ifaces += [Interface(description=arrays[self.OIDS['interfaces']['description']][i],
                                 port_id=int(arrays[self.OIDS['interfaces']['index']][i]),
                                 status=arrays[self.OIDS['interfaces']['description']][i],
                                 trunk_mode=trunk_modes_by_id[int(arrays[self.OIDS['interfaces']['description']][i])],
                                 operational_mode=if_op_modes[i],
                                 vlan=vlans_by_id[
                                     int(if_vlans[self.OIDS['interfaces']['vlan'] + f'.{if_port_ids[i]}'])],
                                 speed=int(if_speeds[i]) / 1000000)]
        return ifaces

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
        if_trunk_mode = self.findById(self.OIDS['interfaces']['trunk_mode'], interface_id)
        if_speed = self.findById(self.OIDS['interfaces']['speed'], interface_id)
        if_mac = self.findById(self.OIDS['interfaces']['mac_address'], interface_id)
        if str(interface_id) == if_port_id:
            return Interface(description=if_description,
                            port_id=int(if_port_id),
                            status=if_status,
                            trunk_mode=if_trunk_mode,
                            operational_mode=if_op_mode,
                            vlan=(self.get_vlan_by_id(int(if_vlan)) if if_vlan else None),
                            speed=(int(if_speed)/1000000 if if_speed else 0))
        else:
            return None

    def set_interface_vlan(self, interface_id, vlan_id):
        try:
            self.set({self.OIDS['interfaces']['sets']['trunk_mode'] +f'.{interface_id}': 2})
        except RuntimeError:
            pass
        finally:
            self.set({self.OIDS['interfaces']['sets']['vlan'] +f'.{interface_id}': vlan_id})
        return True

    def get_cdp_neighbors(self):
        pass

