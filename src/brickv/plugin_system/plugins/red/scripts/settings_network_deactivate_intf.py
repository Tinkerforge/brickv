#!/usr/bin/env python2
# -*- coding: utf-8 -*-


'''
# WIRED APPLY PART
cmd_disconnect_restart_connect = "/usr/bin/wicd-cli --wired -x; \
/etc/init.d/wicd force-reload; /usr/bin/wicd-cli --wired -c"

ps = subprocess.Popen(cmd_disconnect_restart_connect, shell=True)
comm = ps.communicate()
'''


import subprocess

cmd_disconnect_restart = "/usr/bin/wicd-cli --wireless -x; /etc/init.d/wicd force-reload"

ps = subprocess.Popen(cmd_disconnect_restart, shell=True)
comm = ps.communicate()
