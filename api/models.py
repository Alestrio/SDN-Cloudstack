#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.


from pydantic import BaseModel
from pydantic.typing import Optional, Union


class VlanId(BaseModel):
    """
    That class defines the request body for a VLAN switching on an interface
    """
    vlan_id: int


class Vlan(BaseModel):
    """
    That class defines a VLAN as it is described in JSONs sent and received by the API
    """
    description: str
    dot1q_id: int


class Interface(BaseModel):
    """
    That class defines an interface as it is described in JSONs sent and received by the API
    """
    description: str
    port_id: int
    status: Optional[str]
    operational_mode: Union[str, int]  # Can be provided as int for config creation
    trunk_mode: Union[str, int]
    vlan: Optional[Union[Vlan, int]]
    speed: Optional[int]


class Config(BaseModel):
    """
    That class defines the JSON model for add_config POST request
    """
    interfaces: list[Interface]

