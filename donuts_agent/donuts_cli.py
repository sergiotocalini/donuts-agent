# import simplecrypt
import requests
import json
import os
import random
import string
import sys
from prettytable import PrettyTable
from donuts_libs import encrypt_val, decrypt_val, crypt_request
import config
import pprint


BIND_KEY='r43r8fdj3290121p454yhyf!'

def show_zones():
    data = {'request': 'show_zones'}
    return crypt_request("http://dnspub02.prd.srv.tca.ar.internal:5000/", data, BIND_KEY)

def show_zone(zone):
    data = {'request': 'show_zones', 'zone': zone}
    return crypt_request("http://dnspub02.prd.srv.tca.ar.internal:5000/", data, BIND_KEY)

def add_zone(zone, master, master_host):
    data = {'request': 'add_zone', 'master': master, 'zone': zone, 'master_host': master_host}
    return crypt_request("http://dnspub02.prd.srv.tca.ar.internal:5000/", data, BIND_KEY)

def del_zone(zone):
    data = {'request': 'del_zone', 'zone': zone}
    return crypt_request("http://dnspub02.prd.srv.tca.ar.internal:5000/",data, BIND_KEY)

def enabled_zone(zone):
    data = {'request': 'enable_zone', 'zone': zone}
    return crypt_request("http://dnspub02.prd.srv.tca.ar.internal:5000/",data, BIND_KEY)

def disable_zone(zone):
    data = {'request': 'disable_zone', 'zone': zone}
    return crypt_request("http://dnspub02.prd.srv.tca.ar.internal:5000/",data, BIND_KEY)

def raw(data):
    crypt_request("http://dnspub02.prd.srv.tca.ar.internal:5000/", data, BIND_KEY)

def update_zone(zone, action, record, record_type, record_value, ttl, zviews):
    data = {'request': 'update_zone', 'zone': zone,
            'action': action, 'record': record,
            'record_type': record_type,
            'record_value': record_value, 'ttl': ttl,
            'view': zviews}
    return crypt_request("http://dnspub02.prd.srv.tca.ar.internal:5000/", data, BIND_KEY)

def print_menu():
    print '1- show zones'
    print '1.1 - show zone'
    print '2- add zone'
    print '3- del zone'
    print '4- enable zone'
    print '5- disable zone'
    print '6- add zone'
    print '7- del zone'
    print '8- raw'
    print 'q- quit'
    
def display_output(headers, rows):
    table = PrettyTable(headers)
    table.align = "l"
    for i in rows:
        for o in headers: i.setdefault(o, "")
        table.add_row([i[o] for o in headers])
    print (table)

def rand_name():
    txt = [random.choice(string.lowercase) for i in range(10)]
    txt = ''.join(txt)
    return txt

def run_option(option):
    data = None
    if option == '1':
        data = show_zones()
        headers = ['zone', 'view', 'type', 'masters', 'file']
        rows = []
        for i in data['data']['zones']:
            rows.append(i)
        display_output(headers, rows)
    elif option == '1.1':
        zone = raw_input('zone name: ')
        data = show_zone(zone)
    elif option == '2':
        zone = raw_input('zone name: ')
        master = raw_input('master (y/n): ')
        if master == 'y':
            master = True
        else:
            master = False
            master_host = raw_input('master host: ')
        data = add_zone(zone, master, master_host)
    elif option == '3':
        zone = raw_input('zone name: ')
        data = del_zone(zone)
    elif option == '4':
        zone = raw_input('zone name: ')
        data = enabled_zone(zone)
    elif option == '5':
        zone = raw_input('zone name: ')
        data = disable_zone(zone)
    elif option == '6':
        # zone = raw_input('zone name: ')
        # action = raw_input('action: ')
        record = raw_input('record: ')
        # record_type = raw_input('record type: ').upper()
        # record_value = raw_input('record value: ')
        # ttl = raw_input('ttl: ')
        # zviews = raw_input('view: ')
        # zone, action, record, record_type, record_value, ttl, zviews = ('stocalini.com', 'add', rand_name(), 'A', '192.168.0.122', '3600', 'public')
        # data = update_zone(zone, action, record, record_type, record_value, ttl, zviews)
    elif option == '7':
        # zone = raw_input('zone name: ')
        # action = raw_input('action: ')
        record = raw_input('record: ')
        # record_type = raw_input('record type: ').upper()
        # record_value = raw_input('record value: ')
        # ttl = raw_input('ttl: ')
        # zviews = raw_input('view: ')
        # zone, action,  record_type, record_value, ttl, zviews = ('stocalini.com', 'del', 'A', '192.168.0.122', '3600', 'public')
        # data = update_zone(zone, action, record, record_type, record_value, ttl, zviews)
    elif option == 'q':
        sys.exit()
    return data

def main():
    data = ''
    while True:
        os.system('clear')
        print_menu()
        if isinstance(data, str):
            print data
        else:
            pprint.pprint(data)
        option = raw_input('select option: ')
        data = run_option(option)
        cont = raw_input('Press any key to continue.')

if __name__ == '__main__':
    if '-c' in sys.argv:
        params = sys.argv[sys.argv.index('-c') + 1]
        if params.startswith('addzone'):
            opt = params.split()
            if len(opt) > 2:
                add_zone(opt[1], False, opt[2])
    else:
        main()
