from pysnmp.entity.rfc3413.oneliner import cmdgen  

def get_snmp_bulk( host , *list_oid) : 
    x = []
    resultats = [] 
    errorIndication, errorStatus, errorIndex, \
    varBindTable = cmdgen.CommandGenerator().bulkCmd(  
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
            print ('%s at %s\n' % (
                errorStatus.prettyPrint(),
                errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
                ))
        else:
            for varBindTableRow in varBindTable:
                for name, val in varBindTableRow :
                    idt = str(name)[str(name).rfind(".")+1:len(str(name))+1]
                    x.append((str(val),str(idt)))           
    list_id = []              
    for idt in x:
        if idt[len(idt)-1] not in list_id :
            list_id.append(idt[len(idt)-1])

    for idt in list_id  :
        y = []
        for a in x: 
            if (a[1] == idt) and (a[0]!=''):
                y.append(a[0]) 
        y.append(idt)            
        for _ in range(len(list_oid)+1 - len(y)) :
            y.insert(0,"n/a")
        resultats.append(tuple(y))     
    return(resultats) 