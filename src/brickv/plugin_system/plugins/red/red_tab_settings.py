# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red_tab_settings.py: RED settings tab implementation

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

import json
from PyQt4 import Qt, QtCore, QtGui

from brickv.plugin_system.plugins.red.ui_red_tab_settings import Ui_REDTabSettings
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red import config_parser
from brickv.plugin_system.plugins.red.script_manager import ScriptManager

from brickv.async_call import async_call

BOX_INDEX_NETWORK = 0

TAB_INDEX_NETWORK_GENERAL = 0

CONNECTION_TYPE_ETHERNET = 0
CONNECTION_TYPE_WIFI = 1

class REDTabSettings(QtGui.QWidget, Ui_REDTabSettings):
    script_manager = None
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session = None
        self.brickd_conf = None
        
        self.network_general_dict = None
        
        self.cbox_net_gen_contype.addItem("Ethernet")
        self.cbox_net_gen_contype.addItem("WiFi")

        self.cbox_net_eth_contype.addItem("DHCP")
        self.cbox_net_eth_contype.addItem("Static")

        self.cbox_net_wifi_contype.addItem("DHCP")
        self.cbox_net_wifi_contype.addItem("Static")
        
        self.cbox_net_gen_contype.currentIndexChanged.connect(self.cb_cbox_net_gen_contype_changed)

    def tab_on_focus(self):
        self.script_manager.execute_script('settings_network_general',
                                           self.cb_get_network_general_state_changed,
                                           [])
        
        self.wired_settings_conf = REDFile(self.session)
        self.wireless_settings_conf = REDFile(self.session)
        self.brickd_conf = REDFile(self.session)

        async_call(self.wired_settings_conf.open,
        ('/etc/wicd/wired-settings.conf', REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
        self.cb_wired_settings_conf_open, self.cb_wired_settings_conf_open_error)
        
        async_call(self.wireless_settings_conf.open,
        ('/etc/wicd/wireless-settings.conf', REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
        self.cb_wireless_settings_conf_open, self.cb_wireless_settings_conf_open_error)

        async_call(self.brickd_conf.open,
        ('/etc/brickd.conf', REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
        self.cb_brickd_conf_open, self.cb_brickd_conf_open_error)

    def tab_off_focus(self):
        pass

    # the callbacks
    def cb_cbox_net_gen_contype_changed(self, cidx):
        if cidx == CONNECTION_TYPE_ETHERNET:
            if "cconfig_ifs" in self.network_general_dict and\
               "eth0" in self.network_general_dict['cconfig_ifs'] and\
               "ip" in self.network_general_dict['cconfig_ifs']['eth0'] and\
               "mask" in self.network_general_dict['cconfig_ifs']['eth0']:
                self.label_net_gen_ccon_ip.setText(self.network_general_dict['cconfig_ifs']['eth0']['ip'].strip())
                self.label_net_gen_ccon_mask.setText(self.network_general_dict['cconfig_ifs']['eth0']['mask'].strip())
            else:
                self.label_net_gen_ccon_ip.setText("None")
                self.label_net_gen_ccon_mask.setText("None")

        elif cidx == CONNECTION_TYPE_WIFI:
            if "cconfig_ifs" in self.network_general_dict and\
               "wlan0" in self.network_general_dict['cconfig_ifs'] and\
               "ip" in self.network_general_dict['cconfig_ifs']['wlan0'] and\
               "mask" in self.network_general_dict['cconfig_ifs']['wlan0']:
                self.label_net_gen_ccon_ip.setText(self.network_general_dict['cconfig_ifs']['wlan0']['ip'].strip())
                self.label_net_gen_ccon_mask.setText(self.network_general_dict['cconfig_ifs']['wlan0']['mask'].strip())
            else:
                self.label_net_gen_ccon_ip.setText("None")
                self.label_net_gen_ccon_mask.setText("None")

        if "cconfig_dns" in self.network_general_dict and\
           "cconfig_gateway" in self.network_general_dict:
            self.label_net_gen_ccon_gateway.setText(self.network_general_dict['cconfig_dns'].strip())
            self.label_net_gen_ccon_dns.setText(self.network_general_dict['cconfig_gateway'].strip())

        else:
            self.label_net_gen_ccon_gateway.setText("None")
            self.label_net_gen_ccon_dns.setText("None")

    def cb_get_network_general_state_changed(self, result):
        self.network_general_dict = json.loads(result.stdout)
        self.ledit_net_gen_hostname.setText(self.network_general_dict['hostname'].strip())

        if(self.tbox_settings.currentIndex() == BOX_INDEX_NETWORK and\
           self.twidget_net.currentIndex() == TAB_INDEX_NETWORK_GENERAL):
            self.cb_cbox_net_gen_contype_changed(self.cbox_net_gen_contype.currentIndex())

    def cb_wired_settings_conf_open_error(self):
        pass

    def cb_wireless_settings_conf_open_error(self):
        pass

    def cb_brickd_conf_open_error(self):
        pass

    def cb_wired_settings_conf_open(self, result):
        self.wired_settings_conf.read_async(4096, self.cb_read_wired_settings_conf)
    
    def cb_wireless_settings_conf_open(self, result):
        self.wireless_settings_conf.read_async(4096, self.cb_read_wireless_settings_conf)
    
    def cb_brickd_conf_open(self, result):
        self.brickd_conf.read_async(4096, self.cb_read_brickd_conf)
    
    def cb_read_wired_settings_conf(self, result):
        if result == None:
            print "Could not read wired-settings.conf"
        cparser_wired_settings_conf = config_parser.parse_no_fake(result.data)
        #print as_cparser.get('Settings', 'wired_interface')
        self.wired_settings_conf.release()
    
    def cb_read_wireless_settings_conf(self, result):
        self.wired_settings_conf.release()

    def cb_read_brickd_conf(self, result):
        self.brickd_conf.release()
