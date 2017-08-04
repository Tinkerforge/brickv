#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import dbus
import json
import socket
import struct
import traceback
import ConfigParser
from sys import argv

NM_DEVICE_TYPE_ETHERNET = 1
NM_DEVICE_TYPE_WIFI = 2
INTERFACE_TYPE_WIRELESS = 1
INTERFACE_TYPE_WIRED = 2

DBUS_NM_BUS_NAME = "org.freedesktop.NetworkManager"
DBUS_NM_INTERFACE = "org.freedesktop.NetworkManager"
DBUS_NM_OBJECT_PATH = "/org/freedesktop/NetworkManager"
DBUS_PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"
DBUS_NM_DEVICE_INTERFACE = "org.freedesktop.NetworkManager.Device"
DBUS_NM_AP_INTERFACE = "org.freedesktop.NetworkManager.AccessPoint"
DBUS_NM_SETTINGS_INTERFACE = "org.freedesktop.NetworkManager.Settings"
DBUS_NM_SETTINGS_OBJECT_PATH = "/org/freedesktop/NetworkManager/Settings"
DBUS_NM_DEVICE_WIRELESS_INTERFACE = "org.freedesktop.NetworkManager.Device.Wireless"
DBUS_NM_SETTINGS_CONNECTION_INTERFACE = "org.freedesktop.NetworkManager.Settings.Connection"

if len(argv) != 2:
    exit (1)

try:
    dns_org = None
    wifi_address1 = None
    device_object_paths = None
    connection_type_to_delete = None
    connection_specific_object = None
    selected_device_object_path = None
    added_connection_object_path = None
    active_connection_object_path = None
    connection_config = json.loads(argv[1])

    # Disable all active wifi and ethernet connections.
    active_connection_object_paths = \
        dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                       dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_INTERFACE, "ActiveConnections")

    for active_connection_object_path in active_connection_object_paths:
        dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                       dbus_interface = DBUS_NM_INTERFACE).DeactivateConnection(active_connection_object_path)

    # Delete target WiFi and ethernet connections.
    connection_object_paths = \
        dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_SETTINGS_OBJECT_PATH),
                       dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_SETTINGS_INTERFACE, "Connections")

    if connection_config["connection"]["type"] == "802-11-wireless":
        connection_type_to_delete = "_tf_brickv_wifi"
    else:
        connection_type_to_delete = "_tf_brickv_ethernet"

    for connection_object_path in connection_object_paths:
        connection_settings  = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, connection_object_path),
                                              dbus_interface = DBUS_NM_SETTINGS_CONNECTION_INTERFACE).GetSettings()

        if connection_settings["connection"]["id"] == connection_type_to_delete:
            dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, connection_object_path),
                           dbus_interface = DBUS_NM_SETTINGS_CONNECTION_INTERFACE).Delete()

    # Reload connections.
    r = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_SETTINGS_OBJECT_PATH),
                       dbus_interface = DBUS_NM_SETTINGS_INTERFACE).ReloadConnections()

    if not r:
        exit(1)

    # Add new connection.

    # Prepare DNS entry.
    dns_org = connection_config["ipv4"]["dns"]

    if connection_config["ipv4"]["dns"] != "":
        connection_config["ipv4"]["dns"] = \
            [dbus.UInt32(struct.unpack("!L", socket.inet_aton(connection_config["ipv4"]["dns"]))[0])]
    else:
        connection_config["ipv4"]["dns"] = [dbus.UInt32(0L)]

    # Prepare address information entry.
    connection_config["ipv4"]["address-data"]["prefix"] = \
        dbus.UInt32(connection_config["ipv4"]["address-data"]["prefix"])
    connection_config["ipv4"]["address-data"] = \
        dbus.Array([connection_config["ipv4"]["address-data"]], signature = dbus.Signature("a{sv}"))

    # Get list of all available devices.
    device_object_paths = \
        dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                       dbus_interface = DBUS_NM_INTERFACE).GetDevices()

    # Do WiFi connection specific preparations.
    if connection_config["connection"]["type"] == "802-11-wireless":
        # Prepare SSID entry.
        connection_config["802-11-wireless"]["ssid"] = \
            dbus.ByteArray(connection_config["802-11-wireless"]["ssid"])

        # Prepare PSK flags entry.
        if '802-11-wireless-security' in connection_config:
            connection_config["802-11-wireless-security"]["psk-flags"] = \
                dbus.UInt32(connection_config["802-11-wireless-security"]["psk-flags"])

        for device_object_path in device_object_paths:
            device_type = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_object_path),
                                         dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_DEVICE_INTERFACE, "DeviceType")

            device_interface = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_object_path),
                                              dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_DEVICE_INTERFACE, "Interface")

            if device_type != NM_DEVICE_TYPE_WIFI:
                continue

            if device_interface != connection_config["connection"]["interface-name"]:
                continue

            ap_object_paths = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_object_path),
                                             dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_DEVICE_WIRELESS_INTERFACE, "AccessPoints")

            for ap_object_path in ap_object_paths:
                ap_ssid = str(bytearray(dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, ap_object_path),
                                        dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_AP_INTERFACE, "Ssid")))

                if connection_config["802-11-wireless"]["ssid"] != ap_ssid:
                    continue

                connection_specific_object = ap_object_path

                break

        if not connection_specific_object:
            exit(1)

    # Do ethernet connection specific preparations.
    elif connection_config["connection"]["type"] == "802-3-ethernet":
        connection_specific_object = "/"
    else:
        exit(1)

    for device_object_path in device_object_paths:
        interface = \
            dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_object_path),
                           dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_DEVICE_INTERFACE, "Interface")

        if interface == connection_config["connection"]["interface-name"]:
            selected_device_object_path = device_object_path

            break

    if not selected_device_object_path:
        exit(1)

    added_connection_object_path, active_connection_object_path = \
        dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                       dbus_interface = DBUS_NM_INTERFACE).AddAndActivateConnection(connection_config,
                                                                                    device_object_path,
                                                                                    connection_specific_object)

    if not added_connection_object_path or \
       not active_connection_object_path:
            exit(1)

    # Reload connections.
    r = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_SETTINGS_OBJECT_PATH),
                       dbus_interface = DBUS_NM_SETTINGS_INTERFACE).ReloadConnections()

    if not r:
        exit(1)

    # FIXME:
    #
    # For WiFi connections after the connection is initially activated,
    #
    # 1. Rename the connection file on the disk as the name is derived
    #    from the AP SSID.
    # 2. Modify some security and IPv4 related parameters in the conection file.
    # 3. Deactivate previously activated connection.
    # 4. Reload connections.
    # 5. Connect to the modified WiFi connection.
    #
    # This is required because Network Manager handles WiFi connections
    # in a dynamic way which heavily depends on the found APs and their
    # parameters. Even though the required connection parameters are
    # specified they are being modified after adding and activating the
    # connection.

    if connection_config["connection"]["type"] == "802-11-wireless":
        data_connection_file = None
        c_parser = ConfigParser.ConfigParser()
        connection_file_path = "/etc/NetworkManager/system-connections/_tf_brickv_wifi"
        added_connection_settings = \
            dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, added_connection_object_path),
                           dbus_interface = DBUS_NM_SETTINGS_CONNECTION_INTERFACE).GetSettings()

        # Deactivate connection.
        try:
            dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                           dbus_interface = DBUS_NM_INTERFACE).DeactivateConnection(active_connection_object_path)
        except:
            pass

        # Rename connection file.
        os.rename("/etc/NetworkManager/system-connections/" + added_connection_settings["connection"]["id"],
                  connection_file_path)

        # Modify connection file.
        c_parser.read(connection_file_path)

        c_parser.set("connection", "id", "_tf_brickv_wifi")

        if '802-11-wireless-security' in connection_config:
            c_parser.set("wifi-security", "auth-alg", "open")
            c_parser.set("wifi-security", "psk-flags", 0)
            c_parser.set("wifi-security", "psk", connection_config["802-11-wireless-security"]["psk"])

        if connection_config["ipv4"]["method"] == "manual":
            wifi_address1 = connection_config["ipv4"]["address-data"][0]["address"] + \
                            "/" + \
                            str(connection_config["ipv4"]["address-data"][0]["prefix"]) + \
                            "," + \
                            connection_config["ipv4"]["gateway"]

            c_parser.set("ipv4", "address1", wifi_address1)
            c_parser.set("ipv4", "dns", dns_org + ";")
            c_parser.set("ipv4", "method", "manual")
        else:
            c_parser.set("ipv4", "method", "auto")

        with open(connection_file_path, "w") as fh_connection:
            c_parser.write(fh_connection)

        # Reload connections.
        r = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_SETTINGS_OBJECT_PATH),
                           dbus_interface = DBUS_NM_SETTINGS_INTERFACE).ReloadConnections()

        if not r:
            exit(1)

        active_connection_object_path = \
            dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                           dbus_interface = DBUS_NM_INTERFACE).ActivateConnection(added_connection_object_path,
                                                                                  device_object_path,
                                                                                  connection_specific_object)

except:
    traceback.print_exc()
    exit(1)
