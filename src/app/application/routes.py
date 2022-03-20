#  SDN-Cloudstack - APPLICATION
#  Third semester project, Technical Degree, Networks and Telecommunications
#  Copyright (c) 2021-2022
#  Alexis LEBEL, Elwan LEFEVRE, Laurent HUSSENET
#  This code belongs exclusively to its authors, use, redistribution or
#  reproduction forbidden except with authorization from the authors.
import re

import yaml
from application import app
from flask import render_template, session, request, redirect, url_for
import urllib
import json
import requests
from yaml import Loader

api = {'Reseau-1': 'r1', 'Reseau-2': 'r2', 'Reseau-3': 'r3', 'Test': 'test'}
selected_api = 'Reseau-1'
api_base_link = ".api.sdn.chalons.univ-reims.fr/api/v1.5/"

select_paths = ['/', '/resume/', '/config/', '/trunks/', '/config-otg/']
for i in api.keys():
    select_paths.append('/resume/' + i)
    select_paths.append('/config/' + i)
    select_paths.append('/trunks/' + i)
    select_paths.append('/config-otg/' + i)



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
                    return redirect('/resume/')
            return redirect('/')
        else:
            return render_template('errors/e_unauthorized.html', title='Unauthorized', api=api, len=len(api), selected=selected_api, user=session.get('username'))
    else:
        return render_template('pages/t_login.html', title='Config', api=api, len=len(api), selected=selected_api, user=session.get('username'))


@app.route("/logout/")
def logout():
    # Remove the username from the session if it's there
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect('/resume')


@app.route("/config/")
@app.route("/config/<room>")
@app.route("/config/<room>/<name>", methods=['POST'])
def config(room="Reseau-1", name=""):
    selected_api = room
    api_link = f"http://{api[room]}{api_base_link}"
    configs = get_configs(api_link)
    if request.method == 'POST':
        config_id = configs[name]['_id']
        post_request(api_link+"configs/apply/{}".format(config_id), None, None)
    else:
        return render_template('pages/t_config.html', title='Config', room=room, api=api, selected=selected_api,
                               len=len(api), user=session.get('username'), select_paths=select_paths, configs=configs)


@app.route('/config/delete/<room>/<name>', methods=['POST'])
def delete_config(room, name):
    api_link = f"http://{api[room]}{api_base_link}"
    configs = get_configs(api_link)
    delete_request(api_link+"configs/{}".format(name))
    return redirect('/config/'+room)


@app.route("/config-otg/<room>")
@app.route("/config-otg/")
def config_otg(room="Reseau-1"):
    selected_api = room
    api_link = f"http://{api[room]}{api_base_link}"
    print(api_link)
    return render_template('pages/t_configs_on_the_go.html', title='Config On The Go', api=api, len=len(api),
                           interfaces=get_data(api_link, "interfaces"), trunks=get_data(api_link, "trunks"),
                           vlans=get_data(api_link, "vlans"), room=room, selected=selected_api, user=session.get('username'),
                           select_paths=select_paths)


# Route
@app.route("/")
@app.route("/resume/")
@app.route("/resume/<room>")
@app.route("/<room>")
def resume(room="Reseau-1"):
    selected_api = room
    api_link = f"http://{api[room]}{api_base_link}"
    if session.get(api[room]) is None:
        session[api[room]] = {'interfaces': get_interfaces(api_link)}
    return render_template('pages/t_resume.html', interfaces=session[api[room]]['interfaces'], room=room, user=session.get('username'),
                           api=api, selected=selected_api, len=len(api), select_paths=select_paths)


@app.route("/interface/<room>/<iface_id>", methods=['GET', 'POST'])
def interface(room, iface_id):
    selected_api = room
    api_link = f"http://{api[selected_api]}{api_base_link}"
    if session.get(api[room]) is None:
        session[api[room]] = {'interfaces': get_interfaces(api_link)}
    for iface_data in session[api[room]]['interfaces']:
        if iface_data['port_id'] == int(iface_id):
            iface = iface_data
    if not iface:
        return render_template('errors/e_404.html', title='404', api=api, len=len(api), selected=selected_api, user=session.get('username'))
    if request.method == 'POST':
        iface_status = iface['status']
        iface_vlan = iface['vlan']['dot1q_id']
        if int(request.form['vlan']) != iface_vlan:
            # Change the vlan
            response = post_request(f"{api_link}interfaces/{iface_id}/vlan/{request.form['vlan']}", None, None)
            iface['vlan']['dot1q_id'] = int(request.form['vlan'])
            #if response.status_code != 200:
            #    print(response.status_code)
            #    return render_template('errors/e_interface.html', title='500', api=api, len=len(api), selected=selected_api, user=session.get('username'))
        if request.form['status'] != iface_status:
            # Change the status
            print(request.form['status'])
            response = post_request(f"{api_link}interface/{iface_id}/state/{'true' if request.form['status'] == '1' else 'false'}", None, None)
            iface['status'] = 'up' if request.form['status'] == '1' else 'down'
            #if response.status_code != 200:
            #    return render_template('errors/e_interface.html', title='500', api=api, len=len(api), selected=selected_api, user=session.get('username'))
        # Update the interface in the session with the new data iface
        for iface_data in range(len(session[api[room]]['interfaces'])):
            if session[api[room]]['interfaces'][iface_data]['port_id'] == iface['port_id']:
                print(iface)
                session[api[room]]['interfaces'][iface_data] = iface
        for iface_data in range(len(session[api[room]]['interfaces'])):
            if session[api[room]]['interfaces'][iface_data]['port_id'] == iface['port_id']:
                print(session[api[room]]['interfaces'][iface_data])
        return render_template('pages/t_resume.html', interfaces=session[api[room]]['interfaces'], room=room,
                               user=session.get('username'),
                               api=api, selected=selected_api, len=len(api))
    else:
        if session.get('logged_in'):
            return render_template('pages/t_interface.html', interface=iface, user=session.get('username'),
                                       api=api, room=api[selected_api], selected=selected_api, len=len(api))
        else:
            return render_template('errors/e_unauthorized.html', title='Unauthorized', api=api, len=len(api), selected=selected_api, user=session.get('username'))


@app.route('/cache_reload/<selected_api>')
def cache_reload(selected_api="Reseau-1"):
    # Get request
    session[api[selected_api]] = None
    response = get_request(f"http://{api[selected_api]}{api_base_link}rebuild")
    print(f"http://{api[selected_api]}{api_base_link}rebuild")
    return redirect('/resume/' + selected_api)


@app.route('/send_config', methods=["POST"])
def send_config():
    dic = '{'+ request.form['config'][1:] +'\n}'
    dic = json.loads(dic)
    interfaces = []
    vlans = []
    trunks = []
    for element in dic:
        if re.match("interface.*", element):
            interfaces.append(dic.get(element))
        elif re.match("vlan.*", element):
            vlans.append(dic.get(element))
        elif re.match("trunk.*", element):
            trunks.append(dic.get(element))

    new_config = {"name": request.form['config_name'],
                  "hostname": request.form['host_name'],
                  "interfaces": interfaces,
                  "vlans": vlans,
                  "trunks": trunks}
    x = requests.post(f"http://{api[new_config['hostname']]}{api_base_link}config", data=json.dumps(new_config))
    print(x.text)
    return redirect('/')

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


def get_vlans(api_link):
    content = urllib.request.urlopen(f"{api_link}vlans")
    content = json.load(content)
    return content


def get_interfaces(api_link):
    content = urllib.request.urlopen(f"{api_link}interfaces")
    content = json.load(content)
    return content


def get_configs(api_link):
    content = urllib.request.urlopen(f"{api_link}configs")
    content = json.load(content)['configs']
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


def get_request(api_link):
    return urllib.request.urlopen(api_link)


def post_request(api_link, data_type, data):
    """
    Allows to post data to the api
    :param api_link:
    """
    data = json.dumps(data).encode('utf8')
    print(api_link)
    req = urllib.request.Request(api_link, data, headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    return response


def delete_request(api_link):
    """
    Allows to delete data from the api
    :param api_link:
    """
    req = urllib.request.Request(api_link)
    req.method = 'DELETE'
    response = urllib.request.urlopen(req)
    return response
