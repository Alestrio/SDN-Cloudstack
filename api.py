from flask import render_template,make_response,jsonify,abort,Response,request,Flask
import json
import sys
from modules import *
api = Flask(__name__)

ip_switch = str(sys.argv[1])


@api.route("/api/vlans", methods=['GET'])
def get_vlans():
    reponse = make_response(jsonify(vlans(ip_switch)),200)
    return reponse

@api.route("/api/interfaces", methods=['GET'])
def get_interfaces(): 
    reponse = make_response(jsonify(interfaces(ip_switch)),200)
    return reponse


@api.route("/api/vlans/<int:vl_id>", methods=['GET'])    
def vl_Id(vl_id):
    if test(ip_switch,vl_id,'1.3.6.1.4.1.9.9.46.1.3.1.1.4') :
        reponse = make_response(jsonify(vlansbyid(ip_switch,vl_id)),200)
        return reponse
    else :
        reponse = make_response({"message" : "Vlan not found"},404)
        return reponse


@api.route("/api/interfaces/<int:if_id>", methods=['GET','POST'])    
def if_Id(if_id):
    if request.method == 'GET':
        if test(ip_switch,if_id,'1.3.6.1.2.1.2.2.1.2') :
            reponse = make_response(jsonify(interfacebyid(ip_switch,if_id)),200)
            return reponse
        else :
            reponse = make_response({"message" : "Interface not found"},404)
            return reponse
    else : 
        if request.form["vlan_id"] : 
            if new_vlan_if(ip_switch,if_id,request.form["vlan_id"]) : 
                return make_response({"message" : "Vlan successfully changed"},200)
            else :
                return make_response({"message" : "Interface or vlan not found"},404) 



@api.route("/api/neighbors", methods=['GET'])
def get_cdpneighbors(): 
    reponse = make_response(jsonify(cdp_neighbors(ip_switch)),200)
    return reponse


if __name__ == "__main__":
    api.run(host='0.0.0.0',debug=True)