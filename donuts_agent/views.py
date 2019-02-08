import os
import flask
from flask import Flask
from flask import abort
from flask import render_template
from flask import request
import agent
import pprint
import json
from donuts_libs import encrypt_val, decrypt_val

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['DEBUG'] = True

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form['data']
        data = json.loads(decrypt_val(data, app.config['SECRET_KEY']))
        # pprint.pprint(data)
        if 'request' in data:
            if data['request'] == 'show_zones':
                return show_zones(data)
            elif data['request'] == 'add_zone':
                return add_zone(data)
            elif data['request'] == 'del_zone':
                return del_zone(data)
            elif data['request'] == 'zone.get':
                return zone(data)
            elif data['request'] == 'enable_zone':
                return enable_zone(data)
            elif data['request'] == 'disable_zone':
                return disable_zone(data)
            elif data['request'] == 'update_zone':
                return update_zone(data)
            return flask.jsonify({'status': 'unknown request'})
        return flask.jsonify({'status': 'bad request'})
    return 'ok'

def enable_zone(data):
    zone = data.get('zone', None)
    zviews = data.get('view', 'private')
    if zone is None:
        abort(401)
    status = agent.enable_zone(app.config['BIND_CONF'], zviews, zone)
    data = {'status': status}
    return flask.jsonify(data)

def disable_zone(data):
    zone = data.get('zone', None)
    zviews = data.get('view', 'private')
    if zone is None:
        abort(401)
    status = agent.disable_zone(app.config['BIND_CONF'], zone, zviews=zviews)
    data = {'status': status}
    return flask.jsonify(data)

def add_zone(data):
    zone = data.get('zone', None)
    master = data.get('master', None)
    master_host = data.get('master_host', None)
    zview = data.get('view', 'private')
    if zone is None or master is None or master_host is None:
        abort(401)
    status = agent.add_zone(app.config['BIND_CONF'], zone, master, master_host, zview=zview)
    data = {'status': status}
    return flask.jsonify(data)

def del_zone(data):
    zone = data.get('zone', None)
    view = data.get('view', 'private')
    if not zone:
        abort(401)
    status = agent.del_zone(app.config['BIND_CONF'], zone, zviews=view)
    data = {'status': status}
    return flask.jsonify(data)

def show_zones(data):
    zone = data.get('zone', None)
    view = data.get('view', 'private')
    if not zone:
        data = {'data': agent.get_zones(app.config['BIND_ZONES'])}
        pprint.pprint(data)
        return flask.jsonify(data)
    data = {'data': agent.get_zone_file(app.config['BIND_CONF'], zone, view)}
    pprint.pprint(data)
    return flask.jsonify(data)

def zone(data):
    zone = data.get('zone', None)
    view = data.get('view', 'private')
    return flask.jsonify({'data': agent.zone_transfer(app.config['BIND_CONF'], zone, view) })
    
def update_zone(data):
    zone = data.get('zone', None)
    action = data.get('action', None)
    name = data.get('name', None)
    type = data.get('type', None)
    value = data.get('value', None)
    ttl = data.get('ttl', None)
    zviews = data.get('view', 'private')
    if None in (zone, action, name, type, value, ttl, zviews):
        abort(401)
    output = agent.update_zone(app.config['BIND_CONF'], zone, action, name, type, value, ttl, zviews)
    data = {'status': output}
    print(data)
    return flask.jsonify(data)

if __name__ == '__main__':
    app.debug = True
    app.secret_key = '233432432asdblablaasdasdasr34243243adsadasd2'
    app.run('0.0.0.0', 5000)
