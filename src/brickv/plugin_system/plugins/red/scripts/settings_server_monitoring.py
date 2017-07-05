#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import stat
import shlex
import socket
import argparse
import subprocess
from pynag import Model
from sys import argv
from time import sleep
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_ptc import BrickletPTC
from tinkerforge.bricklet_temperature import BrickletTemperature
from tinkerforge.bricklet_humidity import BrickletHumidity
from tinkerforge.bricklet_ambient_light import BrickletAmbientLight

MIN_VERSION_WITH_NAGIOS4 = 2.0

try:
    from tinkerforge.bricklet_ambient_light_v2 import BrickletAmbientLightV2
    has_ambient_light_v2 = True
except ImportError:
    has_ambient_light_v2 = False

if len(argv) < 2:
    exit(1)

def get_image_version():
    image_version = ''

    with open('/etc/tf_image_version', 'r') as fh_version:
        fh_version_lines = fh_version.readlines()

        if len(fh_version_lines) > 0:
            fh_version_lines_0_split = fh_version_lines[0].split(' ')

            if len(fh_version_lines_0_split) > 0:
                image_version = fh_version_lines_0_split[0].strip()

    return image_version

IMAGE_VERSION = get_image_version()
FILE_PATH_CHECK_SCRIPT = '/usr/local/bin/check_tinkerforge.py'

if not IMAGE_VERSION or float(IMAGE_VERSION) < MIN_VERSION_WITH_NAGIOS4:
    FILE_PATH_TF_NAGIOS_CONFIGURATION = '/etc/nagios3/conf.d/tinkerforge.cfg'
else:
    FILE_PATH_TF_NAGIOS_CONFIGURATION = '/usr/local/nagios/etc/objects/tinkerforge.cfg'

SCRIPT_TINKERFORGE_CHECK = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import argparse
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_ptc import BrickletPTC
from tinkerforge.bricklet_temperature import BrickletTemperature
from tinkerforge.bricklet_humidity import BrickletHumidity
from tinkerforge.bricklet_ambient_light import BrickletAmbientLight

try:
    from tinkerforge.bricklet_ambient_light_v2 import BrickletAmbientLightV2
    has_ambient_light_v2 = True
except ImportError:
    has_ambient_light_v2 = False

RETURN_CODE_OK       = 0
RETURN_CODE_WARNING  = 1
RETURN_CODE_CRITICAL = 2
RETURN_CODE_UNKNOWN  = 3

BRICKLET_PTC24         = 'ptc24'
BRICKLET_PTC3          = 'ptc3'
BRICKLET_TEMPERATURE   = 'temperature'
BRICKLET_HUMIDITY      = 'humidity'
BRICKLET_AMBIENT_LIGHT = 'ambient_light'

WIRE_MODE_PTC24 = 2
WIRE_MODE_PTC3  = 3

MESSAGE_CRITICAL_ERROR_CONNECTING = 'CRITICAL - Error occured while connecting'
MESSAGE_CRITICAL_AUTHENTICATION_FAILED = 'CRITICAL - Connection Authentication failed'
MESSAGE_CRITICAL_NO_PTC_CONNECTED = 'CRITICAL - No PTC sensor connected'
MESSAGE_CRITICAL_ERROR_GETTING_PTC_STATE = 'CRITICAL - Error getting PTC sensor connection state'
MESSAGE_CRITICAL_ERROR_SETTING_PTC_MODE = 'CRITICAL - Error setting PTC wire mode'
MESSAGE_CRITICAL_ERROR_READING_VALUE = 'CRITICAL - Error reading value'
MESSAGE_CRITICAL_ERROR_GETTING_DEVICE_IDENTITY = 'CRITICAL - Error getting device identity'
MESSAGE_CRITICAL_ERROR_SETTING_AMBIENT_LIGHT_CONFIGURATION = 'CRITICAL - Error setting Ambient Light configuration'
MESSAGE_CRITICAL_READING_TOO_HIGH = 'CRITICAL - Reading too high - %s'
MESSAGE_CRITICAL_READING_TOO_LOW = 'CRITICAL - Reading too low - %s'
MESSAGE_WARNING_READING_IS_HIGH = 'WARNING - Reading is high - %s'
MESSAGE_WARNING_READING_IS_LOW = 'WARNING - Reading is low - %s'
MESSAGE_OK_READING = 'OK - %s'
MESSAGE_UNKNOWN_READING = 'UNKNOWN - Unknown state'

global args
global ipcon
global return_code
global return_message
args               = None
ipcon              = None
return_code        = None
return_message     = None

def handle_result(message, code):
    try:
        ipcon.disconnect()
    except:
        pass

    global return_code
    global return_message
    return_message = message
    return_code = code

def cb_connect(connect_reason):
    if args.secret:
        try:
            ipcon.authenticate(args.secret)
        except:
            handle_result(MESSAGE_CRITICAL_AUTHENTICATION_FAILED,
                          RETURN_CODE_CRITICAL)

    read(args.bricklet,
         args.uid,
         args.warning,
         args.critical,
         args.warning2,
         args.critical2)

def connect():
    try:
        ipcon.register_callback(IPConnection.CALLBACK_CONNECTED, cb_connect)
        ipcon.connect(args.host, args.port)
        time.sleep(1)
    except:
        handle_result(MESSAGE_CRITICAL_ERROR_CONNECTING,
                      RETURN_CODE_CRITICAL)

def read(bricklet, uid, warning, critical, warning2, critical2):
    reading = None

    if bricklet == BRICKLET_PTC24 or bricklet == BRICKLET_PTC3:
        bricklet_ptc = BrickletPTC(uid, ipcon)

        try:
            if not bricklet_ptc.is_sensor_connected():
                bricklet_ptc = None
                handle_result(MESSAGE_CRITICAL_NO_PTC_CONNECTED,
                              RETURN_CODE_CRITICAL)
        except:
            bricklet_ptc = None
            handle_result(MESSAGE_CRITICAL_ERROR_GETTING_PTC_STATE,
                          RETURN_CODE_CRITICAL)

        if bricklet_ptc != None:
            try:
                if bricklet == BRICKLET_PTC24:
                    bricklet_ptc.set_wire_mode(WIRE_MODE_PTC24)
                elif bricklet == BRICKLET_PTC3:
                    bricklet_ptc.set_wire_mode(WIRE_MODE_PTC3)
            except:
                bricklet_ptc = None
                handle_result(MESSAGE_CRITICAL_ERROR_SETTING_PTC_MODE,
                              RETURN_CODE_CRITICAL)

        if bricklet_ptc != None:
            try:
                reading = bricklet_ptc.get_temperature() / 100.0
            except:
                handle_result(MESSAGE_CRITICAL_ERROR_READING_VALUE,
                              RETURN_CODE_CRITICAL)

    elif bricklet == BRICKLET_TEMPERATURE:
        bricklet_temperature = BrickletTemperature(uid, ipcon)

        try:
            reading = bricklet_temperature.get_temperature() / 100.0
        except:
            handle_result(MESSAGE_CRITICAL_ERROR_READING_VALUE,
                          RETURN_CODE_CRITICAL)

    elif bricklet == BRICKLET_HUMIDITY:
        bricklet_humidity = BrickletHumidity(uid, ipcon)

        try:
            reading = bricklet_humidity.get_humidity() / 10.0
        except:
            handle_result(MESSAGE_CRITICAL_ERROR_READING_VALUE,
                          RETURN_CODE_CRITICAL)

    elif bricklet == BRICKLET_AMBIENT_LIGHT:
        bricklet_ambient_light = BrickletAmbientLight(uid, ipcon)
        divisor = 10.0

        if has_ambient_light_v2:
            device_identifier = None

            try:
                device_identifier = bricklet_ambient_light.get_identity().device_identifier
            except:
                bricklet_ambient_light = None
                handle_result(MESSAGE_CRITICAL_ERROR_GETTING_DEVICE_IDENTITY,
                              RETURN_CODE_CRITICAL)

            if device_identifier == BrickletAmbientLightV2.DEVICE_IDENTIFIER:
                bricklet_ambient_light = BrickletAmbientLightV2(uid, ipcon)
                divisor = 100.0

                try:
                    bricklet_ambient_light.set_configuration(BrickletAmbientLightV2.ILLUMINANCE_RANGE_1300LUX,
                                                             BrickletAmbientLightV2.INTEGRATION_TIME_200MS)
                except:
                    bricklet_ambient_light = None
                    handle_result(MESSAGE_CRITICAL_ERROR_SETTING_AMBIENT_LIGHT_CONFIGURATION,
                                  RETURN_CODE_CRITICAL)

        if bricklet_ambient_light != None:
            try:
                reading = bricklet_ambient_light.get_illuminance() / divisor
            except:
                handle_result(MESSAGE_CRITICAL_ERROR_READING_VALUE,
                              RETURN_CODE_CRITICAL)

    if reading != None:
        if reading >= critical:
            handle_result(MESSAGE_CRITICAL_READING_TOO_HIGH % reading,
                          RETURN_CODE_CRITICAL)
        elif reading >= warning:
            handle_result(MESSAGE_WARNING_READING_IS_HIGH % reading,
                          RETURN_CODE_WARNING)
        elif reading <= critical2:
            handle_result(MESSAGE_CRITICAL_READING_TOO_LOW % reading,
                          RETURN_CODE_CRITICAL)
        elif reading <= warning2:
            handle_result(MESSAGE_WARNING_READING_IS_LOW % reading,
                          RETURN_CODE_WARNING)
        elif reading > warning2 and reading < warning:
            handle_result(MESSAGE_OK_READING % reading,
                          RETURN_CODE_OK)
        else:
            handle_result(MESSAGE_UNKNOWN_READING, RETURN_CODE_UNKNOWN)

if __name__ == '__main__':
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
                       default = None,
                       required = False)

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

    args  = parse.parse_args()
    ipcon = IPConnection()

    if args and ipcon:
        connect()
        time.sleep(3)
        print return_message
        exit(return_code)
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

TEMPLATE_TEST_EMAIL = '''/usr/bin/sendemail \
-f {0} \
-t {1} \
-u ** RED-Brick Server Monitoring Test Email ** \
-m If you received this email message on the target email address then it means \
that the server monitoring email alert is working on the RED-Brick.\n
-s {2}:{3} \
-o username={4} \
-o password={5} \
-o tls={6}'''

ACTION = argv[1]

ipcon  = None
host   = None
port   = None
secret = None
global ignore_enumerate_failed_called
ignore_enumerate_failed_called = False

dict_enumerate = {'host'         : None,
                  'port'         : None,
                  'secret'       : None,
                  'ptc'          : [],
                  'temperature'  : [],
                  'humidity'     : [],
                  'ambient_light': []}

_find_unsafe = re.compile(r'[^\w@%+=:,./-]').search

def quote(s):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"
    if _find_unsafe(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"

def ignore_enumerate_fail():
    global ignore_enumerate_failed_called
    ignore_enumerate_failed_called = True

    if ipcon:
        try:
            ipcon.disconnect()
        except:
            pass

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

    if device_identifier == BrickletPTC.DEVICE_IDENTIFIER and\
       uid not in dict_enumerate['ptc']:
            dict_enumerate['ptc'].append(uid)

    elif device_identifier == BrickletTemperature.DEVICE_IDENTIFIER and\
         uid not in dict_enumerate['temperature']:
            dict_enumerate['temperature'].append(uid)

    elif device_identifier == BrickletHumidity.DEVICE_IDENTIFIER and\
         uid not in dict_enumerate['humidity']:
            dict_enumerate['humidity'].append(uid)

    elif device_identifier == BrickletAmbientLight.DEVICE_IDENTIFIER and\
         uid not in dict_enumerate['ambient_light']:
            dict_enumerate['ambient_light'].append(uid)

    elif has_ambient_light_v2 and\
         device_identifier == BrickletAmbientLightV2.DEVICE_IDENTIFIER and\
         uid not in dict_enumerate['ambient_light']:
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
            arguments = command.command_line.partition('/usr/bin/sendemail')[2]
            tokens = shlex.split(arguments)

            while len(tokens) >= 2:
                if tokens[0] == '-f':
                    dict_email['from'] = tokens[1]
                elif tokens[0] == '-t':
                    dict_email['to'] = tokens[1]
                elif tokens[0] == '-s':
                    server_port = tokens[1].split(':')
                    dict_email['server'] = server_port[0]
                    dict_email['port']   = server_port[1]
                elif tokens[0] == '-o':
                    if tokens[1].startswith('username='):
                        dict_email['username'] = tokens[1][len('username='):]
                    elif tokens[1].startswith('password='):
                        dict_email['password'] = tokens[1][len('password='):]
                    elif tokens[1].startswith('tls='):
                        dict_email['tls'] = tokens[1][len('tls='):]
                    else:
                        tokens = tokens[1:]
                        continue
                else:
                    tokens = tokens[1:]
                    continue

                tokens = tokens[2:]

        if len(list_rules) > 0:
            dict_return['rules'] = list_rules

        if len(dict_email) == 7:
            dict_return['email'] = dict_email

        sys.stdout.write(json.dumps(dict_return))
    except Exception as e:
        sys.stderr.write(unicode(e))
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
            tf_command_notify_service.command_line = TEMPLATE_COMMAND_LINE_NOTIFY_SERVICE.format(quote(apply_dict['email']['from']),
                                                                                                 quote(apply_dict['email']['to']),
                                                                                                 quote(apply_dict['email']['server']),
                                                                                                 quote(apply_dict['email']['port']),
                                                                                                 quote(apply_dict['email']['username']),
                                                                                                 quote(apply_dict['email']['password']),
                                                                                                 quote(apply_dict['email']['tls']))
            tf_command_notify_host.command_name = 'tinkerforge-notify-host-by-email'
            tf_command_notify_host.command_line = TEMPLATE_COMMAND_LINE_NOTIFY_HOST.format(quote(apply_dict['email']['from']),
                                                                                           quote(apply_dict['email']['to']),
                                                                                           quote(apply_dict['email']['server']),
                                                                                           quote(apply_dict['email']['port']),
                                                                                           quote(apply_dict['email']['username']),
                                                                                           quote(apply_dict['email']['password']),
                                                                                           quote(apply_dict['email']['tls']))
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

        if not IMAGE_VERSION or float(IMAGE_VERSION) < MIN_VERSION_WITH_NAGIOS4:
            if os.system('/bin/systemctl restart nagios3') != 0:
                exit(1)
        else:
            if os.system('/bin/systemctl restart nagios') != 0:
                exit(1)
    except Exception as e:
        sys.stderr.write(unicode(e))
        exit(1)

elif ACTION == 'APPLY_EMPTY':
    try:
        if os.path.isfile(FILE_PATH_CHECK_SCRIPT):
            os.remove(FILE_PATH_CHECK_SCRIPT)

        if os.path.isfile(FILE_PATH_TF_NAGIOS_CONFIGURATION):
            os.remove(FILE_PATH_TF_NAGIOS_CONFIGURATION)

        if not IMAGE_VERSION or float(IMAGE_VERSION) < MIN_VERSION_WITH_NAGIOS4:
            if os.system('/bin/systemctl restart nagios3') != 0:
                exit(1)
        else:
            if os.system('/bin/systemctl restart nagios') != 0:
                exit(1)

    except Exception as e:
        sys.stderr.write(unicode(e))
        exit(1)

elif ACTION == 'GET_LOCALHOST':
    try:
        hostname = unicode(socket.gethostname())

        if hostname:
            sys.stdout.write(hostname)
        else:
            exit(1)
    except Exception as e:
        sys.stderr.write(unicode(e))
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
        sleep(2)
    except:
        ignore_enumerate_fail()
        exit(0)

elif ACTION == 'TEST_EMAIL':
    if len(argv) != 3:
        sys.stderr.write(unicode('Too many or too few arguments provided for sending test email'))
        exit(1)
    try:
        test_email_dict = json.loads(argv[2])
        test_email_from = test_email_dict['test_email_from']
        test_email_to = test_email_dict['test_email_to']
        test_email_server = test_email_dict['test_email_server']
        test_email_port = test_email_dict['test_email_port']
        test_email_username = test_email_dict['test_email_username']
        test_email_password = test_email_dict['test_email_password']
        test_email_tls = test_email_dict['test_email_tls']

        test_email_cmd = TEMPLATE_TEST_EMAIL.format(quote(test_email_from),
                                                    quote(test_email_to),
                                                    quote(test_email_server),
                                                    quote(test_email_port),
                                                    quote(test_email_username),
                                                    quote(test_email_password),
                                                    quote(test_email_tls))

        p_sendemail = subprocess.Popen(shlex.split(test_email_cmd),
                                       universal_newlines = True,
                                       stdout = subprocess.PIPE,
                                       stderr = subprocess.PIPE)
        p_sendemail_comm = p_sendemail.communicate()

    except Exception as e:
        sys.stderr.write(unicode(e))
        exit(1)

    if p_sendemail.returncode != 0:
        if p_sendemail_comm[1]:
            sys.stderr.write(unicode(p_sendemail_comm[1]))
        else:
            sys.stderr.write(unicode(p_sendemail_comm[0]))
        exit(1)

else:
    exit(1)

if ACTION == 'ENUMERATE':
    if ipcon:
        try:
            ipcon.disconnect()
        except:
            pass

    if not ignore_enumerate_failed_called:
        sys.stdout.write(json.dumps(dict_enumerate))
