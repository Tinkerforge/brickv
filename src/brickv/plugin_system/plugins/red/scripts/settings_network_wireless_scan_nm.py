#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import dbus

NM_DEVICE_TYPE_WIFI = 2

NM_802_11_AP_SEC_NONE_MASK = 0x00000000
NM_802_11_AP_SEC_KEY_MGMT_PSK_MASK = 0x00000100

DBUS_NM_BUS_NAME = "org.freedesktop.NetworkManager"
DBUS_NM_INTERFACE = "org.freedesktop.NetworkManager"
DBUS_NM_OBJECT_PATH = "/org/freedesktop/NetworkManager"
DBUS_PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"
DBUS_NM_DEVICE_INTERFACE = "org.freedesktop.NetworkManager.Device"
DBUS_NM_AP_INTERFACE = "org.freedesktop.NetworkManager.AccessPoint"
DBUS_NM_DEVICE_WIRELESS_INTERFACE = "org.freedesktop.NetworkManager.Device.Wireless"

return_dict = {}

try:
    if DBUS_NM_BUS_NAME not in dbus.SystemBus().list_names():
        # NetworkManager not running
        exit(1)
except:
    exit(1)

try:
    nm_devices = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                                dbus_interface = DBUS_NM_INTERFACE).GetDevices()

    for device_object_path in nm_devices:
        device_type = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_object_path),
                                     dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_DEVICE_INTERFACE, "DeviceType")

        if device_type != NM_DEVICE_TYPE_WIFI:
            continue

        ap_object_paths = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_object_path),
                                         dbus_interface = DBUS_NM_DEVICE_WIRELESS_INTERFACE).GetAccessPoints()

        for ap_object_path in ap_object_paths:
            nidx = ap_object_path.split("/")[-1]

            ap_props = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, ap_object_path),
                                      dbus_interface = DBUS_PROPERTIES_INTERFACE).GetAll(DBUS_NM_AP_INTERFACE)

            flags = 0
            only_wpa1 = False

            if ap_props["WpaFlags"] == 0 and ap_props["RsnFlags"] == 0:
                encryption = "Off"
                encryption_method = "Unsupported"
            else:
                if ap_props["RsnFlags"] == 0:
                    flags = ap_props["WpaFlags"]
                    only_wpa1 = True
                elif ap_props["WpaFlags"] == 0:
                    flags = ap_props["RsnFlags"]
                else:
                    flags = ap_props["RsnFlags"]

                if flags & NM_802_11_AP_SEC_NONE_MASK:
                    encryption = "Off"
                else:
                    encryption = "On"

                if not flags & NM_802_11_AP_SEC_NONE_MASK:
                    if flags & NM_802_11_AP_SEC_KEY_MGMT_PSK_MASK:
                        if only_wpa1:
                            encryption_method = "WPA1"
                        else:
                            encryption_method = "WPA2"
                    else:
                        encryption_method = "Unsupported"

            apdict = {
                        'essid': str(bytearray(ap_props["Ssid"])),
                        'bssid': ap_props["HwAddress"],
                        'channel': ap_props["Frequency"],
                        'encryption': encryption,
                        'encryption_method': encryption_method,
                        'quality': int(ap_props["Strength"])
                     }

            return_dict[nidx] = apdict

        if len(return_dict) > 0:
            break
except:
    exit(1)

print(json.dumps(return_dict, separators=(',', ':')))
