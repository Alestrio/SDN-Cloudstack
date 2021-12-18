#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.


from pydantic import BaseModel
from pydantic.typing import Optional, Union, List


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
    name: str
    description: str
    port_id: int
    status: Optional[str]
    operstatus: Union[str, int]  # Can be provided as int for config creation
    vlan: Optional[Union[Vlan, int, None]]
    speed: Optional[int]


class CdpNeighbor(BaseModel):
    """
    That class defines a CDP neighbor as it is described in JSONs sent and received by the API
    """
    ip: str
    fqdn: str
    interface: str
    model: str


class Trunk(BaseModel):
    """
    That class defines a trunk as it is described in JSONs sent and received by the API
    """
    interface: Union[Interface, int]
    native_vlan: Union[Vlan, None]
    tagged_vlans: list[Union[Vlan, int]]
    status: str

    def get_tagged_vlans_bit_string(self):
        """
        This method returns a string of octets representing the tagged VLANs
        """
        bit_string = ''
        for i in range(255 * 4):
            for vl in self.tagged_vlans:
                if vl.dot1q_id == i:
                    bit_string += '1'
            else:
                bit_string += '0'
        return bit_string


class Config(BaseModel):
    """
    That class defines the JSON model for add_config POST request
    """
    hostname: Optional[str]
    interfaces: list[Interface]
    vlans: list[Vlan]
    trunks: list[Trunk]


class TrunkBrief(BaseModel):
    """
    That class defines a trunk as it is described in JSONs sent and received by the API
    """
    interface_id: int
    native_vlan: Union[Vlan, None]
    tagged_vlans: str
