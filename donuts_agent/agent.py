import os
import re
import datetime
import commands
import tempfile
import time

def enable_zone(config, zview, zone):
    available, enabled, database = get_zones_path(config, zview, zone)
    status = []
    if os.path.isfile(database) and os.path.isfile(available) and not os.path.isfile(enabled):
        os.symlink(available, enabled)
        status.append({'status': 'file_linked', 'source': available, 'destination': enabled})
        status = refresh_conf(config, zview, status)
    return (False, status)

def disable_zone(config, zone, zviews):
    z = get_zone_file(config, zone, zviews)
    status = 'Zone does not exists'
    if z:
        status = []
        available, enabled, database = get_zones_path(config, zviews, zone)
        os.remove(enabled)
        status.append({'status': 'file_removed', 'source': enabled})
        status = refresh_conf(config, zviews, status)
        return (True, status)
    return (False, status)

def create_zone_file(fpath, dpath, database, zone, master_host):
    f = open(fpath)
    source_txt = f.read()
    f.close()
    data = {'ZONE': zone, 'DATABASE': database, 'MASTER': master_host}
    source_txt = source_txt.format(**data)
    dfile = open(dpath, 'w')
    dfile.write(source_txt)
    dfile.close()
    return {'status': 'file_created', 'content': source_txt, 'path': dpath}

def refresh_conf(config, zview, status):
    cmd = 'cat %s/*.conf > %s' % (config['zones']['enabled'][zview],
                                  config['zones']['activated'][zview])
    commands.getoutput(cmd)
    status.append({'status': 'recreate_zones', 'command': cmd})
    commands.getoutput(config['path']['named-checkconf'])
    status.append({'status': 'run', 'command': config['path']['named-checkconf']})
    commands.getoutput('%s reconfig' %config['path']['rndc'])
    status.append({'status': 'run', 'command': '%s reconfig' %config['path']['rndc']})
    return status

def get_zones_path(config, zview, zone):
    available = '%s/%s.conf' %(config['zones']['available'][zview], zone)
    enabled   = '%s/%s.conf' %(config['zones']['enabled'][zview], zone)
    databases = '%s/db.%s'   %(config['databases'][zview], zone)
    return (available, enabled, databases)

def add_zone(config, zone, master, master_host, zview='public'):
    z = get_zone_file(config, zone, zview)
    if z:
        ok = False
        return (ok, 'Zone already exists')
    zone_db = config['templates']['database']
    if master:
        zone_conf = config['templates']['zones']['master']
    else:
        zone_conf = config['templates']['zones']['slave']
    ok = True
    status = []
    available, enabled, database = get_zones_path(config, zview, zone)
    status.append(create_zone_file(zone_conf, available, database, zone, master_host))
    status.append(create_zone_file(zone_db, database, database, zone, master_host))
    status += enable_zone(config, zview, zone)[1]
    return (ok, status)

def del_zone(config, zone, zviews='public'):
    z = get_zone_file(config, zone, zviews)
    ok = False
    status = "Zone does not exists"
    if z:
        ok = True
        status = []
        command = '%s sync %s' % (config['path']['rndc'], zone)
        output = commands.getstatusoutput(command)
        time.sleep(3)
        available, enabled, database = get_zones_path(config, zviews, zone)
        disable_zone(config, zone, zviews)
        os.remove(available)
        status.append({'status': 'file_removed', 'source': available})
        os.rename(database, '%s/%s' %(config['backup'], database.split('/')[-1]+datetime.datetime.now().strftime('_%Y%m%d_%H%M%S')))
        status.append({'status': 'file_removed', 'source': database})
    return (ok, status)

def record_create(zone, action, record, record_type, record_value, ttl, force=False, verbose=False):
    archive = open(tempfile.mkstemp()[1], "w+b")
    archive.write("server 127.0.0.1\n")
    archive.write("zone %s\n" %(zone))
    fqdn = zone
    if record:
        fqdn = '%s.%s' % (record, zone)
    if record_type == 'MX':
        archive.write("update add %s %s %s %s\n" %(fqdn, ttl, record_type, record_value))
    else:
        archive.write("update add %s %s in %s %s\n" %(fqdn, ttl, record_type, record_value))
    archive.write("show\n")
    archive.write("send\n")
    archive.close()
    return archive.name

def record_delete(zone, action, record, record_type, record_value):
    archive = open(tempfile.mkstemp()[1], "w+b")
    archive.write("server 127.0.0.1\n")
    archive.write("zone %s\n" %(zone))
    r = zone
    if record and record != '@':
        r = '%s.%s' % (record, zone)
    archive.write("update delete %s in %s %s\n" %(r, record_type, record_value))
    archive.write("send\n")
    archive.close()
    return archive.name

def update_dns(config, filename, zone, view):
    command = "%s -k %s %s" %(config['path']['nsupdate'], config['zones']['keys'][view], filename)
    output = 'cmd: %s' % command
    output += '\n' * 2
    output += commands.getoutput(command)
    if os.path.exists(filename):
        os.remove(filename)
    command = '%s sync %s' % (config['path']['rndc'], zone)
    output += '\n ' * 2
    output += command
    output += '\n ' * 2
    output += commands.getoutput(command)
    output += '\n ' * 2
    return output

def update_zone(config, zone, action, record, record_type, record_value, ttl, zview):
    output = 'ok'
    if action == 'add':
        fname = record_create(zone, action, record, record_type, record_value, ttl)
        output = 'Filename: %s ' % fname
        output += '\n ' * 4
        output += commands.getoutput('cat %s ' % fname)
        output += '\n'
        output += update_dns(config, fname, zone, zview)
    elif action == 'del':
        fname = record_delete(zone, action, record, record_type, record_value)
        output = 'Filename: %s ' % fname
        output += '\n ' * 4
        output += commands.getoutput('cat %s ' % fname)
        output += '\n'
        output += update_dns(config, fname, zone, zview)
    return output

def get_zone_file(config, zone, zview):
    available, enable, database = get_zones_path(config, zview, zone)
    if not os.path.isfile(database):
        return False
    f = open(database)
    r = f.read()
    f.close()
    return r


def parse_zone(zp, k, zones):
    z = {}
    if not os.path.isfile(zp):
        return None
    f = open(zp, 'r')
    for line in f:
        line = re.sub('[^/0-9a-zA-Z \.\-]+', '', line)
        line = line.split()
        if line:
            key = line[0]
            value = line[1]
            if key == 'zone' and z:
                z['view'] = k
                zones.append(z)
                z = {'zone': value}
            else:
                z[key] = value
    f.close()
    return z


def get_zones(zones_dir):
    data = {}
    zones = []
    for k in zones_dir:
        zp = zones_dir[k]
        z = parse_zone(zp, k, zones)
        if z:
            z['view'] = k
            zones.append(z)
    data['zones'] = zones
    data['count'] = len(zones)
    return data
