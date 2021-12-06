import json
import sys
from types import SimpleNamespace

from pysnmp.entity.engine import SnmpEngine
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.hlapi import nextCmd, CommunityData, UdpTransportTarget, ContextData, Integer
from pysnmp.smi.rfc1902 import ObjectType, ObjectIdentity
import pysnmp


def construct_value_pairs(list_of_pairs):
    pairs = []
    for key, value in list_of_pairs.items():
        pairs.append(pysnmp.hlapi.ObjectType(pysnmp.hlapi.ObjectIdentity(key), Integer(value)))
    return pairs


def construct_object_types(list_of_oids):
    object_types = []
    for oid in list_of_oids:
        object_types.append(pysnmp.hlapi.ObjectType(pysnmp.hlapi.ObjectIdentity(oid)))
    return object_types


def cast(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            try:
                return str(value)
            except (ValueError, TypeError):
                pass
    return value


def fetch(handler, count):
    result = []
    for i in range(count):
        try:
            error_indication, error_status, error_index, var_binds = next(handler)
            if not error_indication and not error_status:
                items = {}
                for var_bind in var_binds:
                    items[str(var_bind[0])] = cast(var_bind[1])
                result.append(items)
            else:
                print(error_indication, error_status)
                raise RuntimeError('Got SNMP error: {0} {1}'.format(error_indication, error_status))
        except StopIteration:
            break
    return result


class SnmpUtils:
    """
    SNMP Utils Class for walk/bulk/set more easily in python.
    @author: HakkaOfDev
    @version: 1.0.0
    """

    def __init__(self, host, port=161, community="public"):
        self.host = host
        self.port = port
        self.community = community

    def findById(self, oid, id):
        item = self.walk(oid + "." + str(id-1), 1)  # I dunno why, but you need -1 here..
        if str(id) == list(item.keys())[-1].split('.')[-1]:
            return list(item.values())[-1]
        else:
            return None


    def defineOIDsList(self):
        with open('./OIDS.json', ) as file:
            self.OIDS = json.loads(file.read().replace('\n', ''), object_hook=lambda d: SimpleNamespace(**d))

    def bulk(self, *oids_list):
        errorIndication, errorStatus, errorIndex, varBindTable = cmdgen.CommandGenerator().bulkCmd(
            cmdgen.CommunityData(self.community),
            cmdgen.UdpTransportTarget((self.host, self.port)),
            0, 25,
            *oids_list,
        )

        if errorIndication:
            print(errorIndication)

        elif errorStatus:
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                errorIndex and varBindTable[int(errorIndex) - 1][0] or '?'
            ))

        results = {}
        for varBindTableRow in varBindTable:
            for name, val in varBindTableRow:
                results[str(name)] = str(varBindTableRow[0]).split(" = ")[1]

        return results

    def set(self, value_pairs, engine=pysnmp.hlapi.SnmpEngine(), context=pysnmp.hlapi.ContextData()):
        handler = pysnmp.hlapi.setCmd(
            engine,
            pysnmp.hlapi.CommunityData(self.community),
            pysnmp.hlapi.UdpTransportTarget((self.host, self.port)),
            context,
            *construct_value_pairs(value_pairs)
        )
        return fetch(handler, 1)[0]

    def walk(self, oid, n=0, dotPrefix=False):
        if dotPrefix:
            oid = "." + oid

        results = {}
        i = 0
        for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
                                                                            CommunityData(self.community),
                                                                            UdpTransportTarget((self.host, self.port)),
                                                                            ContextData(),
                                                                            ObjectType(ObjectIdentity(oid))):
            if errorIndication:
                print(errorIndication, file=sys.stderr)
                break
            elif errorStatus:
                print('%s at %s' % (errorStatus.prettyPrint(),
                                    errorIndex and varBinds[int(errorIndex) - 1][0] or '?'),
                      file=sys.stderr)
                break
            else:
                for varBind in varBinds:
                    if n == 0:
                        results[str(varBind[0].__str__).split("payload [")[1][:-4]] = str(varBind[1].__str__).split("payload [")[1][:-3]
                    elif n != i:
                        results[str(varBind[0].__str__).split("payload [")[1][:-4]] = str(varBind[1].__str__).split("payload [")[1][:-3]
                        i += 1
                    else:
                        return results
        return results