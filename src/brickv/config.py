# -*- coding: utf-8 -*-

# brickv config

import sys
from config_common import *

def get_host(): return DEFAULT_HOST
def set_host(host): pass
def get_host_history(size): return []
def set_host_history(history): pass
def get_port(): return DEFAULT_PORT
def set_port(port): pass

if sys.platform.startswith('linux') or sys.platform.startswith('freebsd'):
    from config_linux import *
elif sys.platform == 'darwin':
    from config_macosx import *
elif sys.platform == 'win32':
    from config_windows import *
else:
    print "Unsupported platform: " + sys.platform
