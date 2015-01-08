#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import subprocess
import time
from sys import argv

if len(argv) < 2:
    exit (1)

command = unicode(argv[1])

sunxifb_fbdev_config = '''
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

sunxifb_fbturbo_config = '''
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

if command == 'CHECK':
    try:
        cmd = '/sbin/chkconfig | awk -F " " \'{print $1 "<==>" $2}\''
        cmd_ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        if cmd_ps.returncode:
            exit(1)
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

        if os.path.isfile('/etc/tf_x_enabled'):
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

        print json.dumps(return_dict)

    except:
        exit(1)

elif command == 'APPLY':
    if len(argv) < 3:
        exit (1)

    try:
        apply_dict = json.loads(unicode(argv[2]))

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
                fd_fbconf.write(sunxifb_fbturbo_config)

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
                fd_fbconf.write(sunxifb_fbdev_config)

        if apply_dict['desktopenv']:
            with open('/etc/tf_x_enabled', 'w') as fd_x_en:
                pass
        else:
            if os.path.isfile('/etc/tf_x_enabled'):
                os.remove('/etc/tf_x_enabled')

        if apply_dict['webserver']:
            if os.system('/usr/sbin/update-rc.d apache2 defaults'):
                exit(1)
        else:
            if os.system('/usr/sbin/update-rc.d -f apache2 remove'):
                exit(1)

        if apply_dict['splashscreen']:
            if os.system('/usr/sbin/update-rc.d asplashscreen start runlvl S 1'):
                exit(1)
        else:
            if os.system('/usr/sbin/update-rc.d -f asplashscreen remove'):
                exit(1)
        
        if apply_dict['ap']:
            with open('/etc/tf_ap_enabled', 'w') as fd_ap_enabled:
                pass
        else:
            if os.path.isfile('/etc/tf_ap_enabled'):
                os.remove('/etc/tf_ap_enabled')

    except:
        exit(1)

else:
    exit(1)
