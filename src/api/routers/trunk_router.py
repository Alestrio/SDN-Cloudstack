#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

from fastapi import APIRouter, Depends, HTTPException

from src.api.routers import operations, ROUTE_PREFIX

router = APIRouter(prefix=ROUTE_PREFIX,
                   tags=["Trunks"],
                   # dependencies=[Depends(get_current_user)],
                   responses={404: {"description": "Not found"}}
                   )


@router.get("/trunks")
def get_trunks():
    """
    Get all trunks

    Caution: This route is ultra cpu intensive and should not be used in production.

    Please prefer the /trunks/{id} route or the the /trunks/brief/{id} route."""
    try:
        return operations.get_trunks()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/trunks/brief")
def get_trunks_brief():
    """
    Get all trunks in a brief form

    Caution: This route is ultra cpu intensive and should not be used in production.

    Please prefer the /trunks/{id} route or the the /trunks/brief/{id} route.
    """
    try:
        return operations.get_trunks_brief()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/trunks/{id}")
def get_trunk(id: str):
    """
    Get a trunk
    """
    try:
        return operations.get_trunk(id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/trunks/dot1q_id/{dot1q_id}")
def get_trunk_by_dot1q_id(dot1q_id: str):
    """
    Get a trunk by its dot1q id
    """
    try:
        return operations.get_trunk_by_native_vlan(dot1q_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
