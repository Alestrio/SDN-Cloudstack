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

import pysnmp
from pysnmp import hlapi
from api.snmp.snmp_bulk import get_snmp_bulk
from api.snmp.snmp_byid import get_snmp_by_id
from api.snmp.snmp_set import snmp_set
import json

states = json.load(open('../../config/states.json', ))


def check_if_id_exists(ip_switch, idt, oid):
    """
    Testing if the ID exists

    :param ip_switch: IP address of the switch
    :param idt: An ID of which I don't know the use case...
    :param oid: Same as above
    :return: Some kind of list apparently..
    """

    list_id = get_snmp_bulk(ip_switch, oid)
    for x in list_id:
        if int(x[1]) == int(idt):  # TODO find out what this is for...
            return True
    return False


# Find specific information using id
def find(ip_switch, idt, oid):
    """
    TODO Documentation here /!\

    :param ip_switch: IP address of the switch
    :param idt: An ID of which I don't know the use case...
    :param oid: Same as above
    :return: Some kind of list apparently..
    """

    if idt == 'n/a':
        return idt
    else:
        data = get_snmp_by_id(ip_switch, int(idt), oid + str(int(idt) - 1))
        return data[0]


def get_all_vlans(ip_switch):
    """
    Gathers VLAN list

    :param ip_switch: IP address of the switch
    :return: list containing VLANS
    """

    list_vlans = get_snmp_bulk(ip_switch, ('1.3.6.1.4.1.9.9.46.1.3.1.1.4'))
    results = []
    for vlans in list_vlans:
        vlan = {
            "name": vlans[0],
            "id": int(vlans[1])
        }
        results.append(vlan)
    return results


def get_all_interfaces(ip_switch):
    """
    Gathers interfaces list

    :param ip_switch:  IP address of the switch
    :return: list containing interface descriptions
    """

    list_interfaces = get_snmp_bulk(ip_switch, '1.3.6.1.2.1.2.2.1.2',
                                    '1.3.6.1.2.1.31.1.1.1.1',
                                    '1.3.6.1.2.1.2.2.1.8',
                                    '1.3.6.1.2.1.2.2.1.5',
                                    '1.3.6.1.4.1.9.9.68.1.2.2.1.2',
                                    '1.3.6.1.2.1.10.7.2.1.19',
                                    '1.3.6.1.4.1.9.9.46.1.6.1.1.14')
    # TODO Should consider putting this is config file
    results = []
    for interface in list_interfaces:
        interface = {
            "port": interface[3],
            "name": interface[4],
            "mode": states["mode"][interface[2]],
            "status": states["status"][interface[5]],
            "speed": (str(int(int(interface[6]) / 1000000))) + " Mbps",
            "vlan": interface[0],
            "duplex": states["duplex"][interface[1]],
            "id": int(interface[7])
        }
        results.append(interface)
    return results


def get_vlan_by_id(ip_switch, vl_id):
    """
    Gathers information about a specific VLAN

    :param ip_switch: IP address of the switch
    :param vl_id: ID of the vlan
    :return: A JSON object containing a VLAN's information
    """

    vlan = get_snmp_by_id(ip_switch, vl_id, '1.3.6.1.4.1.9.9.46.1.3.1.1.4.1.' + str(vl_id - 1))
    print(vlan)
    results = {
        "name": vlan[0],
        "id": vl_id
    }
    return results


def get_interface_by_id(ip_switch, if_id):
    """
    Gathers information about a specific interface

    :param ip_switch: IP address of the switch
    :param if_id: ID of the interface
    :return: A JSON object containing an interface's information
    """
    clean_if_id = str(if_id - 1)

    interface = get_snmp_by_id(ip_switch, if_id, '1.3.6.1.2.1.2.2.1.2.' + clean_if_id,
                              '1.3.6.1.2.1.31.1.1.1.1.' + clean_if_id,
                              '1.3.6.1.2.1.2.2.1.8.' + clean_if_id,
                              '1.3.6.1.2.1.2.2.1.5.' + clean_if_id,
                              '1.3.6.1.4.1.9.9.68.1.2.2.1.2.' + clean_if_id,
                              '1.3.6.1.2.1.10.7.2.1.19.' + clean_if_id,
                              '1.3.6.1.4.1.9.9.46.1.6.1.1.14.' + clean_if_id)  # Does this OID 
    # list even work ? TODO Should consider putting this is config file
    results = {
        "port": interface[0],
        "name": interface[1],
        "status": states["status"][interface[2]],  # That's honestly pretty clever
        "speed": (str(int(int(interface[3]) / 1000000))) + " Mbps",
        "vlan_id": interface[4],
        "vlan_name": find(ip_switch, interface[4], '1.3.6.1.4.1.9.9.46.1.3.1.1.4.1.'),
        "mode": states["mode"][interface[6]],
        "duplex": states["duplex"][interface[5]],
        "id": if_id
    }
    return results


def set_interface_vlan(ip_switch, if_id, vlan_id):
    """
    Changes an interface's VLAN

    :param ip_switch: IP address of the switch
    :param if_id: ID of the interface
    :param vlan_id: VLAN ID
    :return: A boolean status code
    """
    if check_if_id_exists(ip_switch, int(if_id), '1.3.6.1.2.1.2.2.1.2') and \
            check_if_id_exists(ip_switch, int(vlan_id), '1.3.6.1.4.1.9.9.46.1.3.1.1.4'):  # Soo, that's where test is used !
        snmp_set(ip_switch, {'1.3.6.1.4.1.9.9.68.1.2.2.1.2.' + str(if_id): pysnmp.proto.rfc1902.Integer(int(vlan_id))},
                 # TODO check if that double conversion is really needed
                 hlapi.CommunityData('cloudstack'))
        return True
    return False


def get_cdp_neighbors(ip_switch):
    """
    Gathers a list of CDP neighbors

    :param ip_switch: IP address of the switch
    :return: A list of CDP neighbors
    """
    neighbors = get_snmp_bulk(ip_switch, '1.3.6.1.4.1.9.9.23.1.2.1.1.6',
                              '1.3.6.1.4.1.9.9.23.1.2.1.1.8',
                              '1.3.6.1.4.1.9.9.23.1.2.1.1.5',
                              '1.3.6.1.4.1.9.9.23.1.2.1.1.11',
                              '1.3.6.1.4.1.9.9.23.1.2.1.1.4',
                              '1.3.6.1.4.1.9.9.23.1.2.1.1.7')  # TODO should consider exporting this to a config file
    results = []
    for neighbor in neighbors:
        addr = ''
        for i in range(0, len(neighbor[4])):
            addr = addr + str(neighbor[4].encode("utf-8")[i]) + "."
            i = i + 1
        cdp_neighbor = {
            "deviceId": neighbor[0],
            "Plateform": neighbor[1],
            "Version": str(str(neighbor[2])[str(neighbor[2]).find("Version"): len(str(neighbor[2]))])[
                       0: str(str(neighbor[2])[str(neighbor[2]).find("Version"): len(str(neighbor[2]))]).find(",")],
            # Excuse me wtf ? TODO Simplify this..
            "NativeVlan": neighbor[3],
            "IPAddress": addr[:-1],
            "Port ID": neighbor[5]
        }
        results.append(cdp_neighbor)
    return results
