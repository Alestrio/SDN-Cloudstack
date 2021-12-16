#  SDN-Cloudstack - CLI-CONFIGURATION
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

import yaml
import json

class Cli_configurator:
    """This class will generate for a json or yaml files the cli(Cisco) needed for the configuration"""

    def __init__(self, path):
        self.path = path
        data = self.get_data()
        if data.get('interfaces'):
            self.interfaces = data['interfaces']
        if data.get('trunks'):
            self.trunks = data['trunks']
        if data.get('vlans'):
            self.vlans = data['vlans']

    def get_data(self):
        # This function get the data from path
        if self.path.__contains__(".json"):
            with open(self.path, 'r') as json_files:
                data_dic = json.load(json_files)
        elif self.path.__contains__(".yaml"):
            with open(self.path, 'r') as yaml_files:
                try:
                    data_dic = yaml.safe_load(yaml_files)
                except yaml.YAMLError as exc:
                    print(exc)
        return data_dic
    def set_interface(self):
        # This function will create the config for all interface from self.interfaces and return str(int_config)
        int_config = "INTERFACE\n\n"
        for interface in self.interfaces:
            int_config += f"interface {interface['name']}\n" \
                          f"description {interface['description']}\n"
            if interface['vlan'] != None:
                int_config += f"switchport mode access vlan {interface['vlan']['dot1q_id']}\n"
            int_config += "no shut\n\n"

        return int_config

    def set_vlan(self):
        # This function will create the config for all vlan from self.vlans and return str(vlan_config)
        vlan_config = "VLAN \n\n"
        for vlan in self.vlans:
            vlan_config += f"vlan {vlan['dot1q_id']}\n" \
                           f"description {vlan['description']}\n\n"
        return vlan_config
    def set_trunk(self):
        # This function will create the config for all trunk from self.trunks and return str(trunk_config)
        trunk_config = "TRUNK \n\n"
        for trunk in self.trunks:
            trunk_config += f"interface {trunk['interface']['name']}\n" \
                            f"description {trunk['interface']['description']} native vlan {trunk['native_vlan']['description']}\n" \
                            f"switchport trunk encapsulation dot1q\n" \
                            f"switchport mode trunk native {trunk['native_vlan']['dot1q_id']}\n"
            if len(trunk['tagged_vlans']) != 0:
                for vlan in trunk['tagged_vlans']:
                    trunk_config += f"switchport trunk allow {vlan['dot1q_id']}\n"

            trunk_config += "no shut\n\n"

        return trunk_config

    def create_config_files(self):
        path = self.path.replace(".yaml",".txt").replace(".json",".txt")
        with open(path, 'w') as files:
            config = f"{self.set_vlan()}\n{self.set_interface()}\n{self.set_trunk()}"
            files.write(config)

if __name__=="__main__":
    config=Cli_configurator(input("Path : "))
    config.create_config_files()