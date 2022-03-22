#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

import yaml
import json

from src.api.models import Config


class Cli_configurator:
    """This class will generate for a json or yaml files the cli(Cisco) needed for the configuration"""

    def __init__(self, data: Config):
        self.interfaces = data.interfaces if data.interfaces else None
        self.vlans = data.vlans if data.vlans else None
        self.trunks = data.trunks if data.trunks else None

    def set_interface(self):
        # This function will create the config for all interface from self.interfaces and return str(int_config)
        int_config = "!INTERFACE\n\n"
        for interface in self.interfaces:
            int_config += f"interface {interface.name}\n" \
                          f"description {interface.description}\n"
            if interface.vlan:
                int_config += f"switchport mode access vlan {interface.vlan.dot1q_id}\n"
            int_config += "no shut\n\n"

        return int_config

    def set_vlan(self):
        # This function will create the config for all vlan from self.vlans and return str(vlan_config)
        vlan_config = "!VLAN \n\n"
        for vlan in self.vlans:
            vlan_config += f"vlan {vlan.dot1q_id}\n" \
                           f"description {vlan.description}\n\n"
        return vlan_config

    def set_trunk(self):
        # This function will create the config for all trunk from self.trunks and return str(trunk_config)
        trunk_config = "!TRUNK \n\n"
        for trunk in self.trunks:
            trunk_config += f"interface {trunk.interface.name}\n" \
                            f"description {trunk.interface.description} native vlan {trunk.native_vlan.description}\n" \
                            f"switchport trunk encapsulation dot1q\n" \
                            f"switchport mode trunk native {trunk.native_vlan.dot1q_id}\n"
            if len(trunk.tagged_vlans) != 0:
                for vlan in trunk.tagged_vlans:
                    trunk_config += f"switchport trunk allow {vlan.dot1q_id}\n"

            trunk_config += "no shut\n\n"

        return trunk_config

    def get_config(self):
        return self.set_vlan() + "\n" + \
               self.set_interface() + "\n" + \
               self.set_trunk()
