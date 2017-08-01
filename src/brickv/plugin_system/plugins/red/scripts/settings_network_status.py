#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import dbus
import json
import socket
import netifaces
from wicd import dbusmanager as wicd_dbusmanager
from wicd import misc as wicd_misc

TYPE_WIRELESS = 1
TYPE_WIRED = 2

return_dict = {}
return_dict['cstat_hostname'] = None
return_dict['cstat_status'] = None
return_dict['cstat_intf_active'] = {'name': None, 'type': None, 'ip': None, 'mask': None}
return_dict['cstat_gateway'] = None
return_dict['cstat_dns'] = None

def get_active_interface_info(interface, type):
    try:
        ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
        netmask = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['netmask']
        return_dict['cstat_intf_active']['name'] = interface
        return_dict['cstat_intf_active']['type'] = type
        return_dict['cstat_intf_active']['ip'] = ip
        return_dict['cstat_intf_active']['mask'] = netmask
    except:
        return_dict['cstat_intf_active']['name'] = None
        return_dict['cstat_intf_active']['type'] = '-'
        return_dict['cstat_intf_active']['ip'] = '-'
        return_dict['cstat_intf_active']['mask'] = '-'

# Get hostname
try:
    hname = unicode(socket.gethostname())
    if hname != '':
        return_dict['cstat_hostname'] = hname
except:
    exit(1)

# Get status and active interface
try:
    # Initially return_dict['cstat_intf_active']['name'] None because this field is
    # appended with interface type and to avoid appending interface type when no interface is found
    return_dict['cstat_intf_active']['name'] = None
    return_dict['cstat_intf_active']['type'] = '-'
    return_dict['cstat_intf_active']['ip'] = '-'
    return_dict['cstat_intf_active']['mask'] = '-'

    bus = dbus.SystemBus()
    daemon = dbus.Interface(bus.get_object('org.wicd.daemon', '/org/wicd/daemon'), 'org.wicd.daemon')
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
                    return_dict['cstat_status'] = 'Connected to ' + ap_array[0]
                else:
                    return_dict['cstat_status'] = 'Connected to ' + ap

                get_active_interface_info(unicode(daemon.GetWirelessInterface()), TYPE_WIRELESS)

            else:
                return_dict['cstat_status'] = '-'

    elif status == wicd_misc.WIRED:
        return_dict['cstat_status'] = 'Connected'
        get_active_interface_info(unicode(daemon.GetWiredInterface()), TYPE_WIRED)

    elif status[0] == wicd_misc.SUSPENDED:
        return_dict['cstat_status'] = 'Suspended'

    else:
        if status[0] == 3:
            return_dict['cstat_status'] = 'Connected'
            get_active_interface_info(unicode(daemon.GetWiredInterface()), TYPE_WIRED)
        else:
            return_dict['cstat_status'] = 'Unknown ({0})'.format(status[0])
except:
    return_dict['cstat_status'] = '-'

# Get default gateway
try:
    gws = netifaces.gateways()

    if 'default' in gws and netifaces.AF_INET in gws['default']:
        return_dict['cstat_gateway']  = gws['default'][netifaces.AF_INET][0]
except:
    exit(1)

# Get DNS
try:
    with open('/etc/resolv.conf', 'r') as rcf:
        dns_servers = []
        lines = rcf.readlines()

        for l in lines:
            l_splitted = l.split(' ')

            if l_splitted[0] == 'nameserver' and l_splitted[1] != '':
                dns_servers.append(l_splitted[1].strip())

        if len(dns_servers) <= 0:
            return_dict['cstat_dns'] = '-'
        else:
            return_dict['cstat_dns'] = ', '.join(dns_servers)
except:
    return_dict['cstat_dns'] = None

print(json.dumps(return_dict, separators=(',', ':')))
