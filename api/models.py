#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
#

from pydantic import BaseModel


class VlanId(BaseModel):
    """
    That class defines the request body for a VLAN switching on an interface
    """
    vlan_id: int
