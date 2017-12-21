#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import StringIO
import traceback
import netifaces
import subprocess
import ConfigParser
from sys import argv
from distutils.version import StrictVersion

IMAGE_VERSION = None
MIN_VERSION_FOR_NAT = StrictVersion('1.7')
MIN_VERSION_WITH_NM = StrictVersion('1.10')
MIN_VERSION_FOR_HOSTAPD_UPDATE_1 = StrictVersion('1.10')

with open('/etc/tf_image_version', 'r') as f:
    IMAGE_VERSION = StrictVersion(f.read().split(' ')[0].strip())

PY_SETUP_AP_NAT = '''
#!/usr/bin/env python2
# -*- coding: utf-8 -*

import os
import dbus
import ConfigParser
from xml.dom import minidom

DBUS_MM_BUS_NAME = 'org.freedesktop.ModemManager1'
DBUS_MM_OBJECT_PATH = '/org/freedesktop/ModemManager1'
DBUS_MM_SIM_INTERFACE = 'org.freedesktop.ModemManager1.Sim'
DBUS_PROPERTIES_INTERFACE = 'org.freedesktop.DBus.Properties'
DBUS_MM_MODEM_INTERFACE = 'org.freedesktop.ModemManager1.Modem'
DBUS_MM_BEARER_INTERFACE = 'org.freedesktop.ModemManager1.Bearer'
DBUS_MM_MODEM_OBJECT_PATH = '/org/freedesktop/ModemManager1/Modem'
DBUS_INTROSPECTABLE_INTERFACE = 'org.freedesktop.DBus.Introspectable'
DBUS_MM_MODEM_SIMPLE_INTERFACE = 'org.freedesktop.ModemManager1.Modem.Simple'

DBUS_NM_BUS_NAME = 'org.freedesktop.NetworkManager'
DBUS_NM_INTERFACE = 'org.freedesktop.NetworkManager'
DBUS_NM_OBJECT_PATH = '/org/freedesktop/NetworkManager'
DBUS_PROPERTIES_INTERFACE = 'org.freedesktop.DBus.Properties'
DBUS_NM_DEVICE_INTERFACE = 'org.freedesktop.NetworkManager.Device'
DBUS_NM_AP_INTERFACE = 'org.freedesktop.NetworkManager.AccessPoint'
DBUS_NM_SETTINGS_INTERFACE = 'org.freedesktop.NetworkManager.Settings'
DBUS_NM_SETTINGS_OBJECT_PATH = '/org/freedesktop/NetworkManager/Settings'
DBUS_NM_DEVICE_WIRELESS_INTERFACE = 'org.freedesktop.NetworkManager.Device.Wireless'
DBUS_NM_SETTINGS_CONNECTION_INTERFACE = 'org.freedesktop.NetworkManager.Settings.Connection'
DBUS_NM_SETTINGS_CONNECTION_ACTIVE_INTERFACE = 'org.freedesktop.NetworkManager.Connection.Active'

NM_DEVICE_TYPE_MODEM = 8
NM_DEVICE_STATE_ACTIVATED = 100

def deactivate_ethernet_connections():
    active_connection_object_paths = \
        dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                       dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_INTERFACE, 'ActiveConnections')

    for active_connection_object_path in active_connection_object_paths:
        connection_object_path = \
            dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, active_connection_object_path),
                           dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_NM_SETTINGS_CONNECTION_ACTIVE_INTERFACE, 'Connection')
        connection_settings = \
            dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, connection_object_path),
                           dbus_interface = DBUS_NM_SETTINGS_CONNECTION_INTERFACE).GetSettings()

        if connection_settings['connection']['type'] != 'ethernet' \
           and connection_settings['connection']['type'] != '802-3-ethernet':
                continue

        dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                       dbus_interface = DBUS_NM_INTERFACE).DeactivateConnection(active_connection_object_path)

def get_mm_modem_object_paths():
    modem_object_path_list = []

    xml = dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME,
                                                     DBUS_MM_MODEM_OBJECT_PATH),
                         dbus_interface = DBUS_INTROSPECTABLE_INTERFACE).Introspect()
    xml_parsed = minidom.parseString(xml)
    items = xml_parsed.getElementsByTagName('node')

    items.pop(0)

    for i in items:
        try:
            v = int(i.attributes['name'].value)
        except:
            continue

        modem_object_path_list.append('/org/freedesktop/ModemManager1/Modem/' + str(v))

    return modem_object_path_list

modem_imei = ''
modem_primary_port = ''
c_parser_config = ConfigParser.ConfigParser()

deactivate_ethernet_connections()

if not os.path.isfile('/etc/tf_mobile_internet_enabled'):
    exit(0)

c_parser_config.read('/etc/tf_mobile_internet_enabled')
modem_imei = c_parser_config.get('configuration', 'modem-imei', '')

if not modem_imei:
    exit(0)

modem_object_path_list = get_mm_modem_object_paths()

for o in modem_object_path_list:
    ip_interface_found = False

    imei = \
        dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                       dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'EquipmentIdentifier')

    if imei != modem_imei:
        continue

    modem_primary_port = \
        dbus.Interface(dbus.SystemBus().get_object(DBUS_MM_BUS_NAME, o),
                       dbus_interface = DBUS_PROPERTIES_INTERFACE).Get(DBUS_MM_MODEM_INTERFACE, 'PrimaryPort')

    nm_devices = \
        dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, DBUS_NM_OBJECT_PATH),
                       dbus_interface = DBUS_NM_INTERFACE).GetDevices()

    for device_object_path in nm_devices:
        device_properties = \
            dbus.Interface(dbus.SystemBus().get_object(DBUS_NM_BUS_NAME, device_object_path),
                           dbus_interface = DBUS_PROPERTIES_INTERFACE).GetAll(DBUS_NM_DEVICE_INTERFACE)

        if device_properties['DeviceType'] != NM_DEVICE_TYPE_MODEM:
            continue

        if device_properties['State'] != NM_DEVICE_STATE_ACTIVATED:
            continue

        if device_properties['Interface'] != modem_primary_port:
            continue

        os.system('/sbin/iptables -t nat -D POSTROUTING -o ' + device_properties['IpInterface'] + ' -j MASQUERADE &> /dev/null')
        os.system('/sbin/iptables -D FORWARD -i {0} -j ACCEPT &> /dev/null')
        os.system('/sbin/iptables -t nat -A POSTROUTING -o ' + device_properties['IpInterface'] + ' -j MASQUERADE &> /dev/null')
        os.system('/sbin/iptables -A FORWARD -i {0} -j ACCEPT &> /dev/null')

        ip_interface_found = True

        break

    if ip_interface_found:
        break
'''

SH_SETUP_AP_NAT = '''
#! /bin/bash

gw=$(/sbin/route | /usr/bin/awk '{{if($1=="default") print $8}}')

if [ ! -z "$gw" ] && [ $gw != '{0}' ]; then
    /sbin/iptables -t nat -D POSTROUTING -o $gw -j MASQUERADE &> /dev/null
    /sbin/iptables -D FORWARD -i {0} -j ACCEPT &> /dev/null
    /sbin/iptables -t nat -A POSTROUTING -o $gw -j MASQUERADE &> /dev/null
    /sbin/iptables -A FORWARD -i {0} -j ACCEPT &> /dev/null
fi
'''

UNIT_SETUP_AP_NAT = '''[Unit]
Description=Service to setup/update NAT configuration
Wants=network.target network-online.target
After=network.target network-online.target

[Service]
Type=oneshot
ExecStart={0}

[Install]
WantedBy=default.target
'''

TIMER_SETUP_AP_NAT = '''[Unit]
Description=Execute tf_setup_ap_nat.service every 5 seconds

[Timer]
OnUnitActiveSec=5s
Unit=tf_setup_ap_nat.service

[Install]
WantedBy=timers.target
'''

HOSTAPD_CONF = '''# Checkout https://w1.fi/cgit/hostap/plain/hostapd/hostapd.conf
# for the details of the configuration parameters in this file.
interface={0}
{1}
ssid={2}
channel={3}
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid={4}
wpa=2
wpa_passphrase={5}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
ieee80211n=1
hw_mode=g
'''

DNSMASQ_CONF = '''{0}
no-poll
no-hosts
no-resolv
bogus-priv
expand-hosts
domain-needed
dhcp-authoritative
listen-address=127.0.0.1
listen-address={1}
server=8.8.8.8
local=/{2}/127.0.0.1
domain={2}
host-record={2},{1}
ptr-record={3}.in-addr.arpa,"{2}"
dhcp-range={4},{5},72h
dhcp-option=option:netmask,{6}
dhcp-option=option:router,{1}
dhcp-option=option:dns-server,{1}
dhcp-option=option:ip-forward-enable,0
dhcp-option=option:netbios-nodetype,8
'''

INTERFACES_CONF = '''# interfaces(5) file used by ifup(8) and ifdown(8)
auto lo
iface lo inet loopback

auto {0}
allow-hotplug {0}
iface {0} inet static
    address {1}
    netmask {2}
'''

DEFAULT_DNSMASQ = '''# This file has five functions:
# 1) to completely disable starting dnsmasq,
# 2) to set DOMAIN_SUFFIX by running `dnsdomainname`
# 3) to select an alternative config file
#    by setting DNSMASQ_OPTS to --conf-file=<file>
# 4) to tell dnsmasq to read the files in /etc/dnsmasq.d for
#    more configuration variables.
# 5) to stop the resolvconf package from controlling dnsmasq's
#    idea of which upstream nameservers to use.
# For upgraders from very old versions, all the shell variables set
# here in previous versions are still honored by the init script
# so if you just keep your old version of this file nothing will break.

#DOMAIN_SUFFIX=`dnsdomainname`
#DNSMASQ_OPTS="--conf-file=/etc/dnsmasq.alt"

# Whether or not to run the dnsmasq daemon; set to 0 to disable.
ENABLED=1

# By default search this drop directory for configuration options.
# Libvirt leaves a file here to make the system dnsmasq play nice.
# Comment out this line if you don't want this. The dpkg-* are file
# endings which cause dnsmasq to skip that file. This avoids pulling
# in backups made by dpkg.
CONFIG_DIR=/etc/dnsmasq.d,.dpkg-dist,.dpkg-old,.dpkg-new

# If the resolvconf package is installed, dnsmasq will use its output
# rather than the contents of /etc/resolv.conf to find upstream
# nameservers. Uncommenting this line inhibits this behaviour.
# Not that including a "resolv-file=<filename>" line in
# /etc/dnsmasq.conf is not enough to override resolvconf if it is
# installed: the line below must be uncommented.
#IGNORE_RESOLVCONF=yes
'''

def setup_nat():
    if IMAGE_VERSION and IMAGE_VERSION < MIN_VERSION_FOR_NAT:
        return

    if not IMAGE_VERSION:
        return

    file_path_sysctl_conf = '/etc/sysctl.d/enable_ipv4_forward.conf'
    file_path_systemd_sh = '/usr/local/scripts/_tf_setup_ap_nat.sh'
    file_path_systemd_py = '/usr/local/scripts/_tf_setup_ap_nat.py'
    file_path_systemd_unit = '/etc/systemd/system/tf_setup_ap_nat.service'
    file_path_systemd_timer = '/etc/systemd/system/tf_setup_ap_nat.timer'

    with open(file_path_sysctl_conf, 'w') as fh_sysctl:
        fh_sysctl.write('net.ipv4.ip_forward = 1\n')

    os.chmod(file_path_sysctl_conf, 0644)

    if os.system('/sbin/sysctl -p ' + file_path_sysctl_conf + ' &> /dev/null') == 0:
        if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_NM:
            with open(file_path_systemd_py, 'w') as fh_py:
                fh_py.write(PY_SETUP_AP_NAT.format(interface))

            os.chmod(file_path_systemd_py, 0755)
        else:
            with open(file_path_systemd_sh, 'w') as fh_sh:
                fh_sh.write(SH_SETUP_AP_NAT.format(interface))

            os.chmod(file_path_systemd_sh, 0755)

        if os.path.exists(file_path_systemd_unit):
            os.system('/bin/systemctl stop ' + file_path_systemd_unit + ' &> /dev/null')
            os.system('/bin/systemctl disable ' + file_path_systemd_unit + ' &> /dev/null')

        if os.path.exists(file_path_systemd_timer):
            os.system('/bin/systemctl stop ' + file_path_systemd_timer +' &> /dev/null')
            os.system('/bin/systemctl disable ' + file_path_systemd_timer + ' &> /dev/null')

        with open(file_path_systemd_unit, 'w') as fh_unit:
            if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_NM:
                fh_unit.write(UNIT_SETUP_AP_NAT.format('/usr/bin/python ' + file_path_systemd_py))
            else:
                fh_unit.write(UNIT_SETUP_AP_NAT.format('/bin/bash ' + file_path_systemd_sh))

        with open(file_path_systemd_timer, 'w') as fh_timer:
            fh_timer.write(TIMER_SETUP_AP_NAT)

        os.chmod(file_path_systemd_unit, 0644)
        os.chmod(file_path_systemd_timer, 0644)

        if os.path.exists(file_path_systemd_unit):
            os.system('/bin/systemctl enable ' + file_path_systemd_unit + ' &> /dev/null')
            os.system('/bin/systemctl start tf_setup_ap_nat.service &> /dev/null')

        if os.path.exists(file_path_systemd_timer):
            os.system('/bin/systemctl enable ' + file_path_systemd_timer + ' &> /dev/null')
            os.system('/bin/systemctl start tf_setup_ap_nat.timer &> /dev/null')

        os.system('/bin/systemctl daemon-reload &> /dev/null')

if len(argv) < 2:
    exit (1)

try:
    apply_dict = json.loads(argv[1])

    if IMAGE_VERSION and  IMAGE_VERSION >= MIN_VERSION_FOR_HOSTAPD_UPDATE_1:
        if len(apply_dict) != 13:
            exit(1)
    else:
        if len(apply_dict) != 12:
            exit(1)

    interface        = unicode(apply_dict['interface'])
    interface_ip     = unicode(apply_dict['interface_ip'])
    interface_mask   = unicode(apply_dict['interface_mask'])
    ssid             = unicode(apply_dict['ssid'])
    ssid_hidden      = apply_dict['ssid_hidden']
    wpa_key          = unicode(apply_dict['wpa_key'])
    channel          = unicode(apply_dict['channel'])
    enabled_dns_dhcp = apply_dict['enabled_dns_dhcp']
    domain           = unicode(apply_dict['domain'])
    dhcp_start       = unicode(apply_dict['dhcp_start'])
    dhcp_end         = unicode(apply_dict['dhcp_end'])
    dhcp_mask        = unicode(apply_dict['dhcp_mask'])

    # If there is an existing hostapd configuration with an interface defined
    # then try to disable the interface.
    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_NM:
        if os.path.exists('/etc/hostapd/hostapd.conf'):
            is_hostapd_interface = False

            with open('/etc/hostapd/hostapd.conf', 'r') as fh:
                hostapd_config_buf = '[root]\n' + fh.read()
                hostapd_parser = ConfigParser.ConfigParser()
                hostapd_parser.readfp(StringIO.StringIO(hostapd_config_buf))
                hostapd_interface = hostapd_parser.get('root', 'interface', None)

                if hostapd_interface:
                    is_hostapd_interface = True

            if is_hostapd_interface:
                try:
                    os.system('/sbin/ifdown ' + hostapd_interface + ' &> /dev/null')
                except:
                    pass

    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_FOR_HOSTAPD_UPDATE_1:
        hostapd_driver = unicode(apply_dict['hostapd_driver'])
    else:
        hostapd_driver = ''

    with open('/etc/default/dnsmasq', 'w') as fd_default_dnsmasq:
        fd_default_dnsmasq.write(DEFAULT_DNSMASQ)

    with open('/etc/default/hostapd', 'w') as fd_default_hostapd_conf:
        fd_default_hostapd_conf.write('DAEMON_CONF="/etc/hostapd/hostapd.conf"')

    with open('/etc/hostapd/hostapd.conf', 'w') as fd_hostapd_conf:
        if ssid_hidden:
            fd_hostapd_conf.write(HOSTAPD_CONF.format(interface,
                                                      hostapd_driver,
                                                      ssid,
                                                      channel,
                                                      '2',
                                                      wpa_key))
        else:
            fd_hostapd_conf.write(HOSTAPD_CONF.format(interface,
                                                      hostapd_driver,
                                                      ssid,
                                                      channel,
                                                      '0',
                                                      wpa_key))

    with open('/etc/dnsmasq.conf', 'w') as fd_dnsmasq_conf:
        if enabled_dns_dhcp:
            fd_dnsmasq_conf.write(DNSMASQ_CONF.format('#Enabled',
                                                      interface_ip,
                                                      domain,
                                                      '.'.join(interface_ip.split('.')[::-1]),
                                                      dhcp_start,
                                                      dhcp_end,
                                                      dhcp_mask))
        else:
            fd_dnsmasq_conf.write(DNSMASQ_CONF.format('#Disabled',
                                                      interface_ip,
                                                      domain,
                                                      '.'.join(interface_ip.split('.')[::-1]),
                                                      dhcp_start,
                                                      dhcp_end,
                                                      dhcp_mask))

    with open('/etc/network/interfaces', 'w') as fd_interfaces_conf:
        fd_interfaces_conf.write(INTERFACES_CONF.format(interface, interface_ip, interface_mask))

    with open('/etc/network/interfaces.ap', 'w') as fd_interfaces_ap_conf:
        fd_interfaces_ap_conf.write(INTERFACES_CONF.format(interface, interface_ip, interface_mask))

    for intf in netifaces.interfaces():
        if intf != interface:
            continue

        if os.system('/sbin/ifconfig '+intf+' up &> /dev/null') != 0:
            exit(1)

    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_NM:
        if os.system('/usr/bin/nmcli radio wifi off &> /dev/null') != 0:
            exit(1)
    else:
        if os.system('/bin/systemctl stop wicd &> /dev/null') != 0:
            exit(1)

        if os.system('/bin/systemctl disable wicd &> /dev/null') != 0:
            exit(1)

    if enabled_dns_dhcp:
        if os.system('/bin/systemctl enable dnsmasq &> /dev/null') != 0:
            exit(1)

        if os.system('/bin/systemctl restart dnsmasq &> /dev/null') != 0:
            exit(1)
    else:
        if os.system('/bin/systemctl disable dnsmasq &> /dev/null') != 0:
            exit(1)

        if os.system('/bin/systemctl stop dnsmasq &> /dev/null') != 0:
            exit(1)

    if os.system('/bin/systemctl enable hostapd &> /dev/null') != 0:
        exit(1)

    setup_nat()

    if os.system('/bin/systemctl restart networking &> /dev/null; /bin/systemctl restart hostapd &> /dev/null') != 0:
        exit(1)

except:
    traceback.print_exc()
    exit(1)
