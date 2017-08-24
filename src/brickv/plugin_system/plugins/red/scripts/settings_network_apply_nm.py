#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import dbus
import time
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
DBUS_NM_SETTINGS_CONNECTION_ACTIVE_INTERFACE = 'org.freedesktop.NetworkManager.Connection.Active'

HIDDEN_AP_CMD_CON_RELOAD = "/usr/bin/nmcli connection reload"
HIDDEN_AP_CMD_UP = "/usr/bin/nmcli connection up _tf_brickv_wifi"
HIDDEN_AP_CMD_SET_PSK = "/usr/bin/nmcli connection modify _tf_brickv_wifi wifi-sec.psk {psk}"
HIDDEN_AP_CMD_SET_HIDDEN = "/usr/bin/nmcli connection modify _tf_brickv_wifi wifi.hidden yes"
HIDDEN_AP_CMD_SET_STATIC_DNS = "/usr/bin/nmcli connection modify _tf_brickv_wifi ipv4.dns \"{dns}\""
HIDDEN_AP_CMD_SET_WPA_PSK = "/usr/bin/nmcli connection modify _tf_brickv_wifi wifi-sec.key-mgmt wpa-psk"
HIDDEN_AP_CMD_ADD = "/usr/bin/nmcli connection add type wifi con-name _tf_brickv_wifi ifname {ifname} ssid {ssid}"
HIDDEN_AP_CMD_ADD_STATIC_IP = \
    "/usr/bin/nmcli connection add type wifi con-name _tf_brickv_wifi ifname {ifname} ssid {ssid} ip4 {ip4} gw4 {gw4}"

C_PARSER_WIFI = ConfigParser.ConfigParser()
C_PARSER_ETHERNET = ConfigParser.ConfigParser()
CONNECTED_HIDDEN_WIFI_NETWORKS_FILE_PATH = "/etc/tf_connected_hidden_wifi_networks"
WIFI_CONNECTION_FILE_PATH = "/etc/NetworkManager/system-connections/_tf_brickv_wifi"
ETHERNET_CONNECTION_FILE_PATH = "/etc/NetworkManager/system-connections/_tf_brickv_ethernet"

if len(argv) != 2:
    exit (1)

try:
    ip_org = None
    gw_org = None
    psk_org = None
    dns_org = None
    ssid_org = None
    ifname_org = None
    prefix_org = None
    wifi_address1 = None
    hidden_wifi_networks = []
    device_object_paths = None
    connection_type_to_delete = None
    hidden_wifi_network_found = False
    connection_specific_object = None
    selected_device_object_path = None
    added_connection_object_path = None
    active_connection_object_path = None
    connection_config = json.loads(argv[1])

    # Deactivate target WiFi and ethernet connections.
    active_connection_object_paths = \
        dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                       dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_INTERFACE, "ActiveConnections")

    for active_connection_object_path in active_connection_object_paths:
        connection_object_path = \
            dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, active_connection_object_path),
                           dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_SETTINGS_CONNECTION_ACTIVE_INTERFACE, "Connection")
        connection_settings = \
            dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, connection_object_path),
                           dbus_interface = DBUS_NM_SETTINGS_CONNECTION_INTERFACE).GetSettings()

        if connection_settings["connection"]["id"] != "_tf_brickv_wifi" \
           and connection_settings["connection"]["id"] != "_tf_brickv_ethernet":
                continue

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

    # Get the originals.
    dns_org = connection_config["ipv4"]["dns"]
    gw_org = connection_config["ipv4"]["gateway"]
    ip_org = connection_config["ipv4"]["address-data"]["address"]
    ifname_org = connection_config["connection"]["interface-name"]
    prefix_org = connection_config["ipv4"]["address-data"]["prefix"]

    # Add new connection.

    # Prepare DNS entry.
    if connection_config["ipv4"]["dns"] != "":
        connection_config["ipv4"]["dns"] = \
            [dbus.UInt32(struct.unpack("L", socket.inet_aton(connection_config["ipv4"]["dns"]))[0])]
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
        # Get the originals.
        ssid_org = connection_config["802-11-wireless"]["ssid"]

        if "802-11-wireless-security" in connection_config:
            psk_org = connection_config["802-11-wireless-security"]["psk"]

        # Prepare SSID entry.
        connection_config["802-11-wireless"]["ssid"] = \
            dbus.ByteArray(connection_config["802-11-wireless"]["ssid"])

        # Prepare PSK flags entry.
        if "802-11-wireless-security" in connection_config:
            connection_config["802-11-wireless-security"]["psk-flags"] = \
                dbus.UInt32(connection_config["802-11-wireless-security"]["psk-flags"])

        if not connection_config['802-11-wireless']['hidden']:
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

    if connection_config["connection"]["type"] == "802-11-wireless":
        if not connection_config['802-11-wireless']['hidden']:
            added_connection_object_path, active_connection_object_path = \
                dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                               dbus_interface = DBUS_NM_INTERFACE).AddAndActivateConnection(connection_config,
                                                                                            device_object_path,
                                                                                            connection_specific_object)
            if not added_connection_object_path or \
               not active_connection_object_path:
                    exit(1)
        else:
            if connection_config["ipv4"]["method"] == "manual":
                os.system(HIDDEN_AP_CMD_ADD_STATIC_IP.format(ifname = ifname_org,
                                                             ssid = ssid_org,
                                                             ip4 = ip_org + "/" + str(prefix_org),
                                                             gw4 = gw_org))

                os.system(HIDDEN_AP_CMD_SET_STATIC_DNS.format(dns = dns_org))
            else:
                os.system(HIDDEN_AP_CMD_ADD.format(ifname = ifname_org, ssid = ssid_org))

            os.system(HIDDEN_AP_CMD_SET_HIDDEN)

            if "802-11-wireless-security" in connection_config:
                os.system(HIDDEN_AP_CMD_SET_WPA_PSK)
                os.system(HIDDEN_AP_CMD_SET_PSK.format(psk = psk_org))

                C_PARSER_WIFI.read(WIFI_CONNECTION_FILE_PATH)

                C_PARSER_WIFI.set("wifi-security", "psk-flags", 0)
                C_PARSER_WIFI.set("wifi-security", "auth-alg", "open")

                with open(WIFI_CONNECTION_FILE_PATH, "w") as fh:
                    C_PARSER_WIFI.write(fh)

            if os.path.isfile(ETHERNET_CONNECTION_FILE_PATH):
                C_PARSER_ETHERNET.read(ETHERNET_CONNECTION_FILE_PATH)
                C_PARSER_ETHERNET.set("connection", "autoconnect", "false")

                with open(ETHERNET_CONNECTION_FILE_PATH, "w") as fh_connection:
                    C_PARSER_ETHERNET.write(fh_connection)

            os.system(HIDDEN_AP_CMD_CON_RELOAD)

            time.sleep(2)

            os.system(HIDDEN_AP_CMD_UP)

            if not os.path.isfile(CONNECTED_HIDDEN_WIFI_NETWORKS_FILE_PATH):
                with open(CONNECTED_HIDDEN_WIFI_NETWORKS_FILE_PATH, "w") as fh:
                    fh.write(ssid_org + "\n")
            else:
                with open(CONNECTED_HIDDEN_WIFI_NETWORKS_FILE_PATH, "r") as fh:
                    hidden_wifi_networks = fh.readlines()

                for n in hidden_wifi_networks:
                    if ssid_org == n.strip():
                        hidden_wifi_network_found = True

                        break

                if not hidden_wifi_network_found:
                    with open(CONNECTED_HIDDEN_WIFI_NETWORKS_FILE_PATH, "a") as fh:
                        fh.write(ssid_org + "\n")
    else:
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

    # FIXME: For WiFi connections after the connection is initially activated,
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
        if not connection_config['802-11-wireless']['hidden']:
            data_connection_file = None
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
                      WIFI_CONNECTION_FILE_PATH)

            # Modify connection file.
            C_PARSER_WIFI.read(WIFI_CONNECTION_FILE_PATH)

            C_PARSER_WIFI.set("connection", "id", "_tf_brickv_wifi")
            C_PARSER_WIFI.set("connection",
                              "interface-name",
                              connection_config["connection"]["interface-name"])

            if "802-11-wireless-security" in connection_config:
                C_PARSER_WIFI.set("wifi-security", "auth-alg", "open")
                C_PARSER_WIFI.set("wifi-security", "psk-flags", 0)
                C_PARSER_WIFI.set("wifi-security", "psk", connection_config["802-11-wireless-security"]["psk"])

            if connection_config["ipv4"]["method"] == "manual":
                wifi_address1 = connection_config["ipv4"]["address-data"][0]["address"] + \
                                "/" + \
                                str(connection_config["ipv4"]["address-data"][0]["prefix"]) + \
                                "," + \
                                connection_config["ipv4"]["gateway"]

                C_PARSER_WIFI.set("ipv4", "address1", wifi_address1)
                C_PARSER_WIFI.set("ipv4", "dns", dns_org + ";")
                C_PARSER_WIFI.set("ipv4", "method", "manual")
            else:
                C_PARSER_WIFI.set("ipv4", "method", "auto")

            with open(WIFI_CONNECTION_FILE_PATH, "w") as fh_connection:
                C_PARSER_WIFI.write(fh_connection)

            if os.path.isfile(ETHERNET_CONNECTION_FILE_PATH):
                C_PARSER_ETHERNET.read(ETHERNET_CONNECTION_FILE_PATH)
                C_PARSER_ETHERNET.set("connection", "autoconnect", "false")

                with open(ETHERNET_CONNECTION_FILE_PATH, "w") as fh_connection:
                    C_PARSER_ETHERNET.write(fh_connection)

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
    else:
        if os.path.isfile(WIFI_CONNECTION_FILE_PATH):
            C_PARSER_WIFI.read(WIFI_CONNECTION_FILE_PATH)
            C_PARSER_WIFI.set("connection", "autoconnect", "false")

            with open(WIFI_CONNECTION_FILE_PATH, "w") as fh_connection:
                C_PARSER_WIFI.write(fh_connection)

        # Reload connections.
        r = dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_SETTINGS_OBJECT_PATH),
                           dbus_interface = DBUS_NM_SETTINGS_INTERFACE).ReloadConnections()
except:
    traceback.print_exc()
    exit(1)
