#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
import os
from threading import Thread

import yaml

from src.api.db import database
from src.api.snmp.cisco.ConfigOperations import ConfigOperations
from src.api.snmp.cisco.InterfaceOperations import InterfaceOperations
from src.api.snmp.cisco.MiscOperations import MiscOperations
from src.api.snmp.cisco.TrunkOperations import TrunkOperations
from src.api.snmp.cisco.VlanOperations import VlanOperations


def start_build_cache():
    vlan_operations.rebuild_cache()
    interface_operations.rebuild_cache()
    trunk_operations.rebuild_cache()
    misc_operations.rebuild_cache()
    print("Cache rebuilt")


try:
    config_dir = os.getenv("CONFIG_DIR")
    file = open(f'{config_dir}/config.yaml')
    config = yaml.load(file, Loader=yaml.Loader)
    ROUTE_PREFIX = config['api']['route_prefix']
    db = database.Database(config['database'])
    OIDS = config['oids']
    vlan_operations = VlanOperations(config['snmp']['host'], config['snmp']['port'], config['snmp']['community'], OIDS)
    interface_operations = InterfaceOperations(config['snmp']['host'], config['snmp']['port'],
                                               config['snmp']['community'], OIDS, vlan_operations)
    trunk_operations = TrunkOperations(config['snmp']['host'], config['snmp']['port'],
                                       config['snmp']['community'], OIDS, interface_operations, vlan_operations)
    misc_operations = MiscOperations(config['snmp']['host'], config['snmp']['port'], config['snmp']['community'], OIDS)
    config_operations = ConfigOperations(config['snmp']['host'], config['snmp']['port'],
                                         config['snmp']['community'], OIDS, interface_operations, vlan_operations,
                                         trunk_operations, misc_operations)

    Thread(target=start_build_cache).start()
except FileNotFoundError:
    print('No config file (ERRNO 101)')
    ROUTE_PREFIX = '/api'
