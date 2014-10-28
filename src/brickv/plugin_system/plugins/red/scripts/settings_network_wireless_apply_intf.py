#!/usr/bin/env python2

import subprocess

cmd_disconnect_restart = "/usr/bin/wicd-cli --wireless -x; /etc/init.d/wicd force-reload"

ps = subprocess.Popen(cmd_disconnect_restart, shell=True)
comm = ps.communicate()
