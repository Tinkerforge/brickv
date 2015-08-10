#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import dbus
import ConfigParser
import json
import subprocess
import time
from sys import argv

if len(argv) < 3:
    exit (1)

iname_scan_with = unicode(argv[1])
iname_restore_to = unicode(argv[2])

return_dict = None

config = ConfigParser.ConfigParser()

def set_wireless_interface(interface):
    try:
        with open('/etc/wicd/manager-settings.conf', 'r') as msfp_r:
            config.readfp(msfp_r)
            with open('/etc/wicd/manager-settings.conf', 'w') as msfp_w:
                config.set('Settings', 'wireless_interface', interface)
                config.write(msfp_w)
                wicd_restart_cmd = '/usr/sbin/service wicd restart && :'
                wicd_restart_ps = subprocess.Popen(wicd_restart_cmd, shell=True, stdout=subprocess.PIPE)
                wicd_restart_ps.communicate()[0]
                if wicd_restart_ps.returncode:
                    exit(1)
                else:
                    time.sleep(10)
    except:
        exit(1)

set_wireless_interface(iname_scan_with)

try:
    bus = dbus.SystemBus()
    wireless = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon/wireless'),
                                             'org.wicd.daemon.wireless')
    wireless.Scan(True)
except:
    set_wireless_interface(iname_restore_to)
    exit(1)

return_dict = {}

for network_id in range(0, wireless.GetNumberOfNetworks()):
    try:
        essid = wireless.GetWirelessProperty(network_id, 'essid')
        bssid = wireless.GetWirelessProperty(network_id, 'bssid')
        channel = wireless.GetWirelessProperty(network_id, 'channel')
        quality = wireless.GetWirelessProperty(network_id, 'quality')

        if wireless.GetWirelessProperty(network_id, "encryption"):
            encryption = 'On'
            encryption_method = wireless.GetWirelessProperty(network_id, "encryption_method")
        else:
            encryption = 'Off'
            encryption_method = None

        _apdict = {'essid':essid,
                   'bssid':bssid,
                   'channel':channel,
                   'encryption':encryption,
                   'encryption_method':encryption_method,
                   'quality':quality}
        return_dict[network_id] = _apdict
    except:
        pass

set_wireless_interface(iname_restore_to)

print json.dumps(return_dict, separators=(',', ':'))
