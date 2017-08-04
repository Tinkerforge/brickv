#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import dbus
import json
import socket
import traceback
import netifaces

TYPE_WIRELESS = 1
TYPE_WIRED = 2

NM_STATE_UNKNOWN = 0
NM_STATE_ASLEEP = 10
NM_STATE_DISCONNECTED = 20
NM_STATE_DISCONNECTING = 30
NM_STATE_CONNECTING = 40
NM_STATE_CONNECTED_LOCAL = 50
NM_STATE_CONNECTED_SITE = 60
NM_STATE_CONNECTED_GLOBAL = 70

NM_DEVICE_TYPE_ETHERNET = 1
NM_DEVICE_TYPE_WIFI = 2

DBUS_NM_BUS_NAME = "org.freedesktop.NetworkManager"
DBUS_NM_INTERFACE = "org.freedesktop.NetworkManager"
DBUS_NM_OBJECT_PATH = "/org/freedesktop/NetworkManager"
DBUS_PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"
DBUS_NM_DEVICE_INTERFACE = "org.freedesktop.NetworkManager.Device"
DBUS_NM_AP_INTERFACE = "org.freedesktop.NetworkManager.AccessPoint"
DBUS_NM_DEVICE_WIRELESS_INTERFACE = "org.freedesktop.NetworkManager.Device.Wireless"

return_dict = {}
return_dict['cstat_hostname'] = None
return_dict['cstat_status'] = None
return_dict['cstat_intf_active'] = {'name': None, 'type': None, 'ip': None, 'mask': None}
return_dict['cstat_gateway'] = None
return_dict['cstat_dns'] = None

nm_state = None
gw_interface = None
gw_interface_type = None

try:
    if DBUS_NM_BUS_NAME not in dbus.SystemBus().list_names():
        # NetworkManager not running
        exit(1)
except:
    traceback.print_exc()
    exit(1)

def get_active_interface_info(interface, intf_type):
    try:
        ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
        netmask = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['netmask']
        return_dict['cstat_intf_active']['name'] = interface
        return_dict['cstat_intf_active']['type'] = intf_type
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
    traceback.print_exc()
    exit(1)

# Get default gateway
try:
    gws = netifaces.gateways()

    if 'default' in gws and netifaces.AF_INET in gws['default']:
        return_dict['cstat_gateway'] = gws['default'][netifaces.AF_INET][0]
        gw_interface = gws['default'][netifaces.AF_INET][1]

        nm_devices = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                                    dbus_interface = DBUS_NM_INTERFACE).GetDevices()

        for device_object_path in nm_devices:
            interface_name = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_object_path),
                                            dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_DEVICE_INTERFACE, "Interface")

            interface_type = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_object_path),
                                            dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_DEVICE_INTERFACE, "DeviceType")

            if interface_name != gw_interface:
                continue

            if interface_type == NM_DEVICE_TYPE_ETHERNET:
                gw_interface_type = TYPE_WIRED

                break

            elif interface_type == NM_DEVICE_TYPE_WIFI:
                gw_interface_type = TYPE_WIRELESS

                break

        get_active_interface_info(gw_interface, gw_interface_type)
except:
    traceback.print_exc()
    exit(1)

# Get status and active interface
try:
    if gw_interface != None and gw_interface_type != None:
        nm_state = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                                  dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_INTERFACE, "State")

        return_dict['cstat_status'] = ""

        if nm_state == NM_STATE_UNKNOWN:
            return_dict['cstat_status'] = "Unknown"
        elif nm_state == NM_STATE_ASLEEP:
            return_dict['cstat_status'] = "Sleeping"
        elif nm_state == NM_STATE_DISCONNECTED:
            return_dict['cstat_status'] = "Disconnected"
        elif nm_state == NM_STATE_DISCONNECTING:
            return_dict['cstat_status'] = "Disconnecting"
        elif nm_state == NM_STATE_CONNECTING:
            return_dict['cstat_status'] = "Connecting"
        elif nm_state == NM_STATE_CONNECTED_LOCAL:
            return_dict['cstat_status'] = "Disconnected"
        elif nm_state == NM_STATE_CONNECTED_SITE:
            return_dict['cstat_status'] = "Connected Local"
        elif nm_state == NM_STATE_CONNECTED_GLOBAL:
            return_dict['cstat_status'] = "Connected"
        else:
            return_dict['cstat_status'] = "Unknown"

        if nm_state == NM_STATE_CONNECTED_SITE or nm_state == NM_STATE_CONNECTED_GLOBAL:
            if gw_interface_type == TYPE_WIRELESS:
                nm_devices = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                                            dbus_interface = DBUS_NM_INTERFACE).GetDevices()
                for device_object in nm_devices:
                    device_name = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_object),
                                                 dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_DEVICE_INTERFACE, "Interface")

                    device_type = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_object),
                                                 dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_DEVICE_INTERFACE, "DeviceType")

                    if device_type != NM_DEVICE_TYPE_WIFI or device_name != gw_interface:
                        continue

                    device_active_ap_object_path = \
                        dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_object),
                                       dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_DEVICE_WIRELESS_INTERFACE, "ActiveAccessPoint")

                    active_ap_ssid = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_active_ap_object_path),
                                                    dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_AP_INTERFACE, "Ssid")

                    return_dict['cstat_status'] = return_dict['cstat_status'] + " to " + str(bytearray(active_ap_ssid))

                    break
    else:
        return_dict['cstat_status'] = 'Disconnected'
except:
    return_dict['cstat_status'] = '-'

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
