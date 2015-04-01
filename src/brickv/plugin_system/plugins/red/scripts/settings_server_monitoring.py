#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import json
import stat
import socket
import argparse
from pynag import Model
from sys import argv
from time import sleep
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_ptc import BrickletPTC
from tinkerforge.bricklet_temperature import BrickletTemperature
from tinkerforge.bricklet_humidity import BrickletHumidity
from tinkerforge.bricklet_ambient_light import BrickletAmbientLight

if len(argv) < 2:
    exit(1)

FILE_PATH_CHECK_SCRIPT   = '/usr/local/bin/check_tinkerforge.py'
FILE_PATH_TF_NAGIOS_CONFIGURATION = '/etc/nagios3/conf.d/tinkerforge.cfg'

SCRIPT_TINKERFORGE_CHECK = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
#
# Author: Christopher Dove
# Website: http://www.dove-online.de
# Date: 07.05.2013
#

import time
import argparse 
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_ptc import BrickletPTC
from tinkerforge.bricklet_temperature import BrickletTemperature
from tinkerforge.bricklet_humidity import BrickletHumidity
from tinkerforge.bricklet_ambient_light import BrickletAmbientLight

OK       = 0
WARNING  = 1
CRITICAL = 2
UNKNOWN  = -1

BRICKLET_PTC24         = 'ptc24'
BRICKLET_PTC3          = 'ptc3'
BRICKLET_TEMPERATURE   = 'temperature'
BRICKLET_HUMIDITY      = 'humidity'
BRICKLET_AMBIENT_LIGHT = 'ambient_light'

WIRE_MODE_PTC24 = 2
WIRE_MODE_PTC3  = 3

class CheckTinkerforge(object):
    def __init__(self, args):
        self.args   = args
        self.ipcon  = IPConnection()

    def handle_result(self, message, return_code):
        self.disconnect()
        print message
        raise SystemExit, return_code

    def cb_connect(self, connect_reason):
        if self.args.secret:
            try:
                self.ipcon.authenticate(self.args.secret)
            except:
                self.handle_result('CRITICAL - Connection Authentication failed',
                                   CRITICAL)

        self.read(self.args.bricklet,
                  self.args.uid,
                  self.args.warning,
                  self.args.critical,
                  self.args.warning2,
                  self.args.critical2)

    def connect(self):
        try:
            self.ipcon.register_callback(IPConnection.CALLBACK_CONNECTED, self.cb_connect)
            self.ipcon.connect(self.args.host, self.args.port)
            time.sleep(1)
        except:
            self.handle_result('CRITICAL - Error occured while connecting',
                               CRITICAL)

    def disconnect(self):
        try:
            self.ipcon.disconnect()
        except:
            pass

    def read(self, bricklet, uid, warning, critical, warning2, critical2):
        if bricklet == BRICKLET_PTC24 or bricklet == BRICKLET_PTC3:
            bricklet_ptc = BrickletPTC(uid, self.ipcon)

            try:
                if not bricklet_ptc.is_sensor_connected():
                    self.handle_result('CRITICAL - No PTC sensor connected',
                                       CRITICAL)
            except:
                self.handle_result('CRITICAL - Error getting PTC sensor connection state',
                                   CRITICAL)

            try:
                if bricklet == BRICKLET_PTC24:
                    bricklet_ptc.set_wire_mode(WIRE_MODE_PTC24)
                elif bricklet == BRICKLET_PTC3:
                    bricklet_ptc.set_wire_mode(WIRE_MODE_PTC3)
            except:
                self.handle_result('CRITICAL - Error setting PTC wire mode',
                                   CRITICAL)

            try:
                reading = bricklet_ptc.get_temperature() / 100.0
            except:
                self.handle_result('CRITICAL - Error reading value',
                                   CRITICAL)

        elif bricklet == BRICKLET_TEMPERATURE:
            bricklet_temperature = BrickletTemperature(uid, self.ipcon)

            try:
                reading = bricklet_temperature.get_temperature() / 100.0
            except:
                self.handle_result('CRITICAL - Error reading value',
                                   CRITICAL)

        elif bricklet == BRICKLET_HUMIDITY:
            bricklet_humidity = BrickletHumidity(uid, self.ipcon)

            try:
                reading = bricklet_humidity.get_humidity() / 10.0
            except:
                self.handle_result('CRITICAL - Error reading value',
                                   CRITICAL)

        elif bricklet == BRICKLET_AMBIENT_LIGHT:
            bricklet_ambient_light = BrickletAmbientLight(uid, self.ipcon)

            try:
                reading = bricklet_ambient_light.get_illuminance() / 10.0
            except:
                self.handle_result('CRITICAL - Error reading value',
                                   CRITICAL)

        if reading >= critical:
            self.handle_result('CRITICAL - Reading too high - %s' % reading,
                               CRITICAL)
        elif reading >= warning:
            self.handle_result('WARNING - Reading is high - %s' % reading,
                               WARNING)
        elif reading <= critical2:
            self.handle_result('CRITICAL - Reading too low - %s' % reading,
                               CRITICAL)
        elif reading <= warning2:
            self.handle_result('WARNING - Reading is low - %s' % reading,
                               WARNING)
        elif reading > warning2 and reading < warning:
            self.handle_result('OK - %s' % reading,
                               OK)
        else:
            self.handle_result('UNKNOWN - Unknown state', UNKNOWN)

if __name__ == '__main__':
    # Create connection and connect to brickd
    parse = argparse.ArgumentParser()
    
    parse.add_argument('-H',
                       '--host',
                       help = 'Host (default = localhost)',
                       required = True)

    parse.add_argument('-P',
                       '--port',
                       help = 'Port (default = 4223)',
                       type = int,
                       required = True)

    parse.add_argument('-S',
                       '--secret',
                       help = 'Secret (default = None)',
                       type = str,
                       default = None)

    parse.add_argument('-b',
                       '--bricklet',
                       help = 'Type of bricklet',
                       type = str,
                       choices = ['ptc24', 'ptc3', 'temperature', 'humidity', 'ambient_light'],
                       required = True)

    parse.add_argument('-u',
                       '--uid',
                       help = 'UID of bricklet',
                       required = True)
        
    parse.add_argument('-w',
                       '--warning',
                       help = 'Warning temperature level \
                               (temperatures above this level will trigger a warning \
                               message)',
                       type = float,
                       required = True)
    
    parse.add_argument('-c',
                       '--critical',
                       help = 'Critical temperature level \
                               (temperatures above this level will trigger a critical \
                               message)',
                       type = float,
                       required = True)
    
    parse.add_argument('-w2',
                       '--warning2',
                       help = 'Warning temperature level (temperatures \
                               below this level will trigger a warning message)',
                       type = float,
                       required = True)
    
    parse.add_argument('-c2',
                       '--critical2',
                       help = 'Critical temperature level (temperatures below \
                               this level will trigger a critical message)',
                       type = float,
                       required = True)
 
    args = parse.parse_args()

    service = CheckTinkerforge(args)

    service.connect()
'''

TEMPLATE_COMMAND_LINE_NOTIFY_HOST = '''/usr/bin/printf "%b" "***** Nagios *****\\n\\n \
Notification Type: $NOTIFICATIONTYPE$\\n \
Host: $HOSTNAME$\\n \
State: $HOSTSTATE$\\n \
Address: $HOSTADDRESS$\\n \
Info: $HOSTOUTPUT$\\n\\n \
Date/Time: $LONGDATETIME$\\n" | \
/usr/bin/sendemail \
-f {0} \
-t {1} \
-u "** $NOTIFICATIONTYPE$ Host Alert: $HOSTNAME$ is $HOSTSTATE$ **" \
-s {2}:{3} \
-o username={4} \
-o password={5} \
-o tls={6}'''

TEMPLATE_COMMAND_LINE_NOTIFY_SERVICE = '''/usr/bin/printf "%b" "***** Nagios *****\\n\\n \
Notification Type: $NOTIFICATIONTYPE$\\n\\n \
Service: $SERVICEDESC$\\n \
Host: $HOSTALIAS$\\n \
Address: $HOSTADDRESS$\\n \
State: $SERVICESTATE$\\n\\n \
Date/Time: $LONGDATETIME$\\n\\n \
Additional Info:\\n\\n$SERVICEOUTPUT$\\n" | \
/usr/bin/sendemail \
-f {0} \
-t {1} \
-u "** $NOTIFICATIONTYPE$ Service Alert: $HOSTALIAS$/$SERVICEDESC$ is $SERVICESTATE$ **" \
-s {2}:{3} \
-o username={4} \
-o password={5} \
-o tls={6}'''

ACTION = argv[1]

ipcon  = None
host   = None
port   = None
secret = None

dict_enumerate = {'host'         : None,
                  'port'         : None,
                  'secret'       : None,
                  'ptc'          : [],
                  'temperature'  : [],
                  'humidity'     : [],
                  'ambient_light': []}

def ignore_enumerate_fail():
    dict_enumerate['host']          = host
    dict_enumerate['port']          = port
    dict_enumerate['secret']        = secret
    dict_enumerate['ptc']           = []
    dict_enumerate['temperature']   = []
    dict_enumerate['humidity']      = []
    dict_enumerate['ambient_light'] = []
    sys.stdout.write(json.dumps(dict_enumerate))

def cb_connect(connect_reason, secret):
    if not ipcon:
        ignore_enumerate_fail()
        exit(0)

    if secret:
        try:
            ipcon.authenticate(secret)
        except:
            ignore_enumerate_fail()
            exit(0)

    ipcon.enumerate()

def cb_enumerate(uid,
                 connected_uid,
                 position,
                 hardware_version,
                 firmware_version,
                 device_identifier,
                 enumeration_type,
                 host,
                 port,
                 secret):

    if not ipcon:
        ignore_enumerate_fail()
        exit(0)

    if device_identifier == BrickletPTC.DEVICE_IDENTIFIER:
        dict_enumerate['ptc'].append(uid)

    elif device_identifier == BrickletTemperature.DEVICE_IDENTIFIER:
        dict_enumerate['temperature'].append(uid)

    elif device_identifier == BrickletHumidity.DEVICE_IDENTIFIER:
        dict_enumerate['humidity'].append(uid)

    elif device_identifier == BrickletAmbientLight.DEVICE_IDENTIFIER:
        dict_enumerate['ambient_light'].append(uid)

if ACTION == 'GET':
    try:
        dict_return = {}
        list_rules  = []
        dict_email  = {}

        dict_return['rules'] = None
        dict_return['email'] = None
        dict_return['hosts'] = {}

        for command in Model.Command.objects.filter(command_name__startswith = 'tinkerforge-command-'):
            for service in Model.Service.objects.filter(check_command = command.command_name):
                parse = argparse.ArgumentParser()

                parse.add_argument('-H')
                parse.add_argument('-P')
                parse.add_argument('-S')
                parse.add_argument('-b')
                parse.add_argument('-u')
                parse.add_argument('-m')
                parse.add_argument('-w')
                parse.add_argument('-c')
                parse.add_argument('-w2')
                parse.add_argument('-c2')

                map_args = parse.parse_args(command.command_line.split('/usr/local/bin/check_tinkerforge.py ')[1].split(' '))

                a_rule = {'name'                      : service.service_description,
                          'host'                      : map_args.H,
                          'bricklet'                  : map_args.b,
                          'uid'                       : map_args.u,
                          'warning_low'               : map_args.w2,
                          'warning_high'              : map_args.w,
                          'critical_low'              : map_args.c2,
                          'critical_high'             : map_args.c,
                          'email_notification_enabled': service.notifications_enabled,
                          'email_notifications'       : service.notification_options}

                list_rules.append(a_rule)

                if not map_args.S:
                    secret = ''
                else:
                    secret = map_args.S

                if map_args.H not in dict_return['hosts']:
                    dict_return['hosts'][map_args.H] = {'port':map_args.P, 'secret':secret}

        for command in Model.Command.objects.filter(command_name = 'tinkerforge-notify-service-by-email'):
            delims = ['-f ',
                      '-t ',
                      '-s ',
                      '-o username=',
                      '-o password=',
                      '-o tls=']

            for d in delims:
                partitioned = command.command_line.partition(d)

                if len(partitioned) != 3:
                    break

                if d == '-f ':
                    dict_email['from'] = partitioned[2].partition(' ')[0]
                elif d == '-t ':
                    dict_email['to'] = partitioned[2].partition(' ')[0]
                elif d == '-s ':
                    server_port = partitioned[2].partition(' ')[0].split(':')
                    dict_email['server'] = server_port[0]
                    dict_email['port']   = server_port[1]
                elif d == '-o username=':
                    dict_email['username'] = partitioned[2].partition(' ')[0]
                elif d == '-o password=':
                    dict_email['password'] = partitioned[2].partition(' ')[0]
                elif d == '-o tls=':
                    dict_email['tls'] = partitioned[2].partition(' ')[0]

        if len(list_rules) > 0:
            dict_return['rules'] = list_rules

        if len(dict_email) == 7:
            dict_return['email'] = dict_email

        sys.stdout.write(json.dumps(dict_return))
    except:
        exit(1)

elif ACTION == 'APPLY':
    try:
        if len(argv) < 3:
            exit(1)

        apply_dict = json.loads(argv[2])

        with open(FILE_PATH_CHECK_SCRIPT, 'w') as fh_cs:
            fh_cs.write(SCRIPT_TINKERFORGE_CHECK)

        os.chmod(FILE_PATH_CHECK_SCRIPT,
                 stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH | \
                 stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

        if os.path.isfile(FILE_PATH_TF_NAGIOS_CONFIGURATION):
            os.remove(FILE_PATH_TF_NAGIOS_CONFIGURATION)

        for rule in apply_dict['rules']:
            tf_command = Model.Command()
            tf_service = Model.Service()
            tf_command.set_filename(FILE_PATH_TF_NAGIOS_CONFIGURATION)
            tf_service.set_filename(FILE_PATH_TF_NAGIOS_CONFIGURATION)
            tf_command.command_name = rule['check_command']
            tf_command.command_line = rule['command_line']
            tf_service.use                      = 'generic-service'
            tf_service.host_name                = 'localhost'
            tf_service.service_description      = rule['service_description']
            tf_service.check_command            = rule['check_command']
            tf_service.max_check_attempts       = '4'
            tf_service.check_interval           = '1'
            tf_service.retry_interval           = '1'
            tf_service.check_period             = '24x7'
            tf_service.notification_interval    = '5'
            tf_service.first_notification_delay = '0'
            tf_service.notification_period      = '24x7'
            tf_service.notification_options     = rule['notification_options']
            tf_service.notifications_enabled    = rule['notifications_enabled']
            tf_service.contact_groups           = rule['contact_groups']
            tf_command.save()
            tf_service.save()

        if apply_dict['email']:
            tf_command_notify_service = Model.Command()
            tf_command_notify_host    = Model.Command()
            tf_contact                = Model.Contact()
            tf_contact_group          = Model.Contactgroup()
            tf_command_notify_service.set_filename(FILE_PATH_TF_NAGIOS_CONFIGURATION)
            tf_command_notify_host.set_filename(FILE_PATH_TF_NAGIOS_CONFIGURATION)
            tf_contact.set_filename(FILE_PATH_TF_NAGIOS_CONFIGURATION)
            tf_contact_group.set_filename(FILE_PATH_TF_NAGIOS_CONFIGURATION)
            tf_command_notify_service.command_name = 'tinkerforge-notify-service-by-email'
            tf_command_notify_service.command_line = TEMPLATE_COMMAND_LINE_NOTIFY_SERVICE.format(apply_dict['email']['from'],
                                                                                                 apply_dict['email']['to'],
                                                                                                 apply_dict['email']['server'],
                                                                                                 apply_dict['email']['port'],
                                                                                                 apply_dict['email']['username'],
                                                                                                 apply_dict['email']['password'],
                                                                                                 apply_dict['email']['tls'])
            tf_command_notify_host.command_name = 'tinkerforge-notify-host-by-email'
            tf_command_notify_host.command_line = TEMPLATE_COMMAND_LINE_NOTIFY_HOST.format(apply_dict['email']['from'],
                                                                                           apply_dict['email']['to'],
                                                                                           apply_dict['email']['server'],
                                                                                           apply_dict['email']['port'],
                                                                                           apply_dict['email']['username'],
                                                                                           apply_dict['email']['password'],
                                                                                           apply_dict['email']['tls'])
            tf_contact.contact_name                  = 'tinkerforge-contact'
            tf_contact.host_notifications_enabled    = '0'
            tf_contact.service_notifications_enabled = '1'
            tf_contact.host_notification_period      = '24x7'
            tf_contact.service_notification_period   = '24x7'
            tf_contact.host_notification_options     = 'd,u,r'
            tf_contact.service_notification_options  = 'w,u,c,r'
            tf_contact.host_notification_commands    = 'tinkerforge-notify-host-by-email'
            tf_contact.service_notification_commands = 'tinkerforge-notify-service-by-email'
            tf_contact_group.contactgroup_name       = 'tinkerforge-contact-group'
            tf_contact_group.alias                   = 'Tinkerforge Contact Group'
            tf_contact_group.members                 = 'tinkerforge-contact'
            tf_command_notify_service.save()
            tf_command_notify_host.save()
            tf_contact.save()
            tf_contact_group.save()

        if os.system('/bin/systemctl restart nagios3') != 0:
            exit(1)
    except:
        exit(1)

elif ACTION == 'APPLY_EMPTY':
    try:
        if os.path.isfile(FILE_PATH_CHECK_SCRIPT):
            os.remove(FILE_PATH_CHECK_SCRIPT)

        if os.path.isfile(FILE_PATH_TF_NAGIOS_CONFIGURATION):
            os.remove(FILE_PATH_TF_NAGIOS_CONFIGURATION)

        if os.system('/bin/systemctl restart nagios3') != 0:
            exit(1)
    except:
        exit(1)

elif ACTION == 'GET_LOCALHOST':
    try:
        hostname = unicode(socket.gethostname())

        if hostname:
            sys.stdout.write(hostname)
        else:
            exit(1)
    except:
        exit(1)

elif ACTION == 'ENUMERATE':
    try:
        if len(argv) < 5:
            exit(1)

        host   = argv[2]
        port   = argv[3]
        secret = argv[4]

        dict_enumerate['host']   = host
        dict_enumerate['port']   = port
        dict_enumerate['secret'] = secret

        ipcon = IPConnection()
        ipcon.register_callback(IPConnection.CALLBACK_CONNECTED, lambda connect_reason: cb_connect(connect_reason, secret))
        ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE, lambda uid,
                                                                        connected_uid,
                                                                        position,
                                                                        hardware_version,
                                                                        firmware_version,
                                                                        device_identifier,
                                                                        enumeration_type: cb_enumerate(uid,
                                                                                                       connected_uid,
                                                                                                       position,
                                                                                                       hardware_version,
                                                                                                       firmware_version,
                                                                                                       device_identifier,
                                                                                                       enumeration_type,
                                                                                                       host,
                                                                                                       port,
                                                                                                       secret))
        ipcon.connect(host, int(port))
        sleep(1)
    except:
        pass
else:
    exit(1)

if ACTION == 'ENUMERATE':
    if ipcon:
        try:
            ipcon.disconnect()
        except:
            pass

    sys.stdout.write(json.dumps(dict_enumerate))
