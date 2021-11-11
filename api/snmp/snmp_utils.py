import json
import sys
from types import SimpleNamespace

from pysnmp.entity.engine import SnmpEngine
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.hlapi import nextCmd, CommunityData, UdpTransportTarget, ContextData
from pysnmp.smi.rfc1902 import ObjectType, ObjectIdentity


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
        return self.walk(oid + "." + str(id), 1)

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

    def set(self, oid, value):
        errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CommandGenerator().setCmd(
            cmdgen.CommunityData(self.community),
            cmdgen.UdpTransportTarget((self.host, self.port)),
            (ObjectType(ObjectIdentity(oid)), value)
        )
        if errorIndication:
            print(errorIndication)
        elif errorStatus:
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'
            ))

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


if __name__ == "__main__":
    snmp = SnmpUtils("10.59.10.20")
    for k,v in snmp.walk(snmp.OIDS.OLT.ONU.MAC_ADDRESS, 8).items():
        #print(k,v)
        pass
