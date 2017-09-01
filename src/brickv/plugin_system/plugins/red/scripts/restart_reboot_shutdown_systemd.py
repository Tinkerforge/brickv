#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import traceback
from sys import argv
from distutils.version import StrictVersion

CMD_REBOOT = "1"
CMD_SHUTDOWN = "2"
IMAGE_VERSION = None
MIN_VERSION_WITH_SYSTEMD = StrictVersion("1.4")

with open("/etc/tf_image_version", "r") as f:
    IMAGE_VERSION = StrictVersion(f.read().split(' ')[0].strip())

if len(argv) != 2:
    sys.stderr.write(u'Invalid number of arguments provided'.encode('utf-8'))
    exit(1)

try:
    if argv[1] == CMD_REBOOT:
        if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_SYSTEMD:
            os.system("/bin/systemctl reboot &> /dev/null")
        else:
            os.system("/sbin/init 6 &> /dev/null")
    elif argv[1] == CMD_SHUTDOWN:
        if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_SYSTEMD:
            os.system("/bin/systemctl poweroff &> /dev/null")
        else:
            os.system("/sbin/halt &> /dev/null")
    else:
        sys.stderr.write(u'Unknown command'.encode('utf-8'))
        exit(1)
except :
    traceback.print_exc()
    exit(1)
