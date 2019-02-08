#!/usr/bin/env python
import os
import re
import datetime
import commands
import tempfile
import time
import dns.zone


def commands_exec(commands):
    return [{ 'cmd': c, 'out': commands.getoutput(c)} for c in commands]


def rndc_sync(config, zone=''):
    return commands_exec([ '%s sync %s' % (config['path']['rndc'], zone) ])
    

def zone_read(zone, view, config):
    zone_sync(config, zone)
    zone = dns.zone.from_file(get_zone_file(config, zone, view, content=False), zone)
    names = zone.nodes.keys()
    names.sort()
    soa = {}
    records = []
    for n in names:
        txt = zone[n].to_text(n)
        for t in txt.split('\n'):
            if 'SOA' in t:
                soa['raw'] = t
                soa['ts'] = t.split('.')[-1].strip().split()[0]
            else:
                values = t.split()
                if len(values) == 5:
                    records.append({ 'name': values[0], 'ttl': values[1], 'type': values[3], 'value': values[4] })
                else:
                    values = t.split('"')
                    if len(values) == 3:
                        v = values[0].split()
                        records.append({ 'name': v[0], 'ttl': v[1], 'type': v[3], 'value': values[1] })
                    else:
                        for k in ['SRV', 'MX', 'RSIG', 'TXT', 'DNSKEY', 'NSEC3PARAM', 'TYPE65534']:
                            if key in t:
                                values = t.split(key)
                                v = values[0].split()
                                records.append({ 'name': v[0], 'ttl': v[1], 'type': key, 'value': values[1] })
                                break
    return soa, records


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


def add_zone(config, zone, master, master_host, zview='private'):
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


def del_zone(config, zone, zviews='private'):
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
    if record and record != '@':
        if not record.endswith(zone):
            fqdn = '%s.%s' % (record, zone)
        else:
            fqdn = record
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
        if not record.endswith(zone):
           r = '%s.%s' % (record, zone)
        else:
           r = record
    archive.write("update delete %s in %s %s\n" %(r, record_type, record_value))
    archive.write("show\n")
    archive.write("send\n")
    archive.close()
    return archive.name


def nsupdate_file(zone, operations):
    archive = open(tempfile.mkstemp()[1], "w+b")
    archive.write("server 127.0.0.1\n")
    if not filter(lambda x: zone.endswith(x), ['.in-addr.arpa']):
        archive.write("zone %s\n" %(zone))
    for o in operations:
        o['record'] = '.'.join(filter(lambda x: x not in [None, '@', ''], [o['name']]))
        if not o['record'].endswith(zone):
            o['record']+='.%s' %zone 
        if o['type'] not in ['MX']:
            archive.write("update %(action)s %(record)s %(ttl)s IN %(type)s %(value)s\n" %(o))
        else:
            archive.write("update %(action)s %(record)s %(ttl)s %(type)s %(value)s\n" %(o))
    archive.write("show\n")
    archive.write("send\n")
    archive.close()
    return archive.name    


def nsupdate(zone, view, operations, config):
    fname = nsupdate_file(zone, operations)
    commands = [
        'cat "%s"' % fname,
        "%s -k %s %s" %(config['path']['nsupdate'], config['zones']['keys'][view], fname),
        '%s sync %s' %(config['path']['rndc'], zone)
    ]
    return commands_exec(commands)
    

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
        output = '~# cat "%s"\n' % fname
        output += commands.getoutput('cat "%s"' % fname)
        output += '\n~#\n'
        output += update_dns(config, fname, zone, zview)
    elif action == 'del':
        fname = record_delete(zone, action, record, record_type, record_value)
        output = '~# cat "%s"\n' % fname
        output += commands.getoutput('cat "%s"' % fname)
        output += '\n~#\n'
        output += update_dns(config, fname, zone, zview)
    return output


def get_zone_file(config, zone, zview, content=True):
    available, enable, database = get_zones_path(config, zview, zone)
    if not os.path.isfile(database):
        return False
    if content:
        f = open(database)
        r = f.read()
        f.close()
        return r
    else:
        return database


def zone_transfer(config, zone, view, parse=True):
    available, enable, database = get_zones_path(config, view, zone)
    if not os.path.isfile(database):
        return False
    if parse:
        records = []
        soa = {}

        z = dns.zone.from_file(database, check_origin=False)
        names = z.nodes.keys()
        names.sort()
        for n in names:
            txt = z[n].to_text(n)
            for t in txt.split('\n'):
                if 'SOA' in t:
                    soa['raw'] = t
                    ts = t.split('.')[-1].strip().split()[0]
                    soa['ts'] = ts
                r = parse_record(zone, t)
                if r:
                    records.append(r)
        return soa, records
    else:
        return database

def parse_record(zone, ovalues):
    if 'SOA' in ovalues:
        return None
    values = ovalues.split()
    record = {}
    print(zone, values)
    if len(values) == 5:
        record['name'] = values[0]
        record['ttl'] = values[1]
        record['type'] = values[3]
        record['value'] = values[4]
    else:
        values = ovalues.split('"')
        if len(values) == 3:
            record_value = values[1]
            values = values[0].split()
            record['name'] = values[0]
            record['ttl'] = values[1]
            record['type'] = values[3]
            record['value'] = record_value
        else:
            found = False
            for key in ['SRV', 'MX', 'RSIG', 'TXT', 'DNSKEY', 'NSEC3PARAM', 'TYPE65534']:
                if key in ovalues:
                    record = get_record(key, ovalues)
                    found = True
                    break
    return record
    
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

