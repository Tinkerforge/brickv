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

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

import json
from PyQt4 import Qt, QtCore, QtGui

from brickv.plugin_system.plugins.red.ui_red_tab_settings import Ui_REDTabSettings
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red import config_parser
from brickv.plugin_system.plugins.red.script_manager import ScriptManager

from brickv.async_call import async_call

REFRESH_TIMEOUT = 7000 # 7 seconds

NET_MANAGER_SETTINGS_CONF_FILE = "/etc/wicd/manager-settings.conf"
NET_WIRELESS_SETTINGS_CONF_FILE = "/etc/wicd/wireless-settings.conf"
NET_WIRED_SETTINGS_CONF_FILE = "/etc/wicd/wired-settings.conf"
BRICKD_BRICKD_CONF_FILE = "/etc/brickd.conf"

BOX_INDEX_NETWORK = 0
BOX_INDEX_BRICKD = 1
BOX_INDEX_DATETIME = 2
TAB_INDEX_NETWORK_GENERAL = 0
TAB_INDEX_NETWORK_WIRELESS = 1
TAB_INDEX_NETWORK_WIRED = 2
TAB_INDEX_BRICKD_GENERAL = 0
TAB_INDEX_BRICKD_ADVANCED = 1
TAB_INDEX_DATETIME_GENERAL = 0
CBOX_NET_CONTYPE_INDEX_DHCP = 0
CBOX_NET_CONTYPE_INDEX_STATIC = 1
CBOX_BRICKD_LOG_LEVEL_ERROR = 0
CBOX_BRICKD_LOG_LEVEL_WARN = 1
CBOX_BRICKD_LOG_LEVEL_INFO = 2
CBOX_BRICKD_LOG_LEVEL_DEBUG = 3
CBOX_BRICKD_LED_TRIGGER_CPU = 0
CBOX_BRICKD_LED_TRIGGER_GPIO = 1
CBOX_BRICKD_LED_TRIGGER_HEARTBEAT = 2
CBOX_BRICKD_LED_TRIGGER_MMC = 3
CBOX_BRICKD_LED_TRIGGER_OFF = 4
CBOX_BRICKD_LED_TRIGGER_ON = 5

class REDTabSettings(QtGui.QWidget, Ui_REDTabSettings):
    script_manager = None
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session = None

        self.refresh_timer = QtCore.QTimer()

        self.net_manager_settings_conf = None
        self.net_wireless_settings_conf = None
        self.net_wired_settings_conf = None
        self.brickd_brickd_conf = None
        self.net_gen_dict = {}
        self.dict_net_interfaces = {}
        self.cparser_net_manager_settings_conf = None
        self.cparser_net_wireless_settings_conf = None
        self.dict_net_wireless_scan_result = {}
        self.cparser_net_wired_settings_conf = None
        self.brickd_conf = {}

        self.mbox_settings = QtGui.QMessageBox()

        self.cbox_net_wired_contype.addItem("DHCP")
        self.cbox_net_wired_contype.addItem("Static")
        self.cbox_net_wireless_contype.addItem("DHCP")
        self.cbox_net_wireless_contype.addItem("Static")
        self.cbox_net_wireless_enctype.addItem("WPA 1/2 (Hex [0-9/A-F])")
        self.cbox_brickd_adv_ll.addItem("Error")
        self.cbox_brickd_adv_ll.addItem("Warn")
        self.cbox_brickd_adv_ll.addItem("Info")
        self.cbox_brickd_adv_ll.addItem("Debug")
        self.cbox_brickd_adv_rt.addItem("cpu")
        self.cbox_brickd_adv_rt.addItem("gpio")
        self.cbox_brickd_adv_rt.addItem("heartbeat")
        self.cbox_brickd_adv_rt.addItem("mmc")
        self.cbox_brickd_adv_rt.addItem("off")
        self.cbox_brickd_adv_rt.addItem("on")
        self.cbox_brickd_adv_gt.addItem("cpu")
        self.cbox_brickd_adv_gt.addItem("gpio")
        self.cbox_brickd_adv_gt.addItem("heartbeat")
        self.cbox_brickd_adv_gt.addItem("mmc")
        self.cbox_brickd_adv_gt.addItem("off")
        self.cbox_brickd_adv_gt.addItem("on")

        self.twidget_net.setTabEnabled(TAB_INDEX_NETWORK_WIRELESS, 0)
        self.twidget_net.setTabEnabled(TAB_INDEX_NETWORK_WIRED, 0)

        # connecting signals to slots
        self.refresh_timer.timeout.connect(self.cb_refresh_timer_timedout)
        self.tbox_settings.currentChanged.connect(self.cb_tbox_settings_current_changed)
        self.twidget_net.currentChanged.connect(self.cb_twidget_net_current_changed)
        self.cbox_net_wireless_contype.currentIndexChanged.connect\
            (self.cb_cbox_net_wireless_contype_current_idx_changed)
        self.cbox_net_wired_contype.currentIndexChanged.connect\
            (self.cb_cbox_net_wired_contype_current_idx_changed)
        self.pbutton_net_wired_activate.clicked.connect(self.cb_pbutton_net_wired_activate_clicked)
        
        # brickd buttons
        self.pbutton_brickd_general_save.pressed.connect(self.brickd_save_pressed)
        self.pbutton_brickd_general_refresh.pressed.connect(self.brickd_refresh_pressed)
        
        self.pbutton_brickd_adv_save.pressed.connect(self.brickd_save_pressed)
        self.pbutton_brickd_adv_refresh.pressed.connect(self.brickd_refresh_pressed)
        
        # brickd fields
        self.sbox_brickd_la_ip1.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_la_ip2.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_la_ip3.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_la_ip4.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_lp.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_lwsp.valueChanged.connect(self.brickd_settings_changed)
        self.ledit_brickd_secret.textEdited.connect(self.brickd_settings_changed)
        self.cbox_brickd_adv_ll.currentIndexChanged.connect(self.brickd_settings_changed)
        self.cbox_brickd_adv_rt.currentIndexChanged.connect(self.brickd_settings_changed)
        self.cbox_brickd_adv_gt.currentIndexChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_adv_spi_dly.valueChanged.connect(self.brickd_settings_changed)
        self.sbox_brickd_adv_rs485_dly.valueChanged.connect(self.brickd_settings_changed)


    def tab_on_focus(self):
        index = self.tbox_settings.currentIndex()
        if index == BOX_INDEX_BRICKD:
            self.brickd_refresh_pressed()
        elif index == BOX_INDEX_NETWORK:
            # Use self.network_general_refresh_pressed() or similar
            self.update_settings_net_all_data()
            self.refresh_timer.start(REFRESH_TIMEOUT)

    def tab_off_focus(self):
        self.refresh_timer.stop()

    def update_net_gen_widget_data(self):
        if self.net_gen_dict['cstat_hostname'] is not None:
            self.ledit_net_gen_hostname.setText(self.net_gen_dict['cstat_hostname'].strip())
        else:
            self.ledit_net_gen_hostname.setText("")

        if self.net_gen_dict['cstat_ifs']['active']['if_name'] is not None:
            self.label_net_gen_cstat_intf.setText(self.net_gen_dict['cstat_ifs']['active']['if_name'].strip())
        else:
            self.label_net_gen_cstat_intf.setText("Not Connected")
        self.label_net_gen_cstat_ip.setText(self.net_gen_dict['cstat_ifs']['active']['ip'].strip())
        self.label_net_gen_cstat_mask.setText(self.net_gen_dict['cstat_ifs']['active']['mask'].strip())
        self.label_net_gen_cstat_gateway.setText(self.net_gen_dict['cstat_gateway'].strip())
        self.label_net_gen_cstat_dns.setText(self.net_gen_dict['cstat_dns'].strip())

    def update_net_wireless_widget_data(self):
        if "wireless" in self.dict_net_interfaces:
            if self.dict_net_interfaces['wireless'] is None:
                self.twidget_net.setTabEnabled(TAB_INDEX_NETWORK_WIRELESS, 0)

            elif len(self.dict_net_interfaces['wireless']) > 0:
                    self.twidget_net.setTabEnabled(TAB_INDEX_NETWORK_WIRELESS, 1)
                    cbox_net_wireless_intf_clist = [self.cbox_net_wireless_intf.itemText(i)\
                                                    for i in range(self.cbox_net_wireless_intf.count())]

                    if cmp(cbox_net_wireless_intf_clist, self.dict_net_interfaces['wireless']) == -1:
                        self.cbox_net_wireless_intf.clear()
                        self.cbox_net_wireless_intf.addItems(self.dict_net_interfaces['wireless'])

    def update_net_wired_widget_data(self):
        if "wired" in self.dict_net_interfaces:
            if self.dict_net_interfaces['wired'] is None:
                self.twidget_net.setTabEnabled(TAB_INDEX_NETWORK_WIRED, 0)

            elif len(self.dict_net_interfaces['wired']) > 0:
                    self.twidget_net.setTabEnabled(TAB_INDEX_NETWORK_WIRED, 1)
                    cbox_net_wired_intf_clist = [self.cbox_net_wired_intf.itemText(i)\
                                                 for i in range(self.cbox_net_wired_intf.count())]

                    if cmp(cbox_net_wired_intf_clist, self.dict_net_interfaces['wired']) == -1:
                        self.cbox_net_wired_intf.clear()
                        self.cbox_net_wired_intf.addItems(self.dict_net_interfaces['wired'])



    def update_datetime_gen_widget_data(self):
        pass

    def update_settings_net_all_data(self):
        self.script_manager.execute_script('settings_network_gen',
                                           self.cb_settings_network_gen_returned,
                                           [])

        self.script_manager.execute_script('settings_network_wireless_scan',
                                           self.cb_settings_network_wireless_scan_returned,
                                           ['cache'])

        self.script_manager.execute_script('settings_network_get_interfaces',
                                           self.cb_settings_network_get_interfaces_returned,
                                           [])

        self.net_manager_settings_conf = REDFile(self.session)
        self.net_wired_settings_conf = REDFile(self.session)
        self.net_wireless_settings_conf = REDFile(self.session)

        async_call(self.net_manager_settings_conf.open,
                   (NET_MANAGER_SETTINGS_CONF_FILE, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   self.cb_net_manager_settings_conf_open,
                   self.cb_net_manager_settings_conf_open_error)

        async_call(self.net_wireless_settings_conf.open,
                   (NET_WIRELESS_SETTINGS_CONF_FILE, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   self.cb_net_wireless_settings_conf_open,
                   self.cb_net_wireless_settings_conf_open_error)

        async_call(self.net_wired_settings_conf.open,
                   (NET_WIRED_SETTINGS_CONF_FILE, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   self.cb_net_wired_settings_conf_open,
                   self.cb_net_wired_settings_conf_open_error)

    # the callbacks
    def cb_refresh_timer_timedout(self):
        self.refresh_timer.stop()
        self.update_settings_net_all_data()
        self.refresh_timer.start(REFRESH_TIMEOUT)

    def cb_settings_network_gen_returned(self, result):
        if result.stderr == "":
            self.net_gen_dict = json.loads(result.stdout)
            self.update_net_gen_widget_data()

    def cb_settings_network_wireless_scan_returned(self, result):
        if result.stderr == "":
            self.dict_net_wireless_scan_result = json.loads(result.stdout)
            self.update_net_wireless_widget_data()

    def cb_settings_network_get_interfaces_returned(self, result):
        if result.stderr == "":
            self.dict_net_interfaces = json.loads(result.stdout)
            self.update_net_wireless_widget_data()
            self.update_net_wired_widget_data()

    def cb_net_manager_settings_conf_open(self, result):
        self.net_manager_settings_conf.read_async(4096, self.cb_read_net_manager_settings_conf)

    def cb_net_manager_settings_conf_open_error(self, result):
        self.net_manager_settings_conf.release()

    def cb_net_wireless_settings_conf_open(self, result):
        self.net_wireless_settings_conf.read_async(4096, self.cb_read_net_wireless_settings_conf)

    def cb_net_wireless_settings_conf_open_error(self, result):
        self.net_wireless_settings_conf.release()

    def cb_net_wired_settings_conf_open(self, result):
        self.net_wired_settings_conf.read_async(4096, self.cb_read_net_wired_settings_conf)

    def cb_net_wired_settings_conf_open_error(self, result):
        self.net_wired_settings_conf.release()

    def cb_read_net_manager_settings_conf(self, result):
        if result is not None:
            self.cparser_net_manager_settings_conf = config_parser.parse_no_fake(result.data)
            self.update_net_wireless_widget_data()
            self.update_net_wired_widget_data()
        self.net_manager_settings_conf.release()

    def cb_read_net_wireless_settings_conf(self, result):
        if result is not None:
            self.cparser_net_wireless_settings_conf = config_parser.parse_no_fake(result.data)
            self.update_net_wireless_widget_data()
        self.net_wireless_settings_conf.release()

    def cb_read_net_wired_settings_conf(self, result):
        if result is not None:
            self.cparser_net_wired_settings_conf = config_parser.parse_no_fake(result.data)
            self.update_net_wired_widget_data()
        self.net_wired_settings_conf.release()

    def cb_tbox_settings_current_changed(self, ctidx):
        if ctidx == BOX_INDEX_BRICKD:
            self.brickd_refresh_pressed()

    def cb_twidget_net_current_changed(self, ctidx):
        if ctidx == TAB_INDEX_NETWORK_WIRELESS:
            if self.cbox_net_wireless_contype.currentIndex() == CBOX_NET_CONTYPE_INDEX_DHCP:
                self.frame_net_wireless_staticipconf.hide()
            elif self.cbox_net_wireless_contype.currentIndex() == CBOX_NET_CONTYPE_INDEX_STATIC:
                self.frame_net_wireless_staticipconf.show()

        elif ctidx == TAB_INDEX_NETWORK_WIRED:
            if self.cbox_net_wired_contype.currentIndex() == CBOX_NET_CONTYPE_INDEX_DHCP:
                self.frame_net_wired_staticipconf.hide()
            elif self.cbox_net_wired_contype.currentIndex() == CBOX_NET_CONTYPE_INDEX_STATIC:
                self.frame_net_wired_staticipconf.show()

    def cb_cbox_net_wireless_contype_current_idx_changed(self, cidx):
        if cidx == CBOX_NET_CONTYPE_INDEX_DHCP:
            self.frame_net_wireless_staticipconf.hide()
        elif cidx == CBOX_NET_CONTYPE_INDEX_STATIC:
            self.frame_net_wireless_staticipconf.show()

    def cb_cbox_net_wired_contype_current_idx_changed(self, cidx):
        if cidx == CBOX_NET_CONTYPE_INDEX_DHCP:
            self.frame_net_wired_staticipconf.hide()
        elif cidx == CBOX_NET_CONTYPE_INDEX_STATIC:
            self.frame_net_wired_staticipconf.show()

    def cb_pbutton_net_wired_activate_clicked(self):
        if self.cbox_net_wired_contype.currentIndex() == CBOX_NET_CONTYPE_INDEX_DHCP:
            self.cparser_net_wired_settings_conf.set("wired-default", "ip", "None")
            self.cparser_net_wired_settings_conf.set("wired-default", "netmask", "None")
            self.cparser_net_wired_settings_conf.set("wired-default", "gateway", "None")
            self.cparser_net_wired_settings_conf.set("wired-default", "search_domain", "None")
            self.cparser_net_wired_settings_conf.set("wired-default", "dns_domain", "None")
            self.cparser_net_wired_settings_conf.set("wired-default", "dns1", "None")
            self.cparser_net_wired_settings_conf.set("wired-default", "dns2", "None")
            self.cparser_net_wired_settings_conf.set("wired-default", "dns3", "None")
            if  self.net_gen_dict['cstat_hostname'] is not None:
                self.cparser_net_wired_settings_conf.set("wired-default", "dhcphostname", self.net_gen_dict['cstat_hostname'])
            else:
                self.cparser_net_wired_settings_conf.set("wired-default", "dhcphostname", self.net_gen_dict["None"])

        elif self.cbox_net_wired_contype.currentIndex() == CBOX_NET_CONTYPE_INDEX_STATIC:
            pass

        async_call(self.net_wired_settings_conf.open,
                   (NET_WIRED_SETTINGS_CONF_FILE,
                   REDFile.FLAG_WRITE_ONLY |
                   REDFile.FLAG_CREATE |
                   REDFile.FLAG_NON_BLOCKING |
                   REDFile.FLAG_TRUNCATE, 0500, 0, 0),
                   self.cb_net_wired_settings_conf_write_open,
                   self.cb_net_wired_settings_conf_write_open_error)

    def cb_net_wired_settings_conf_write_open(self, result):
        _strio_conf = StringIO()
        self.cparser_net_wired_settings_conf.write(_strio_conf)
        self.net_wired_settings_conf.write_async(_strio_conf.getvalue(), self.cb_net_wired_settings_conf_write_error, None)
        
    def cb_net_wired_settings_conf_write_open_error(self, error):
        self.net_wired_settings_conf.release()

    def cb_net_wired_settings_conf_write_error(self, error):
        if error == None:
            self.script_manager.execute_script('settings_network_connect_wired',
                                               self.cb_settings_network_connect_wired_changed,
                                               [])
            self.net_wired_settings_conf.release()
        else:
            self.net_wired_settings_conf.release()

    def cb_settings_network_connect_wired_changed(self, result):
        pass
    
    
    
    
    
    # ======== brickd settings =========
    
    def brickd_button_refresh_enabled(self, state):
        self.pbutton_brickd_general_refresh.setEnabled(state)
        self.pbutton_brickd_adv_refresh.setEnabled(state)
        
        if state:
            self.pbutton_brickd_general_refresh.setText("Refresh")
            self.pbutton_brickd_adv_refresh.setText("Refresh")
        else:
            self.pbutton_brickd_general_refresh.setText("Refreshing...")
            self.pbutton_brickd_adv_refresh.setText("Refreshing...")
        
    
    def brickd_button_save_enabled(self, state):
        self.pbutton_brickd_general_save.setEnabled(state)
        self.pbutton_brickd_adv_save.setEnabled(state)
        
        if state:
            self.pbutton_brickd_general_save.setText("Save")
            self.pbutton_brickd_adv_save.setText("Save")
        else:
            self.pbutton_brickd_general_save.setText("Saved")
            self.pbutton_brickd_adv_save.setText("Saved")
    
    def brickd_update_widget_data(self):
        print self.brickd_conf
        if self.brickd_conf == None:
            return
        
        # Fill keys with default values if not available
        if not 'listen.address' in self.brickd_conf:
            self.brickd_conf['listen.address'] = '0.0.0.0'
        if not 'listen.plain_port' in self.brickd_conf:
            self.brickd_conf['listen.plain_port'] = '4223'
        if not 'listen.websocket_port' in self.brickd_conf:
            self.brickd_conf['listen.websocket_port'] = '0'
        if not 'authentication.secret' in self.brickd_conf:
            self.brickd_conf['authentication.secret'] = ''
        if not 'log_level.event' in self.brickd_conf:
            self.brickd_conf['log_level.event'] = 'info'
        if not 'log_level.usb' in self.brickd_conf:
            self.brickd_conf['log_level.usb'] = 'info'
        if not 'log_level.network' in self.brickd_conf:
            self.brickd_conf['log_level.network'] = 'info'
        if not 'log_level.hotplug' in self.brickd_conf:
            self.brickd_conf['log_level.hotplug'] = 'info'
        if not 'log_level.hardware' in self.brickd_conf:
            self.brickd_conf['log_level.hardware'] = 'info'
        if not 'log_level.websocket' in self.brickd_conf:
            self.brickd_conf['log_level.websocket'] = 'info'
        if not 'log_level.red_brick' in self.brickd_conf:
            self.brickd_conf['log_level.red_brick'] = 'info'
        if not 'log_level.spi' in self.brickd_conf:
            self.brickd_conf['log_level.spi'] = 'info'
        if not 'log_level.rs485' in self.brickd_conf:
            self.brickd_conf['log_level.rs485'] = 'info'
        if not 'log_level.other' in self.brickd_conf:
            self.brickd_conf['log_level.other'] = 'info'
        if not 'led_trigger.green' in self.brickd_conf:
            self.brickd_conf['led_trigger.green'] = 'heartbeat'
        if not 'led_trigger.red' in self.brickd_conf:
            self.brickd_conf['led_trigger.red'] = 'off'
        if not 'poll_delay.spi' in self.brickd_conf:
            self.brickd_conf['poll_delay.spi'] = '50'
        if not 'poll_delay.rs485' in self.brickd_conf:
            self.brickd_conf['poll_delay.rs485'] = '4000'

        l_addr = self.brickd_conf['listen.address'].split('.')
        self.sbox_brickd_la_ip1.setValue(int(l_addr[0]))
        self.sbox_brickd_la_ip2.setValue(int(l_addr[1]))
        self.sbox_brickd_la_ip3.setValue(int(l_addr[2]))
        self.sbox_brickd_la_ip4.setValue(int(l_addr[3]))
        
        self.sbox_brickd_lp.setValue(int(self.brickd_conf['listen.plain_port']))
        self.sbox_brickd_lwsp.setValue(int(self.brickd_conf['listen.websocket_port']))
        self.ledit_brickd_secret.setText(self.brickd_conf['authentication.secret'])
        
        log_level = self.brickd_conf['log_level.other']
        if log_level == 'debug':
            self.cbox_brickd_adv_ll.setCurrentIndex(3)
        elif log_level == 'info':
            self.cbox_brickd_adv_ll.setCurrentIndex(2)
        elif log_level == 'warn':
            self.cbox_brickd_adv_ll.setCurrentIndex(1)
        elif log_level == 'error':
            self.cbox_brickd_adv_ll.setCurrentIndex(0)
        
        trigger_green = self.brickd_conf['led_trigger.green']
        if trigger_green == 'cpu':
            self.cbox_brickd_adv_gt.setCurrentIndex(0)
        elif trigger_green == 'gpio':
            self.cbox_brickd_adv_gt.setCurrentIndex(1)
        elif trigger_green == 'heartbeat':
            self.cbox_brickd_adv_gt.setCurrentIndex(2)
        elif trigger_green == 'mmc':
            self.cbox_brickd_adv_gt.setCurrentIndex(3)
        elif trigger_green == 'off':
            self.cbox_brickd_adv_gt.setCurrentIndex(4)
        elif trigger_green == 'on':
            self.cbox_brickd_adv_gt.setCurrentIndex(5)
            
        trigger_red = self.brickd_conf['led_trigger.red']
        if trigger_red == 'cpu':
            self.cbox_brickd_adv_rt.setCurrentIndex(0)
        elif trigger_red == 'gpio':
            self.cbox_brickd_adv_rt.setCurrentIndex(1)
        elif trigger_red == 'heartbeat':
            self.cbox_brickd_adv_rt.setCurrentIndex(2)
        elif trigger_red == 'mmc':
            self.cbox_brickd_adv_rt.setCurrentIndex(3)
        elif trigger_red == 'off':
            self.cbox_brickd_adv_rt.setCurrentIndex(4)
        elif trigger_red == 'on':
            self.cbox_brickd_adv_rt.setCurrentIndex(5)
        
        self.sbox_brickd_adv_spi_dly.setValue(int(self.brickd_conf['poll_delay.spi']))
        self.sbox_brickd_adv_rs485_dly.setValue(int(self.brickd_conf['poll_delay.rs485']))

    def brickd_refresh_pressed(self):
        self.brickd_button_refresh_enabled(False)
        
        def cb_open(red_file):
            def cb_read(red_file, result):
                red_file.release()

                if result is not None:
                    self.brickd_conf = config_parser.parse(result.data)
                    self.brickd_update_widget_data()
                else:
                    # TODO: Error popup for user?
                    print result

                self.brickd_button_refresh_enabled(True)
                self.brickd_button_save_enabled(False)
                
            red_file.read_async(4096, lambda x: cb_read(red_file, x))
            
        def cb_open_error(result):
            self.brickd_button_refresh_enabled(True)
            
            # TODO: Error popup for user?
            print result
            
        async_call(REDFile(self.session).open,
                   (BRICKD_BRICKD_CONF_FILE, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open,
                   cb_open_error)
    
    def brickd_save_pressed(self):
        self.brickd_button_save_enabled(False)

        # general
        adr = '.'.join((str(self.sbox_brickd_la_ip1.value()),
                        str(self.sbox_brickd_la_ip2.value()),
                        str(self.sbox_brickd_la_ip3.value()),
                        str(self.sbox_brickd_la_ip4.value())))
        self.brickd_conf['listen.address'] = adr
        self.brickd_conf['listen.plain_port'] = str(self.sbox_brickd_lp.value())
        self.brickd_conf['listen.websocket_port'] = str(self.sbox_brickd_lwsp.value())
        self.brickd_conf['authentication.secret'] = str(self.ledit_brickd_secret.text())
        
        def set_all_log_level(level):
            self.brickd_conf['log_level.event'] = level
            self.brickd_conf['log_level.usb'] = level
            self.brickd_conf['log_level.network'] = level
            self.brickd_conf['log_level.hotplug'] = level
            self.brickd_conf['log_level.hardware'] = level
            self.brickd_conf['log_level.websocket'] = level
            self.brickd_conf['log_level.red_brick'] = level
            self.brickd_conf['log_level.spi'] = level
            self.brickd_conf['log_level.rs485'] = level
            self.brickd_conf['log_level.other'] = level            
        
        # advanced
        index = self.cbox_brickd_adv_ll.currentIndex()
        if index == 0:
            set_all_log_level('error')
        elif index == 1:
            set_all_log_level('warn')
        elif index == 2:
            set_all_log_level('info')
        elif index == 3:
            set_all_log_level('debug')
            
        index = self.cbox_brickd_adv_gt.currentIndex()
        if index == 0:
            self.brickd_conf['led_trigger.green'] = 'cpu'
        elif index == 1:
            self.brickd_conf['led_trigger.green'] = 'gpio'
        elif index == 2:
            self.brickd_conf['led_trigger.green'] = 'heartbeat'
        elif index == 3:
            self.brickd_conf['led_trigger.green'] = 'mmc'
        elif index == 4:
            self.brickd_conf['led_trigger.green'] = 'off'
        elif index == 5:
            self.brickd_conf['led_trigger.green'] = 'on'
        
        index = self.cbox_brickd_adv_rt.currentIndex()
        if index == 0:
            self.brickd_conf['led_trigger.red'] = 'cpu'
        elif index == 1:
            self.brickd_conf['led_trigger.red'] = 'gpio'
        elif index == 2:
            self.brickd_conf['led_trigger.red'] = 'heartbeat'
        elif index == 3:
            self.brickd_conf['led_trigger.red'] = 'mmc'
        elif index == 4:
            self.brickd_conf['led_trigger.red'] = 'off'
        elif index == 5:
            self.brickd_conf['led_trigger.red'] = 'on'
            
        self.brickd_conf['poll_delay.spi'] = str(self.sbox_brickd_adv_spi_dly.value())
        self.brickd_conf['poll_delay.rs485'] = str(self.sbox_brickd_adv_rs485_dly.value())
        
        config = config_parser.to_string(self.brickd_conf)
        
        def cb_open(config, red_file):
            def cb_write(red_file, result):
                red_file.release()

                if result is not None:
                    self.brickd_button_save_enabled(True)
                    # TODO: Error popup for user?
                    print result
                else:
                    # TODO: Can brickd reload configuration? Otherwise we need to restart it.
                    pass
                
            red_file.write_async(config, lambda x: cb_write(red_file, x), None)
            
        def cb_open_error(result):
            self.brickd_button_save_enabled(True)
            
            # TODO: Error popup for user?
            print result
        
        async_call(REDFile(self.session).open,
                   (BRICKD_BRICKD_CONF_FILE,                    
                    REDFile.FLAG_WRITE_ONLY |
                    REDFile.FLAG_CREATE |
                    REDFile.FLAG_NON_BLOCKING |
                    REDFile.FLAG_TRUNCATE, 0500, 0, 0),
                   lambda x: cb_open(config, x),
                   cb_open_error)
            
        
    def brickd_settings_changed(self, value):
        self.brickd_button_save_enabled(True)
        