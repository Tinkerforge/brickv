#!/usr/bin/env python2

import time
import subprocess

cmd_restart_wicd = "/etc/init.d/wicd force-reload"
subprocess.Popen(cmd_restart_wicd, shell=True)
time.sleep(5)
