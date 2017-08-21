#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import dbus
import traceback
import ConfigParser

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
config_wifi_ssid = None
config_wifi_hidden = None
c_parser_wifi_config = None

if os.path.isfile("/etc/NetworkManager/system-connections/_tf_brickv_wifi"):
    try:
        c_parser_wifi_config = ConfigParser.ConfigParser()

        c_parser_wifi_config.read("/etc/NetworkManager/system-connections/_tf_brickv_wifi")

        config_wifi_ssid = c_parser_wifi_config.get("wifi", "ssid", "")
        config_wifi_hidden = c_parser_wifi_config.get("wifi", "hidden", "")
    except:
        pass

try:
    if DBUS_NM_BUS_NAME not in dbus.SystemBus().list_names():
        # NetworkManager not running
        exit(1)
except:
    traceback.print_exc()
    exit(1)

try:
    # Try to request scan with all available WiFi interfaces. Ignore errors.
    nm_devices = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                                dbus_interface = DBUS_NM_INTERFACE).GetDevices()

    try:
        for device_object_path in nm_devices:
            device_type = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_object_path),
                                         dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_DEVICE_INTERFACE, "DeviceType")

            if device_type != NM_DEVICE_TYPE_WIFI:
                continue

            device_type = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_object_path),
                                         dbus_interface = DBUS_NM_DEVICE_WIRELESS_INTERFACE).RequestScan(dbus.Array([], signature = dbus.Signature("a{sv}")))
    except:
        pass

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

            if c_parser_wifi_config \
               and config_wifi_ssid \
               and config_wifi_hidden:
                    if config_wifi_ssid == str(bytearray(ap_props["Ssid"])):
                        continue

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
                        "essid": str(bytearray(ap_props["Ssid"])),
                        "bssid": ap_props["HwAddress"],
                        "channel": ap_props["Frequency"],
                        "encryption": encryption,
                        "encryption_method": encryption_method,
                        "quality": int(ap_props["Strength"])
                     }

            return_dict[nidx] = apdict

        if len(return_dict) > 0:
            break
except:
    traceback.print_exc()
    exit(1)

print(json.dumps(return_dict, separators=(",", ":")))
