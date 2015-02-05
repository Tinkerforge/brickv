#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import subprocess
import time
import sys

if len(sys.argv) < 2:
    sys.stderr.write(u'Missing parameters'.encode('utf-8'))
    exit(2)

command = sys.argv[1]

SUNXI_FBDEV_X11_DRIVER_CONF = '''
# This is a minimal sample config file, which can be copied to
# /etc/X11/xorg.conf in order to make the Xorg server pick up
# and load xf86-video-fbturbo driver installed in the system.
#
# When troubleshooting, check /var/log/Xorg.0.log for the debugging
# output and error messages.
#
# Run "man fbturbo" to get additional information about the extra
# configuration options for tuning the driver.

Section "Device"
        Identifier      "Allwinner A10/A13 FBDEV"
        Driver          "fbdev"
        Option          "fbdev" "/dev/fb0"
        Option          "SwapbuffersWait" "true"
        Option          "AccelMethod" "G2D"
EndSection
'''

SUNXI_FBTURBO_X11_DRIVER_CONF = '''
# This is a minimal sample config file, which can be copied to
# /etc/X11/xorg.conf in order to make the Xorg server pick up
# and load xf86-video-fbturbo driver installed in the system.
#
# When troubleshooting, check /var/log/Xorg.0.log for the debugging
# output and error messages.
#
# Run "man fbturbo" to get additional information about the extra
# configuration options for tuning the driver.

Section "Device"
        Identifier      "Allwinner A10/A13 FBDEV"
        Driver          "fbturbo"
        Option          "fbdev" "/dev/fb0"
        Option          "SwapbuffersWait" "true"
        Option          "AccelMethod" "G2D"
EndSection
'''

INTERFACES_CONF = '''# interfaces(5) file used by ifup(8) and ifdown(8)
auto lo
iface lo inet loopback
'''

SERVER_MONITORING_MAIN_SCRIPT = '''#!/usr/bin/env python
# -*- coding: utf8 -*-
# based on Wiki project:
# http://www.tinkerunity.org/wiki/index.php/EN/Projects/IT_Infrastructure_Monitoring_-_Nagios_Plugin
 
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

TYPE_PTC = "ptc"
TYPE_TEMPERATURE = "temp"
TYPE_HUMIDITY = "humidity"
 
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_temperature import Temperature
from tinkerforge.bricklet_humidity import Humidity
from tinkerforge.bricklet_ptc import PTC
import argparse
import sys
 
class CheckTFValue(object):
    def __init__(self, host='localhost', port=4223):
        self.host = host
        self.port = port
        self.ipcon = IPConnection()

 
    def connect(self, type, uid):
        self.ipcon.connect(self.host, self.port)
        self.connected_type = type

        if self.connected_type == TYPE_PTC:
            ptc = PTC(uid,self.ipcon)
            self.func = ptc.get_temperature
            self.divisor = 100.0
        elif self.connected_type == TYPE_TEMPERATURE:
            temperature = Temperature(uid,self.ipcon)
            self.func = temperature.get_temperature
            self.divisor = 100.0
        elif self.connected_type == TYPE_HUMIDITY:
            humidity = Humidity(uid,self.ipcon)
            self.func = humidity.get_humidity
            self.divisor = 10.0
 
    def disconnect(self):
        self.ipcon.disconnect()
 
    def read(self, warning, critical, mode='none', warning2=0, critical2=0):
        value = self.func()/self.divisor

        if mode == 'none':
            print "Value %s " % value
        else:
        
            if mode == 'low':
                warning2 = warning
                critical2 = critical

            if value >= critical and (mode == 'high' or mode == 'range'):
                print "CRITICAL : Value too high %s " % value
                return CRITICAL
            elif value >= warning and (mode == 'high' or mode == 'range'):
                print "WARNING : Value is high %s " % value
                return WARNING
            elif value <= critical2 and (mode == 'low' or mode == 'range'):
                print "CRITICAL : Value too low %s " % value
                return CRITICAL
            elif value <= warning2 and (mode == 'low' or mode == 'range'):
                print "WARNING : Value is low %s " % value
                return WARNING
            elif (value < warning and mode == 'high') or (value > warning2 and mode == 'low') or (value < warning and value > warning2 and mode == 'range'):
                print "OK : %s " % value
                return OK
            else:
                print "UNKOWN: Can't read value"
                return UNKNOWN

if __name__ == "__main__":

    parse = argparse.ArgumentParser()
    parse.add_argument("-u", "--uid", help="UID of Bricklet", required=True)
    parse.add_argument("-t", "--type", help="Type: temp = Temperature Bricklet, ptc = PTC Bricklet, humidity= Humidity Bricklet", type=str, choices=[TYPE_TEMPERATURE, TYPE_PTC, TYPE_HUMIDITY], required=True)
    parse.add_argument("-H", "--host", help="Host Server (default=localhost)", default='localhost')
    parse.add_argument("-P", "--port", help="Port (default=4223)", type=int, default=4223)
    parse.add_argument("-m", "--modus", help="Modus: none (default, only print value), high, low or range",type=str, choices=['none', 'high','low','range'], default='none')
    parse.add_argument("-w", "--warning", help="Warning value level (values above this level will trigger a warning message in high mode, value below this level will trigger a warning message in low mode)", required=False,type=float)
    parse.add_argument("-c", "--critical", help="Critical value level (value above this level will trigger a critical message in high mode, value below this level will trigger a critical message in low mode)", required=False,type=float)
    parse.add_argument("-w2", "--warning2", help="Warning value level (value below this level will trigger a warning message in range mode)", type=float)
    parse.add_argument("-c2", "--critical2", help="Critical value level (value below this level will trigger a critical message in range mode)", type=float)
 
    args = parse.parse_args()

    tf = CheckTFValue(args.host, args.port)
    tf.connect(args.type, args.uid)
    exit_code = tf.read(args.warning, args.critical, args.modus, args.warning2, args.critical2)
    tf.disconnect()
    sys.exit(exit_code)
'''

SERVER_MONITORING_NAGIOS_SERVICE = '''define service {
    use                             generic-service
    host_name                       localhost
    service_description             Check Temperature
    check_command                   check_tf_temp
    check_interval                  1
}

define service {
    use                             generic-service
    host_name                       localhost
    service_description             Check Humidity
    check_command                   check_tf_hum
    check_interval                  1
}
'''

if command == 'CHECK':
    try:
        cmd = '/sbin/chkconfig | awk -F " " \'{print $1 "<==>" $2}\''
        cmd_ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

        if cmd_ps.returncode:
            exit(3)

        init_script_list_str = cmd_ps.communicate()[0].strip()
        init_script_list_list = init_script_list_str.splitlines()
        return_dict = {'gpu'              : None,
                       'desktopenv'       : None,
                       'webserver'        : None,
                       'splashscreen'     : None,
                       'ap'               : None,
                       'servermonitoring' : None}

        for script in init_script_list_list:
            script_stat = script.split('<==>')
            if len(script_stat) == 2:
                if script_stat[0] == 'apache2':
                    if script_stat[1] == 'on':
                        return_dict['webserver'] = True
                    else:
                        return_dict['webserver'] = False

                if script_stat[0] == 'asplashscreen':
                    if script_stat[1] == 'on':
                        return_dict['splashscreen'] = True
                    else:
                        return_dict['splashscreen'] = False

        if os.path.isfile('/etc/tf_x11_enabled'):
            return_dict['desktopenv'] = True
        else:
            return_dict['desktopenv'] = False

        if os.path.isfile('/etc/modprobe.d/mali-blacklist.conf'):
            return_dict['gpu'] = False
        else:
            return_dict['gpu'] = True

        if os.path.isfile('/etc/tf_ap_enabled'):
            return_dict['ap'] = True
        else:
            return_dict['ap'] = False

        if os.path.isfile('/etc/tf_server_monitoring_enabled'):
            return_dict['servermonitoring'] = True
        else:
            return_dict['servermonitoring'] = False

        sys.stdout.write(json.dumps(return_dict, separators=(',', ':')))
        exit(0)

    except Exception as e:
        sys.stderr.write(unicode(e).encode('utf-8'))
        exit(4)

elif command == 'APPLY':
    if len(sys.argv) < 3:
        sys.stderr.write(u'Missing parameters'.encode('utf-8'))
        exit(5)

    try:
        apply_dict = json.loads(sys.argv[2])

        if apply_dict['gpu']:
            lines = []

            with open('/etc/modules', 'r') as fd_r_modules:
                lines = fd_r_modules.readlines()
                for i, l in enumerate(lines):
                    if l.strip() == '#mali':
                        lines[i] = l[1:]

            with open('/etc/modules', 'w') as fd_w_modules:
                fd_w_modules.write(''.join(lines))

            if os.path.isfile('/etc/modprobe.d/mali-blacklist.conf'):
                os.remove('/etc/modprobe.d/mali-blacklist.conf')

            with open('/usr/share/X11/xorg.conf.d/99-sunxifb.conf', 'w') as fd_fbconf:
                fd_fbconf.write(SUNXI_FBTURBO_X11_DRIVER_CONF)

        else:
            lines = []
            with open('/etc/modules', 'r') as fd_r_modules:
                lines = fd_r_modules.readlines()

                for i, l in enumerate(lines):
                    if l.strip() == 'mali':
                        lines[i] = '#'+l

            with open('/etc/modules', 'w') as fd_w_modules:
                fd_w_modules.write(''.join(lines))

            with open('/etc/modprobe.d/mali-blacklist.conf', 'w') as fd_w_malibl:
                fd_w_malibl.write('blacklist mali')

            with open('/usr/share/X11/xorg.conf.d/99-sunxifb.conf', 'w') as fd_fbconf:
                fd_fbconf.write(SUNXI_FBDEV_X11_DRIVER_CONF)

        if apply_dict['desktopenv']:
            with open('/etc/tf_x11_enabled', 'w') as fd_x11_enabled:
                pass
        else:
            if os.path.isfile('/etc/tf_x11_enabled'):
                os.remove('/etc/tf_x11_enabled')

        if apply_dict['webserver']:
            if os.system('/bin/systemctl enable apache2') != 0:
                exit(6)
        else:
            if os.system('/bin/systemctl disable apache2') != 0:
                exit(7)

        if apply_dict['splashscreen']:
            if os.system('/bin/systemctl enable asplashscreen') != 0:
                exit(8)
        else:
            if os.system('/bin/systemctl disable asplashscreen') != 0:
                exit(9)

        if apply_dict['ap']:
            with open('/etc/tf_ap_enabled', 'w') as fd_ap_enabled:
                pass

            if os.system('/bin/systemctl enable hostapd') != 0:
                exit(10)

            if os.system('/bin/systemctl enable dnsmasq') != 0:
                exit(11)

            if os.system('/bin/systemctl disable wicd') != 0:
                exit(12)

            if os.path.isfile('/etc/xdg/autostart/wicd-tray.desktop'):
                os.rename('/etc/xdg/autostart/wicd-tray.desktop',
                          '/etc/xdg/autostart/wicd-tray.desktop.block')

        else:
            if os.path.isfile('/etc/tf_ap_enabled'):
                os.remove('/etc/tf_ap_enabled')

            if os.system('/bin/systemctl disable hostapd') != 0:
                exit(13)

            if os.system('/bin/systemctl disable dnsmasq') != 0:
                exit(14)

            if os.system('/bin/systemctl enable wicd ') != 0:
                exit(15)

            with open('/etc/network/interfaces', 'w') as fd_interfaces:
                fd_interfaces.write(INTERFACES_CONF)
            
            if os.path.isfile('/etc/xdg/autostart/wicd-tray.desktop.block'):
                os.rename('/etc/xdg/autostart/wicd-tray.desktop.block',
                          '/etc/xdg/autostart/wicd-tray.desktop')

        if apply_dict['servermonitoring']:
            if not apply_dict['webserver']:
                if os.system('/bin/systemctl enable apache2') != 0:
                    exit(6)

            with open('/etc/tf_server_monitoring_enabled', 'w') as fd_server_monitoring_enabled:
                pass

            with open('/usr/local/bin/check_tf_value.py', 'w') as fd_server_monitoring_main_script:
                fd_server_monitoring_main_script.write(SERVER_MONITORING_MAIN_SCRIPT)

            with open('/etc/nagios3/conf.d/services_tf_nagios2.cfg', 'w') as fd_server_monitoring_nagios_service:
                fd_server_monitoring_nagios_service.write(SERVER_MONITORING_NAGIOS_SERVICE)

            if os.system('/bin/systemctl enable nagios3') != 0:
                exit(16)

            if os.system('/bin/systemctl enable postfix') != 0:
                exit(17)

        else:
            if os.path.isfile('/etc/tf_server_monitoring_enabled'):
                os.remove('/etc/tf_server_monitoring_enabled')

            if os.system('/bin/systemctl disable nagios3') != 0:
                exit(18)

            if os.system('/bin/systemctl disable postfix') != 0:
                exit(19)

        exit(0)

    except Exception as e:
        sys.stderr.write(unicode(e).encode('utf-8'))
        exit(20)

else:
    sys.stderr.write(u'Invalid parameters'.encode('utf-8'))
    exit(21)
