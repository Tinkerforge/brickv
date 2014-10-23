#!/usr/bin/env python2

import time
import subprocess

cmd_restart_wicd = "/etc/init.d/wicd force-reload"
cmd_connect_wired = "/usr/bin/wicd-cli --wired -n0 -c"

subprocess.Popen(cmd_restart_wicd, shell=True)
time.sleep(5)
subprocess.Popen(cmd_connect_wired, shell=True)
