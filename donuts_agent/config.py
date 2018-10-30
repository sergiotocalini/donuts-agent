#!/usr/bin/env python
import os

class Config(object):
    BIND = '0.0.0.0'
    PORT = 5000
    DEBUG = False
    CSRF_ENABLED = True
    SECRET_KEY = 'r43r8fdj3290121p454yhyf!'
    APPLICATION_ROOT = '/donuts-agent'
    APP_PATH = os.path.dirname(os.path.abspath(__file__))
    PATH_BIN = '/usr/bin'
    PATH_SBIN = '/usr/sbin'
    PATH_CONF = '/etc/named'
    PATH_CHECKCONF = '%s/named-checkconf' %PATH_SBIN
    PATH_RNDC = '%s/rndc' %PATH_SBIN
    PATH_NSUPDATE = '%s/nsupdate' %PATH_BIN
    BIND_CONF = {
        'key': '%s/keys/updates.key' %PATH_CONF,
        'backup': '%s/backups' %PATH_CONF,
        'path': {
            'named-checkconf':'%s/named-checkconf' %PATH_SBIN,
            'rndc': '%s/rndc' %PATH_SBIN, 'nsupdate':'%s/nsupdate' %PATH_BIN
        },
        'databases': {
            'private': '%s/databases/private' %PATH_CONF,
            'public': '%s/databases/public' %PATH_CONF
        },
        'zones': {
            'available': {
                'public':'%s/zones-available/public' %PATH_CONF,
                'private':'%s/zones-available/private' %PATH_CONF
            },
            'enabled': {
                'public': '%s/zones-enabled/public' %PATH_CONF,
                'private': '%s/zones-enabled/private' %PATH_CONF
            },
            'activated': {
                'public': '%s/conf.d/zones_public.conf' %PATH_CONF,
                'private': '%s/conf.d/zones_private.conf' %PATH_CONF
            }
        },
        'templates': {
            'database': '%s/templates/db.ZONE' %APP_PATH,
            'zones': {
                'slave': '%s/templates/ZONE.slave.conf' %APP_PATH,
                'master': '%s/templates/ZONE.conf' %APP_PATH
            }
        }
    }
    BIND_KEY = '%s/keys/updates.key' %PATH_CONF
    BIND_ZONES = {
        'public': '%s/conf.d/zones_public.conf' %PATH_CONF,
        'private': '%s/conf.d/zones_private.conf' %PATH_CONF
    }
    BIND_ZONES_DB = {
        'private': '%s/databases/private/' %PATH_CONF,
        'public': '%s/databases/public/' %PATH_CONF
    }
    BIND_ZONES_AVAILABLE = {
        'public': '%s/zones-available/public/' %PATH_CONF,
        'private': '%s/zones-available/private/' %PATH_CONF
    }
    BIND_ZONES_ENABLED = {
        'public': '%s/zones-enabled/public/' %PATH_CONF,
        'private': '%s/zones-enabled/private/' %PATH_CONF
    }
    BIND_ZONES_BACKUP = '%s/backups/' %PATH_CONF

class Development(Config):
    DEBUG = True

class Production(Config):
    DEBUG = False
    
class Debian(Config):
    PATH_BIN = '/usr/bin'
    PATH_SBIN = '/usr/sbin'
    PATH_CONF = '/etc/bind'
    PATH_CHECKCONF = '%s/named-checkconf' %PATH_SBIN
    PATH_RNDC = '%s/rndc' %PATH_SBIN
    PATH_NSUPDATE = '%s/nsupdate' %PATH_BIN
    BIND_CONF = {
        'key': '%s/keys/updates.key' %PATH_CONF,
        'backup': '%s/backups' %PATH_CONF,
        'path': {
            'named-checkconf':'%s/named-checkconf' %PATH_SBIN,
            'rndc': '%s/rndc' %PATH_SBIN, 'nsupdate':'%s/nsupdate' %PATH_BIN
        },
        'databases': {
            'private': '%s/databases/private' %PATH_CONF,
            'public': '%s/databases/public' %PATH_CONF
        },
        'zones': {
            'available': {
                'public':'%s/zones-available/public' %PATH_CONF,
                'private':'%s/zones-available/private' %PATH_CONF
            },
            'enabled': {
                'public': '%s/zones-enabled/public' %PATH_CONF,
                'private': '%s/zones-enabled/private' %PATH_CONF
            },
            'activated': {
                'public': '%s/conf.d/zones_public.conf' %PATH_CONF,
                'private': '%s/conf.d/zones_private.conf' %PATH_CONF
            }
        },
        'templates': {
            'database': '%s/templates/db.ZONE' %APP_PATH,
            'zones': {
                'slave': '%s/templates/ZONE.slave.conf' %APP_PATH,
                'master': '%s/templates/ZONE.conf' %APP_PATH
            }
        }
    }
    BIND_KEY = '%s/keys/updates.key' %PATH_CONF
    BIND_ZONES = {
        'public': '%s/conf.d/zones_public.conf' %PATH_CONF,
        'private': '%s/conf.d/zones_private.conf' %PATH_CONF
    }
    BIND_ZONES_DB = {
        'private': '%s/databases/private/' %PATH_CONF,
        'public': '%s/databases/public/' %PATH_CONF
    }
    BIND_ZONES_AVAILABLE = {
        'public': '%s/zones-available/public/' %PATH_CONF,
        'private': '%s/zones-available/private/' %PATH_CONF
    }
    BIND_ZONES_ENABLED = {
        'public': '%s/zones-enabled/public/' %PATH_CONF,
        'private': '%s/zones-enabled/private/' %PATH_CONF
    }
    BIND_ZONES_BACKUP = '%s/backups/' %PATH_CONF

