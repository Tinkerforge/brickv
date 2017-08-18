#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import re
import os
import sys
import json
import time
import dbus
import shlex
import signal
import serial
import socket
import struct
import netifaces
import traceback
import netifaces
import subprocess
import ConfigParser
from xml.dom import minidom
from distutils.version import StrictVersion

if len(sys.argv) < 2:
    exit (1)

IMAGE_VERSION = None

try:
    with open('/etc/tf_image_version', 'r') as f:
        IMAGE_VERSION = StrictVersion(f.read().split(' ')[0].strip())
except:
    exit(1)

ACTION = sys.argv[1]

MIN_VERSION_WITH_MM = StrictVersion('1.10')
CMD_MM_SEARCH_MODEMS = '/usr/bin/mmcli -S &> /dev/null'

MM_MODEM_STATE_FAILED = 0
MM_MODEM_STATE_UNKNOWN = 1
MM_MODEM_STATE_INITIALIZING = 2
MM_MODEM_STATE_LOCKED = 3
MM_MODEM_STATE_DISABLED = 4
MM_MODEM_STATE_DISABLING = 5
MM_MODEM_STATE_ENABLING = 6
MM_MODEM_STATE_ENABLED = 7
MM_MODEM_STATE_SEARCHING = 8
MM_MODEM_STATE_REGISTERED = 9
MM_MODEM_STATE_DISCONNECTING = 10
MM_MODEM_STATE_CONNECTING = 11
MM_MODEM_STATE_CONNECTED = 12

MM_MODEM_STATE_FAILED_REASON_NONE = 0
MM_MODEM_STATE_FAILED_REASON_UNKNOWN = 1
MM_MODEM_STATE_FAILED_REASON_SIM_MISSING = 2
MM_MODEM_STATE_FAILED_REASON_SIM_ERROR = 3

MM_MODEM_POWER_STATE_UNKNOWN = 0
MM_MODEM_POWER_STATE_OFF = 1
MM_MODEM_POWER_STATE_LOW = 2
MM_MODEM_POWER_STATE_ON = 3

NM_DEVICE_TYPE_MODEM = 8
NM_DEVICE_STATE_ACTIVATED = 100

DBUS_MM_BUS_NAME = 'org.freedesktop.ModemManager1'
DBUS_MM_OBJECT_PATH = '/org/freedesktop/ModemManager1'
DBUS_MM_SIM_INTERFACE = 'org.freedesktop.ModemManager1.Sim'
DBUS_PROPERTIES_INTERFACE = 'org.freedesktop.DBus.Properties'
DBUS_MM_MODEM_INTERFACE = 'org.freedesktop.ModemManager1.Modem'
DBUS_MM_BEARER_INTERFACE = 'org.freedesktop.ModemManager1.Bearer'
DBUS_MM_MODEM_OBJECT_PATH = '/org/freedesktop/ModemManager1/Modem'
DBUS_INTROSPECTABLE_INTERFACE = 'org.freedesktop.DBus.Introspectable'
DBUS_MM_MODEM_SIMPLE_INTERFACE = 'org.freedesktop.ModemManager1.Modem.Simple'

DBUS_NM_BUS_NAME = 'org.freedesktop.NetworkManager'
DBUS_NM_INTERFACE = 'org.freedesktop.NetworkManager'
DBUS_NM_OBJECT_PATH = '/org/freedesktop/NetworkManager'
DBUS_PROPERTIES_INTERFACE = 'org.freedesktop.DBus.Properties'
DBUS_NM_DEVICE_INTERFACE = 'org.freedesktop.NetworkManager.Device'
DBUS_NM_AP_INTERFACE = 'org.freedesktop.NetworkManager.AccessPoint'
DBUS_NM_SETTINGS_INTERFACE = 'org.freedesktop.NetworkManager.Settings'
DBUS_NM_SETTINGS_OBJECT_PATH = '/org/freedesktop/NetworkManager/Settings'
DBUS_NM_IPV4_CONFIG_INTERFACE = 'org.freedesktop.NetworkManager.IP4Config'
DBUS_NM_DEVICE_WIRELESS_INTERFACE = 'org.freedesktop.NetworkManager.Device.Wireless'
DBUS_NM_SETTINGS_CONNECTION_INTERFACE = 'org.freedesktop.NetworkManager.Settings.Connection'
DBUS_NM_SETTINGS_CONNECTION_ACTIVE_INTERFACE = 'org.freedesktop.NetworkManager.Connection.Active'

TAG_CONFIG_SAKIS_OPERATORS = "conf['sakisOperators']"
TAG_PARAM_SIM_PIN = 'SIM_PIN'
TAG_PARAM_DIAL = 'DIAL'
TAG_PARAM_APN = 'FORCE_APN'
TAG_PARAM_APN_USER = 'APN_USER'
TAG_PARAM_APN_PASS = 'APN_PASS'
TAG_PARAM_USBMODEM = 'USBMODEM'

SERVICE_SYSTEMD_TF_MOBILE_INTERNET = 'tf_mobile_internet.service'
FILE_UNIT_TF_MOBILE_INTERNET = '/etc/systemd/system/' + SERVICE_SYSTEMD_TF_MOBILE_INTERNET
FILE_UNIT_TF_MOBILE_INTERNET_NM = '/etc/systemd/system/tf_mobile_internet_nm.service'
FILE_CONFIG_UMTSKEEPER = '/usr/umtskeeper/umtskeeper.conf'
FILE_TMP_SAKIS3GNET = '/tmp/sakis3g.3gnet'
FILE_UNIT_TIMER = '/etc/systemd/system/tf_mobile_internet_nm.timer'
FILE_UNIT_TARGET_SCRIPT = '/usr/local/scripts/_tf_mobile_internet_nm.py'
FILE_MOBILE_INTERNET_CONFIG = '/etc/tf_mobile_internet_enabled'

BINARY_SAKIS3G = '/usr/umtskeeper/sakis3g'
BINARY_LSUSB = '/usr/bin/lsusb'
BINARY_UMTSKEEPER = '/usr/umtskeeper/umtskeeper'
BINARY_KILLALL = '/usr/bin/killall'
BINARY_SYSTEMCTL = '/bin/systemctl'
BINARY_UDEVADM = '/sbin/udevadm'

SPLIT_SEARCH_INTERFACE = 'Interface: '
SPLIT_SEARCH_OPERATOR = 'Operator name: '
SPLIT_SEARCH_IP = 'IP Address: '
SPLIT_SEARCH_SUBNET_MASK = 'Subnet Mask: '
SPLIT_SEARCH_GATEWAY = 'Default route(s): '

DIR_SYS_CLASS_TTY = '/sys/class/tty'

UNIT_SYSTEMD = '''[Unit]
Description=systemd service for Tinkerforge mobile internet

[Service]
Type=simple
TimeoutStartSec=5
ExecStart=/usr/umtskeeper/umtskeeper --conf /usr/umtskeeper/umtskeeper.conf
TimeoutStopSec=5
ExecStop=/usr/bin/killall -9 umtskeeper sakis3g pppd

[Install]
WantedBy=multi-user.target
'''

CONFIG_UMTSKEEPER = '''
conf['deviceName'] = 'modem_mobile_internet'
conf['sakisSwitches'] = "--nostorage --pppd --console"
conf['sakisOperators'] = "{0}"
conf['sakisMaxFails'] = 8
conf['sakisFailLockDuration'] = 120
conf['wrongPinDelay'] = 60
conf['DNSprobeDomain'] = 'google.com'
conf['DNSprobeCycle'] = 600
conf['writeStats'] = False
conf['printMsg'] = False
conf['logMsg'] = False
conf['logFile'] = '/var/log/umtskeeper.log'
conf['statCycle'] = 20 # slow down all checking by 5x
'''

PY_TF_MOBILE_INTERNET = '''
#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import dbus
import ConfigParser
from xml.dom import minidom

DBUS_MM_BUS_NAME = 'org.freedesktop.ModemManager1'
DBUS_MM_OBJECT_PATH = '/org/freedesktop/ModemManager1'
DBUS_MM_SIM_INTERFACE = 'org.freedesktop.ModemManager1.Sim'
DBUS_PROPERTIES_INTERFACE = 'org.freedesktop.DBus.Properties'
DBUS_MM_MODEM_INTERFACE = 'org.freedesktop.ModemManager1.Modem'
DBUS_MM_BEARER_INTERFACE = 'org.freedesktop.ModemManager1.Bearer'
DBUS_MM_MODEM_OBJECT_PATH = '/org/freedesktop/ModemManager1/Modem'
DBUS_INTROSPECTABLE_INTERFACE = 'org.freedesktop.DBus.Introspectable'
DBUS_MM_MODEM_SIMPLE_INTERFACE = 'org.freedesktop.ModemManager1.Modem.Simple'

DBUS_NM_BUS_NAME = 'org.freedesktop.NetworkManager'
DBUS_NM_INTERFACE = 'org.freedesktop.NetworkManager'
DBUS_NM_OBJECT_PATH = '/org/freedesktop/NetworkManager'
DBUS_PROPERTIES_INTERFACE = 'org.freedesktop.DBus.Properties'
DBUS_NM_DEVICE_INTERFACE = 'org.freedesktop.NetworkManager.Device'
DBUS_NM_AP_INTERFACE = 'org.freedesktop.NetworkManager.AccessPoint'
DBUS_NM_SETTINGS_INTERFACE = 'org.freedesktop.NetworkManager.Settings'
DBUS_NM_SETTINGS_OBJECT_PATH = '/org/freedesktop/NetworkManager/Settings'
DBUS_NM_DEVICE_WIRELESS_INTERFACE = 'org.freedesktop.NetworkManager.Device.Wireless'
DBUS_NM_SETTINGS_CONNECTION_INTERFACE = 'org.freedesktop.NetworkManager.Settings.Connection'
DBUS_NM_SETTINGS_CONNECTION_ACTIVE_INTERFACE = 'org.freedesktop.NetworkManager.Connection.Active'

def get_mm_modem_object_paths():
    modem_object_path_list = []

    xml = dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME,
                                                     DBUS_MM_MODEM_OBJECT_PATH),
                         dbus_interface = DBUS_INTROSPECTABLE_INTERFACE).Introspect()
    xml_parsed = minidom.parseString(xml)
    items = xml_parsed.getElementsByTagName('node')

    items.pop(0)

    for i in items:
        try:
            v = int(i.attributes['name'].value)
        except:
            continue

        modem_object_path_list.append('/org/freedesktop/ModemManager1/Modem/' + str(v))

    return modem_object_path_list

modem_imei = ''
interface_name = ''
gsm_connection_active = False
c_parser_config = ConfigParser.ConfigParser()
c_parser_brickv_gsm = ConfigParser.ConfigParser()

if not os.path.isfile('/etc/tf_mobile_internet_enabled'):
    exit(0)

if not os.path.isfile('/etc/NetworkManager/system-connections/_tf_brickv_gsm'):
    exit(0)

c_parser_config.read('/etc/tf_mobile_internet_enabled')
modem_imei = c_parser_config.get('configuration', 'modem-imei', '')

if not modem_imei:
    exit(0)

c_parser_brickv_gsm.read('/etc/NetworkManager/system-connections/_tf_brickv_gsm')
interface_name = c_parser_brickv_gsm.get('connection', 'interface-name', '')

if not interface_name:
    exit(0)

active_connection_object_paths = \
    dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                   dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_INTERFACE, 'ActiveConnections')

for active_connection_object_path in active_connection_object_paths:
    connection_object_path = \
        dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, active_connection_object_path),
                       dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_SETTINGS_CONNECTION_ACTIVE_INTERFACE, 'Connection')
    connection_settings = \
        dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, connection_object_path),
                       dbus_interface = DBUS_NM_SETTINGS_CONNECTION_INTERFACE).GetSettings()

    if not connection_settings['connection']['type'] \
       or connection_settings['connection']['type'] != 'gsm':
            continue

    if not connection_settings['connection']['interface-name'] \
       or connection_settings['connection']['interface-name'] != interface_name:
            dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                           dbus_interface = DBUS_NM_INTERFACE).DeactivateConnection(active_connection_object_path)

modem_object_path_list = get_mm_modem_object_paths()

for o in modem_object_path_list:
    imei = \
        dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                       dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'EquipmentIdentifier')

    if imei != modem_imei:
        continue

    active_connection_object_paths = \
        dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                       dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_INTERFACE, 'ActiveConnections')

    for active_connection_object_path in active_connection_object_paths:
        connection_object_path = \
            dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, active_connection_object_path),
                           dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_SETTINGS_CONNECTION_ACTIVE_INTERFACE, 'Connection')
        connection_settings = \
            dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, connection_object_path),
                           dbus_interface = DBUS_NM_SETTINGS_CONNECTION_INTERFACE).GetSettings()

        if connection_settings['connection']['id'] == '_tf_brickv_gsm':
            gsm_connection_active = True

            break

    if gsm_connection_active:
        break

    primary_port = \
        dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                       dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'PrimaryPort')

    c_parser_brickv_gsm.set('connection', 'interface-name', primary_port)

    with open('/etc/NetworkManager/system-connections/_tf_brickv_gsm', 'w') as fh:
        c_parser_brickv_gsm.write(fh)

    os.system('/usr/bin/nmcli connection reload')
    os.system('/usr/bin/nmcli connection up _tf_brickv_gsm')
'''

UNIT_TF_MOBILE_INTERNET = '''[Unit]
Description=Check state of configured mobile internet modem and try to keep it connected
Wants=network.target network-online.target
After=network.target network-online.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python /usr/local/scripts/_tf_mobile_internet_nm.py

[Install]
WantedBy=multi-user.target
'''

TIMER_TF_MOBILE_INTERNET = '''[Unit]
Description=Execute tf_mobile_internet_nm.service every 5 seconds

[Timer]
OnUnitActiveSec=5s
Unit=tf_mobile_internet_nm.service

[Install]
WantedBy=timers.target
'''

dict_status = {'status'     : None,
               'interface'  : None,
               'ip'         : None,
               'subnet_mask': None,
               'gateway'    : None,
               'dns'        : None}

dict_configuration = {'modem_list'      : None,
                      'modem_configured': None,
                      'dial'            : None,
                      'apn'             : None,
                      'username'        : None,
                      'password'        : None,
                      'sim_card_pin'    : None}

c_parser_config = ConfigParser.ConfigParser()

if os.path.isfile(FILE_MOBILE_INTERNET_CONFIG):
    c_parser_config.read(FILE_MOBILE_INTERNET_CONFIG)

def get_value_from_line(line):
    split_line = line.split('=', 1)

    if len(split_line) == 2:
        return split_line[1]
    else:
        return False

def get_vid_pid(pstdout):
    vid = ''
    pid = ''

    for line in pstdout.splitlines():
        if 'ID_VENDOR_ID=' in line:
            value = get_value_from_line(line)

            if value:
                vid = value

        if 'ID_MODEL_ID=' in line:
            value = get_value_from_line(line)

            if value:
                pid = value

    if not vid or not pid:
        return False

    return ':'.join([vid, pid])

def get_device_name(pstdout):
    vendor = None
    model = None

    for line in pstdout.splitlines():
        if 'ID_VENDOR_FROM_DATABASE=' in line:
            value = get_value_from_line(line)

            if value:
                vendor = value

        if 'ID_MODEL_FROM_DATABASE=' in line:
            value = get_value_from_line(line)

            if value:
                model = value

    if not vendor and not model:
        return False

    if vendor and not model:
        return vendor

    if not vendor and model:
        return model

    return ' '.join([vendor, model])

def get_usb_tty_devices():

    usb_tty_devices = []

    for device_node in os.listdir(DIR_SYS_CLASS_TTY):

        device_node_path = '/dev/' + device_node

        p = subprocess.Popen([BINARY_UDEVADM, 'info', device_node_path],
                             stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE)
        pstdout = p.communicate()[0]

        if not pstdout:
            continue

        if p.returncode != 0:
            continue

        if not 'ID_' in pstdout:
            continue

        if not 'N: ' in pstdout:
            continue

        if not 'ID_VENDOR_ID=' in pstdout:
            continue

        if not 'ID_MODEL_ID=' in pstdout:
            continue

        vid_pid = get_vid_pid(pstdout)
        device_name = get_device_name(pstdout)

        if not vid_pid:
            conitnue

        if not device_name:
            device_name = ''

        usb_tty_devices.append({'device_node_path': device_node_path,
                                'vid_pid': vid_pid,
                                'device_name': device_name})

    if len(usb_tty_devices) <= 0:
        return False

    return usb_tty_devices

def killall_processes():
    os.system(' -9 '.join([BINARY_KILLALL, 'umtskeeper sakis3g pppd']) + ' &> /dev/null')

def test_connection(command_test_connection):
    def remove_tmp_sakis3gnet():
        if os.path.exists(FILE_TMP_SAKIS3GNET):
            try:
                os.remove(FILE_TMP_SAKIS3GNET)
            except:
                pass

    killall_processes()
    remove_tmp_sakis3gnet()

    ret_command_test_connection = execute_command(shlex.split(command_test_connection))

    if ret_command_test_connection != 0:
        killall_processes()
        remove_tmp_sakis3gnet()
        sys.stdout.write('ERRORCODE = ' + str(ret_command_test_connection))
        if ret_command_test_connection == 7 or \
           ret_command_test_connection == 8 or \
           ret_command_test_connection == 12 or \
           ret_command_test_connection == 13 or \
           ret_command_test_connection == 98:
                return ret_command_test_connection
        return 2

    killall_processes()
    remove_tmp_sakis3gnet()

    return 0

def enable_start_systemd_service():
    if execute_command([BINARY_SYSTEMCTL, 'enable', FILE_UNIT_TF_MOBILE_INTERNET]) != 0:
        stop_disable_remove_systemd_service()
        return 3

    if execute_command([BINARY_SYSTEMCTL, 'start', SERVICE_SYSTEMD_TF_MOBILE_INTERNET]) != 0:
        stop_disable_remove_systemd_service()
        return 4

    return 0

def stop_disable_remove_systemd_service():
    os.system(' stop '.join([BINARY_SYSTEMCTL, SERVICE_SYSTEMD_TF_MOBILE_INTERNET]) + ' &> /dev/null')
    os.system(' disable '.join([BINARY_SYSTEMCTL, SERVICE_SYSTEMD_TF_MOBILE_INTERNET]) + ' &> /dev/null')

    if os.path.exists(FILE_UNIT_TF_MOBILE_INTERNET):
        os.remove(FILE_UNIT_TF_MOBILE_INTERNET)

    killall_processes()

# This function is used when a command must be executed with subprocess.Popen and
# only returncode is needed
def execute_command(command):
    p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    p.communicate()
    return p.returncode

def prepare_test_command_and_umtskeeper_configuration(usb_modem,
                                                      dial,
                                                      apn,
                                                      apn_user,
                                                      apn_pass,
                                                      sim_pin):
    command_test_connection = ''
    configuration_umtskeeper = ''
    sakis_operators = '''DIAL="{0}" FORCE_APN="{1}" APN_USER="{2}" APN_PASS="{3}" OTHER="USBMODEM" USBMODEM="{4}" MODEM="{4}"'''
    sakis_operators_sim_pin = '''SIM_PIN="{0}" DIAL="{1}" FORCE_APN="{2}" APN_USER="{3}" APN_PASS="{4}" OTHER="USBMODEM" USBMODEM="{5}" MODEM="{5}"'''

    if sim_pin != '':
        command_test_connection_args = ' connect --nostorage --pppd --nofix --console ' +\
            sakis_operators_sim_pin.format(sim_pin,
                                           dial,
                                           apn,
                                           apn_user,
                                           apn_pass,
                                           usb_modem)
        command_test_connection = BINARY_SAKIS3G + command_test_connection_args
        configuration_umtskeeper = CONFIG_UMTSKEEPER.format(sakis_operators_sim_pin.replace('"', "'").format(sim_pin,
                                                                                                             dial,
                                                                                                             apn,
                                                                                                             apn_user,
                                                                                                             apn_pass,
                                                                                                             usb_modem))
        return command_test_connection, configuration_umtskeeper

    else:
        command_test_connection_args = ' connect --nostorage --pppd --nofix --console ' +\
            sakis_operators.format(dial,
                                   apn,
                                   apn_user,
                                   apn_pass,
                                   usb_modem)
        command_test_connection = BINARY_SAKIS3G + command_test_connection_args
        configuration_umtskeeper = CONFIG_UMTSKEEPER.format(sakis_operators.replace('"', "'").format(dial,
                                                                                                     apn,
                                                                                                     apn_user,
                                                                                                     apn_pass,
                                                                                                     usb_modem))
        return command_test_connection, configuration_umtskeeper

def find_whole_word(word):
    return re.compile(r'\b({0})\b'.format(word), flags=re.IGNORECASE).search

def get_DNS():
    if not os.path.exists('/etc/resolv.conf'):
        return None

    with open('/etc/resolv.conf', 'r') as rcfh:
        dns_servers = []

        for line in rcfh.readlines():
            line_split = line.split(' ')

            if len(line_split) == 2 and \
               'nameserver' in line_split[0] and line_split[1] != '':
                    dns_servers.append(line_split[1].strip())

        if len(dns_servers) <= 0:
            return '-'

        return ', '.join(dns_servers)

def find_modem_ports(vid, pid):
    ports_modem = []
    id_v = ''
    id_p = ''

    try:
        for device_number in os.listdir('/sys/bus/usb/devices'):
            device_dir = os.path.join('/sys/bus/usb/devices', device_number)

            if not os.path.exists(os.path.join(device_dir, 'idVendor')):
                continue

            with open(os.path.join(device_dir, 'idVendor')) as idvfh:
                id_v = idvfh.read().strip()

            if id_v != vid:
                continue

            with open(os.path.join(device_dir, 'idProduct')) as idpfh:
                id_p = idpfh.read().strip()

            if id_p != pid:
                continue

            for subdir in os.listdir(device_dir):
                if not subdir.startswith(device_number + ':'):
                    continue

                for subsubdir in os.listdir(os.path.join(device_dir, subdir)):
                    if not subsubdir.startswith('ttyUSB'):
                        continue

                    ports_modem.append(os.path.join('/dev', subsubdir))
    except:
        pass

    return ports_modem

def get_signal_quality():
    def close_modem(modem):
        if modem:
            modem.close()
            modem = None

    def handler_timeout_signal(self, signal_number, frame):
        raise Exception

    lines = []
    ports_modem = []
    modem = None
    signal_quality = None

    if not os.path.exists(FILE_CONFIG_UMTSKEEPER):
        return signal_quality

    try:
        with open(FILE_CONFIG_UMTSKEEPER, 'r') as ucfh:
            lines = ucfh.readlines()
    except:
        return signal_quality

    if len(lines) == 0:
        return signal_quality

    try:
        for line in lines:
            if ' MODEM=' not in line:
                continue

            split_sakisops = line.split(' MODEM=')

            if len(split_sakisops) != 2:
                continue

            vid_pid = split_sakisops[1].replace('"', '').replace("'", '').strip()

            split_vid_pid = vid_pid.split(':')

            if len(split_vid_pid) != 2:
                continue

            vid = split_vid_pid[0].strip()
            pid = split_vid_pid[1].strip()

            if len(vid) != 4 or len(pid) != 4:
                continue

            ports_modem = find_modem_ports(vid, pid)

            if len(ports_modem) > 0:
                break
    except:
        pass

    if len(ports_modem) == 0:
        return signal_quality

    signal.signal(signal.SIGALRM, handler_timeout_signal)

    for port in ports_modem:
        try:
            close_modem(modem)
            modem = serial.Serial(port, 9600, timeout = 2, writeTimeout = 2)
            # Even though pySerial provides read and write timeouts the write timeout
            # doesn't work if the port is currently being used by some other process.
            # This is why the timeout signal exception mechanism is used with 4 seconds
            # timeout.
            signal.alarm(4)
            modem.write(b'AT+CSQ\r')
            signal.alarm(0) # Reset timeout signal if write call returned
            time.sleep(0.2)
            at_response = modem.read(32)

            if not at_response:
                continue

            signal_quality_stripped = at_response.replace('\r', '')\
                                                 .replace('\n', '')\
                                                 .replace('OK', '')\
                                                 .replace(' ', '')\
                                                 .strip()
            signal_quality_csq_split = signal_quality_stripped.split('+CSQ:')

            if len(signal_quality_csq_split) != 2:
                continue

            signal_quality_comma_split = signal_quality_csq_split[1].split(',')

            if len(signal_quality_comma_split) != 2:
                continue

            signal_quality_raw = signal_quality_comma_split[0]

            if int(signal_quality_raw) > 1 and int(signal_quality_raw) < 10:
                close_modem(modem)
                signal_quality = '25%'
                break
            elif int(signal_quality_raw) > 9 and int(signal_quality_raw) < 15:
                close_modem(modem)
                signal_quality = '50%'
                break
            elif int(signal_quality_raw) > 14 and int(signal_quality_raw) < 20:
                close_modem(modem)
                signal_quality = '75%'
                break
            elif int(signal_quality_raw) > 19 and int(signal_quality_raw) < 31:
                close_modem(modem)
                signal_quality = '100%'
                break
            else:
                close_modem(modem)
                signal_quality = None
                break
        except:
            signal.alarm(0) # Reset timeout signal

    return signal_quality

def populate_dict_configuration():
    dict_configuration['modem_configured'] = ''
    dict_configuration['dial'] = ''
    dict_configuration['apn'] = ''
    dict_configuration['user'] = ''
    dict_configuration['password'] = ''
    dict_configuration['sim_card_pin'] = ''

    try:
        dict_configuration['modem_configured'] = c_parser_config.get('configuration', 'modem-imei', '')
    except:
        pass

    try:
        dict_configuration['dial'] = c_parser_config.get('configuration', 'dial-number', '')
    except:
        pass

    try:
        dict_configuration['apn'] = c_parser_config.get('configuration', 'apn', '')
    except:
        pass

    try:
        dict_configuration['username'] = c_parser_config.get('configuration', 'user', '')
    except:
        pass

    try:
        dict_configuration['password'] = c_parser_config.get('configuration', 'password', '')
    except:
        pass

    try:
        dict_configuration['sim_card_pin'] = c_parser_config.get('configuration', 'sim-pin', '')
    except:
        pass

def cidr_to_netmask(cidr):
    host_bits = 32 - int(cidr)
    return socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))

def populate_dict_status():
    imei = ''
    dict_status['status'] = '-'
    dict_status['signal_quality'] = '-'
    dict_status['interface'] = '-'
    dict_status['ip'] = '-'
    dict_status['subnet_mask'] = '-'
    dict_status['gateway'] = '-'
    dict_status['dns'] = '-'

    try:
        imei = c_parser_config.get('configuration', 'modem-imei', '')
    except:
        pass

    if imei == '':
        return

    modem_object_path_list = get_mm_modem_object_paths()

    for o in modem_object_path_list:
        modem_imei = dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                                    dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'EquipmentIdentifier')
        if modem_imei != imei:
            continue

        bearers = []
        nm_devices = []
        modem_primary_port = ''
        modem_state = MM_MODEM_STATE_UNKNOWN

        modem_state = \
            dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                           dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'State')

        if modem_state == MM_MODEM_STATE_FAILED or modem_state == -1:
            modem_fail_reason = \
                dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                               dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'StateFailedReason')

            if modem_fail_reason == MM_MODEM_STATE_FAILED_REASON_SIM_MISSING:
                dict_status['status'] = 'Modem is not usable, SIM missing'
            elif modem_fail_reason == MM_MODEM_STATE_FAILED_REASON_SIM_ERROR:
                dict_status['status'] = 'Modem is not usable, SIM error'
            else:
                dict_status['status'] = 'Modem is not usable, unknown error'
        elif modem_state == MM_MODEM_STATE_UNKNOWN:
            dict_status['status'] = 'Modem is in unknown state'
        elif modem_state == MM_MODEM_STATE_INITIALIZING:
            dict_status['status'] = 'Modem is initializing'
        elif modem_state == MM_MODEM_STATE_DISABLED \
             or modem_state == MM_MODEM_STATE_LOCKED:
                dict_status['status'] = 'Modem is disabled/locked'

                dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                               dbus_interface = DBUS_MM_MODEM_INTERFACE).Enable(True)
        elif modem_state == MM_MODEM_STATE_DISABLING:
            dict_status['status'] = 'Modem is disabling'
        elif modem_state == MM_MODEM_STATE_ENABLING:
            dict_status['status'] = 'Modem is enabling'
        elif modem_state == MM_MODEM_STATE_ENABLED:
            dict_status['status'] = 'Modem is enabled'
        elif modem_state == MM_MODEM_STATE_REGISTERED \
             or modem_state == MM_MODEM_STATE_SEARCHING:
                operator_name = ''
                dict_status['status'] = 'Modem is searching for network'
                sim_object_path = \
                    dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                                   dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'Sim')
                operator_name = \
                    dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, sim_object_path),
                                   dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_SIM_INTERFACE, 'OperatorName')

                if operator_name:
                    dict_status['status'] = 'Modem registered to network ' + operator_name
        elif modem_state == MM_MODEM_STATE_DISCONNECTING:
            dict_status['status'] = 'Modem is disconnecting'
        elif modem_state == MM_MODEM_STATE_CONNECTING \
             or modem_state == MM_MODEM_STATE_CONNECTED:
                operator_name = ''
                dict_status['status'] = 'Modem is connecting'

                sim_object_path = \
                    dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                                   dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'Sim')
                operator_name = \
                    dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, sim_object_path),
                                   dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_SIM_INTERFACE, 'OperatorName')

                if operator_name:
                    dict_status['status'] = 'Modem registered and connected to ' + operator_name
        else:
            dict_status['status'] = 'Modem is in unknown state'

        dict_status['signal_quality'] = \
            str(dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                           dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'SignalQuality')[0]) + '%'

        modem_primary_port = \
            dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                           dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'PrimaryPort')

        nm_devices = \
            dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                           dbus_interface = DBUS_NM_INTERFACE).GetDevices()

        for device_object_path in nm_devices:
            device_properties = \
                dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_object_path),
                               dbus_interface = DBUS_PROPERTIES_INTERFACE).GetAll(DBUS_NM_DEVICE_INTERFACE)

            if device_properties['DeviceType'] != NM_DEVICE_TYPE_MODEM:
                continue

            if device_properties['State'] != NM_DEVICE_STATE_ACTIVATED:
                continue

            if device_properties['Interface'] != modem_primary_port:
                continue

            dict_status['interface'] = device_properties['IpInterface'] + ' (IMEI: ' + modem_imei +')'

            ipv4_properties = \
                dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_properties['Ip4Config']),
                               dbus_interface = DBUS_PROPERTIES_INTERFACE).GetAll(DBUS_NM_IPV4_CONFIG_INTERFACE)

            dict_status['ip'] = ipv4_properties['AddressData'][0]['address']
            dict_status['subnet_mask'] = cidr_to_netmask(ipv4_properties['AddressData'][0]['prefix'])
            dict_status['gateway'] = ipv4_properties['Gateway']
            dict_status['dns'] = get_DNS()

        break

def get_mm_modem_object_paths():
    modem_object_path_list = []

    xml = dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME,
                                                     DBUS_MM_MODEM_OBJECT_PATH),
                         dbus_interface = DBUS_INTROSPECTABLE_INTERFACE).Introspect()
    xml_parsed = minidom.parseString(xml)
    items = xml_parsed.getElementsByTagName('node')

    items.pop(0)

    for i in items:
        try:
            v = int(i.attributes['name'].value)
        except:
            continue

        modem_object_path_list.append('/org/freedesktop/ModemManager1/Modem/' + str(v))

    return modem_object_path_list

try:
    # Handle command GET_STATUS
    if ACTION == 'GET_STATUS':
        if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_MM:
            populate_dict_status()

            sys.stdout.write(json.dumps(dict_status))
        else:
            if not os.path.exists(FILE_TMP_SAKIS3GNET):
                p = subprocess.Popen([BINARY_SYSTEMCTL,
                                      'status',
                                      SERVICE_SYSTEMD_TF_MOBILE_INTERNET],
                                      stdout = subprocess.PIPE,
                                      stderr = subprocess.PIPE)
                p_out_str = p.communicate()[0]

                if p_out_str and \
                   'Loaded: loaded' in p_out_str and \
                   'Active: active' in p_out_str:
                        dict_status['status'] = 'Connecting...'
                else:
                    dict_status['status'] = 'Not connected'

                dict_status['signal_quality'] = None
                dict_status['interface'] = None
                dict_status['ip'] = None
                dict_status['subnet_mask'] = None
                dict_status['gateway'] = None
                dict_status['dns'] = get_DNS()
                sys.stdout.write(json.dumps(dict_status))
                exit(0)

            p = subprocess.Popen([BINARY_SAKIS3G, 'info'],
                                 stdout = subprocess.PIPE,
                                 stderr = subprocess.PIPE)
            p_out_str = p.communicate()[0]

            if p.returncode != 0:
                exit(1)

            if not p_out_str:
                exit(1)

            # The file /tmp/sakis3g.3gnet file might exist when the modem is not connected.
            # For example when a connected modem is disconnected physically from USB port or got
            # disconnected from the network and currently in retry phase.
            if 'Not connected' in p_out_str:
                _p = subprocess.Popen([BINARY_SYSTEMCTL,
                                      'status',
                                      SERVICE_SYSTEMD_TF_MOBILE_INTERNET],
                                      stdout = subprocess.PIPE,
                                      stderr = subprocess.PIPE)
                _p_out_str = _p.communicate()[0]

                if _p_out_str and \
                   'Loaded: loaded' in _p_out_str and \
                   'Active: active' in _p_out_str:
                        dict_status['status'] = 'Connecting...'
                else:
                    dict_status['status'] = 'Not connected'

                dict_status['signal_quality'] = None
                dict_status['interface'] = None
                dict_status['ip'] = None
                dict_status['subnet_mask'] = None
                dict_status['gateway'] = None
                dict_status['dns'] = get_DNS()
                sys.stdout.write(json.dumps(dict_status))
                exit(0)

            for line in p_out_str.splitlines():
                if SPLIT_SEARCH_OPERATOR in line and len(line.split(SPLIT_SEARCH_OPERATOR)) == 2:
                    if line.split(SPLIT_SEARCH_OPERATOR)[0] == '':
                        dict_status['status'] = 'Connected to ' + line.split(SPLIT_SEARCH_OPERATOR)[1]

                elif SPLIT_SEARCH_INTERFACE in line and len(line.split(SPLIT_SEARCH_INTERFACE)) == 2:
                    if line.split(SPLIT_SEARCH_INTERFACE)[0] == '':
                        dict_status['interface'] = line.split(SPLIT_SEARCH_INTERFACE)[1]

                elif SPLIT_SEARCH_IP in line and len(line.split(SPLIT_SEARCH_IP)) == 2:
                    if line.split(SPLIT_SEARCH_IP)[0] == '':
                        dict_status['ip'] = line.split(SPLIT_SEARCH_IP)[1]

                elif SPLIT_SEARCH_SUBNET_MASK in line and len(line.split(SPLIT_SEARCH_SUBNET_MASK)) == 2:
                    if line.split(SPLIT_SEARCH_SUBNET_MASK)[0] == '':
                        dict_status['subnet_mask'] = line.split(SPLIT_SEARCH_SUBNET_MASK)[1]

                elif SPLIT_SEARCH_GATEWAY in line and len(line.split(SPLIT_SEARCH_GATEWAY)) == 2:
                    if line.split(SPLIT_SEARCH_GATEWAY)[0] == '':
                        dict_status['gateway'] = line.split(SPLIT_SEARCH_GATEWAY)[1]

            dict_status['signal_quality'] = get_signal_quality()
            dict_status['dns'] = get_DNS()
            sys.stdout.write(json.dumps(dict_status))

    # Handle command REFRESH
    elif ACTION == 'REFRESH':
        if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_MM:
            imei = ''
            list_modem = []
            dict_configuration['modem_list'] = None
            modem_object_path_list = get_mm_modem_object_paths()

            os.system(CMD_MM_SEARCH_MODEMS)

            for o in modem_object_path_list:
                manufacturer = dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                                              dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'Manufacturer')
                model = dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                                       dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'Model')
                imei = dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                                       dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'EquipmentIdentifier')

                list_modem.append({'name': manufacturer + ' ' + model + ' (IMEI: ' + imei + ')',
                                   'imei': imei})

            dict_configuration['modem_list'] = list_modem

            populate_dict_configuration()
        else:
            usb_tty_devices = get_usb_tty_devices()

            if usb_tty_devices:
                list_modem = []
                list_vid_pid = []

                for dict_device in usb_tty_devices:
                    if dict_device['vid_pid'] in list_vid_pid:
                        continue

                    list_vid_pid.append(dict_device['vid_pid'])
                    list_modem.append({'vid_pid': dict_device['vid_pid'],
                                       'name'   : dict_device['device_name']})

                dict_configuration['modem_list'] = list_modem
            else:
                dict_configuration['modem_list'] = None

            # Process configuration file if it exists
            if os.path.exists(FILE_CONFIG_UMTSKEEPER):
                with open(FILE_CONFIG_UMTSKEEPER, 'r') as ucfh:
                    for line in ucfh.readlines():
                        if TAG_CONFIG_SAKIS_OPERATORS not in line:
                            continue

                        splitted_line = line.split('=', 1)

                        if len(splitted_line) != 2:
                            continue

                        splitted_params = splitted_line[1].strip().split(' ')

                        if len(splitted_params) < 1:
                            continue

                        for raw_param in splitted_params:
                            splitted_raw_param = raw_param.split('=')

                            if len(splitted_raw_param) != 2:
                                continue

                            if find_whole_word(TAG_PARAM_USBMODEM)(splitted_raw_param[0]):
                                dict_configuration['modem_configured'] =\
                                    splitted_raw_param[1].strip().replace("'", '').replace('"', '')

                            elif find_whole_word(TAG_PARAM_DIAL)(splitted_raw_param[0]):
                                dict_configuration['dial'] =\
                                    splitted_raw_param[1].strip().replace("'", '').replace('"', '')

                            elif find_whole_word(TAG_PARAM_APN)(splitted_raw_param[0]):
                                dict_configuration['apn'] =\
                                    splitted_raw_param[1].strip().replace("'", '').replace('"', '')

                            elif find_whole_word(TAG_PARAM_APN_USER)(splitted_raw_param[0]):
                                dict_configuration['username'] =\
                                    splitted_raw_param[1].strip().replace("'", '').replace('"', '')

                            elif find_whole_word(TAG_PARAM_APN_PASS)(splitted_raw_param[0]):
                                dict_configuration['password'] =\
                                    splitted_raw_param[1].strip().replace("'", '').replace('"', '')

                            elif find_whole_word(TAG_PARAM_SIM_PIN)(splitted_raw_param[0]):
                                dict_configuration['sim_card_pin'] =\
                                    splitted_raw_param[1].strip().replace("'", '').replace('"', '')

        sys.stdout.write(json.dumps(dict_configuration))

    # Handle command CONNECT
    elif ACTION == 'CONNECT':
        if len(sys.argv) < 8:
            exit(1)

        usb_modem = sys.argv[2]
        dial = sys.argv[3]
        apn = sys.argv[4]
        apn_user = sys.argv[5]
        apn_pass = sys.argv[6]
        sim_pin = sys.argv[7]

        if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_MM:
            modem_imei = ''
            modem_primary_serial_port = ''
            modem_object_path_list = []
            c_parser_brickv_gsm = ConfigParser.ConfigParser()
            gsm_connection_config_nm = \
                {
                    'connection':
                    {
                        'id': '_tf_brickv_gsm',
                        'interface-name': None,
                        'type': 'gsm',
                        'autoconnect': False
                    },

                    'gsm':
                    {
                        'number': None,
                        'username': None,
                        'password': None,
                        'password-flags': dbus.UInt32(0L),
                        'apn': None,
                        'pin': None,
                        'pin-flags': dbus.UInt32(0L)
                    }
                }

            try:
                c_parser_config.add_section('configuration')
            except:
                pass

            c_parser_config.set('configuration', 'modem-imei', usb_modem)
            c_parser_config.set('configuration', 'dial-number', dial)
            c_parser_config.set('configuration', 'apn', apn)
            c_parser_config.set('configuration', 'user', apn_user)
            c_parser_config.set('configuration', 'password', apn_pass)
            c_parser_config.set('configuration', 'sim-pin', sim_pin)

            with open(FILE_MOBILE_INTERNET_CONFIG, 'w') as fh:
                c_parser_config.write(fh)

            os.chmod(FILE_MOBILE_INTERNET_CONFIG, 0600)

            modem_object_path_list = get_mm_modem_object_paths()

            # Get primary serial port of the target modem
            for o in modem_object_path_list:
                modem_imei = \
                    dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                                   dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'EquipmentIdentifier')

                if modem_imei != usb_modem:
                    continue

                modem_primary_serial_port = \
                    dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                                   dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'PrimaryPort')

                break

            # Deactivate target mobile internet connection
            active_connection_object_paths = \
                dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                               dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_INTERFACE, 'ActiveConnections')

            for active_connection_object_path in active_connection_object_paths:
                connection_object_path = \
                    dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, active_connection_object_path),
                                   dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_SETTINGS_CONNECTION_ACTIVE_INTERFACE, 'Connection')
                connection_settings = \
                    dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, connection_object_path),
                                   dbus_interface = DBUS_NM_SETTINGS_CONNECTION_INTERFACE).GetSettings()

                if connection_settings['connection']['id'] != '_tf_brickv_gsm':
                        continue

                dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                               dbus_interface = DBUS_NM_INTERFACE).DeactivateConnection(active_connection_object_path)

            # Delete target mobile internet connection
            connection_object_paths = \
                dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_SETTINGS_OBJECT_PATH),
                               dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_SETTINGS_INTERFACE, 'Connections')

            for connection_object_path in connection_object_paths:
                connection_settings = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, connection_object_path),
                                                     dbus_interface = DBUS_NM_SETTINGS_CONNECTION_INTERFACE).GetSettings()

                if connection_settings['connection']['id'] == '_tf_brickv_gsm':
                    dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, connection_object_path),
                                   dbus_interface = DBUS_NM_SETTINGS_CONNECTION_INTERFACE).Delete()

            # Reload connections.
            r = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_SETTINGS_OBJECT_PATH),
                               dbus_interface = DBUS_NM_SETTINGS_INTERFACE).ReloadConnections()

            if not r:
                exit(1)

            # Add new mobile internet connection, reload connections and activate
            gsm_connection_config_nm['connection']['interface-name'] = modem_primary_serial_port
            gsm_connection_config_nm['gsm']['number'] = dial
            gsm_connection_config_nm['gsm']['username'] = apn_user
            gsm_connection_config_nm['gsm']['password'] = apn_pass
            gsm_connection_config_nm['gsm']['apn'] = apn
            gsm_connection_config_nm['gsm']['pin'] = sim_pin

            dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_SETTINGS_OBJECT_PATH),
                           dbus_interface = DBUS_NM_SETTINGS_INTERFACE).AddConnection(gsm_connection_config_nm)

            c_parser_brickv_gsm.read('/etc/NetworkManager/system-connections/_tf_brickv_gsm')

            with open('/etc/NetworkManager/system-connections/_tf_brickv_gsm', 'w') as fh:
                c_parser_brickv_gsm.write(fh)

            os.system('/usr/bin/nmcli connection reload')
            os.system('/usr/bin/nmcli connection up _tf_brickv_gsm')

            if os.path.isfile(FILE_UNIT_TIMER):
                try:
                    os.system('/bin/systemctl stop tf_mobile_internet_nm.timer &> /dev/null')
                    os.system('/bin/systemctl disable tf_mobile_internet_nm.timer &> /dev/null')
                except:
                    pass

            if os.path.isfile(FILE_UNIT_TF_MOBILE_INTERNET_NM):
                try:
                    os.system('/bin/systemctl stop tf_mobile_internet_nm.service &> /dev/null')
                    os.system('/bin/systemctl disable tf_mobile_internet_nm.service &> /dev/null')
                except:
                    pass

            with open(FILE_UNIT_TARGET_SCRIPT, 'w') as fh:
                fh.write(PY_TF_MOBILE_INTERNET)

            os.chmod(FILE_UNIT_TARGET_SCRIPT, 0755)

            with open(FILE_UNIT_TF_MOBILE_INTERNET_NM, 'w') as fh:
                fh.write(UNIT_TF_MOBILE_INTERNET)

            os.chmod(FILE_UNIT_TF_MOBILE_INTERNET_NM, 0644)

            with open(FILE_UNIT_TIMER, 'w') as fh:
                fh.write(TIMER_TF_MOBILE_INTERNET)

            os.chmod(FILE_UNIT_TIMER, 0644)

            os.system('/bin/systemctl enable tf_mobile_internet_nm.service &> /dev/null')
            os.system('/bin/systemctl enable tf_mobile_internet_nm.timer &> /dev/null')
            os.system('/bin/systemctl start tf_mobile_internet_nm.service &> /dev/null')
            os.system('/bin/systemctl start tf_mobile_internet_nm.timer &> /dev/null')
        else:
            command_test_connection, configuration_umtskeeper =\
                prepare_test_command_and_umtskeeper_configuration(usb_modem,
                                                                  dial,
                                                                  apn,
                                                                  apn_user,
                                                                  apn_pass,
                                                                  sim_pin)

            # Disable and remove the systemd service if it exists
            stop_disable_remove_systemd_service()

            # Test connection to verify provided configuration
            ret_test_connection = test_connection(command_test_connection)

            if ret_test_connection != 0:
                exit(ret_test_connection)

            # Write umtskeeper configuration file
            with open(FILE_CONFIG_UMTSKEEPER, 'w') as ucfh:
                ucfh.write(configuration_umtskeeper)

            # Write the systemd unit file
            with open(FILE_UNIT_TF_MOBILE_INTERNET, 'w') as ufh:
                ufh.write(UNIT_SYSTEMD)

            os.chmod(FILE_UNIT_TF_MOBILE_INTERNET, 0644)

            ret_enable_start_systemd_service = enable_start_systemd_service()

            if ret_enable_start_systemd_service != 0:
                exit(ret_enable_start_systemd_service)

    else:
        exit(1)

except SystemExit as e:
    # For handling the exit() calls within the try block
    exit(e.code)

except:
    traceback.print_exc()
    # For all the other exceptions raised from the try block
    exit(1)
