#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import json
import stat
import argparse
from pynag import Model
from sys import argv


FILE_PATH_CONTACTS       = '/etc/nagios3/conf.d/tinkerforge_contacts.cfg'
FILE_PATH_COMMANDS       = '/etc/nagios3/conf.d/tinkerforge_commands.cfg'
FILE_PATH_SERVICES       = '/etc/nagios3/conf.d/tinkerforge_services.cfg'
FILE_PATH_CHECK_SCRIPT   = '/usr/local/bin/check_tinkerforge.py'

SCRIPT_TINKERFORGE_CHECK = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
#
# Author: Christopher Dove
# Website: http://www.dove-online.de
# Date: 07.05.2013
#

import argparse 
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_temperature import Temperature
from tinkerforge.bricklet_humidity import Humidity

OK       = 0
WARNING  = 1
CRITICAL = 2
UNKNOWN  = -1

BRICKLET_TEMPERATURE = 'temperature'
BRICKLET_HUMIDITY    = 'humidity'

class TinkerforgeNagiosService(object):
    def __init__(self, host = 'localhost', port = 4223):
        self.host = host
        self.port = port
        self.ipcon = IPConnection()
 
    def connect(self):
        self.ipcon.connect(self.host, self.port)
 
    def disconnect(self):
        self.ipcon.disconnect()
 
    def read(self, bricklet, uid, warning, critical, mode = 'high', warning2 = 0, critical2 = 0):

        if bricklet == BRICKLET_TEMPERATURE:
            bricklet_temperature = Temperature(uid, self.ipcon)
            reading = bricklet_temperature.get_temperature() / 100.0

        elif bricklet == BRICKLET_HUMIDITY:
            bricklet_humidity = Humidity(uid, self.ipcon)
            reading = bricklet_humidity.get_humidity() / 10.0

        if mode == 'high':
            if reading >= critical:
                print 'CRITICAL - Reading too high - %s' % reading
                raise SystemExit, CRITICAL
            elif reading >= warning:
                print 'WARNING - Reading is high - %s' % reading
                raise SystemExit, WARNING
            elif reading < warning:
                print 'OK - %s' % reading
                raise SystemExit, OK
            else:
                print 'UNKOWN - Unknown reading'
                raise SystemExit, UNKNOWN

        elif mode == 'low':
            if reading <= critical:
                print 'CRITICAL - Reading too low - %s' % reading
                raise SystemExit, CRITICAL
            elif reading <= warning:
                print 'WARNING - Reading is low - %s' % reading
                raise SystemExit, WARNING
            elif reading > warning:
                print 'OK - %s' % reading
                raise SystemExit, OK
            else:
                print 'UNKOWN - Unknown reading'
                raise SystemExit, UNKNOWN

        elif mode == 'range':
            if reading >= critical:
                print 'CRITICAL - Reading too high - %s' % reading
                raise SystemExit, CRITICAL
            elif reading >= warning:
                print 'WARNING - Reading is high - %s' % reading
                raise SystemExit, WARNING
            elif reading <= critical2:
                print 'CRITICAL - Reading too low - %s' % reading
                raise SystemExit, CRITICAL
            elif reading <= warning2:
                print 'WARNING - Reading is low - %s' % reading
                raise SystemExit, WARNING
            elif reading > warning2 and reading < warning:
                print 'OK - %s' % reading
                raise SystemExit, OK
            else:
                print 'UNKOWN - Unknown reading'
                raise SystemExit, UNKNOWN
 
if __name__ == '__main__':
    # Create connection and connect to brickd
    parse = argparse.ArgumentParser()
    
    parse.add_argument('-H',
                       '--host',
                       help = 'Host (default = localhost)',
                       default = 'localhost')
    
    parse.add_argument('-P',
                       '--port',
                       help = 'Port (default = 4223)',
                       type = int,
                       default = 4223)
    
    parse.add_argument('-b',
                       '--bricklet',
                       help = 'Type of bricklet',
                       type = str,
                       required = True,
                       choices = ['temperature', 'humidity'])

    parse.add_argument('-u',
                       '--uid',
                       help = 'UID of bricklet',
                       required = True)
    
    parse.add_argument('-m',
                       '--mode',
                       help = 'Mode: high (default), low or range',
                       type = str,
                       choices = ['high', 'low', 'range'],
                       default = 'high')
    
    parse.add_argument('-w',
                       '--warning',
                       help = 'Warning temperature level \
                               (temperatures above this level will trigger a warning \
                               message in high mode,temperature below this level will \
                               trigger a warning message in low mode)',
                       required = True,
                       type = float)
    
    parse.add_argument('-c',
                       '--critical',
                       help = 'Critical temperature level \
                               (temperatures above this level will trigger a critical \
                               message in high mode, temperature below this level will \
                               trigger a critical message in low mode)',
                       required=True,
                       type = float)
    
    parse.add_argument('-w2',
                       '--warning2',
                       help = 'Warning temperature level (temperatures \
                               below this level will trigger a warning message \
                               in range mode)',
                       type = float)
    
    parse.add_argument('-c2',
                       '--critical2',
                       help = 'Critical temperature level (temperatures below \
                               this level will trigger a critical message in range mode)',
                       type = float)
 
    args = parse.parse_args()

    service = TinkerforgeNagiosService(args.host, args.port)

    service.connect()

    service.read(args.bricklet,
                 args.uid,
                 args.warning,
                 args.critical,
                 args.mode,
                 args.warning2,
                 args.critical2)
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

if len(argv) < 2:
    exit (1)

ACTION = argv[1]

try:
    if ACTION == 'GET':
        dict_return = {}
        list_rules  = []
        dict_email  = {}

        dict_return['rules'] = None
        dict_return['email'] = None

        for command in Model.Command.objects.filter(command_name__startswith = 'tinkerforge_command_'):
            for service in Model.Service.objects.filter(check_command = command.command_name):
                parse = argparse.ArgumentParser()

                parse.add_argument('-b')
                parse.add_argument('-u')
                parse.add_argument('-m')
                parse.add_argument('-w')
                parse.add_argument('-c')
                parse.add_argument('-w2')
                parse.add_argument('-c2')

                map_args = parse.parse_args(command.command_line.split('/usr/local/bin/check_tinkerforge.py ')[1].split(' '))

                a_rule = {'name'                      : service.service_description,
                          'bricklet'                  : map_args.b,
                          'uid'                       : map_args.u,
                          'warning_low'               : map_args.w2,
                          'warning_high'              : map_args.w,
                          'critical_low'              : map_args.c2,
                          'critical_high'             : map_args.c,
                          'email_notification_enabled': service.notifications_enabled,
                          'email_notifications'       : service.notification_options}

                list_rules.append(a_rule)

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

    elif ACTION == 'APPLY':
        if len(argv) < 3:
            exit (1)

        apply_dict = json.loads(argv[2])

        if os.path.isfile(FILE_PATH_CONTACTS):
            os.remove(FILE_PATH_CONTACTS)

        if os.path.isfile(FILE_PATH_COMMANDS):
            os.remove(FILE_PATH_COMMANDS)

        if os.path.isfile(FILE_PATH_SERVICES):
            os.remove(FILE_PATH_SERVICES)

        with open(FILE_PATH_CHECK_SCRIPT, 'w') as fh_ns:
            fh_ns.write(SCRIPT_TINKERFORGE_CHECK)

        os.chmod(FILE_PATH_CHECK_SCRIPT,
                 stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH | \
                 stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

        for rule in apply_dict['rules']:
            tf_command = Model.Command()
            tf_service = Model.Service()
            tf_command.set_filename(FILE_PATH_COMMANDS)
            tf_service.set_filename(FILE_PATH_SERVICES)

            tf_command.command_name = rule['check_command']
            tf_command.command_line = rule['command_line']

            tf_service.host_name                = 'localhost'
            tf_service.service_description      = rule['service_description']
            tf_service.check_command            = rule['check_command']
            tf_service.max_check_attempts       = '10'
            tf_service.check_interval           = '1'
            tf_service.retry_interval           = '1'
            tf_service.check_period             = '24x7'
            tf_service.notification_interval    = '5'
            tf_service.first_notification_delay = '0'
            tf_service.notification_period      = '24x7'
            tf_service.notification_options     = rule['notification_options']
            tf_service.notifications_enabled    = rule['notifications_enabled']
            tf_service.contacts                 = rule['contacts']

            tf_command.save()
            tf_service.save()

        if apply_dict['email']:
            tf_contact                = Model.Contact()
            tf_command_notify_service = Model.Command()
            tf_command_notify_host    = Model.Command()

            tf_contact.set_filename(FILE_PATH_CONTACTS)
            tf_command_notify_service.set_filename(FILE_PATH_COMMANDS)
            tf_command_notify_host.set_filename(FILE_PATH_COMMANDS)

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

            tf_contact.contact_name                  = 'tinkerforge_contact'
            tf_contact.alias                         = 'Tinkerforge Contact'
            tf_contact.host_notifications_enabled    = '0'
            tf_contact.service_notifications_enabled = '1'
            tf_contact.host_notification_period      = '24x7'
            tf_contact.service_notification_period   = '24x7'
            tf_contact.host_notification_options     = 'd,u,r,f,s,n'
            tf_contact.service_notification_options  = 'w,u,c,r,f,s,n'
            tf_contact.host_notification_commands    = 'tinkerforge-notify-host-by-email'
            tf_contact.service_notification_commands = 'tinkerforge-notify-service-by-email'
            tf_contact.email                         = apply_dict['email']['to']

            tf_command_notify_service.save()
            tf_command_notify_host.save()
            tf_contact.save()
 
        if os.system('/bin/systemctl restart nagios3') != 0:
            exit(1)

    elif ACTION == 'APPLY_EMPTY':
        if os.path.isfile(FILE_PATH_CONTACTS):
            os.remove(FILE_PATH_CONTACTS)

        if os.path.isfile(FILE_PATH_COMMANDS):
            os.remove(FILE_PATH_COMMANDS)

        if os.path.isfile(FILE_PATH_SERVICES):
            os.remove(FILE_PATH_SERVICES)

        if os.path.isfile(FILE_PATH_CHECK_SCRIPT):
            os.remove(FILE_PATH_CHECK_SCRIPT)
        
        if os.system('/bin/systemctl restart nagios3') != 0:
            exit(1)
    else:
        exit(1)

except:
    exit(1)
