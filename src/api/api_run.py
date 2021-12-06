#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
import json

import uvicorn as uvicorn
import yaml

from models import *
from db import database
from fastapi import FastAPI, HTTPException
from snmp.SwitchOperations import SwitchOperations as SwitchOperations
api = FastAPI()
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


@api.get(f"{ROUTE_PREFIX}/vlans")
def get_vlans():
    """Returns the list of vlans by issuing an SNMP Table request on the switch with snmp_cmds"""



@api.get(f"{ROUTE_PREFIX}/interfaces")
def get_interfaces():
    """Returns the list of interfaces by issuing an SNMP Table request on the switch with snmp_cmds"""
    return operations.get_interfaces()


@api.get(ROUTE_PREFIX+"/vlans/{vl_id}")
def get_vlan_id(vl_id: int):
    raise HTTPException(status_code=404, detail="Vlan not found")

@api.get(ROUTE_PREFIX+"/interfaces/{if_id}")
def get_if_id(if_id: int):
    raise HTTPException(status_code=404, detail="Interface not found")

@api.post(ROUTE_PREFIX+"/interfaces/{if_id}")
def set_vlan_on_interface(if_id: int, body: VlanId):
    raise HTTPException(status_code=404, detail="Interface or Vlan not found")


@api.get(f"{ROUTE_PREFIX}/neighbors")
def get_cdp_neighbors():
    # Return the CDP neighbors from the switch
    #try:
    neighbors = operations.get_cdp_neighbors()
    #except Exception as e:
    #    raise HTTPException(status_code=500, detail='Server error while getting CDP neighbors')

    return neighbors


@api.post(f"{ROUTE_PREFIX}/config")
def add_config(configuration: Config):
    # Add a config from a YAML body to the mongoDB database
    try:
        db.add_config(configuration.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while inserting configuration')

    return {'message': 'Configuration added'}


@api.get(f"{ROUTE_PREFIX}/configs")
def get_configs():
    # Return all the configs from the mongoDB database
    try:
        configs = db.get_configs()
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while getting configurations')

    return {'configs': configs}


@api.get(ROUTE_PREFIX+"/configs/{config_id}")
def get_config(config_id: str):
    # Return a config from the mongoDB database
    try:
        config = db.get_config(config_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while getting configuration')

    return {config}


@api.delete(ROUTE_PREFIX+"/configs/{config_id}")
def delete_config(config_id: str):
    # Delete a config from the mongoDB database
    try:
        db.delete_config(config_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while deleting configuration')

    return {'message': 'Configuration deleted'}


if __name__ == "__main__":
    uvicorn.run(api, host='127.0.0.1', debug=True)

