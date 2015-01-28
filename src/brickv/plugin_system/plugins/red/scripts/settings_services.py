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

if command == 'CHECK':
    try:
        cmd = '/sbin/chkconfig | awk -F " " \'{print $1 "<==>" $2}\''
        cmd_ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

        if cmd_ps.returncode:
            exit(3)

        init_script_list_str = cmd_ps.communicate()[0].strip()
        init_script_list_list = init_script_list_str.splitlines()
        return_dict = {'gpu'         : None,
                       'desktopenv'  : None,
                       'webserver'   : None,
                       'splashscreen': None,
                       'ap'          : None}

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
            if os.system('/usr/sbin/update-rc.d apache2 defaults') != 0:
                exit(6)
        else:
            if os.system('/usr/sbin/update-rc.d -f apache2 remove') != 0:
                exit(7)

        if apply_dict['splashscreen']:
            if os.system('/usr/sbin/update-rc.d asplashscreen start runlvl S 1') != 0:
                exit(8)
        else:
            if os.system('/usr/sbin/update-rc.d -f asplashscreen remove') != 0:
                exit(9)

        if apply_dict['ap']:
            with open('/etc/tf_ap_enabled', 'w') as fd_ap_enabled:
                if os.system('/usr/sbin/update-rc.d hostapd defaults') != 0:
                    exit(10)

                if os.system('/usr/sbin/update-rc.d dnsmasq defaults') != 0:
                    exit(11)

                if os.system('/usr/sbin/update-rc.d -f wicd remove') != 0:
                    exit(12)

        else:
            if os.path.isfile('/etc/tf_ap_enabled'):
                os.remove('/etc/tf_ap_enabled')

            if os.system('/usr/sbin/update-rc.d -f hostapd remove') != 0:
                exit(13)

            if os.system('/usr/sbin/update-rc.d -f dnsmasq remove') != 0:
                exit(14)

            if os.system('/usr/sbin/update-rc.d wicd defaults') != 0:
                exit(15)

            with open('/etc/network/interfaces', 'w') as fd_interfaces:
                fd_interfaces.write(INTERFACES_CONF)

        exit(0)

    except Exception as e:
        sys.stderr.write(unicode(e).encode('utf-8'))
        exit(16)

else:
    sys.stderr.write(u'Invalid parameters'.encode('utf-8'))
    exit(17)
