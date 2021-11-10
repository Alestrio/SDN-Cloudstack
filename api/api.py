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
from models import *
from fastapi import FastAPI, HTTPException
from snmp.modules import *

api = FastAPI()

ip_switch = str(sys.argv[1])


@api.get("/api/vlans")
def get_vlans():
    response = get_all_vlans(ip_switch)
    return response


@api.get("/api/interfaces")
def get_interfaces():
    response = get_all_interfaces(ip_switch)
    return response


@api.get("/api/vlans/{vl_id}")
def get_vlan_id(vl_id: int):
    if check_if_id_exists(ip_switch, vl_id, '1.3.6.1.4.1.9.9.46.1.3.1.1.4'):
        response = get_vlan_by_id(ip_switch, vl_id)
    else:
        raise HTTPException(status_code=404, detail="Vlan not found")
    return response


@api.get("/api/interfaces/{if_id}")
def get_if_id(if_id: int):
    if check_if_id_exists(ip_switch, if_id, '1.3.6.1.2.1.2.2.1.2'):
        response = get_interface_by_id(ip_switch, if_id)
    else:
        raise HTTPException(status_code=404, detail="Interface not found")
    return response


@api.post("/api/interfaces/{if_id}")
def set_vlan_on_interface(if_id: int, body: VlanId):
    if body:
        if set_interface_vlan(ip_switch, if_id, body.vlan_id):
            return {"message": "Vlan successfully changed"}
        else:
            raise HTTPException(status_code=404, detail="Interface or Vlan not found")


@api.get("/api/neighbors")
def get_cdpneighbors():
    response = get_cdp_neighbors(ip_switch)
    return response


if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True)
