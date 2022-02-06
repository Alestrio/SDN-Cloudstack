#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
from src.api.models import Config
from src.api.snmp.AbstractOperations import AbstractOperations
from src.api.snmp.cisco.InterfaceOperations import InterfaceOperations
from src.api.snmp.cisco.MiscOperations import MiscOperations
from src.api.snmp.cisco.TrunkOperations import TrunkOperations
from src.api.snmp.cisco.VlanOperations import VlanOperations


class ConfigOperations(AbstractOperations):

    def invalidate_cache(self):
        pass

    def rebuild_cache(self):
        pass

    def __init__(self, ip, port, community, config, interface_operations: InterfaceOperations,
                 vlan_operations: VlanOperations, trunk_operations: TrunkOperations,
                 misc_operations: MiscOperations):
        super().__init__(ip, port, community, config)
        self.interface_operations = interface_operations
        self.vlan_operations = vlan_operations
        self.trunk_operations = trunk_operations
        self.misc_operations = misc_operations

    def translate_config_and_set_to_switch(self, config: Config):
        """Translate a config and set it to a switch
        :param config: the config to translate
        """
        vlans = self.vlan_operations.get_vlannames_and_ids()
        for vlan in config.vlans:
            if vlan not in vlans:
                self.vlan_operations.add_vlan(vlan)
        for interface in config.interfaces:
            self.interface_operations.set_interface_vlan(interface.vlan.dot1q_id, interface.port_id)
        for trunk in config.trunks:
            self.trunk_operations.set_trunk(trunk.vlan.dot1q_id, trunk.port_id)
        self.misc_operations.set_hostname(config.hostname)
        # rebuild the cache
        self.rebuild_cache_background()
        return

    def get_running_config(self):
        """Return the running config of the switch"""
        name = "running-config"
        hostname = self.misc_operations.get_hostname()
        vlans = self.vlan_operations.get_vlannames_and_ids()
        interfaces = self.interface_operations.get_interfaces()
        trunks = self.trunk_operations.get_trunks()

        config = Config(vlans=vlans, interfaces=interfaces, trunks=trunks, hostname=hostname)
        return config