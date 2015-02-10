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

TINKERFORGE_NAGIOS_SERVICE = '''#!/usr/bin/env python
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
                       'servermonitoring' : None,
                       'openhab'          : None}

        for script in init_script_list_list:
            script_stat = script.split('<==>')
            if len(script_stat) == 2:
                if script_stat[0] == 'apache2':
                    return_dict['webserver'] = script_stat[1] == 'on'
                elif script_stat[0] == 'asplashscreen':
                    return_dict['splashscreen'] = script_stat[1] == 'on'
                elif script_stat[0] == 'openhab':
                    return_dict['openhab'] = script_stat[1] == 'on'

        if return_dict['openhab'] == None:
            return_dict['openhab'] = False # openHAB is not installed at all

        return_dict['desktopenv'] = os.path.isfile('/etc/tf_x11_enabled')
        return_dict['gpu'] = not os.path.isfile('/etc/modprobe.d/mali-blacklist.conf')
        return_dict['ap'] = os.path.isfile('/etc/tf_ap_enabled')
        return_dict['servermonitoring'] = os.path.isfile('/etc/tf_server_monitoring_enabled')

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
                    exit(16)

            with open('/etc/tf_server_monitoring_enabled', 'w') as fd_server_monitoring_enabled:
                pass

            with open('/usr/local/bin/tinkerforge_nagios_service.py', 'w') as fd_tinkerforge_nagios_service:
                fd_tinkerforge_nagios_service.write(TINKERFORGE_NAGIOS_SERVICE)
                
            if os.system('/bin/systemctl enable nagios3') != 0:
                exit(17)

        else:
            if os.path.isfile('/etc/tf_server_monitoring_enabled'):
                os.remove('/etc/tf_server_monitoring_enabled')

            if os.system('/bin/systemctl disable nagios3') != 0:
                exit(18)

        if apply_dict['openhab']:
            if os.system('/bin/systemctl enable openhab') != 0:
                exit(19)
        else:
            if os.system('/bin/systemctl disable openhab') != 0:
                exit(20)

        exit(0)

    except Exception as e:
        sys.stderr.write(unicode(e).encode('utf-8'))
        exit(21)

else:
    sys.stderr.write(u'Invalid parameters'.encode('utf-8'))
    exit(22)
