#!/usr/bin/env python2

import subprocess

cmd_disconnect_restart_connect = "/usr/bin/wicd-cli --wired -x; \
/etc/init.d/wicd force-reload; /usr/bin/wicd-cli --wired -c"

ps = subprocess.Popen(cmd_disconnect_restart_connect, shell=True)
comm = ps.communicate()
