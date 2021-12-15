#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

from fastapi import APIRouter, HTTPException

from src.api.models import Config
from src.api.routers import ROUTE_PREFIX, db, operations

router = APIRouter(prefix=ROUTE_PREFIX,
                   tags=["Config"],
                   # dependencies=[Depends(get_current_user)],
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
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while getting running configuration')


@router.get("/configs/{config_id}")
def get_config(config_id: str):
    # Return a config from the mongoDB database
    #try:
    config = db.get_config(config_id)
    #except Exception as e:
    #    raise HTTPException(status_code=500, detail='Server error while getting configuration')

    return config


@router.delete("/configs/{config_id}")
def delete_config(config_id: str):
    # Delete a config from the mongoDB database
    try:
        db.delete_config(config_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while deleting configuration')

    return {'message': 'Configuration deleted'}