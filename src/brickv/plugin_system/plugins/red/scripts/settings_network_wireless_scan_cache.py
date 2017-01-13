#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import dbus
import subprocess

return_dict = None

try:
    bus = dbus.SystemBus()
    wireless = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon/wireless'),
                                             'org.wicd.daemon.wireless')
except:
    exit(1)

return_dict = {}

for network_id in range(0, wireless.GetNumberOfNetworks()):
    try:
        essid = wireless.GetWirelessProperty(network_id, 'essid')
        bssid = wireless.GetWirelessProperty(network_id, 'bssid')
        channel = wireless.GetWirelessProperty(network_id, 'channel')
        quality = wireless.GetWirelessProperty(network_id, 'quality')

        # Ignore hidden wireless networks in scan result.
        if str(essid) == '<hidden>':
            continue

        if wireless.GetWirelessProperty(network_id, "encryption"):
            encryption = 'On'
            encryption_method = wireless.GetWirelessProperty(network_id, "encryption_method")
        else:
            encryption = 'Off'
            encryption_method = None

        ap_exists = False

        for key, ap in return_dict.items():
            if str(ap['bssid']) == str(bssid):
                ap_exists = True
                break

        if ap_exists:
            continue

        _apdict = {'essid':essid,
                   'bssid':bssid,
                   'channel':channel,
                   'encryption':encryption,
                   'encryption_method':encryption_method,
                   'quality':quality}

        return_dict[network_id] = _apdict
    except:
        pass

print(json.dumps(return_dict, separators=(',', ':')))
