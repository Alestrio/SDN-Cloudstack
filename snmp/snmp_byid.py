#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
#

from pysnmp.hlapi import *
import sys


def get_snmp_by_id(host, test_id, *list_oid):
    """
    TODO Code cleanup
    Get several SNMP values from an host

    :param host: IP address of the host
    :param test_id: I dunno what this is needed for wtf ? You can get that at the end of the OID
    :param list_oid: A list of OIDs to be gathered on the host
    :return: A list of values from the OIDs
    """
    data = []
    for oid in list_oid:
        data.append(ObjectType(ObjectIdentity(oid)))  # Yeah, seems legit
    tuple(data)  # Excuse me, wtf ?
    results = []
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(SnmpEngine(),
                              CommunityData('public'),
                              UdpTransportTarget((host, 161)),
                              ContextData(),
                              *data
                              ):
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
                str(varBind).replace(" ", "").split("=")  # Useless, var value not reassigned..
                # Keeping this to understand intention of the author
                data = str(varBind[1])
                idt = str(varBind[0])[str(varBind[0]).rfind(".") + 1:len(str(varBind[0])) + 1]  # Excuse me, wtf ? #2
                if int(idt) == test_id:
                    # What is this test for wtf ??
                    results.append(data)
                else:
                    results.append('n/a')
        break
    return results
