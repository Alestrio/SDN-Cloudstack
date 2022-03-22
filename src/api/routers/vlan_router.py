#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

from fastapi import APIRouter, HTTPException

from src.api.models import Vlan
from src.api.routers import ROUTE_PREFIX
from src.api.routers import vlan_operations as operations

router = APIRouter(prefix=ROUTE_PREFIX,
                   tags=["VLANs"],
                   # dependencies=[Depends(get_current_user)],
                   responses={404: {"description": "Not found"}}
                   )


@router.get("/vlans")
def get_vlans():
    """Returns the list of vlans by issuing an SNMP Table request on the switch with snmp_cmds"""
    return operations.get_vlannames_and_ids()


@router.get("/vlans/{vl_id}")
def get_vlan_id(vl_id: int):
    # Return a vlan from operations by it's id
    try:
        vlan = operations.get_vlan_by_id(vl_id)
        return vlan
    except Exception as e:
        raise HTTPException(status_code=404, detail="Vlan not found")


@router.post("/vlans")
def create_vlan(vlan: Vlan):
    """Create a new vlan on the switch by issuing an SNMP Set request on the switch with snmp_cmds"""
    #try:
    operations.create_vlan(vlan.dot1q_id, vlan.description)
    #except Exception as e:
        #raise HTTPException(status_code=404, detail="cannot create vlan" + str(e))


