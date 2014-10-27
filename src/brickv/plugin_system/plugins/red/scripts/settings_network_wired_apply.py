#!/usr/bin/env python2

import subprocess

cmd = "/etc/init.d/wicd force-reload && /usr/bin/wicd-cli --wired -n0 -c"

subprocess.Popen(cmd, shell=True)
