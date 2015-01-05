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
                       'splashscreen': None}

        for script in init_script_list_list:
            script_stat = script.split('<==>')
            if len(script_stat) == 2:
                if script_stat[0] == 'x11-common':
                    if script_stat[1] == 'on':
                        return_dict['desktopenv'] = True
                    else:
                        return_dict['desktopenv'] = False
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

        if os.path.exists('/etc/modprobe.d/mali-blacklist.conf'):
            return_dict['gpu'] = False
        else:
            return_dict['gpu'] = True

        print json.dumps(return_dict)

    except:
        exit(1)

elif command == 'APPLY':
    if len(argv) < 3:
        exit (1)

    try:
        apply_dict = json.loads(unicode(argv[2]))

        if apply_dict['gpu']:
            # Use Python logic for removal
            if os.system('/bin/rm -rf /etc/modprobe.d/mali-blacklist.conf'):
                exit(1)
        else:
            # Use Python logic for writing file
            if os.system('/bin/echo \'blacklist mali\' > /etc/modprobe.d/mali-blacklist.conf'):
                exit(1)

        if apply_dict['desktopenv']:
            if os.system('/usr/sbin/update-rc.d x11-common start runlvl S'):
                exit(1)
        else:
            if os.system('/usr/sbin/update-rc.d -f x11-common remove'):
                exit(1)

        '''
        if apply_dict['webserver']:
            if os.system('/usr/sbin/update-rc.d apache2 defaults'):
                exit(1)
        else:
            if os.system('/usr/sbin/update-rc.d -f apache2 remove'):
                exit(1)
        '''

        if apply_dict['splashscreen']:
            if os.system('/usr/sbin/update-rc.d asplashscreen start runlvl S 1'):
                exit(1)
        else:
            if os.system('/usr/sbin/update-rc.d -f asplashscreen remove'):
                exit(1)

    except Exception as e:
        exit(1)

else:
    exit(1)
