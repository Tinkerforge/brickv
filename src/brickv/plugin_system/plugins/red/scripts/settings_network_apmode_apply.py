#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import netifaces
from sys import argv

HOSTAPD_CONF = '''# AP netdevice name (without 'ap' postfix, i.e., wlan0 uses wlan0ap for
# management frames with the Host AP driver); wlan0 with many nl80211 drivers
interface={0}

# SSID to be used in IEEE 802.11 management frames
ssid={1}

# Channel number (IEEE 802.11)
# (default: 0, i.e., not set)
# Please note that some drivers do not use this value from hostapd and the
# channel will need to be configured separately with iwconfig.
#
# If CONFIG_ACS build option is enabled, the channel can be selected
# automatically at run time by setting channel=acs_survey or channel=0, both of
# which will enable the ACS survey based algorithm.
channel={2}

# Station MAC address -based authentication
# Please note that this kind of access control requires a driver that uses
# hostapd to take care of management frame processing and as such, this can be
# used with driver=hostap or driver=nl80211, but not with driver=atheros.
# 0 = accept unless in deny list
# 1 = deny unless in accept list
# 2 = use external RADIUS server (accept/deny lists are searched first)
macaddr_acl=0

# IEEE 802.11 specifies two authentication algorithms. hostapd can be
# configured to allow both of these or only one. Open system authentication
# should be used with IEEE 802.1X.
# Bit fields of allowed authentication algorithms:
# bit 0 = Open System Authentication
# bit 1 = Shared Key Authentication (requires WEP)
auth_algs=1

# Send empty SSID in beacons and ignore probe request frames that do not
# specify full SSID, i.e., require stations to know SSID.
# default: disabled (0)
# 1 = send empty (length=0) SSID in beacon and ignore probe request for
#     broadcast SSID
# 2 = clear SSID (ASCII 0), but keep the original length (this may be required
#     with some clients that do not support empty SSID) and ignore probe
#     requests for broadcast SSID
ignore_broadcast_ssid={3}

# Enable WPA. Setting this variable configures the AP to require WPA (either
# WPA-PSK or WPA-RADIUS/EAP based on other configuration). For WPA-PSK, either
# wpa_psk or wpa_passphrase must be set and wpa_key_mgmt must include WPA-PSK.
# Instead of wpa_psk / wpa_passphrase, wpa_psk_radius might suffice.
# For WPA-RADIUS/EAP, ieee8021x must be set (but without dynamic WEP keys),
# RADIUS authentication server must be configured, and WPA-EAP must be included
# in wpa_key_mgmt.
# This field is a bit field that can be used to enable WPA (IEEE 802.11i/D3.0)
# and/or WPA2 (full IEEE 802.11i/RSN):
# bit0 = WPA
# bit1 = IEEE 802.11i/RSN (WPA2) (dot11RSNAEnabled)
wpa=2

# WPA pre-shared keys for WPA-PSK. This can be either entered as a 256-bit
# secret in hex format (64 hex digits), wpa_psk, or as an ASCII passphrase
# (8..63 characters) that will be converted to PSK. This conversion uses SSID
# so the PSK changes when ASCII passphrase is used and the SSID is changed.
# wpa_psk (dot11RSNAConfigPSKValue)
# wpa_passphrase (dot11RSNAConfigPSKPassPhrase)
wpa_passphrase={4}

# Set of accepted key management algorithms (WPA-PSK, WPA-EAP, or both). The
# entries are separated with a space. WPA-PSK-SHA256 and WPA-EAP-SHA256 can be
# added to enable SHA256-based stronger algorithms.
# (dot11RSNAConfigAuthenticationSuitesTable)
wpa_key_mgmt=WPA-PSK

# Set of accepted cipher suites (encryption algorithms) for pairwise keys
# (unicast packets). This is a space separated list of algorithms:
# CCMP = AES in Counter mode with CBC-MAC [RFC 3610, IEEE 802.11i/D7.0]
# TKIP = Temporal Key Integrity Protocol [IEEE 802.11i/D7.0]
# Group cipher suite (encryption algorithm for broadcast and multicast frames)
# is automatically selected based on this configuration. If only CCMP is
# allowed as the pairwise cipher, group cipher will also be CCMP. Otherwise,
# TKIP will be used as the group cipher.
# (dot11RSNAConfigPairwiseCiphersTable)
# Pairwise cipher for WPA (v1) (default: TKIP)
wpa_pairwise=TKIP

# If Windows clients are going to be connecting, you should leave CMP
# encryption out of the wpa_pairwise option, as some windows drivers
# have problems with systems that enable it.

# Pairwise cipher for RSN/WPA2 (default: use wpa_pairwise value)
rsn_pairwise=CCMP

# ieee80211n: Whether IEEE 802.11n (HT) is enabled
# 0 = disabled (default)
# 1 = enabled
# Note: You will also need to enable WMM for full HT functionality.
ieee80211n=1

# Operation mode (a = IEEE 802.11a, b = IEEE 802.11b, g = IEEE 802.11g,
# ad = IEEE 802.11ad (60 GHz); a/g options are used with IEEE 802.11n, too, to
# specify band)
# Default: IEEE 802.11b
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
local=/{2}/
domain={2}
address=/{3}/{1}
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

if len(argv) < 2:
    exit (1)

try:
    apply_dict = json.loads(argv[1])
    
    if len(apply_dict) != 13:
        exit(1)
    
    interface        = unicode(apply_dict['interface'])
    interface_ip     = unicode(apply_dict['interface_ip'])
    interface_mask   = unicode(apply_dict['interface_mask'])
    ssid             = unicode(apply_dict['ssid'])
    ssid_hidden      = apply_dict['ssid_hidden']
    wpa_key          = unicode(apply_dict['wpa_key'])
    channel          = unicode(apply_dict['channel'])
    enabled_dns_dhcp = apply_dict['enabled_dns_dhcp']
    server_name      = unicode(apply_dict['server_name'])
    domain           = unicode(apply_dict['domain'])
    dhcp_start       = unicode(apply_dict['dhcp_start'])
    dhcp_end         = unicode(apply_dict['dhcp_end'])
    dhcp_mask        = unicode(apply_dict['dhcp_mask'])

    with open('/etc/default/dnsmasq', 'w') as fd_default_dnsmasq:
        fd_default_dnsmasq.write(DEFAULT_DNSMASQ)

    with open('/etc/default/hostapd', 'w') as fd_default_hostapd_conf:
        fd_default_hostapd_conf.write('DAEMON_CONF="/etc/hostapd/hostapd.conf"')

    with open('/etc/hostapd/hostapd.conf', 'w') as fd_hostapd_conf:
        if ssid_hidden:
            fd_hostapd_conf.write(HOSTAPD_CONF.format(interface, ssid, channel, '2', wpa_key))
        else:
            fd_hostapd_conf.write(HOSTAPD_CONF.format(interface, ssid, channel, '0', wpa_key))
    
    with open('/etc/dnsmasq.conf', 'w') as fd_dnsmasq_conf:
        if enabled_dns_dhcp:
            fd_dnsmasq_conf.write(DNSMASQ_CONF.format('#Enabled',
                                                      interface_ip,
                                                      domain,
                                                      server_name,
                                                      dhcp_start,
                                                      dhcp_end,
                                                      dhcp_mask))
        else:
            fd_dnsmasq_conf.write(DNSMASQ_CONF.format('#Disabled',
                                                      interface_ip,
                                                      domain,
                                                      server_name,
                                                      dhcp_start,
                                                      dhcp_end,
                                                      dhcp_mask))

    with open('/etc/network/interfaces', 'w') as fd_interfaces_conf:
        fd_interfaces_conf.write(INTERFACES_CONF.format(interface, interface_ip, interface_mask))

    for intf in netifaces.interfaces():
        if intf == 'lo' or intf == 'tunl0':
            continue

        if intf == interface:
            if os.system('/sbin/ifconfig '+intf+' up'):
                exit(1)

            continue
            
        if os.system('/sbin/ifconfig '+intf+' down'):
            exit(1)

    if os.system('/usr/sbin/service wicd stop'):
        exit(1)

    if os.system('/usr/sbin/update-rc.d -f wicd remove'):
        exit(1)
        
    if enabled_dns_dhcp:
        if os.system('/usr/sbin/update-rc.d dnsmasq defaults'):
            exit(1)
        
        if os.system('/usr/sbin/service dnsmasq restart'):
            exit(1)
    else:
        if os.system('/usr/sbin/update-rc.d -f dnsmasq remove'):
            exit(1)
        
        if os.system('/usr/sbin/service dnsmasq stop'):
            exit(1)

    if os.system('/usr/sbin/update-rc.d hostapd defaults'):
        exit(1)

    if os.system('/usr/sbin/service hostapd restart'):
        exit(1)

    if os.system('/usr/sbin/service networking restart'):
        exit(1)

except Exception as e:
    exit(1)
