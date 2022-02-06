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
    status: Optional[Union[str, int]]
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
    native_vlan: Optional[Union[Vlan, int]]
    tagged_vlans: list[Union[Vlan, int]]
    status: str

    def get_tagged_vlans_bit_string(self):
        """
        This method returns a string of octets representing the tagged VLANs
        """
        bit_string = ''
        for i in range(128 * 4):
            vlans_ids = [vlan.dot1q_id for vlan in self.tagged_vlans if isinstance(vlan, Vlan)]
            if i in self.tagged_vlans:
                bit_string += '1'
            elif i in vlans_ids:
                bit_string += '1'
            else:
                bit_string += '0'
        return bit_string


class Config(BaseModel):
    """
    That class defines the JSON model for add_config POST request
    """
    name: str
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


class User(BaseModel):
    """
    That class defines the user model
    """
    id: str
    username: str
    hashed_password: str
    email: str
    is_admin: bool
    is_active: bool

    @staticmethod
    def from_db_item(item: dict):
        """
        This method returns a User object from a DB item
        """
        return User(
            id=str(item['_id']),
            username=item['username'],
            hashed_password=item['hashed_password'],
            email=item['email'],
            is_admin=item['is_admin'],
            is_active=item['is_active']
        )


class UserIn(User):
    """
    That class defines the user model for POST request
    """
    password: str
    id: Optional[int]
    hashed_password: Optional[str]
    is_admin = False
    is_active = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class TrunkIn(BaseModel):
    """
    That class defines the trunk model for POST request
    """
    interface_id: int
    native_vlan: Optional[int]
    tagged_vlans: Optional[List[int]]
