#  SDN-Cloudstack - API
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
#

from pysnmp.entity.rfc3413.oneliner import cmdgen


def get_snmp_bulk(host, *list_oid):
    """
    Equivalent of an SNMP BULK (All values of an OID)

    :param host: IP address of the switch
    :param list_oid: a list of OID to get in BULK
    :return: A list of values from the SNMP BULK
    """

    x = []  # Is this really the best name you found ?
    results = []
    errorIndication, errorStatus, errorIndex, varBindTable = cmdgen.CommandGenerator().bulkCmd(
        cmdgen.CommunityData('test-agent', 'public'),
        cmdgen.UdpTransportTarget((host, 161)),
        0,
        25,
        *list_oid
    )

    if errorIndication:
        print(errorIndication)
    else:
        if errorStatus:
            print('%s at %s\n' % (
                errorStatus.prettyPrint(),
                errorIndex and varBindTable[-1][int(errorIndex) - 1] or '?'
            ))
        else:
            for varBindTableRow in varBindTable:
                for name, val in varBindTableRow:
                    idt = str(name)[str(name).rfind(".") + 1:len(str(name)) + 1]
                    x.append((str(val), str(idt)))
    list_id = []
    for idt in x:  # What is idt ? what is x ? TODO find out what this is for..
        if idt[len(idt) - 1] not in list_id:
            list_id.append(idt[len(idt) - 1])

    for idt in list_id:
        y = []  # Another great inspiration variable name
        for a in x:
            if (a[1] == idt) and (a[0] != ''):
                y.append(a[0])
        y.append(idt)
        for _ in range(len(list_oid) + 1 - len(y)):  # That's a bit more original... maybe too original...
            y.insert(0, "n/a")  # TODO understand that, comment, clean up..
        results.append(tuple(y))
    return (results)
