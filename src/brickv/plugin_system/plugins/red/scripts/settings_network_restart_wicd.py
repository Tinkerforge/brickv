#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os

wicd_restart_cmd = '/usr/sbin/service wicd restart && /bin/sleep 2'
wicd_restart_cmd_code = os.system(wicd_restart_cmd)

if wicd_restart_cmd_code:
    exit(1)
