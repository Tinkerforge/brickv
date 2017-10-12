#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import subprocess
from distutils.version import StrictVersion

IMAGE_VERSION = None
MIN_VERSION_WITH_NAGIOS4 = StrictVersion('1.10')
MAX_VERSION_WITH_CHKCONFIG = StrictVersion('1.9')
MAX_VERSION_WITH_ASPLASH_SCREEN = StrictVersion('1.9')
MAX_VERSION_WITH_GPU_2D_3D = StrictVersion('1.9')
MIN_VERSION_WITH_OPENHAB2 = StrictVersion('1.10')
MIN_VERSION_WITH_NM = StrictVersion('1.10')

with open('/etc/tf_image_version', 'r') as f:
    IMAGE_VERSION = StrictVersion(f.read().split(' ')[0].strip())

if len(sys.argv) < 2:
    sys.stderr.write(u'Missing parameters'.encode('utf-8'))
    exit(2)

command = sys.argv[1]

SUNXI_FBDEV_X11_DRIVER_CONF = '''
# This configuration file is copied to the following locations,
#   /etc/X11/xorg.conf
#   /usr/share/X11/xorg.conf.d/99-sunxifb.conf

# When troubleshooting, check /var/log/Xorg.0.log for the debugging
# output and error messages.
#
# Run "man fbdev" to get additional information about the extra
# configuration options for tuning the driver.

Section "ServerLayout"
    Identifier      "Default Layout"
    Screen          "Screen 0" 0 0
EndSection

Section "Device"
    Identifier      "Allwinner A10/A13 FBDEV"
    Driver          "fbdev"
    Option          "fbdev" "/dev/fb0"
    Option          "ShadowFB" "false"
EndSection

Section "Monitor"
    Identifier      "Default Monitor"
    Option          "DPMS" "false"
EndSection

Section "Screen"
    Identifier      "Screen 0"
    Device          "Allwinner A10/A13 FBDEV"
    Monitor         "Default Monitor"
    DefaultDepth    24
    Option          "AllowEmptyInitialConfiguration"

    SubSection      "Display"
        Depth       24
    EndSubSection
EndSection
'''

SUNXI_FBTURBO_X11_DRIVER_CONF = '''
# This configuration file is copied to the following locations,
#   /etc/X11/xorg.conf
#   /usr/share/X11/xorg.conf.d/99-sunxifb.conf

# When troubleshooting, check /var/log/Xorg.0.log for the debugging
# output and error messages.
#
# Run "man fbturbo" to get additional information about the extra
# configuration options for tuning the driver.

Section "ServerLayout"
    Identifier      "Default Layout"
    Screen          "Screen 0" 0 0
EndSection

Section "Device"
    Identifier      "Allwinner A10/A13 FBDEV"
    Driver          "fbturbo"
    Option          "fbdev" "/dev/fb0"
    Option          "ShadowFB" "false"
    Option          "DRI2" "false"
    Option          "SwapbuffersWait" "true"
    Option          "AccelMethod" "CPU"
EndSection

Section "Monitor"
    Identifier      "Default Monitor"
    Option          "DPMS" "false"
EndSection

Section "Screen"
    Identifier      "Screen 0"
    Device          "Allwinner A10/A13 FBDEV"
    Monitor         "Default Monitor"
    DefaultDepth    24
    Option          "AllowEmptyInitialConfiguration"

    SubSection      "Display"
        Depth       24
    EndSubSection
EndSection
'''

INTERFACES_CONF = '''# interfaces(5) file used by ifup(8) and ifdown(8)
auto lo
iface lo inet loopback
'''

is_enabled_mi = None
is_enabled_wicd = None
is_enabled_mi_nm = None
is_enabled_ap_nat = None
is_enabled_nagios = None
is_enabled_hostapd = None
is_enabled_dnsmasq = None
is_enabled_openhab = None
is_enabled_web_server = None
is_enabled_mi_nm_timer = None
is_enabled_ap_nat_timer = None
is_enabled_splashscreen = None

def get_svc_states():
    ps = None
    ps_stdout = None

    global is_enabled_mi
    global is_enabled_wicd
    global is_enabled_mi_nm
    global is_enabled_ap_nat
    global is_enabled_nagios
    global is_enabled_hostapd
    global is_enabled_dnsmasq
    global is_enabled_openhab
    global is_enabled_web_server
    global is_enabled_mi_nm_timer
    global is_enabled_ap_nat_timer
    global is_enabled_splashscreen

    # Sakis3G mobile internet
    if not IMAGE_VERSION or IMAGE_VERSION < MIN_VERSION_WITH_NM:
        if os.path.isfile('/etc/systemd/system/tf_mobile_internet.service'):
            ps = subprocess.Popen('/bin/systemctl is-enabled tf_mobile_internet.service',
                                  shell=True,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

            ps_stdout = ps.communicate()[0].strip()

            if ps_stdout and ps_stdout == 'disabled':
                is_enabled_mi = False
            elif ps_stdout and ps_stdout == 'enabled':
                is_enabled_mi = True

        # WICD
        ps = subprocess.Popen('/bin/systemctl is-enabled wicd.service',
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        ps_stdout = ps.communicate()[0].strip()

        if ps_stdout and ps_stdout == 'disabled':
            is_enabled_wicd = False
        elif ps_stdout and ps_stdout == 'enabled':
            is_enabled_wicd = True

    # NetworkManager mobile internet service and timer
    if os.path.isfile('/etc/systemd/system/tf_mobile_internet_nm.service'):
        ps = subprocess.Popen('/bin/systemctl is-enabled tf_mobile_internet_nm.service',
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        ps_stdout = ps.communicate()[0].strip()

        if ps_stdout and ps_stdout == 'disabled':
            is_enabled_mi_nm = False
        elif ps_stdout and ps_stdout == 'enabled':
            is_enabled_mi_nm = True

    if os.path.isfile('/etc/systemd/system/tf_mobile_internet_nm.timer'):
        ps = subprocess.Popen('/bin/systemctl is-enabled tf_mobile_internet_nm.timer',
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        ps_stdout = ps.communicate()[0].strip()

        if ps_stdout and ps_stdout == 'disabled':
            is_enabled_mi_nm_timer = False
        elif ps_stdout and ps_stdout == 'enabled':
            is_enabled_mi_nm_timer = True

    # AP NAT setup service and timer
    if os.path.isfile('/etc/systemd/system/tf_setup_ap_nat.service'):
        ps = subprocess.Popen('/bin/systemctl is-enabled tf_setup_ap_nat.service',
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        ps_stdout = ps.communicate()[0].strip()

        if ps_stdout and ps_stdout == 'disabled':
            is_enabled_ap_nat = False
        elif ps_stdout and ps_stdout == 'enabled':
            is_enabled_ap_nat = True
    else:
        is_enabled_ap_nat = False

    if os.path.isfile('/etc/systemd/system/tf_setup_ap_nat.timer'):
        ps = subprocess.Popen('/bin/systemctl is-enabled tf_setup_ap_nat.timer',
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        ps_stdout = ps.communicate()[0].strip()

        if ps_stdout and ps_stdout == 'disabled':
            is_enabled_ap_nat_timer = False
        elif ps_stdout and ps_stdout == 'enabled':
            is_enabled_ap_nat_timer = True
    else:
        is_enabled_ap_nat_timer = False

    # Nagios
    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_NAGIOS4:
        ps = subprocess.Popen('/bin/systemctl is-enabled nagios.service',
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        ps_stdout = ps.communicate()[0].strip()

        if ps_stdout and ps_stdout == 'disabled':
            is_enabled_nagios = False
        elif ps_stdout and ps_stdout == 'enabled':
            is_enabled_nagios = True
    else:
        ps = subprocess.Popen('/bin/systemctl is-enabled nagios3.service',
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        ps_stdout = ps.communicate()[0].strip()

        if ps_stdout and ps_stdout == 'disabled':
            is_enabled_nagios = False
        elif ps_stdout and ps_stdout == 'enabled':
            is_enabled_nagios = True

    # Hostpad
    ps = subprocess.Popen('/bin/systemctl is-enabled hostapd.service',
                          shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

    ps_stdout = ps.communicate()[0].strip()

    if ps_stdout and ps_stdout == 'disabled':
        is_enabled_hostapd = False
    elif ps_stdout and ps_stdout == 'enabled':
        is_enabled_hostapd = True

    # Dnsmasq
    ps = subprocess.Popen('/bin/systemctl is-enabled dnsmasq.service',
                          shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

    ps_stdout = ps.communicate()[0].strip()

    if ps_stdout and ps_stdout == 'disabled':
        is_enabled_dnsmasq = False
    elif ps_stdout and ps_stdout == 'enabled':
        is_enabled_dnsmasq = True

    # OpenHAB
    if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
        ps = subprocess.Popen('/bin/systemctl is-enabled openhab2.service',
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        ps_stdout = ps.communicate()[0].strip()

        if ps_stdout and ps_stdout == 'disabled':
            is_enabled_openhab = False
        elif ps_stdout and ps_stdout == 'enabled':
            is_enabled_openhab = True
    else:
        ps = subprocess.Popen('/bin/systemctl is-enabled openhab.service',
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        ps_stdout = ps.communicate()[0].strip()

        if ps_stdout and ps_stdout == 'disabled':
            is_enabled_openhab = False
        elif ps_stdout and ps_stdout == 'enabled':
            is_enabled_openhab = True

    # Webserver
    ps = subprocess.Popen('/bin/systemctl is-enabled apache2.service',
                          shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

    ps_stdout = ps.communicate()[0].strip()

    if ps_stdout and ps_stdout == 'disabled':
        is_enabled_web_server = False
    elif ps_stdout and ps_stdout == 'enabled':
        is_enabled_web_server = True

    # Splashscreen
    if IMAGE_VERSION and IMAGE_VERSION > MAX_VERSION_WITH_ASPLASH_SCREEN:
        ps = subprocess.Popen('/bin/systemctl is-enabled splashscreen.service',
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        ps_stdout = ps.communicate()[0].strip()

        if ps_stdout and ps_stdout == 'disabled':
            is_enabled_splashscreen = False
        elif ps_stdout and ps_stdout == 'enabled':
            is_enabled_splashscreen = True
    else:
        ps = subprocess.Popen('/bin/systemctl is-enabled asplashscreen.service',
                              shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        ps_stdout = ps.communicate()[0].strip()

        if ps_stdout and ps_stdout == 'disabled':
            is_enabled_splashscreen = False
        elif ps_stdout and ps_stdout == 'enabled':
            is_enabled_splashscreen = True

get_svc_states()

if command == 'CHECK':
    try:
        return_dict = {'gpu'              : None,
                       'desktopenv'       : None,
                       'webserver'        : None,
                       'splashscreen'     : None,
                       'ap'               : None,
                       'servermonitoring' : None,
                       'openhab'          : None,
                       'mobileinternet'   : None}

        if IMAGE_VERSION and IMAGE_VERSION > MAX_VERSION_WITH_CHKCONFIG:
            if is_enabled_web_server:
                return_dict['webserver'] = True
            else:
                return_dict['webserver'] = False

            if is_enabled_splashscreen:
                return_dict['splashscreen'] = True
            else:
                return_dict['splashscreen'] = False

            if is_enabled_openhab:
                return_dict['openhab'] = True
            else:
                return_dict['openhab'] = False

            return_dict['gpu'] = os.path.isfile('/etc/tf_gpu_2d_only')
        else:
            cmd = '/sbin/chkconfig | awk -F " " \'{print $1 "<==>" $2}\''
            cmd_ps = subprocess.Popen(cmd, shell=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

            if cmd_ps.returncode:
                exit(3)

            init_script_list_str = cmd_ps.communicate()[0].strip()
            init_script_list_list = init_script_list_str.splitlines()

            for script in init_script_list_list:
                script_stat = script.split('<==>')
                if len(script_stat) == 2:
                    if script_stat[0] == 'apache2':
                        return_dict['webserver'] = script_stat[1] == 'on'
                    elif script_stat[0] == 'asplashscreen':
                        return_dict['splashscreen'] = script_stat[1] == 'on'
                    elif script_stat[0] == 'openhab':
                        return_dict['openhab'] = script_stat[1] == 'on'

            if return_dict['openhab'] == None:
                return_dict['openhab'] = False # openHAB is not installed at all

            return_dict['gpu'] = not os.path.isfile('/etc/modprobe.d/mali-blacklist.conf')

        return_dict['desktopenv'] = os.path.isfile('/etc/tf_x11_enabled')
        return_dict['ap'] = os.path.isfile('/etc/tf_ap_enabled')
        return_dict['servermonitoring'] = os.path.isfile('/etc/tf_server_monitoring_enabled')
        return_dict['mobileinternet'] = os.path.isfile('/etc/tf_mobile_internet_enabled')

        sys.stdout.write(json.dumps(return_dict, separators=(',', ':')))
        exit(0)

    except Exception as e:
        sys.stderr.write(unicode(e).encode('utf-8'))
        exit(4)

elif command == 'APPLY':
    if len(sys.argv) < 3:
        sys.stderr.write(u'Missing parameters'.encode('utf-8'))
        exit(5)

    try:
        apply_dict = json.loads(sys.argv[2])

        if apply_dict['gpu']:
            lines = []

            if IMAGE_VERSION and IMAGE_VERSION > MAX_VERSION_WITH_GPU_2D_3D:
                with open('/etc/tf_gpu_2d_only', 'w') as fd_gpu_2d_only:
                    pass
            else:
                with open('/etc/modules', 'r') as fd_r_modules:
                    lines = fd_r_modules.readlines()
                    for i, l in enumerate(lines):
                        if l.strip() == '#mali':
                            lines[i] = l[1:]

                with open('/etc/modules', 'w') as fd_w_modules:
                    fd_w_modules.write(''.join(lines))

                if os.path.isfile('/etc/modprobe.d/mali-blacklist.conf'):
                    os.remove('/etc/modprobe.d/mali-blacklist.conf')

            with open('/etc/X11/xorg.conf', 'w') as fd_fbconf:
                fd_fbconf.write(SUNXI_FBTURBO_X11_DRIVER_CONF)

            with open('/usr/share/X11/xorg.conf.d/99-sunxifb.conf', 'w') as fd_fbconf:
                fd_fbconf.write(SUNXI_FBTURBO_X11_DRIVER_CONF)

        else:
            if IMAGE_VERSION and IMAGE_VERSION > MAX_VERSION_WITH_GPU_2D_3D:
                if os.path.isfile('/etc/tf_gpu_2d_only'):
                    os.remove('/etc/tf_gpu_2d_only')
            else:
                lines = []
                with open('/etc/modules', 'r') as fd_r_modules:
                    lines = fd_r_modules.readlines()

                    for i, l in enumerate(lines):
                        if l.strip() == 'mali':
                            lines[i] = '#'+l

                with open('/etc/modules', 'w') as fd_w_modules:
                    fd_w_modules.write(''.join(lines))

                with open('/etc/modprobe.d/mali-blacklist.conf', 'w') as fd_w_malibl:
                    fd_w_malibl.write('blacklist mali')

            with open('/etc/X11/xorg.conf', 'w') as fd_fbconf:
                fd_fbconf.write(SUNXI_FBDEV_X11_DRIVER_CONF)

            with open('/usr/share/X11/xorg.conf.d/99-sunxifb.conf', 'w') as fd_fbconf:
                fd_fbconf.write(SUNXI_FBDEV_X11_DRIVER_CONF)

        if apply_dict['desktopenv']:
            with open('/etc/tf_x11_enabled', 'w') as fd_x11_enabled:
                pass
        else:
            if os.path.isfile('/etc/tf_x11_enabled'):
                os.remove('/etc/tf_x11_enabled')

        if apply_dict['webserver']:
            if is_enabled_web_server != None and not is_enabled_web_server:
                if os.system('/bin/systemctl enable apache2') != 0:
                    exit(6)
        else:
            if is_enabled_web_server != None and is_enabled_web_server:
                if os.system('/bin/systemctl disable apache2') != 0:
                    exit(7)

        if apply_dict['splashscreen']:
            if IMAGE_VERSION and IMAGE_VERSION > MAX_VERSION_WITH_ASPLASH_SCREEN:
                if is_enabled_splashscreen != None and not is_enabled_splashscreen:
                    if os.system('/bin/systemctl enable splashscreen') != 0:
                        exit(8)
            else:
                if is_enabled_splashscreen != None and not is_enabled_splashscreen:
                    if os.system('/bin/systemctl enable asplashscreen') != 0:
                        exit(8)
        else:
            if IMAGE_VERSION and IMAGE_VERSION > MAX_VERSION_WITH_ASPLASH_SCREEN:
                if is_enabled_splashscreen != None and is_enabled_splashscreen:
                    if os.system('/bin/systemctl disable splashscreen') != 0:
                        exit(8)
            else:
                if is_enabled_splashscreen != None and is_enabled_splashscreen:
                    if os.system('/bin/systemctl disable asplashscreen') != 0:
                        exit(9)

        if apply_dict['ap']:
            with open('/etc/tf_ap_enabled', 'w') as fd_ap_enabled:
                pass

            if is_enabled_hostapd != None and not is_enabled_hostapd:
                if os.system('/bin/systemctl enable hostapd') != 0:
                    exit(10)

            if is_enabled_dnsmasq != None and not is_enabled_dnsmasq:
                if os.system('/bin/systemctl enable dnsmasq') != 0:
                    exit(11)

            if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_NM:
                if os.system('/usr/bin/nmcli radio wifi off') != 0:
                    exit(12)
            else:
                if is_enabled_wicd != None and is_enabled_wicd:
                    if os.system('/bin/systemctl disable wicd') != 0:
                        exit(12)

            if os.path.isfile('/etc/network/interfaces.ap'):
                os.rename('/etc/network/interfaces.ap', '/etc/network/interfaces')

            if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_NM:
                pass
            else:
                if os.path.isfile('/etc/xdg/autostart/wicd-tray.desktop'):
                    os.rename('/etc/xdg/autostart/wicd-tray.desktop',
                              '/etc/xdg/autostart/wicd-tray.desktop.block')

            if os.path.isfile('/etc/systemd/system/tf_setup_ap_nat.service') and \
               os.path.isfile('/etc/systemd/system/tf_setup_ap_nat.timer'):
                    if is_enabled_ap_nat != None and not is_enabled_ap_nat:
                        os.system('/bin/systemctl enable /etc/systemd/system/tf_setup_ap_nat.service &> /dev/null')

                    if is_enabled_ap_nat_timer != None and not is_enabled_ap_nat_timer:
                        os.system('/bin/systemctl enable /etc/systemd/system/tf_setup_ap_nat.timer &> /dev/null')

        else:
            if os.path.isfile('/etc/tf_ap_enabled'):
                os.remove('/etc/tf_ap_enabled')

            if is_enabled_hostapd != None and is_enabled_hostapd:
                if os.system('/bin/systemctl disable hostapd') != 0:
                    exit(13)

            if is_enabled_dnsmasq != None and is_enabled_dnsmasq:
                if os.system('/bin/systemctl disable dnsmasq') != 0:
                    exit(14)

            if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_NM:
                if os.system('/usr/bin/nmcli radio wifi on') != 0:
                    exit(15)
            else:
                if is_enabled_wicd != None and not is_enabled_wicd:
                    if os.system('/bin/systemctl enable wicd') != 0:
                        exit(15)

            with open('/etc/network/interfaces', 'w') as fd_interfaces:
                fd_interfaces.write(INTERFACES_CONF)

            if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_NM:
                pass
            else:
                if os.path.isfile('/etc/xdg/autostart/wicd-tray.desktop.block'):
                    os.rename('/etc/xdg/autostart/wicd-tray.desktop.block',
                              '/etc/xdg/autostart/wicd-tray.desktop')

            if os.path.isfile('/etc/systemd/system/tf_setup_ap_nat.service') and \
               os.path.isfile('/etc/systemd/system/tf_setup_ap_nat.timer'):
                    if is_enabled_ap_nat != None and is_enabled_ap_nat:
                        os.system('/bin/systemctl disable /etc/systemd/system/tf_setup_ap_nat.service &> /dev/null')

                    if is_enabled_ap_nat_timer != None and is_enabled_ap_nat_timer:
                        os.system('/bin/systemctl disable /etc/systemd/system/tf_setup_ap_nat.timer &> /dev/null')

        if apply_dict['servermonitoring']:
            if not apply_dict['webserver']:
                if is_enabled_web_server != None and not is_enabled_web_server:
                    if os.system('/bin/systemctl enable apache2') != 0:
                        exit(16)

            with open('/etc/tf_server_monitoring_enabled', 'w') as fd_server_monitoring_enabled:
                pass

            if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_NAGIOS4:
                if is_enabled_nagios != None and not is_enabled_nagios:
                    if os.system('/bin/systemctl enable nagios') != 0:
                        exit(17)
            else:
                if is_enabled_nagios != None and not is_enabled_nagios:
                    if os.system('/bin/systemctl enable nagios3') != 0:
                        exit(17)

        else:
            if os.path.isfile('/etc/tf_server_monitoring_enabled'):
                os.remove('/etc/tf_server_monitoring_enabled')

            if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_NAGIOS4:
                if is_enabled_nagios != None and is_enabled_nagios:
                    if os.system('/bin/systemctl disable nagios') != 0:
                        exit(18)
            else:
                if is_enabled_nagios != None and is_enabled_nagios:
                    if os.system('/bin/systemctl disable nagios3') != 0:
                        exit(18)

        if apply_dict['openhab']:
            if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
                if is_enabled_openhab != None and not is_enabled_openhab:
                    if os.system('/bin/systemctl enable openhab2') != 0:
                        exit(19)
            else:
                if is_enabled_openhab != None and not is_enabled_openhab:
                    if os.system('/bin/systemctl enable openhab') != 0:
                        exit(19)
        else:
            if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_OPENHAB2:
                if is_enabled_openhab != None and is_enabled_openhab:
                    if os.system('/bin/systemctl disable openhab2') != 0:
                        exit(20)
            else:
                if is_enabled_openhab != None and is_enabled_openhab:
                    if os.system('/bin/systemctl disable openhab') != 0:
                        exit(20)

        if apply_dict['mobileinternet']:
            if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_NM:
                if not os.path.isfile('/etc/tf_mobile_internet_enabled.disabled'):
                    if not os.path.isfile('/etc/tf_mobile_internet_enabled'):
                        with open('/etc/tf_mobile_internet_enabled', 'w') as fd_ap_enabled:
                            pass
                else:
                    os.rename('/etc/tf_mobile_internet_enabled.disabled',
                              '/etc/tf_mobile_internet_enabled')

                if os.path.isfile('/etc/systemd/system/tf_mobile_internet_nm.service') \
                   and os.path.isfile('/etc/systemd/system/tf_mobile_internet_nm.timer'):
                        if is_enabled_mi_nm != None and not is_enabled_mi_nm:
                            if os.system('/bin/systemctl enable tf_mobile_internet_nm.service') != 0:
                                exit(21)

                        if is_enabled_mi_nm_timer != None and not is_enabled_mi_nm_timer:
                            if os.system('/bin/systemctl enable tf_mobile_internet_nm.timer') != 0:
                                exit(21)
            else:
                with open('/etc/tf_mobile_internet_enabled', 'w') as fd_ap_enabled:
                    pass

                if os.path.isfile('/etc/systemd/system/tf_mobile_internet.service'):
                    if is_enabled_mi != None and not is_enabled_mi:
                        if os.system('/bin/systemctl enable tf_mobile_internet') != 0:
                            exit(21)
        else:
            if IMAGE_VERSION and IMAGE_VERSION >= MIN_VERSION_WITH_NM:
                if not os.path.isfile('/etc/tf_mobile_internet_enabled'):
                    if not os.path.isfile('/etc/tf_mobile_internet_enabled.disabled'):
                        with open('/etc/tf_mobile_internet_enabled.disabled', 'w') as fd_ap_disabled:
                            pass
                else:
                    os.rename('/etc/tf_mobile_internet_enabled',
                              '/etc/tf_mobile_internet_enabled.disabled')

                if os.path.isfile('/etc/systemd/system/tf_mobile_internet_nm.service') \
                   and os.path.isfile('/etc/systemd/system/tf_mobile_internet_nm.timer'):
                        if is_enabled_mi_nm != None and is_enabled_mi_nm:
                            if os.system('/bin/systemctl disable tf_mobile_internet_nm.service') != 0:
                                exit(22)

                        if is_enabled_mi_nm_timer != None and is_enabled_mi_nm_timer:
                            if os.system('/bin/systemctl disable tf_mobile_internet_nm.timer') != 0:
                                exit(22)
            else:
                if os.path.isfile('/etc/tf_mobile_internet_enabled'):
                    os.remove('/etc/tf_mobile_internet_enabled')

                if os.path.isfile('/etc/systemd/system/tf_mobile_internet.service'):
                    if is_enabled_mi != None and is_enabled_mi:
                        if os.system('/bin/systemctl disable tf_mobile_internet') != 0:
                            exit(22)

        exit(0)

    except Exception as e:
        sys.stderr.write(unicode(e).encode('utf-8'))
        exit(23)

else:
    sys.stderr.write(u'Invalid parameters'.encode('utf-8'))
    exit(22)
