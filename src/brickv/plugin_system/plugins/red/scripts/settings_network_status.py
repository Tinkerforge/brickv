#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import socket
import netifaces
import subprocess
from wicd import dbusmanager as wicd_dbusmanager
from wicd import misc as wicd_misc

return_dict = {}
return_dict['cstat_hostname'] = None
return_dict['cstat_intf_active'] = {'name': None, 'type': None, 'ip': None, 'mask': None}
return_dict['cstat_gateway'] = None
return_dict['cstat_dns'] = None
return_dict['cstat_status'] = None

try:
    hname = unicode(socket.gethostname())
    if hname != '':
        return_dict['cstat_hostname'] = hname
except:
    exit(1)

try:
    cmd_get_if_ok = "ip route | head -1 | awk -F' ' '{print $1}'"
    ps_get_if_ok = subprocess.Popen(cmd_get_if_ok, shell=True, stdout=subprocess.PIPE)
    intf_ok = ps_get_if_ok.communicate()[0].strip()
    if ps_get_if_ok.returncode:
        exit(1)
    if intf_ok == 'default':
        cmd_get_if_active = "ip route | head -1 | awk -F' ' '{print $5}'"
        ps_get_if_active = subprocess.Popen(cmd_get_if_active, shell=True, stdout=subprocess.PIPE)
        intf_active = ps_get_if_active.communicate()[0].strip()
        if ps_get_if_active.returncode:
            exit(1)
    else:
        intf_active = ''

    if intf_active != '':
        return_dict['cstat_intf_active']['name'] = intf_active
        for intf in netifaces.interfaces():
            if intf == intf_active:
                if os.path.isdir('/sys/class/net/'+intf_active+'/wireless'):
                    return_dict['cstat_intf_active']['type'] = 1
                else:
                    return_dict['cstat_intf_active']['type'] = 2
                break
        intf_addrs = netifaces.ifaddresses(intf_active)
        if netifaces.AF_INET in intf_addrs and\
           'addr' in intf_addrs[netifaces.AF_INET][0] and\
           'netmask' in intf_addrs[netifaces.AF_INET][0]:
            return_dict['cstat_intf_active']['ip'] = intf_addrs[netifaces.AF_INET][0]['addr']
            return_dict['cstat_intf_active']['mask'] = intf_addrs[netifaces.AF_INET][0]['netmask']

    gws = netifaces.gateways()
    if 'default' in gws and netifaces.AF_INET in gws['default']:
        return_dict['cstat_gateway']  = gws['default'][netifaces.AF_INET][0]
except:
    exit(1)

try:
    with open('/etc/resolv.conf', 'r') as rcf:
        lines = rcf.readlines()
        for i, l in enumerate(lines):
            l_splitted = l.split(' ')
            if l_splitted[0] == 'nameserver' and l_splitted[1] != '':
                return_dict['cstat_dns'] = l_splitted[1]
                break
except:
    return_dict['cstat_dns'] = None

try:
    wicd_dbusmanager.connect_to_dbus()
    status = wicd_dbusmanager.get_dbus_ifaces()['daemon'].GetConnectionStatus()

    if status[0] == wicd_misc.NOT_CONNECTED:
        return_dict['cstat_status'] = 'Not connected'
    elif status[0] == wicd_misc.CONNECTING:
        return_dict['cstat_status'] = 'Connecting ({0})...'.format(status[1][0][0].upper() + status[1][0][1:])
    elif status[0] == wicd_misc.WIRELESS:
        try:
            iwconfig = wicd_dbusmanager.get_dbus_ifaces()['wireless'].GetIwconfig()
            ap = unicode(wicd_dbusmanager.get_dbus_ifaces()['wireless'].GetCurrentNetwork(iwconfig))
        except:
            return_dict['cstat_status'] = '-'
        else:
            if ap != 'None':
                ap_array = ap.split('"')
                if len(ap_array) > 1:
                    return_dict['cstat_status'] = 'Connected to '+ap_array[0]
                else:
                    return_dict['cstat_status'] = 'Connected to '+ap
            else:
                return_dict['cstat_status'] = '-'
    elif status == wicd_misc.WIRED:
        return_dict['cstat_status'] = 'Connected'
    elif status[0] == wicd_misc.SUSPENDED:
        return_dict['cstat_status'] = 'Suspended'
    else:
        if status[0] == 3:
            return_dict['cstat_status'] = 'Connected'
        else:
            return_dict['cstat_status'] = 'Unknown ({0})'.format(status[0])
except:
    return_dict['cstat_status'] = '-'

print json.dumps(return_dict)
