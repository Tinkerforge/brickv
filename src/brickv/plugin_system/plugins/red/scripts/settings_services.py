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
    cmd = '/sbin/chkconfig | awk -F " " \'{print $1 "<==>" $2}\''
    cmd_ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    if cmd_ps.returncode:
        exit(1)
    init_script_list_str = ps_cmd.communicate()[0].strip()
    init_script_list_list = init_script_list_str.splitlines()
    for script in init_script_list_list:
        script_stat = script.split('<==>')
        if len(script_stat) == 2:
            if script_stat[0] == 'x11-common':
                if script_stat[1] == 'on':
                    
            if script_stat[0] == 'apache2':
                pass
            if script_stat[0] == 'asplashscreen':
                pass

    if os.path.exists('/etc/modprobe.d/mali'):
        pass
    if
    if
    if
    print json.dumps(return_dict)

elif command == 'APPLY':
    if len(argv) < 3:
        exit (1)

    try:
        apply_dict = json.loads(unicode(argv[2]))

        if apply_dict['gpu']:
            pass
        else:
            pass

        if apply_dict['de']:
            if os.system('/usr/sbin/update-rc.d x11-common start runlvl S'):
                exit(1)
        else:
            if os.system('/usr/sbin/update-rc.d -f x11-common remove'):
                exit(1)

        if apply_dict['web']:
            if os.system('/usr/sbin/update-rc.d apache2 defaults'):
                exit(1)
        else:
            if os.system('/usr/sbin/update-rc.d -f apache2 remove'):
                exit(1)

        if apply_dict['splash']:
            if os.system('/usr/sbin/update-rc.d asplashscreen start runlvl S 1'):
                exit(1)
        else:
            if os.system('/usr/sbin/update-rc.d -f asplashscreen remove'):
                exit(1)
    except:
        exit(1)

else:
    exit(1)
