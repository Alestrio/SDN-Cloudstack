import pysnmp
from pysnmp import hlapi
from snmp.snmp_bulk import get_snmp_bulk
from snmp.snmp_byid import get_snmp_byid
from snmp.snmp_set import snmp_set
import json
etat = json.load(open('../config/etat.json', ))


# Faire un test pour savoir si l'id existe :
def test(ip_switch,idt,oid):
    list_id = get_snmp_bulk(ip_switch,oid)
    for x in list_id:
        if int(x[1]) == int(idt) :
            return True       
    return False   

# Trouver l'information spécifique à l'id :
def find(ip_switch,idt,oid):
    if idt == 'n/a': 
        data = 'n/a'
        return (data)
    else : 
        data = get_snmp_byid(ip_switch,int(idt),oid+str(int(idt)-1))
        return data[0]


# Mettre la liste des vlans en format JSON :
def vlans(ip_switch):
    list_vlans = get_snmp_bulk(ip_switch,('1.3.6.1.4.1.9.9.46.1.3.1.1.4'))
    resultats = []
    for vlans in list_vlans :
        vlan = {
                "name" : vlans[0],
                "id" : int(vlans[1]) 
               }
        resultats.append(vlan)      
    return resultats



# Mettre la liste des interfaces en format JSON :
def interfaces(ip_switch):
    list_interfaces = get_snmp_bulk(ip_switch,'1.3.6.1.2.1.2.2.1.2','1.3.6.1.2.1.31.1.1.1.1','1.3.6.1.2.1.2.2.1.8','1.3.6.1.2.1.2.2.1.5','1.3.6.1.4.1.9.9.68.1.2.2.1.2','1.3.6.1.2.1.10.7.2.1.19','1.3.6.1.4.1.9.9.46.1.6.1.1.14')
    resultats = []
    for interface in list_interfaces :
        interface = {
                "port" : interface[3],
                "name" : interface[4],
                "mode" : etat["mode"][interface[2]],
                "status" : etat["status"][interface[5]], 
                "speed" : (str(int(int(interface[6])/1000000))) + " Mbps", 
                "vlan" : interface[0],
                "duplex" : etat["duplex"][interface[1]],
                "id" : int(interface[7])
               }
        resultats.append(interface)       
    return resultats


# Mettre un vlan en format JSON :
def vlansbyid(ip_switch,vl_id):
    vlan = get_snmp_byid(ip_switch,vl_id,'1.3.6.1.4.1.9.9.46.1.3.1.1.4.1.'+str(vl_id - 1))
    print(vlan)
    resultats = {
                "name" : vlan[0],
                "id" : vl_id
               }      
    return resultats    

# Mettre une interface en format JSON :
def interfacebyid (ip_switch,if_id) :

    interface = get_snmp_byid(ip_switch,if_id,'1.3.6.1.2.1.2.2.1.2.'+str(if_id - 1),'1.3.6.1.2.1.31.1.1.1.1.'+str(if_id - 1),'1.3.6.1.2.1.2.2.1.8.'+str(if_id - 1),'1.3.6.1.2.1.2.2.1.5.'+str(if_id - 1),'1.3.6.1.4.1.9.9.68.1.2.2.1.2.'+str(if_id - 1),'1.3.6.1.2.1.10.7.2.1.19.'+str(if_id - 1),'1.3.6.1.4.1.9.9.46.1.6.1.1.14.'+str(if_id - 1))
    resultats = {
                "port" : interface[0],
                "name" : interface[1],
                "status" : etat["status"][interface[2]], 
                "speed" : (str(int(int(interface[3])/1000000))) + " Mbps", 
                "vlan_id" : interface[4],
                "vlan_name" : find(ip_switch,interface[4],'1.3.6.1.4.1.9.9.46.1.3.1.1.4.1.'),
                "mode" : etat["mode"][interface[6]],
                "duplex" : etat["duplex"][interface[5]],
                "id" : if_id
               }
    return resultats           

# Changer le vlan d'une interface :
def new_vlan_if(ip_switch,if_id,vlan_id) : 
    if test(ip_switch,int(if_id),'1.3.6.1.2.1.2.2.1.2') and test(ip_switch,int(vlan_id),'1.3.6.1.4.1.9.9.46.1.3.1.1.4') :
        snmp_set(ip_switch, {'1.3.6.1.4.1.9.9.68.1.2.2.1.2.'+str(if_id):pysnmp.proto.rfc1902.Integer(int(vlan_id)) }, hlapi.CommunityData('cloudstack'))
        return True
    return False

# Mettre la liste des CDP neighbors en format JSON  :
def cdp_neighbors(ip_switch) :
    list_cdp = get_snmp_bulk(ip_switch,'1.3.6.1.4.1.9.9.23.1.2.1.1.6','1.3.6.1.4.1.9.9.23.1.2.1.1.8','1.3.6.1.4.1.9.9.23.1.2.1.1.5','1.3.6.1.4.1.9.9.23.1.2.1.1.11','1.3.6.1.4.1.9.9.23.1.2.1.1.4','1.3.6.1.4.1.9.9.23.1.2.1.1.7')
    resultats = []
    for cdps in list_cdp:
        addr =''
        for i in range(0,len(cdps[4])):
            addr = addr +str(cdps[4].encode("utf-8")[i]) + "."
            i = i+1
        cdp = {
            "deviceId" : cdps[0], 
            "Plateform" : cdps[1],
            "Version" : str(str(cdps[2])[str(cdps[2]).find("Version"):len(str(cdps[2]))])[0:str(str(cdps[2])[str(cdps[2]).find("Version"):len(str(cdps[2]))]).find(",")],
            "NativeVlan" : cdps[3],
            "IPAddress" : addr[:-1],
            "Port ID" : cdps[5]
        }
        resultats.append(cdp)      
    return resultats        