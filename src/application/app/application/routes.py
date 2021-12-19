#  SDN-Cloudstack - APPLICATION
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.

from application import app
from flask import render_template
import urllib
import json

api=['Reseau-1','Reseau-2','Reseau-3']
api_link = "http://10.59.50.233:8064/api/v1.5/"


# Route
@app.route("/")
@app.route("/home/")
def home():
    return render_template('pages/t_index.html', title='Index', api=api, len=len(api))


@app.route("/resume/")
def resume():
    return render_template("pages/t_resume.html", title='Resume', api=api, len=len(api))


@app.route("/login/")
def login():
    return render_template('pages/t_login.html', title='Login', api=api, len=len(api))


@app.route("/config/")
def config():
    return render_template('pages/t_config.html', title='Config', api=api, len=len(api))


@app.route("/config-otg/")
def config_otg():
    return render_template('pages/t_configs_on_the_go.html', title='Config On The Go', api=api, len=len(api), interfaces=get_interfaces(api_link), trunks=get_trunks(api_link), vlans=get_vlans(api_link))


#Error

@app.errorhandler(404)
def custom_error(error):
    return render_template('errors/e_not_found.html', title='Page Not Found', api=api, len=len(api))


@app.errorhandler(403)
def custom_error(error):
    return render_template('errors/e_forbidden.html', title='Forbiden Acces', api=api, len=len(api))


@app.errorhandler(400)
def custom_error(error):
    return render_template('errors/e_bad_request.html', title='Bad Request', api=api, len=len(api))


#Get from api
def get_trunks(api_link):
    content = urllib.request.urlopen(f"{api_link}trunks")
    content = json.load(content)
    return content


def get_vlans(api_link):
    content = urllib.request.urlopen(f"{api_link}vlans")
    content = json.load(content)
    return content


def get_interfaces(api_link):
    content = urllib.request.urlopen(f"{api_link}interfaces")
    content = json.load(content)
    return content