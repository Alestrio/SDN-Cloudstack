from pysnmp.hlapi import *


def get_snmp_byid(host,test_id, *list_oid):
    data = []
    for oid in list_oid :
        data.append(ObjectType(ObjectIdentity(oid)),)
    tuple(data)     
    resultats = [] 
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
                str(varBind).replace(" ", "").split("=")
                data = str(varBind[1])
                idt = str(varBind[0])[str(varBind[0]).rfind(".")+1:len(str(varBind[0]))+1]
                if int(idt) == test_id :
                    resultats.append(data)
                else :
                    resultats.append('n/a')            
        break  
    return resultats