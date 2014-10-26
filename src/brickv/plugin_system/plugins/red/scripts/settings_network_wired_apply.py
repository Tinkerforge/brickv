#!/usr/bin/env python2

import subprocess

cmd_restart_wicd = "/etc/init.d/wicd force-reload"
cmd_connect_wired = "/usr/bin/wicd-cli --wired -n0 -c"

subprocess.Popen(cmd_restart_wicd, shell=True)
subprocess.Popen(cmd_connect_wired, shell=True)
