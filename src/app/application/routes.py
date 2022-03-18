#  SDN-Cloudstack - APPLICATION
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
import yaml
from application import app
from flask import render_template, session, request, redirect, url_for
import urllib
import json

from yaml import Loader

api = {'Reseau-1': 'r1', 'Reseau-2': 'r2', 'Reseau-3': 'r3', 'Test': 'test'}
selected_api = 'Reseau-1'
api_base_link = ".api.sdn.chalons.univ-reims.fr/api/v1.5/"


@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Load the users from the config file
        with open('config/config_app.yaml') as yaml_file:
            data = yaml.load(yaml_file, Loader=Loader)['users']
        # Get the username and password from the form
        username = request.form['username']
        password = request.form['password']
        print(username in data)
        print(data)
        # Check if the username and password match
        # [{'admin': {'password': 'admin', 'roles': ['admin', 'user']}}, {'user': {'password': 'user', 'roles': ['user']}}]
        for i in data:
            if username in i:
                if password == i[username]['password']:
                    # Set the session variable
                    session['logged_in'] = True
                    session['username'] = username
                    # Redirect to the home page
                    return redirect(url_for('interfaces'))
            return render_template('pages/t_config.html', title='Config', api=api, len=len(api), user=session.get('username'), selected=selected_api)
        else:
            return render_template('errors/e_unauthorized.html', title='Unauthorized', api=api, len=len(api), selected=selected_api, user=session.get('username'))
    else:
        return render_template('pages/t_login.html', title='Config', api=api, len=len(api), selected=selected_api, user=session.get('username'))


@app.route("/logout/")
def logout():
    # Remove the username from the session if it's there
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('resume'))


@app.route("/config/")
def config():
    return render_template('pages/t_config.html', title='Config', api=api, selected=selected_api, len=len(api), user=session.get('username'))


@app.route("/config-otg/<room>")
@app.route("/config-otg/")
def config_otg(room="Reseau-1"):
    selected_api = room
    api_link = f"http://{api[room]}{api_base_link}"
    print(api_link)
    return render_template('pages/t_configs_on_the_go.html', title='Config On The Go', api=api, len=len(api),
                           interfaces=get_data(api_link, "interfaces"), trunks=get_data(api_link, "trunks"),
                           vlans=get_data(api_link, "vlans"), room=room, selected=selected_api, user=session.get('username'))


# Route
@app.route("/")
@app.route("/resume/")
@app.route("/resume/<room>")
@app.route("/<room>")
def interfaces(room="Reseau-1"):
    selected_api = room
    api_link = f"http://{api[room]}{api_base_link}"
    interfaces = get_interfaces(api_link)
    filteredInterfaces = {'top': [], 'bottom': [], 'r3': []}
    return render_template('pages/t_resume.html', interfaces=interfaces, room=room, user=session.get('username'),
                           api=api, selected=selected_api, len=len(api))


@app.route("/interface/<room>/<iface_id>")
def interface(room, iface_id):
    selected_api = room
    if session.get('logged_in'):
        api_link = f"http://{api[selected_api]}{api_base_link}"
        interfaces = get_interfaces(api_link)
        for iface in interfaces:
            if iface['port_id'] == int(iface_id):
                print(iface['status'])
                return render_template('pages/t_interface.html', interface=iface, user=session.get('username'),
                                       api=api, selected=selected_api, len=len(api))
        return render_template('errors/e_interface.html', user=session.get('username'), api=api, selected=selected_api, len=len(api))
    else:
        return render_template('errors/e_unauthorized.html', title='Unauthorized', api=api, len=len(api), selected=selected_api, user=session.get('username'))


# Error handlers.
@app.errorhandler(404)
def custom_error(error):
    return render_template('errors/e_not_found.html', title='Page Not Found', api=api, selected=selected_api, len=len(api))


@app.errorhandler(403)
def custom_error(error):
    return render_template('errors/e_forbidden.html', title='Forbiden Acces', selected=selected_api, api=api, len=len(api))


@app.errorhandler(400)
def custom_error(error):
    return render_template('errors/e_bad_request.html', title='Bad Request', selected=selected_api, api=api, len=len(api))


# Get from api
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


def get_data(api_link, data_type):
    content = urllib.request.urlopen(f"{api_link}{data_type}")
    content = json.load(content)
    if data_type == "trunks":
        i = 0
        for data in content:
            if data['interface']['vlan'] is None:
                content[i]['interface']['vlan'] = 'None'
            i += 1
    elif data_type == 'interfaces':
        i = 0
        for data in content:
            if data['vlan'] is None:
                content[i]['vlan'] = 'None'
            i += 1

    return content
