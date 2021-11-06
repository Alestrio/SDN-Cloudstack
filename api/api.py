import sys
from models import *
from fastapi import FastAPI, HTTPException
from modules import *

api = FastAPI()

ip_switch = str(sys.argv[1])


@api.get("/api/vlans")
def get_vlans():
    response = vlans(ip_switch)
    return response


@api.get("/api/interfaces")
def get_interfaces():
    response = interfaces(ip_switch)
    return response


@api.get("/api/vlans/{vl_id}")
def get_vlan_id(vl_id: int):
    if test(ip_switch, vl_id, '1.3.6.1.4.1.9.9.46.1.3.1.1.4'):
        response = vlansbyid(ip_switch, vl_id)
    else:
        raise HTTPException(status_code=404, detail="Vlan not found")
    return response


@api.get("/api/interfaces/{if_id}")
def get_if_id(if_id: int):
    if test(ip_switch, if_id, '1.3.6.1.2.1.2.2.1.2'):
        response = interfacebyid(ip_switch, if_id)
    else:
        raise HTTPException(status_code=404, detail="Interface not found")
    return response


@api.post("/api/interfaces/{if_id}")
def set_vlan_on_interface(if_id: int, body: VlanId):
    if body:
        if new_vlan_if(ip_switch, if_id, body.vlan_id):
            return {"message": "Vlan successfully changed"}
        else:
            raise HTTPException(status_code=404, detail="Interface or Vlan not found")


@api.get("/api/neighbors")
def get_cdpneighbors():
    response = cdp_neighbors(ip_switch)
    return response


if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True)
