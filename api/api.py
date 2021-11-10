#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
#
#
#
#

import sys

import yaml

from models import *
from api.snmp import modules
from db import database
from fastapi import FastAPI, HTTPException

api = FastAPI()
db = database.Database()
try:
    with open('../config/config.yaml') as file:
        config = yaml.load(file, Loader=yaml.Loader)['api']
        ROUTE_PREFIX = config['route_prefix']
except:
    print('No config file (ERRNO 101)')


ip_switch = str(sys.argv[1])


@api.get(f"{ROUTE_PREFIX}/vlans")
def get_vlans():
    response = modules.get_all_vlans(ip_switch)
    return response


@api.get(f"{ROUTE_PREFIX}/interfaces")
def get_interfaces():
    response = modules.get_all_interfaces(ip_switch)
    return response


@api.get(ROUTE_PREFIX+"/vlans/{vl_id}")
def get_vlan_id(vl_id: int):
    if modules.check_if_id_exists(ip_switch, vl_id, '1.3.6.1.4.1.9.9.46.1.3.1.1.4'):
        response = modules.get_vlan_by_id(ip_switch, vl_id)
    else:
        raise HTTPException(status_code=404, detail="Vlan not found")
    return response


@api.get(ROUTE_PREFIX+"/interfaces/{if_id}")
def get_if_id(if_id: int):
    if modules.check_if_id_exists(ip_switch, if_id, '1.3.6.1.2.1.2.2.1.2'):
        response = modules.get_interface_by_id(ip_switch, if_id)
    else:
        raise HTTPException(status_code=404, detail="Interface not found")
    return response


@api.post(ROUTE_PREFIX+"/interfaces/{if_id}")
def set_vlan_on_interface(if_id: int, body: VlanId):
    if body:
        if modules.set_interface_vlan(ip_switch, if_id, body.vlan_id):
            return {"message": "Vlan successfully changed"}
        else:
            raise HTTPException(status_code=404, detail="Interface or Vlan not found")


@api.get(f"{ROUTE_PREFIX}/neighbors")
def get_cdp_neighbors():
    response = modules.get_cdp_neighbors(ip_switch)
    return response


@api.post(f"{ROUTE_PREFIX}/config")
def add_config(configuration: Config):
    try:
        db.add_config(configuration.dict())
    except:
        raise HTTPException(status_code=500, detail='Server error while inserting configuration')


if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True)
