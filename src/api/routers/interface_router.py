#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

from fastapi import APIRouter, Depends, HTTPException

from src.api.auth_utils import get_current_admin_user
from src.api.models import VlanId
from src.api.routers import ROUTE_PREFIX
from src.api.routers import interface_operations as operations


router = APIRouter(prefix=ROUTE_PREFIX,
                   tags=["Interfaces"],
                   # dependencies=[Depends(get_current_user)],
                   responses={404: {"description": "Not found"}}
                   )


@router.get("/interfaces")
def get_interfaces():
    """Returns the list of interfaces by issuing an SNMP Table request on the switch with snmp_cmds"""
    return operations.get_interfaces()


@router.get("/interfaces/{if_id}")
def get_if_id(if_id: int):
    # Return an interface by its id
    #try:
    interface = operations.get_interface_by_id(if_id)
    return interface
    #except Exception as e:
    #    raise HTTPException(status_code=404, detail="Interface not found" + str(e))


@router.get("/interfaces/by_vlan/{vlan_id}")
def get_interfaces_by_vlan(vlan_id: int):
    # Return interfaces by vlan id
    try:
        interfaces = operations.get_interfaces_by_vlan(vlan_id)
        if len(interfaces) == 0:
            return {"message": "No interface found"}
        return interfaces
    except Exception as e:
        raise HTTPException(status_code=404, detail="Interfaces not found")


@router.post("/interfaces/{if_id}/vlan/{vlan_id}")
def set_vlan_on_interface(if_id: int, vlan_id: int, user=Depends(get_current_admin_user)):
    # Set a vlan on an interface
    try:
        operations.set_interface_vlan(vlan_id, if_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Interface or Vlan not found")

    return {"message": "Vlan set on interface"}


# Route to set up or down an interface
@router.post('/interface/{if_id}/state/{state}')
def set_interface_state(if_id: int, state: bool, user=Depends(get_current_admin_user)):
    try:
        operations.set_interface_state(if_id, state)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Interface not found" + str(e))

    return {"message": "Interface state set"}


@router.post('/interface/{if_id}/description')
def set_interface_description(if_id: int, body: str, user=Depends(get_current_admin_user)):
    try:
        operations.set_interface_description(if_id, body)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Interface not found")

    return {"message": "Interface description set"}

