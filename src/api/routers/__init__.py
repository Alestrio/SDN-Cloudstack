#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

import yaml

from src.api.db import database
from src.api.snmp.SwitchOperations import SwitchOperations

try:
    file = open('../../config/config.yaml')
    config = yaml.load(file, Loader=yaml.Loader)
    ROUTE_PREFIX = config['api']['route_prefix']
    db = database.Database(config['database'])
    OIDS = config['oids']
    operations = SwitchOperations(config['snmp']['host'], config['snmp']['port'], config['snmp']['community'], OIDS)
except FileNotFoundError:
    print('No config file (ERRNO 101)')
    ROUTE_PREFIX = '/api'