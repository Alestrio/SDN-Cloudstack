#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
import snmp_cmds
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from pysnmp.error import PySnmpError

from src.api.auth_utils import get_current_admin_user
from src.api.data.cli_configurator import Cli_configurator
from src.api.models import Config
from src.api.routers import ROUTE_PREFIX, db
from src.api.routers import config_operations as operations

router = APIRouter(prefix=ROUTE_PREFIX,
                   tags=["Config"],
                   #dependencies=[Depends(get_current_admin_user)],
                   responses={404: {"description": "Not found"}}
                   )


@router.post("/config")
def add_config(configuration: Config):
    # Add a config from a YAML body to the mongoDB database
    try:
        db.add_config(configuration.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while inserting configuration')

    return {'message': 'Configuration added'}


@router.get("/configs")
def get_configs():
    # Return all the configs from the mongoDB database
    try:
        configs = db.get_configs()
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while getting configurations')

    return {'configs': configs}


@router.get("/configs/running")
def get_running_config():
    # Return the running config from the switch
    try:
        config = operations.get_running_config()
        return config
    except snmp_cmds.exceptions.SNMPTimeout as e:
        raise HTTPException(status_code=500, detail='SNMP timeout while getting CDP neighbors')
    except PySnmpError as e:
        raise HTTPException(status_code=500, detail='SNMP error while getting CDP neighbors')
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while getting CDP neighbors')


@router.get("/configs/running_cisco", response_class=PlainTextResponse)
def get_running_config_cisco():
    # Return the running config from the switch
    try:
        config = operations.get_running_config()
        configurator = Cli_configurator(config)
        return configurator.get_config()
    except snmp_cmds.exceptions.SNMPTimeout as e:
        raise HTTPException(status_code=500, detail='SNMP timeout while getting CDP neighbors')
    except PySnmpError as e:
        raise HTTPException(status_code=500, detail='SNMP error while getting CDP neighbors')
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while getting CDP neighbors')


@router.get("/configs/{config_id}")
def get_config(config_id: str):
    # Return a config from the mongoDB database
    try:
        config = db.get_config(config_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while getting configuration')

    return config


@router.delete("/configs/{config_name}")
def delete_config(config_name: str):
    # Delete a config from the mongoDB database
    try:
        db.delete_config(config_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while deleting configuration')

    return {'message': 'Configuration deleted'}


@router.get("/configs/brief")
def get_brief_configs():
    # Return all the configs from the mongoDB database
    try:
        configs = db.get_brief_configs()
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while getting configurations')

    return {'configs': configs}


@router.post("/configs/apply/{config_id}")
def apply_config(config_id: str):
    # Apply a config from the mongoDB database to the switch
    try:
        config = db.get_config(config_id)
        print(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while getting configuration')

    try:
        operations.translate_config_and_set_to_switch(Config.from_dict(config))
    except snmp_cmds.exceptions.SNMPTimeout as e:
        raise HTTPException(status_code=500, detail='SNMP timeout while getting CDP neighbors')
    except PySnmpError as e:
        raise HTTPException(status_code=500, detail='SNMP error while getting CDP neighbors')
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while getting CDP neighbors')

    return {'message': 'Configuration applied'}