#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

from fastapi import APIRouter, HTTPException

from src.api.routers import ROUTE_PREFIX, operations

router = APIRouter(prefix=ROUTE_PREFIX,
                   tags=["General Infos"],
                   # dependencies=[Depends(get_current_user)],
                   responses={404: {"description": "Not found"}}
                   )


@router.get("/neighbors")
def get_cdp_neighbors():
    # Return the CDP neighbors from the switch
    try:
        neighbors = operations.get_cdp_neighbors()
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while getting CDP neighbors')

    return neighbors


@router.get("/hostname")
def get_hostname():
    # Return the hostname of the switch
    try:
        hostname = operations.get_hostname()
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while getting hostname')

    return {'hostname': hostname}


@router.get("/uptime")
def get_uptime():
    # Return the uptime of the switch
    try:
        uptime = operations.get_uptime()
    except Exception as e:
        raise HTTPException(status_code=500, detail='Server error while getting uptime')

    return {'uptime': uptime}
