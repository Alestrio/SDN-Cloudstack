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

    @staticmethod
    def from_dict(vlan):
        """
        This method is used to convert a dictionary to a Vlan object
        :param vlan: a dictionary containing the VLAN's description and the VLAN's ID
        :return: a Vlan object
        """
        vlan = Vlan(
            description=vlan['description'],
            dot1q_id=vlan['dot1q_id']
        )
        return vlan


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

    @staticmethod
    def from_dict(interface):
        """
        This method is used to convert a dictionary to an Interface object
        :param interface: a dictionary containing the interface's name, description, port ID, status, operation status,
        VLAN ID and speed
        :return: an Interface object
        """
        interface = Interface(
            name=interface['name'],
            description=interface['description'],
            port_id=interface['port_id'],
            status=interface['status'],
            operstatus=interface['operstatus'],
            vlan=interface['vlan'],
            speed=interface['speed']
        )
        return interface


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

    @staticmethod
    def from_dict(trunk):
        """
        This method is used to convert a dictionary to a Trunk object
        :param trunk: a dictionary containing the trunk's interface, native VLAN, tagged VLANs and status
        :return: a Trunk object
        """
        trunk = Trunk(
            interface=Interface.from_dict(trunk['interface']),
            native_vlan=trunk['native_vlan'],
            tagged_vlans=trunk['tagged_vlans'],
            status=trunk['status']
        )
        return trunk


class Config(BaseModel):
    """
    That class defines the JSON model for add_config POST request
    """
    name: Optional[str]
    hostname: Optional[str]
    interfaces: list[Interface]
    vlans: list[Vlan]
    trunks: list[Trunk]

    @staticmethod
    def from_dict(dict_config):
        """
        This method converts a dict to a Config object
        """
        config = Config(
            name=dict_config.get('name'),
            hostname=dict_config.get('hostname'),
            interfaces=[Interface.from_dict(interface) for interface in dict_config['interfaces']],
            vlans=[Vlan.from_dict(vlan) for vlan in dict_config['vlans']],
            trunks=[Trunk.from_dict(trunk) for trunk in dict_config['trunks']]
        )

        return config



class TrunkBrief(BaseModel):
    """
    That class defines a trunk as it is described in JSONs sent and received by the API
    """
    interface_id: int
    native_vlan: Union[Vlan, None]
    tagged_vlans: str


class UserIn(BaseModel):
    """
    That class defines the user model for POST request
    """
    username: str
    email: str
    password: str


class User(BaseModel):
    """
    That class defines the user model
    """
    id: Optional[str]
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

    @staticmethod
    def from_userin(userin: UserIn):
        """
        This method returns a User object from a UserIn object
        """
        return User(
            username=userin.username,
            hashed_password=userin.password,
            email=userin.email,
            is_admin=False,
            is_active=True
        )


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
