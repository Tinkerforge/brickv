# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

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
import time
from PyQt4 import Qt, QtCore, QtGui

from brickv.plugin_system.plugins.red.ui_red_tab_settings import Ui_REDTabSettings
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red import config_parser
from brickv.async_call import async_call

MANAGER_SETTINGS_CONF_PATH = '/etc/wicd/manager-settings.conf'
WIRELESS_SETTINGS_CONF_PATH = '/etc/wicd/wireless-settings.conf'
WIRED_SETTINGS_CONF_PATH = '/etc/wicd/wired-settings.conf'
BRICKD_CONF_PATH = '/etc/brickd.conf'

# Indexes
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

INTERFACE_TYPE_WIRELESS = 1
INTERFACE_TYPE_WIRED = 2
INTERFACE_STATE_ACTIVE = 1
INTERFACE_STATE_INACTIVE = 2
AP_STATUS_ASSOCIATED = 1
AP_STATUS_NOT_ASSOCIATED = 2

INTERFACE_NAME_USER_ROLE = QtCore.Qt.UserRole + 1
INTERFACE_TYPE_USER_ROLE = QtCore.Qt.UserRole + 2
INTERFACE_STATE_USER_ROLE = QtCore.Qt.UserRole + 3
INTERFACE_TYPE_WIRED_ADDRESS_CONF_USER_ROLE = QtCore.Qt.UserRole + 4
INTERFACE_TYPE_WIRED_IP_USER_ROLE = QtCore.Qt.UserRole + 5
INTERFACE_TYPE_WIRED_MASK_USER_ROLE = QtCore.Qt.UserRole + 6
INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE = QtCore.Qt.UserRole + 7
INTERFACE_TYPE_WIRED_DNS_USER_ROLE = QtCore.Qt.UserRole + 8

AP_NAME_USER_ROLE = QtCore.Qt.UserRole + 1
AP_STATUS_USER_ROLE = QtCore.Qt.UserRole + 2
AP_NETWORK_INDEX_USER_ROLE = QtCore.Qt.UserRole + 3
AP_CHANNEL_USER_ROLE = QtCore.Qt.UserRole + 4
AP_ENCRYPTION_USER_ROLE = QtCore.Qt.UserRole + 5
AP_ENCRYPTION_METHOD_USER_ROLE = QtCore.Qt.UserRole + 6
AP_KEY_USER_ROLE = QtCore.Qt.UserRole + 7
AP_BSSID_USER_ROLE = QtCore.Qt.UserRole + 8
AP_ADDRESS_CONF_USER_ROLE = QtCore.Qt.UserRole + 9
AP_IP_USER_ROLE = QtCore.Qt.UserRole + 10
AP_MASK_USER_ROLE = QtCore.Qt.UserRole + 11
AP_GATEWAY_USER_ROLE = QtCore.Qt.UserRole + 12
AP_DNS_USER_ROLE = QtCore.Qt.UserRole + 13

WORKING_STATE_REFRESH = 1
WORKING_STATE_SCAN = 2
WORKING_STATE_DONE = 3
WORKING_STATE_SAVE = 4

class REDTabSettings(QtGui.QWidget, Ui_REDTabSettings):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session        = None # set from RED after construction
        self.script_manager = None # set from RED after construction

        self.time_refresh_timer = QtCore.QTimer()
        self.time_refresh_timer.setInterval(1000)
        self.time_refresh_timer.timeout.connect(self.time_refresh)
        
        self.time_local_old = 0
        self.time_red_old = 0
        self.last_index = -1
        self.network_refresh_tasks_remaining = -1
        self.work_on_progress = False

        self.network_all_data = {'status': None,
                                 'interfaces': None,
                                 'scan_result': None,
                                 'manager_settings': None,
                                 'wireless_settings': None,
                                 'wired_settings': None}
        self.brickd_conf = {}

        self.cbox_brickd_adv_ll.addItem('Error')
        self.cbox_brickd_adv_ll.addItem('Warn')
        self.cbox_brickd_adv_ll.addItem('Info')
        self.cbox_brickd_adv_ll.addItem('Debug')
        self.cbox_brickd_adv_rt.addItem('cpu')
        self.cbox_brickd_adv_rt.addItem('gpio')
        self.cbox_brickd_adv_rt.addItem('heartbeat')
        self.cbox_brickd_adv_rt.addItem('mmc')
        self.cbox_brickd_adv_rt.addItem('off')
        self.cbox_brickd_adv_rt.addItem('on')
        self.cbox_brickd_adv_gt.addItem('cpu')
        self.cbox_brickd_adv_gt.addItem('gpio')
        self.cbox_brickd_adv_gt.addItem('heartbeat')
        self.cbox_brickd_adv_gt.addItem('mmc')
        self.cbox_brickd_adv_gt.addItem('off')
        self.cbox_brickd_adv_gt.addItem('on')

        # Signals and slots

        # Tabs
        self.tbox_settings.currentChanged.connect(self.slot_tbox_settings_current_changed)

        # Network Buttons
        self.pbutton_net_wireless_scan.clicked.connect(self.slot_pbutton_net_wireless_scan_clicked)
        self.pbutton_net_refresh.clicked.connect(self.slot_network_refresh_clicked)
        self.pbutton_net_save.clicked.connect(self.slot_network_save_clicked)

        # Network fields
        self.frame_net_conftype.hide()
        self.frame_static_ip_conf.hide()
        self.frame_working_please_wait.hide()
        self.ledit_net_hostname.setReadOnly(True)
        self.cbox_net_intf.currentIndexChanged.connect(self.slot_network_settings_changed)
        self.cbox_net_intf.currentIndexChanged.connect(self.slot_cbox_net_intf_current_idx_changed)
        self.cbox_net_conftype.currentIndexChanged.connect(self.slot_network_settings_changed)
        self.cbox_net_conftype.currentIndexChanged.connect(self.slot_cbox_net_conftype_current_idx_changed)
        self.cbox_net_wireless_ap.currentIndexChanged.connect(self.slot_network_settings_changed)
        self.cbox_net_wireless_ap.currentIndexChanged.connect(self.slot_cbox_net_wireless_ap_current_idx_changed)
        self.ledit_net_wireless_key.textEdited.connect(self.slot_network_settings_changed)
        self.ledit_net_wireless_key.setEchoMode(QtGui.QLineEdit.Password)
        self.cbox_net_wireless_key_show.stateChanged.connect(self.slot_net_wireless_key_show_state_changed)
        self.sbox_net_ip1.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_ip2.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_ip3.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_ip4.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_mask1.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_mask2.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_mask3.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_mask4.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_gw1.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_gw2.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_gw3.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_gw4.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_dns1.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_dns2.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_dns3.valueChanged.connect(self.slot_network_settings_changed)
        self.sbox_net_dns4.valueChanged.connect(self.slot_network_settings_changed)

        # Brick daemon buttons
        self.pbutton_brickd_general_save.clicked.connect(self.slot_brickd_save_clicked)
        self.pbutton_brickd_general_refresh.clicked.connect(self.slot_brickd_refresh_clicked)
        self.pbutton_brickd_adv_save.clicked.connect(self.slot_brickd_save_clicked)
        self.pbutton_brickd_adv_refresh.clicked.connect(self.slot_brickd_refresh_clicked)
        
        # Brick daemon fields
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

        # Date/Time buttons
        self.time_sync_button.clicked.connect(self.time_sync_clicked)

    def tab_on_focus(self):
        self.manager_settings_conf_rfile = REDFile(self.session)
        self.wired_settings_conf_rfile = REDFile(self.session)
        self.wireless_settings_conf_rfile = REDFile(self.session)
        self.brickd_conf_rfile = REDFile(self.session)

        index = self.tbox_settings.currentIndex()
        if index == BOX_INDEX_NETWORK:
            if not self.work_on_progress:
                self.slot_network_refresh_clicked()
        elif index == BOX_INDEX_BRICKD:
            self.slot_brickd_refresh_clicked()
        elif index == BOX_INDEX_DATETIME:
            self.time_start()

    def tab_off_focus(self):
        index = self.tbox_settings.currentIndex()
        self.last_index = index

        if index == BOX_INDEX_BRICKD:
            pass
        elif index == BOX_INDEX_NETWORK:
            pass
        elif index == BOX_INDEX_DATETIME:
            self.time_stop()

    def tab_destroy(self):
        pass

    def show_wireless_configuration(self, show):
        self.cbox_net_wireless_ap.clear()
        self.cbox_net_wireless_ap.addItem('Scan to get access points...')
        self.cbox_net_wireless_ap.setEnabled(False)
        self.label_net_wireless_channel.setText('')
        self.label_net_wireless_enctype.setText('')
        self.ledit_net_wireless_key.setText('')
        if show:
            self.frame_wireless_conf.show()
            self.cbox_net_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_DHCP)
            self.frame_net_conftype.hide()
        else:
            self.frame_wireless_conf.hide()
            self.frame_net_conftype.show()

    def show_please_wait(self, state):
        self.frame_working_please_wait.show()
        self.sarea_net.setEnabled(False)
        self.network_button_refresh_enabled(False)
        self.network_button_save_enabled(False)

        if state == WORKING_STATE_REFRESH:
            self.work_on_progress = True
            self.label_net_gen_cstat_intf.setText('')
            self.label_net_gen_cstat_ip.setText('')
            self.label_net_gen_cstat_mask.setText('')
            self.label_net_gen_cstat_gateway.setText('')
            self.label_net_gen_cstat_dns.setText('')
            self.ledit_net_hostname.setText('')

            self.cbox_net_intf.clear()
            self.cbox_net_intf.setEnabled(False)
            
            self.cbox_net_wireless_ap.clear()
            self.cbox_net_wireless_ap.addItem('')
            self.cbox_net_wireless_ap.setEnabled(False)
            self.label_net_wireless_channel.setText('')
            self.label_net_wireless_enctype.setText('')
            self.ledit_net_wireless_key.setEnabled(False)
            self.ledit_net_wireless_key.setText('')
            self.frame_wireless_conf.hide()

            self.cbox_net_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_DHCP)
            self.frame_net_conftype.hide()

        elif state == WORKING_STATE_SCAN:
            self.work_on_progress = True
            self.cbox_net_wireless_ap.clear()
            self.cbox_net_wireless_ap.addItem('Scanning...')
            self.cbox_net_wireless_ap.setEnabled(False)
            self.label_net_wireless_channel.setText('')
            self.label_net_wireless_enctype.setText('')
            self.ledit_net_wireless_key.setEnabled(False)
            self.ledit_net_wireless_key.setText('')

        elif state == WORKING_STATE_SAVE:
            self.work_on_progress = True
            self.network_button_refresh_enabled(True)
            self.network_button_save_enabled(True)

        elif state == WORKING_STATE_DONE:
            self.work_on_progress = False
            self.frame_working_please_wait.hide()
            self.sarea_net.setEnabled(True)
            self.network_button_refresh_enabled(True)
            self.network_button_save_enabled(False)

    def update_access_points(self):
        self.cbox_net_wireless_ap.clear()

        def no_ap_found():
            self.cbox_net_wireless_ap.clear()
            self.label_net_wireless_channel.setText('')
            self.label_net_wireless_enctype.setText('')
            self.ledit_net_wireless_key.setText('')
            self.cbox_net_wireless_ap.addItem('No access points found. Scan?')
            self.cbox_net_wireless_ap.setEnabled(False)

        if self.network_all_data['scan_result'] is not None and\
           self.network_all_data['interfaces']['wireless'] is not None and\
           self.network_all_data['interfaces']['wireless_links'] is not None:

                if len(self.network_all_data['scan_result']) <= 0 or\
                   len(self.network_all_data['interfaces']['wireless']) <= 0:
                       no_ap_found()
                       return

                for nidx, apdict in self.network_all_data['scan_result'].iteritems():
                    self.cbox_net_wireless_ap.addItem(unicode(apdict['essid']))

                    idx_cbox = self.cbox_net_wireless_ap.count() - 1
                
                    self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                          QtCore.QVariant(unicode(apdict['essid'])),
                                                          AP_NAME_USER_ROLE)
                
                    self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                          QtCore.QVariant(AP_STATUS_NOT_ASSOCIATED),
                                                          AP_STATUS_USER_ROLE)
                
                    self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                          QtCore.QVariant(nidx),
                                                          AP_NETWORK_INDEX_USER_ROLE)
                
                    self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                          QtCore.QVariant(apdict['channel']),
                                                          AP_CHANNEL_USER_ROLE)
                
                    self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                          QtCore.QVariant(apdict['encryption']),
                                                          AP_ENCRYPTION_USER_ROLE)

                    if apdict['encryption'] != 'Off':
                        if apdict['encryption_method'] == 'WPA1' or\
                           apdict['encryption_method'] == 'WPA2':
                                self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                      QtCore.QVariant(apdict['encryption_method']),
                                                                      AP_ENCRYPTION_METHOD_USER_ROLE)
                        else:
                            self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                  QtCore.QVariant('Unsupported'),
                                                                  AP_ENCRYPTION_METHOD_USER_ROLE)
                
                    self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                          QtCore.QVariant(apdict['bssid']),
                                                          AP_BSSID_USER_ROLE)
                
                    try:
                        _key = self.network_all_data['wireless_settings'].get(apdict['bssid'], 'key', '')
                        self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                              QtCore.QVariant(unicode(key)),
                                                              AP_KEY_USER_ROLE)
                    except:
                        self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                              QtCore.QVariant(''),
                                                              AP_KEY_USER_ROLE)
                
                    # Checking if the accesspoint is associated
                    for key, value in self.network_all_data['interfaces']['wireless_links'].iteritems():
                        if unicode(value['essid']) == unicode(apdict['essid']) and value['status']:
                            self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                  QtCore.QVariant(AP_STATUS_ASSOCIATED),
                                                                  AP_STATUS_USER_ROLE)
                    try:
                        _ip = self.network_all_data['wireless_settings'].get(apdict['bssid'], 'ip', '')
                        if _ip == '' or _ip == 'None':
                            self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                  QtCore.QVariant(CBOX_NET_CONTYPE_INDEX_DHCP),
                                                                  AP_ADDRESS_CONF_USER_ROLE)
                            self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                  QtCore.QVariant('0.0.0.0'),
                                                                  AP_IP_USER_ROLE)
                        else:
                            self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                  QtCore.QVariant(CBOX_NET_CONTYPE_INDEX_STATIC),
                                                                  AP_ADDRESS_CONF_USER_ROLE)
                            self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                  QtCore.QVariant(_ip),
                                                                  AP_IP_USER_ROLE)
                    except:
                        self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                              QtCore.QVariant(CBOX_NET_CONTYPE_INDEX_DHCP),
                                                              AP_ADDRESS_CONF_USER_ROLE)
                        self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                              QtCore.QVariant('0.0.0.0'),
                                                              AP_IP_USER_ROLE)
                
                    try:
                        _mask = self.network_all_data['wireless_settings'].get(apdict['bssid'], 'netmask', '')
                        if _mask == '' or _ip == 'None':
                            self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                  QtCore.QVariant('0.0.0.0'),
                                                                  AP_MASK_USER_ROLE)
                        else:
                            self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                  QtCore.QVariant(_mask),
                                                                  AP_MASK_USER_ROLE)
                    except:
                        self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                  QtCore.QVariant('0.0.0.0'),
                                                                  AP_MASK_USER_ROLE)
                
                    try:
                        _gw = self.network_all_data['wireless_settings'].get(apdict['bssid'], 'gateway', '')
                        if _gw == '' or _gw == 'None':
                            self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                  QtCore.QVariant('0.0.0.0'),
                                                                  AP_GATEWAY_USER_ROLE)
                        else:
                            self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                  QtCore.QVariant(_gw),
                                                                  AP_GATEWAY_USER_ROLE)
                    except:
                        self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                  QtCore.QVariant('0.0.0.0'),
                                                                  AP_GATEWAY_USER_ROLE)
                
                    try:
                        _dns = self.network_all_data['wireless_settings'].get(apdict['bssid'], 'dns1', '')
                        if _dns == '' or _dns == 'None':
                            self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                  QtCore.QVariant('0.0.0.0'),
                                                                  AP_DNS_USER_ROLE)
                        else:
                            self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                  QtCore.QVariant(_dns),
                                                                  AP_DNS_USER_ROLE)
                    except:
                        self.cbox_net_wireless_ap.setItemData(idx_cbox,
                                                                  QtCore.QVariant('0.0.0.0'),
                                                                  AP_DNS_USER_ROLE)

                if self.cbox_net_wireless_ap.count() == 0:
                    no_ap_found()
                    return

                self.cbox_net_wireless_ap.setEnabled(True)

                # Select first associated accesspoint if not then the first item
                self.cbox_net_wireless_ap.setCurrentIndex(-1)
                for i in range(self.cbox_net_wireless_ap.count()):
                    ap_status = self.cbox_net_wireless_ap.itemData(i, AP_STATUS_USER_ROLE).toInt()[0]
                    if ap_status == AP_STATUS_ASSOCIATED:
                        self.cbox_net_wireless_ap.setCurrentIndex(i)
                        break
                    if i == self.cbox_net_wireless_ap.count() - 1:
                        self.cbox_net_wireless_ap.setCurrentIndex(0)

        else:
            no_ap_found()

    def update_network_gui(self):
        def update_no_interface_available():
            self.cbox_net_intf.clear()
            self.cbox_net_intf.addItem('No interfaces available')
            self.cbox_net_intf.setEnabled(False)
            self.frame_wireless_conf.hide()
            self.cbox_net_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_DHCP)
            self.frame_net_conftype.hide()
            self.frame_static_ip_conf.hide()

        # Populating the current network status section and hostname
        if self.network_all_data['status'] is not None:
            self.ledit_net_hostname.setText\
                (self.network_all_data['status']['cstat_hostname'])

            if self.network_all_data['status']['cstat_intf_active']['name'] is not None:
                self.label_net_gen_cstat_ip.setText(self.network_all_data['status']['cstat_intf_active']['ip'])
                self.label_net_gen_cstat_mask.setText(self.network_all_data['status']['cstat_intf_active']['mask'])
            else:
                self.label_net_gen_cstat_intf.setText('None')
                self.label_net_gen_cstat_ip.setText('None')
                self.label_net_gen_cstat_mask.setText('None')

            if self.network_all_data['status']['cstat_gateway'] is not None:
                self.label_net_gen_cstat_gateway.setText(self.network_all_data['status']['cstat_gateway'])
            else:
                self.label_net_gen_cstat_gateway.setText('None')
            
            if self.network_all_data['status']['cstat_dns'] is not None:
                self.label_net_gen_cstat_dns.setText(self.network_all_data['status']['cstat_dns'].strip())
            else:
                self.label_net_gen_cstat_dns.setText('None')
        else:
            self.ledit_net_hostname.setText('None')
            self.label_net_gen_cstat_intf.setText('None')
            self.label_net_gen_cstat_ip.setText('None')
            self.label_net_gen_cstat_mask.setText('None')
            self.label_net_gen_cstat_gateway.setText('None')
            self.label_net_gen_cstat_dns.setText('None')

        # Populating available interfaces
        self.cbox_net_intf.clear()

        if self.network_all_data['interfaces'] is not None and\
           self.network_all_data['status'] is not None and\
           (self.network_all_data['interfaces']['wireless'] is not None or\
           self.network_all_data['interfaces']['wired'] is not None or\
           self.network_all_data['interfaces']['wireless_links'] is not None):
                #active_intf_found = False

                # Processing wireless interfaces
                if self.network_all_data['interfaces']['wireless'] is not None and\
                   len(self.network_all_data['interfaces']['wireless']) > 0:
                        for intf in self.network_all_data['interfaces']['wireless']:
                            '''if intf == self.network_all_data['status']['cstat_intf_active']['name']:
                                active_intf_found = True
                                self.cbox_net_intf.addItem(intf+' : Wireless (active)')
                            else:
                                self.cbox_net_intf.addItem(intf+' : Wireless')
                            '''

                            self.cbox_net_intf.addItem(intf+' : Wireless')
                            
                            self.cbox_net_intf.setItemData(self.cbox_net_intf.count() - 1,
                                                           QtCore.QVariant(unicode(intf)), INTERFACE_NAME_USER_ROLE)
        
                            self.cbox_net_intf.setItemData(self.cbox_net_intf.count() - 1,
                                                           QtCore.QVariant(INTERFACE_TYPE_WIRELESS), INTERFACE_TYPE_USER_ROLE)

                            if intf == self.network_all_data['status']['cstat_intf_active']['name']:
                                self.cbox_net_intf.setItemData(self.cbox_net_intf.count() - 1,
                                                               QtCore.QVariant(INTERFACE_STATE_ACTIVE),
                                                               INTERFACE_STATE_USER_ROLE)
                            else:
                                self.cbox_net_intf.setItemData(self.cbox_net_intf.count() - 1,
                                                               QtCore.QVariant(INTERFACE_STATE_INACTIVE),
                                                               INTERFACE_STATE_USER_ROLE)

                # Processing wired interfaces
                if self.network_all_data['interfaces']['wired'] is not None and\
                   len(self.network_all_data['interfaces']['wired']) > 0:
                        try:
                            cwintf = unicode(self.network_all_data['manager_settings'].get('Settings', 'wired_interface', 'None'))
                        except:
                            cwintf = 'None'

                        for intf in self.network_all_data['interfaces']['wired']:
                            '''
                            if intf == self.network_all_data['status']['cstat_intf_active']['name']:
                                active_intf_found = True
                                self.cbox_net_intf.addItem(intf+' : Wired (active)')
                            else:
                                self.cbox_net_intf.addItem(intf+' : Wired')
                            '''
                    
                            self.cbox_net_intf.addItem(intf+' : Wired')
                    
                            idx_cbox = self.cbox_net_intf.count() - 1
                            
                            if intf == self.network_all_data['status']['cstat_intf_active']['name']:
                                self.cbox_net_intf.setItemData(idx_cbox,
                                                               QtCore.QVariant(INTERFACE_STATE_ACTIVE),
                                                               INTERFACE_STATE_USER_ROLE)
                            else:
                                self.cbox_net_intf.setItemData(idx_cbox,
                                                               QtCore.QVariant(INTERFACE_STATE_INACTIVE),
                                                               INTERFACE_STATE_USER_ROLE)
                    
                            self.cbox_net_intf.setItemData(self.cbox_net_intf.count() - 1,
                                                           QtCore.QVariant(unicode(intf)), INTERFACE_NAME_USER_ROLE)
                    
                            self.cbox_net_intf.setItemData(idx_cbox,
                                                           QtCore.QVariant(INTERFACE_TYPE_WIRED), INTERFACE_TYPE_USER_ROLE)
                    
                            # Populating wired interface fields
                            if cwintf == intf:
                                try:
                                    _ip = self.network_all_data['wired_settings'].get('wired-default', 'ip', 'None')
                                except:
                                    _ip == 'None'
                    
                                if _ip == 'None':
                                    self.cbox_net_intf.setItemData(idx_cbox,
                                                                   QtCore.QVariant(CBOX_NET_CONTYPE_INDEX_DHCP),
                                                                   INTERFACE_TYPE_WIRED_ADDRESS_CONF_USER_ROLE)
                                    self.cbox_net_intf.setItemData(idx_cbox,
                                                                   QtCore.QVariant('0.0.0.0'),
                                                                   INTERFACE_TYPE_WIRED_IP_USER_ROLE)
                                    self.cbox_net_intf.setItemData(idx_cbox,
                                                                  QtCore.QVariant('0.0.0.0'),
                                                                  INTERFACE_TYPE_WIRED_MASK_USER_ROLE)
                                    self.cbox_net_intf.setItemData(idx_cbox,
                                                                  QtCore.QVariant('0.0.0.0'),
                                                                  INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE)
                                    self.cbox_net_intf.setItemData(idx_cbox,
                                                                  QtCore.QVariant('0.0.0.0'),
                                                                  INTERFACE_TYPE_WIRED_DNS_USER_ROLE)
                                else:
                                    self.cbox_net_intf.setItemData(idx_cbox,
                                                                   QtCore.QVariant(CBOX_NET_CONTYPE_INDEX_STATIC),
                                                                   INTERFACE_TYPE_WIRED_ADDRESS_CONF_USER_ROLE)
                                    self.cbox_net_intf.setItemData(idx_cbox,
                                                                   QtCore.QVariant(_ip),
                                                                   INTERFACE_TYPE_WIRED_IP_USER_ROLE)
                                    try:
                                        _mask = self.network_all_data['wired_settings'].get('wired-default', 'netmask', '')
                                        if _mask == '' or _mask == 'None':
                                            self.cbox_net_intf.setItemData(idx_cbox,
                                                                           QtCore.QVariant('0.0.0.0'),
                                                                           INTERFACE_TYPE_WIRED_MASK_USER_ROLE)
                                        else:
                                            self.cbox_net_intf.setItemData(idx_cbox,
                                                                           QtCore.QVariant(_mask),
                                                                           INTERFACE_TYPE_WIRED_MASK_USER_ROLE)
                                    except:
                                        self.cbox_net_intf.setItemData(idx_cbox,
                                                                       QtCore.QVariant('0.0.0.0'),
                                                                       INTERFACE_TYPE_WIRED_MASK_USER_ROLE)
                                                                  
                                    try:
                                        _gw = self.network_all_data['wired_settings'].get('wired-default', 'gateway', '')
                                        if _gw == '' or _gw == 'None':
                                            self.cbox_net_intf.setItemData(idx_cbox,
                                                                           QtCore.QVariant('0.0.0.0'),
                                                                           INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE)
                                        else:
                                            self.cbox_net_intf.setItemData(idx_cbox,
                                                                           QtCore.QVariant(_gw),
                                                                           INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE)
                                    except:
                                        self.cbox_net_intf.setItemData(idx_cbox,
                                                                       QtCore.QVariant('0.0.0.0'),
                                                                       INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE)
                               
                                        
                                    try:
                                        _dns = self.network_all_data['wired_settings'].get('wired-default', 'dns1', '')
                                        if _dns == '' or _dns == 'None':
                                            self.cbox_net_intf.setItemData(idx_cbox,
                                                                           QtCore.QVariant('0.0.0.0'),
                                                                           INTERFACE_TYPE_WIRED_DNS_USER_ROLE)
                                        else:
                                            self.cbox_net_intf.setItemData(idx_cbox,
                                                                           QtCore.QVariant(_dns),
                                                                           INTERFACE_TYPE_WIRED_DNS_USER_ROLE)
                                    except:
                                        self.cbox_net_intf.setItemData(idx_cbox,
                                                                       QtCore.QVariant('0.0.0.0'),
                                                                       INTERFACE_TYPE_WIRED_DNS_USER_ROLE)
                            else:
                                self.cbox_net_intf.setItemData(idx_cbox,
                                                              QtCore.QVariant(CBOX_NET_CONTYPE_INDEX_DHCP),
                                                              INTERFACE_TYPE_WIRED_ADDRESS_CONF_USER_ROLE)
                                self.cbox_net_intf.setItemData(idx_cbox,
                                                              QtCore.QVariant('0.0.0.0'),
                                                              INTERFACE_TYPE_WIRED_IP_USER_ROLE)
                                self.cbox_net_intf.setItemData(idx_cbox,
                                                              QtCore.QVariant('0.0.0.0'),
                                                              INTERFACE_TYPE_WIRED_MASK_USER_ROLE)
                                self.cbox_net_intf.setItemData(idx_cbox,
                                                              QtCore.QVariant('0.0.0.0'),
                                                              INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE)
                                self.cbox_net_intf.setItemData(idx_cbox,
                                                              QtCore.QVariant('0.0.0.0'),
                                                              INTERFACE_TYPE_WIRED_DNS_USER_ROLE)
                                
                if self.cbox_net_intf.count() <= 0:
                    update_no_interface_available()
                    self.label_net_gen_cstat_intf.setText('None')
                    return
                else:
                    # Select first active interface by default if not then the first item
                    self.label_net_gen_cstat_intf.setText('None')
                    self.cbox_net_intf.setCurrentIndex(-1)
                    for i in range(self.cbox_net_intf.count()):
                        istate = self.cbox_net_intf.itemData(i, INTERFACE_STATE_USER_ROLE).toInt()[0]
                        if istate == INTERFACE_STATE_ACTIVE:
                            self.cbox_net_intf.setCurrentIndex(i)
                            iname = self.cbox_net_intf.itemData(i, INTERFACE_NAME_USER_ROLE).toString()
                            itype = self.cbox_net_intf.itemData(i, INTERFACE_TYPE_USER_ROLE).toInt()[0]
                            if itype == INTERFACE_TYPE_WIRELESS:
                                cstat_intf_name = iname+' : Wireless'
                            else:
                                cstat_intf_name = iname+' : Wired'
                            self.label_net_gen_cstat_intf.setText(cstat_intf_name)
                            break
                        if i == self.cbox_net_intf.count() - 1:
                            self.cbox_net_intf.setCurrentIndex(0)

                self.cbox_net_intf.setEnabled(True)

        elif self.network_all_data['interfaces']['wireless'] is None and\
           self.network_all_data['interfaces']['wired'] is None:
                update_no_interface_available()

        elif self.network_all_data['interfaces']['wireless'] is not None and\
             self.network_all_data['interfaces']['wired'] is not None:
                 if len(self.network_all_data['interfaces']['wireless']) <= 0 and\
                    len(self.network_all_data['interfaces']['wired']) <= 0:
                        update_no_interface_available()

    def update_brickd_widget_data(self):
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
        if not 'log.level' in self.brickd_conf:
            self.brickd_conf['log.level'] = 'info'
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
        
        log_level = self.brickd_conf['log.level']
        if log_level == 'debug':
            self.cbox_brickd_adv_ll.setCurrentIndex(CBOX_BRICKD_LOG_LEVEL_DEBUG)
        elif log_level == 'info':
            self.cbox_brickd_adv_ll.setCurrentIndex(CBOX_BRICKD_LOG_LEVEL_INFO)
        elif log_level == 'warn':
            self.cbox_brickd_adv_ll.setCurrentIndex(CBOX_BRICKD_LOG_LEVEL_WARN)
        elif log_level == 'error':
            self.cbox_brickd_adv_ll.setCurrentIndex(CBOX_BRICKD_LOG_LEVEL_ERROR)
        
        trigger_green = self.brickd_conf['led_trigger.green']
        if trigger_green == 'cpu':
            self.cbox_brickd_adv_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_CPU)
        elif trigger_green == 'gpio':
            self.cbox_brickd_adv_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_GPIO)
        elif trigger_green == 'heartbeat':
            self.cbox_brickd_adv_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_HEARTBEAT)
        elif trigger_green == 'mmc':
            self.cbox_brickd_adv_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_MMC)
        elif trigger_green == 'off':
            self.cbox_brickd_adv_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_OFF)
        elif trigger_green == 'on':
            self.cbox_brickd_adv_gt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_ON)
            
        trigger_red = self.brickd_conf['led_trigger.red']
        if trigger_red == 'cpu':
            self.cbox_brickd_adv_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_CPU)
        elif trigger_red == 'gpio':
            self.cbox_brickd_adv_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_GPIO)
        elif trigger_red == 'heartbeat':
            self.cbox_brickd_adv_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_HEARTBEAT)
        elif trigger_red == 'mmc':
            self.cbox_brickd_adv_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_MMC)
        elif trigger_red == 'off':
            self.cbox_brickd_adv_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_OFF)
        elif trigger_red == 'on':
            self.cbox_brickd_adv_rt.setCurrentIndex(CBOX_BRICKD_LED_TRIGGER_ON)
        
        self.sbox_brickd_adv_spi_dly.setValue(int(self.brickd_conf['poll_delay.spi']))
        self.sbox_brickd_adv_rs485_dly.setValue(int(self.brickd_conf['poll_delay.rs485']))

    def network_show_hide_static_ipconf(self, tidx, contype):
        pass
        '''
        if tidx == TAB_INDEX_NETWORK_WIRELESS:
            if contype == CBOX_NET_CONTYPE_INDEX_DHCP:
                self.frame_static_ip_conf.hide()
            elif contype == CBOX_NET_CONTYPE_INDEX_STATIC:
                self.frame_static_ip_conf.show()

        elif tidx == TAB_INDEX_NETWORK_WIRED:
            if contype == CBOX_NET_CONTYPE_INDEX_DHCP:
                self.frame_net_wired_staticipconf.hide()
            elif contype == CBOX_NET_CONTYPE_INDEX_STATIC:
                self.frame_net_wired_staticipconf.show()
        '''

    # The slots
    def slot_tbox_settings_current_changed(self, ctidx):
        if self.last_index == BOX_INDEX_BRICKD:
            pass
        elif self.last_index == BOX_INDEX_NETWORK:
            pass
        elif self.last_index == BOX_INDEX_DATETIME:
            self.time_stop()
            
        self.last_index = ctidx

        if ctidx == BOX_INDEX_NETWORK:
            if not self.work_on_progress:
                self.slot_network_refresh_clicked()

        elif ctidx == BOX_INDEX_BRICKD:
            self.slot_brickd_refresh_clicked()

        elif ctidx == BOX_INDEX_DATETIME:
            self.time_start()

    def network_button_refresh_enabled(self, state):
        self.pbutton_net_refresh.setEnabled(state)

        if state:
            self.pbutton_net_refresh.setText('Refresh')
        else:
            self.pbutton_net_refresh.setText('Refreshing...')

    def network_button_save_enabled(self, state):
        self.pbutton_net_save.setEnabled(state)

        if state:
            self.pbutton_net_save.setText('Save')
        else:
            self.pbutton_net_save.setText('Saved')

    def brickd_button_refresh_enabled(self, state):
        self.pbutton_brickd_general_refresh.setEnabled(state)
        self.pbutton_brickd_adv_refresh.setEnabled(state)
        
        if state:
            self.pbutton_brickd_general_refresh.setText('Refresh')
            self.pbutton_brickd_adv_refresh.setText('Refresh')
        else:
            self.pbutton_brickd_general_refresh.setText('Refreshing...')
            self.pbutton_brickd_adv_refresh.setText('Refreshing...')
        
    
    def brickd_button_save_enabled(self, state):
        self.pbutton_brickd_general_save.setEnabled(state)
        self.pbutton_brickd_adv_save.setEnabled(state)
        
        if state:
            self.pbutton_brickd_general_save.setText('Save')
            self.pbutton_brickd_adv_save.setText('Save')
        else:
            self.pbutton_brickd_general_save.setText('Saved')
            self.pbutton_brickd_adv_save.setText('Saved')

    def slot_brickd_refresh_clicked(self):
        self.brickd_button_refresh_enabled(False)

        def cb_open(red_file):
            def cb_read(red_file, result):
                red_file.release()

                if result is not None:
                    self.brickd_conf = config_parser.parse(result.data.decode('utf-8'))
                    self.update_brickd_widget_data()
                else:
                    # TODO: Error popup for user?
                    print 'slot_brickd_refresh_clicked cb_open', result

                self.brickd_button_refresh_enabled(True)
                self.brickd_button_save_enabled(False)
                
            red_file.read_async(4096, lambda x: cb_read(red_file, x))
            
        def cb_open_error(result):
            self.brickd_button_refresh_enabled(True)
            
            # TODO: Error popup for user?
            print 'slot_brickd_refresh_clicked cb_open_error', result

        async_call(self.brickd_conf_rfile.open,
                   (BRICKD_CONF_PATH, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open,
                   cb_open_error)

    def slot_pbutton_net_wireless_scan_clicked(self):
        print 'slot_pbutton_net_wireless_scan_clicked()'

        cbox_cidx = self.cbox_net_intf.currentIndex()
        interface_name = unicode(self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_NAME_USER_ROLE).toString())
        interface_type = self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_TYPE_USER_ROLE).toInt()[0]

        if interface_type == INTERFACE_TYPE_WIRELESS:
            def cb_open_ms(config_ms, red_file):
                def cb_write_ms(red_file, result):
                    def cb_settings_network_wireless_scan(result):
                        self.cbox_net_wireless_ap.clear()
                        self.show_please_wait(WORKING_STATE_DONE)

                        if result != None and result.stderr == '' and result.exit_code == 0:
                            self.network_all_data['scan_result'] = json.loads(result.stdout)
                            self.update_access_points()

                            QtGui.QMessageBox.information(None,
                                                          'Settings | Network',
                                                          'Scan finished.',
                                                          QtGui.QMessageBox.Ok)
                        else:
                            err_msg = 'Wireless scan failed\n\n'+unicode(result.stderr)
                            QtGui.QMessageBox.critical(None,
                                                       'Settings | Network',
                                                       err_msg,
                                                       QtGui.QMessageBox.Ok)

                    red_file.release()
    
                    self.script_manager.execute_script('settings_network_wireless_scan',
                                                       cb_settings_network_wireless_scan,
                                                       [])
    
                red_file.write_async(config_ms, lambda x: cb_write_ms(red_file, x), None)

            def cb_open_ms_error():
                self.cbox_net_wireless_ap.clear()
                self.show_please_wait(WORKING_STATE_DONE)
                QtGui.QMessageBox.critical(None,
                                           'Settings | Network',
                                           'Wireless scan failed.',
                                           QtGui.QMessageBox.Ok)

            try:
                self.network_all_data['manager_settings'].set('Settings', 'manager_settings', interface_name)
                config_ms = config_parser.to_string_no_fake(self.network_all_data['manager_settings'])
            except Exception as e:
                err_msg = 'Wireless scan failed\n\n'+unicode(e)
                QtGui.QMessageBox.critical(None,
                                           'Settings | Network',
                                           err_msg,
                                           QtGui.QMessageBox.Ok)
                return

            self.show_please_wait(WORKING_STATE_SCAN)

            async_call(self.manager_settings_conf_rfile.open,
                       (MANAGER_SETTINGS_CONF_PATH,
                       REDFile.FLAG_WRITE_ONLY |
                       REDFile.FLAG_CREATE |
                       REDFile.FLAG_NON_BLOCKING |
                       REDFile.FLAG_TRUNCATE, 0500, 0, 0),
                       lambda x: cb_open_ms(config_ms, x),
                       cb_open_ms_error)

        else:
            QtGui.QMessageBox.critical(None,
                                       'Settings | Network',
                                       'Scan only possible for wireless interfaces.',
                                       QtGui.QMessageBox.Ok)

    def slot_network_refresh_clicked(self):
        def network_refresh_tasks_done(refresh_all_ok):
            self.show_please_wait(WORKING_STATE_DONE)
            self.network_refresh_tasks_remaining = -1
            if refresh_all_ok:
                self.update_network_gui()

        def cb_settings_network_status(result):
            self.network_refresh_tasks_remaining -= 1
            if result.stdout and not result.stderr and result.exit_code == 0:
                self.network_all_data['status'] = json.loads(result.stdout)
                if self.network_refresh_tasks_remaining == 0:
                    network_refresh_tasks_done(True)
            else:
                if self.network_refresh_tasks_remaining == 0:
                    network_refresh_tasks_done(False)
    
                QtGui.QMessageBox.critical(None,
                                           'Settings | Network',
                                           'Error executing network status script.',
                                           QtGui.QMessageBox.Ok)

        def cb_settings_network_get_interfaces(result):
            self.network_refresh_tasks_remaining -= 1
            if result.stdout and not result.stderr and result.exit_code == 0:
                self.network_all_data['interfaces'] = json.loads(result.stdout)
                if self.network_refresh_tasks_remaining == 0:
                    network_refresh_tasks_done(True)
            else:
                if self.network_refresh_tasks_remaining == 0:
                    network_refresh_tasks_done(False)
    
                QtGui.QMessageBox.critical(None,
                                           'Settings | Network',
                                           'Error executing network get interfaces script.',
                                           QtGui.QMessageBox.Ok)

        def cb_open_manager_settings(red_file):
            def cb_read(red_file, result):
                self.network_refresh_tasks_remaining -= 1

                red_file.release()

                if result.data is not None and result.error is None:
                    self.network_all_data['manager_settings'] = config_parser.parse_no_fake(result.data.decode('utf-8'))
                else:
                    self.network_refresh_tasks_remaining -= 1

                    if self.network_refresh_tasks_remaining == 0:
                        network_refresh_tasks_done(False)
        
                    QtGui.QMessageBox.critical(None,
                                               'Settings | Network',
                                               'Error reading wired settings file.',
                                               QtGui.QMessageBox.Ok)
                
            red_file.read_async(4096, lambda x: cb_read(red_file, x))
            
        def cb_open_error_manager_settings():
            self.network_refresh_tasks_remaining -= 1

            if self.network_refresh_tasks_remaining == 0:
                network_refresh_tasks_done(False)

            QtGui.QMessageBox.critical(None,
                                       'Settings | Network',
                                       'Error opening manager settings file.',
                                       QtGui.QMessageBox.Ok)

        def cb_open_wireless_settings(red_file):
            def cb_read(red_file, result):
                self.network_refresh_tasks_remaining -= 1

                red_file.release()

                if result.data is not None and result.error is None:
                    self.network_all_data['wireless_settings'] = config_parser.parse_no_fake(result.data.decode('utf-8'))
                else:
                    if self.network_refresh_tasks_remaining == 0:
                        network_refresh_tasks_done(False)
        
                    QtGui.QMessageBox.critical(None,
                                               'Settings | Network',
                                               'Error reading wireless settings file.',
                                               QtGui.QMessageBox.Ok)

            red_file.read_async(4096, lambda x: cb_read(red_file, x))
            
        def cb_open_error_wireless_settings():
            self.network_refresh_tasks_remaining -= 1

            if self.network_refresh_tasks_remaining == 0:
                network_refresh_tasks_done(False)

            QtGui.QMessageBox.critical(None,
                                       'Settings | Network',
                                       'Error opening wireless settings file.',
                                       QtGui.QMessageBox.Ok)

        def cb_open_wired_settings(red_file):
            def cb_read(red_file, result):
                self.network_refresh_tasks_remaining -= 1

                red_file.release()

                if result.data is not None and result.error is None:
                    self.network_all_data['wired_settings'] = config_parser.parse_no_fake(result.data.decode('utf-8'))
                else:
                    if self.network_refresh_tasks_remaining == 0:
                        network_refresh_tasks_done(False)
            
                    QtGui.QMessageBox.critical(None,
                                               'Settings | Network',
                                               'Error reading wired settings file.',
                                               QtGui.QMessageBox.Ok)

            red_file.read_async(4096, lambda x: cb_read(red_file, x))
            
        def cb_open_error_wired_settings():
            self.network_refresh_tasks_remaining -= 1

            if self.network_refresh_tasks_remaining == 0:
                network_refresh_tasks_done(False)

            QtGui.QMessageBox.critical(None,
                                       'Settings | Network',
                                       'Error opening wired settings file.',
                                       QtGui.QMessageBox.Ok)

        self.network_refresh_tasks_remaining = 5

        self.show_please_wait(WORKING_STATE_REFRESH)

        self.script_manager.execute_script('settings_network_status',
                                           cb_settings_network_status,
                                           [])

        self.script_manager.execute_script('settings_network_get_interfaces',
                                           cb_settings_network_get_interfaces,
                                           [])

        async_call(self.manager_settings_conf_rfile.open,
                   (MANAGER_SETTINGS_CONF_PATH, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open_manager_settings,
                   cb_open_error_manager_settings)

        async_call(self.wireless_settings_conf_rfile.open,
                   (WIRELESS_SETTINGS_CONF_PATH, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open_wireless_settings,
                   cb_open_error_wireless_settings)

        async_call(self.wired_settings_conf_rfile.open,
                   (WIRED_SETTINGS_CONF_PATH, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open_wired_settings,
                   cb_open_error_wired_settings)

    def slot_network_save_clicked(self):
        print 'slot_network_save_clicked()'

        cbox_cidx = self.cbox_net_intf.currentIndex()

        iname = unicode(self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_NAME_USER_ROLE).toString())
        itype =  self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_TYPE_USER_ROLE).toInt()[0]

        # Wireless
        if itype == INTERFACE_TYPE_WIRELESS:
            pass
            #WIRELESS SAVE
            '''
            self.network_button_save_enabled(False)
    
            self.network_all_data['manager_settings'].set('Settings', 'wired_interface', unicode("None"))
            config_ms = config_parser.to_string_no_fake(self.network_all_data['manager_settings'])
    
            if self.cbox_net_wireless_ap.currentText() == "Nothing found. Scan again?":
                QtGui.QMessageBox.critical(None,
                                           'Settings | Network | Wireless',
                                           'Please select an access point.',
                                           QtGui.QMessageBox.Ok)
                return
    
            for key, apdict in self.network_all_data['scan_result'].iteritems():
                if apdict['essid'] == unicode(self.cbox_net_wireless_ap.currentText()):
                    nidx = key
                    break
            if self.cbox_net_conftype.currentIndex() == CBOX_NET_CONTYPE_INDEX_DHCP:
                ip = "None"
                mask = "None"
                gw = "None"
                dns = "None"
            else:
                ip = '.'.join((str(self.sbox_net_ip1.value()),
                               str(self.sbox_net_ip2.value()),
                               str(self.sbox_net_ip3.value()),
                               str(self.sbox_net_ip4.value())))
    
                mask = '.'.join((str(self.sbox_net_mask1.value()),
                               str(self.sbox_net_mask2.value()),
                               str(self.sbox_net_mask3.value()),
                               str(self.sbox_net_mask4.value())))
            
                gw = '.'.join((str(self.sbox_net_gw1.value()),
                               str(self.sbox_net_gw2.value()),
                               str(self.sbox_net_gw3.value()),
                               str(self.sbox_net_gw4.value())))
    
                dns = '.'.join((str(self.sbox_net_dns1.value()),
                               str(self.sbox_net_dns2.value()),
                               str(self.sbox_net_dns3.value()),
                               str(self.sbox_net_dns4.value())))
            if self.label_net_wireless_enctype.text() == "WPA 1/2":
                enct = "wpa"
                key = self.ledit_net_wireless_key.displayText()
            elif self.label_net_wireless_enctype.text() == "Open":
                enct = "None"
                key = "None"
            elif self.label_net_wireless_enctype.text() == "Unsupported":
                QtGui.QMessageBox.critical(None,
                                           'Settings | Network | Wireless',
                                           'Please select an access point with supported encryption.',
                                           QtGui.QMessageBox.Ok)
                return
    
            search_domain = "None"
            dns_domain = "None"
            dns2 = "None"
            dns3 = "None"
            automatic = "True"
    
            def cb_settings_network_wireless_apply(result):
                self.show_please_wait(False)
                if result != None and result.stderr == "":
                    QtGui.QMessageBox.information(None,
                                                  'Settings | Network | Wireless',
                                                  'Wireless connection configuration saved and activated.',
                                                  QtGui.QMessageBox.Ok)
                else:
                    # TODO: Error popup for user?
                    QtGui.QMessageBox.critical(None,
                                               'Settings | Network | Wireless',
                                               'Error saving wireless connection configuration.',
                                               QtGui.QMessageBox.Ok)
    
            self.show_please_wait(True)
    
            def cb_open_ms(config, red_file):
                def cb_write_ms(red_file, result):
                    red_file.release()
    
                    if result is not None:
                        self.network_button_save_enabled(True)
                        # TODO: Error popup for user?
                        print 'cb_open_ms cb_write_ms', result
                        self.show_please_wait(False)
                    else:
                        self.script_manager.execute_script('settings_network_wireless_apply',
                                                           cb_settings_network_wireless_apply,
                                                           [str(nidx),
                                                            str(ip),
                                                            str(mask),
                                                            str(gw),
                                                            str(dns),
                                                            str(enct),
                                                            str(key),
                                                            str(search_domain),
                                                            str(dns_domain),
                                                            str(dns2),
                                                            str(dns3),
                                                            str(automatic)])
    
                red_file.write_async(config_ms, lambda x: cb_write_ms(red_file, x), None)
    
            def cb_open_ms_error(result):
                self.brickd_button_save_enabled(True)
                # TODO: Error popup for user?
                print 'cb_open_ms cb_open_ms_error', result
                self.show_please_wait(False)
    
            async_call(self.manager_settings_conf_rfile.open,
                       (MANAGER_SETTINGS_CONF_PATH,
                       REDFile.FLAG_WRITE_ONLY |
                       REDFile.FLAG_CREATE |
                       REDFile.FLAG_NON_BLOCKING |
                       REDFile.FLAG_TRUNCATE, 0500, 0, 0),
                       lambda x: cb_open_ms(config_ms, x),
                       cb_open_ms_error)
            '''

        # Wired
        elif itype == INTERFACE_TYPE_WIRED:
            if self.cbox_net_conftype.currentIndex() == CBOX_NET_CONTYPE_INDEX_DHCP:
                self.show_please_wait(WORKING_STATE_SAVE)
                try:
                    self.network_all_data['manager_settings'].set('Settings', 'wired_interface', iname)
                    self.network_all_data['wired_settings'].set('wired-default', 'ip', 'None')
                    self.network_all_data['wired_settings'].set('wired-default', 'broadcast', 'None')
                    self.network_all_data['wired_settings'].set('wired-default', 'netmask', 'None')
                    self.network_all_data['wired_settings'].set('wired-default', 'gateway', 'None')
                    self.network_all_data['wired_settings'].set('wired-default', 'search_domain', 'None')
                    self.network_all_data['wired_settings'].set('wired-default', 'dns_domain', 'None')
                    self.network_all_data['wired_settings'].set('wired-default', 'dns1', 'None')
                    self.network_all_data['wired_settings'].set('wired-default', 'dns2', 'None')
                    self.network_all_data['wired_settings'].set('wired-default', 'dns3', 'None')
                    self.network_all_data['wired_settings'].set('wired-default', 'default', 'True')
                except:
                    self.show_please_wait(WORKING_STATE_DONE)
                    self.network_button_save_enabled(True)
                    QtGui.QMessageBox.critical(None,
                                               'Settings | Network',
                                               'Error saving configuration.',
                                               QtGui.QMessageBox.Ok)
                    return
            else:
                # Save for wired static config
                self.show_please_wait(WORKING_STATE_SAVE)
                try:
                    self.network_all_data['manager_settings'].set('Settings', 'wired_interface', iname)
                    
                    ip = '.'.join((str(self.sbox_net_ip1.value()),
                                   str(self.sbox_net_ip2.value()),
                                   str(self.sbox_net_ip3.value()),
                                   str(self.sbox_net_ip4.value())))
                    
                    mask = '.'.join((str(self.sbox_net_mask1.value()),
                                     str(self.sbox_net_mask2.value()),
                                     str(self.sbox_net_mask3.value()),
                                     str(self.sbox_net_mask4.value())))
                    
                    gw = '.'.join((str(self.sbox_net_gw1.value()),
                                   str(self.sbox_net_gw2.value()),
                                   str(self.sbox_net_gw3.value()),
                                   str(self.sbox_net_gw4.value())))
                    
                    dns = '.'.join((str(self.sbox_net_dns1.value()),
                                    str(self.sbox_net_dns2.value()),
                                    str(self.sbox_net_dns3.value()),
                                    str(self.sbox_net_dns4.value())))

                    self.network_all_data['wired_settings'].set('wired-default', 'ip', ip)
                    self.network_all_data['wired_settings'].set('wired-default', 'netmask', mask)
                    self.network_all_data['wired_settings'].set('wired-default', 'gateway', gw)
                    self.network_all_data['wired_settings'].set('wired-default', 'use_static_dns', 'True')
                    self.network_all_data['wired_settings'].set('wired-default', 'dns1', dns)
                    self.network_all_data['wired_settings'].set('wired-default', 'broadcast', 'None')
                    self.network_all_data['wired_settings'].set('wired-default', 'search_domain', 'None')
                    self.network_all_data['wired_settings'].set('wired-default', 'dns_domain', 'None')
                    self.network_all_data['wired_settings'].set('wired-default', 'dns2', 'None')
                    self.network_all_data['wired_settings'].set('wired-default', 'dns3', 'None')
                    self.network_all_data['wired_settings'].set('wired-default', 'default', 'True')
                except:
                    self.show_please_wait(WORKING_STATE_DONE)
                    self.network_button_save_enabled(True)
                    QtGui.QMessageBox.critical(None,
                                               'Settings | Network',
                                               'Error saving configuration.',
                                               QtGui.QMessageBox.Ok)
                    return

            def cb_settings_network_apply(result):
                    self.show_please_wait(WORKING_STATE_DONE)
                    if result != None and result.stderr == '' and result.exit_code == 0:
                        self.slot_network_refresh_clicked()
                        QtGui.QMessageBox.information(None,
                                                      'Settings | Network',
                                                      'Configuration saved.',
                                                      QtGui.QMessageBox.Ok)
                    else:
                        self.network_button_save_enabled(True)
                        QtGui.QMessageBox.critical(None,
                                                   'Settings | Network',
                                                   'Error saving configuration.',
                                                   QtGui.QMessageBox.Ok)

            def cb_open(config, write_wired_settings, red_file):
                def cb_write(red_file, write_wired_settings, result):
                    red_file.release()
                    if result is not None:
                        self.show_please_wait(WORKING_STATE_DONE)
                        self.network_button_save_enabled(True)
                        QtGui.QMessageBox.critical(None,
                                                   'Settings | Network',
                                                   'Error saving configuration.',
                                                   QtGui.QMessageBox.Ok)
                        print 'slot_brickd_save_clicked cb_open cb_write', result
                    else:
                        if write_wired_settings:
                            self.script_manager.execute_script('settings_network_apply',
                                                               cb_settings_network_apply,
                                                               [iname, 'wired'])
                        else:
                            config = config_parser.to_string_no_fake(self.network_all_data['wired_settings'])
                            write_wired_settings = True
                            async_call(self.wired_settings_conf_rfile.open,
                                       (WIRED_SETTINGS_CONF_PATH,
                                       REDFile.FLAG_WRITE_ONLY |
                                       REDFile.FLAG_CREATE |
                                       REDFile.FLAG_NON_BLOCKING |
                                       REDFile.FLAG_TRUNCATE, 0500, 0, 0),
                                       lambda x: cb_open(config, write_wired_settings, x),
                                       cb_open_error)

                red_file.write_async(config, lambda x: cb_write(red_file, write_wired_settings, x), None)
    
            def cb_open_error(result):
                self.show_please_wait(WORKING_STATE_DONE)
                self.network_button_save_enabled(True)
                
                QtGui.QMessageBox.critical(None,
                                           'Settings | Network',
                                           'Error saving configuration.',
                                           QtGui.QMessageBox.Ok)
                
                print 'slot_brickd_save_clicked cb_open_error', result

            config = config_parser.to_string_no_fake(self.network_all_data['manager_settings'])
            write_wired_settings = False

            async_call(self.manager_settings_conf_rfile.open,
                       (MANAGER_SETTINGS_CONF_PATH,
                       REDFile.FLAG_WRITE_ONLY |
                       REDFile.FLAG_CREATE |
                       REDFile.FLAG_NON_BLOCKING |
                       REDFile.FLAG_TRUNCATE, 0500, 0, 0),
                       lambda x: cb_open(config, write_wired_settings, x),
                       cb_open_error)

    def slot_brickd_save_clicked(self):
        self.brickd_button_save_enabled(False)

        # General
        adr = '.'.join((str(self.sbox_brickd_la_ip1.value()),
                        str(self.sbox_brickd_la_ip2.value()),
                        str(self.sbox_brickd_la_ip3.value()),
                        str(self.sbox_brickd_la_ip4.value())))
        self.brickd_conf['listen.address'] = adr
        self.brickd_conf['listen.plain_port'] = unicode(self.sbox_brickd_lp.value())
        self.brickd_conf['listen.websocket_port'] = unicode(self.sbox_brickd_lwsp.value())
        self.brickd_conf['authentication.secret'] = unicode(self.ledit_brickd_secret.text())

        # Advanced
        index = self.cbox_brickd_adv_ll.currentIndex()
        if index == CBOX_BRICKD_LOG_LEVEL_ERROR:
            self.brickd_conf['log.level'] = 'error'
        elif index == CBOX_BRICKD_LOG_LEVEL_WARN:
            self.brickd_conf['log.level'] = 'warn'
        elif index == CBOX_BRICKD_LOG_LEVEL_INFO:
            self.brickd_conf['log.level'] = 'info'
        elif index == CBOX_BRICKD_LOG_LEVEL_DEBUG:
            self.brickd_conf['log.level'] = 'debug'
            
        index = self.cbox_brickd_adv_gt.currentIndex()
        if index == CBOX_BRICKD_LED_TRIGGER_CPU:
            self.brickd_conf['led_trigger.green'] = 'cpu'
        elif index == CBOX_BRICKD_LED_TRIGGER_GPIO:
            self.brickd_conf['led_trigger.green'] = 'gpio'
        elif index == CBOX_BRICKD_LED_TRIGGER_HEARTBEAT:
            self.brickd_conf['led_trigger.green'] = 'heartbeat'
        elif index == CBOX_BRICKD_LED_TRIGGER_MMC:
            self.brickd_conf['led_trigger.green'] = 'mmc'
        elif index == CBOX_BRICKD_LED_TRIGGER_OFF:
            self.brickd_conf['led_trigger.green'] = 'off'
        elif index == CBOX_BRICKD_LED_TRIGGER_ON:
            self.brickd_conf['led_trigger.green'] = 'on'
        
        index = self.cbox_brickd_adv_rt.currentIndex()
        if index == CBOX_BRICKD_LED_TRIGGER_CPU:
            self.brickd_conf['led_trigger.red'] = 'cpu'
        elif index == CBOX_BRICKD_LED_TRIGGER_GPIO:
            self.brickd_conf['led_trigger.red'] = 'gpio'
        elif index == CBOX_BRICKD_LED_TRIGGER_HEARTBEAT:
            self.brickd_conf['led_trigger.red'] = 'heartbeat'
        elif index == CBOX_BRICKD_LED_TRIGGER_MMC:
            self.brickd_conf['led_trigger.red'] = 'mmc'
        elif index == CBOX_BRICKD_LED_TRIGGER_OFF:
            self.brickd_conf['led_trigger.red'] = 'off'
        elif index == CBOX_BRICKD_LED_TRIGGER_ON:
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
                    print 'slot_brickd_save_clicked cb_open cb_write', result
                else:
                    self.script_manager.execute_script('restart_brickd', None)
                    QtGui.QMessageBox.information(None,
                                                  'Settings | Brick Daemon',
                                                  'Saved configuration successfully, restarting brickd.',
                                                  QtGui.QMessageBox.Ok)

            red_file.write_async(config, lambda x: cb_write(red_file, x), None)

        def cb_open_error(result):
            self.brickd_button_save_enabled(True)
            
            # TODO: Error popup for user?
            print 'slot_brickd_save_clicked cb_open_error', result

        async_call(self.brickd_conf_rfile.open,
                   (BRICKD_CONF_PATH,
                   REDFile.FLAG_WRITE_ONLY |
                   REDFile.FLAG_CREATE |
                   REDFile.FLAG_NON_BLOCKING |
                   REDFile.FLAG_TRUNCATE, 0500, 0, 0),
                   lambda x: cb_open(config, x),
                   cb_open_error)

    def slot_cbox_net_intf_current_idx_changed(self, idx):
        print 'slot_cbox_net_intf_current_idx_changed()', idx

        interface_name = unicode(self.cbox_net_intf.itemData(idx, INTERFACE_NAME_USER_ROLE).toString())
        interface_type = self.cbox_net_intf.itemData(idx, INTERFACE_TYPE_USER_ROLE).toInt()[0]

        if interface_type == INTERFACE_TYPE_WIRELESS:
            # Set AP list to currently associated
            for i in range(self.cbox_net_wireless_ap.count()):
                ap_associated_state = self.cbox_net_wireless_ap.itemData(i, AP_STATUS_USER_ROLE).toInt()[0]
                if ap_associated_state == AP_STATUS_ASSOCIATED:
                    self.cbox_net_wireless_ap.setCurrentIndex(i)
                    break
            self.show_wireless_configuration(True)

        else:
            self.show_wireless_configuration(False)
            self.frame_net_conftype.show()

            net_conf_type = self.cbox_net_intf.itemData(idx, INTERFACE_TYPE_WIRED_ADDRESS_CONF_USER_ROLE).toInt()[0]

            if net_conf_type == CBOX_NET_CONTYPE_INDEX_DHCP:
                self.sbox_net_ip1.setValue(0)
                self.sbox_net_ip2.setValue(0)
                self.sbox_net_ip3.setValue(0)
                self.sbox_net_ip4.setValue(0)
                
                self.sbox_net_mask1.setValue(0)
                self.sbox_net_mask2.setValue(0)
                self.sbox_net_mask3.setValue(0)
                self.sbox_net_mask4.setValue(0)
                
                self.sbox_net_gw1.setValue(0)
                self.sbox_net_gw2.setValue(0)
                self.sbox_net_gw3.setValue(0)
                self.sbox_net_gw4.setValue(0)
                
                self.sbox_net_dns1.setValue(0)
                self.sbox_net_dns2.setValue(0)
                self.sbox_net_dns3.setValue(0)
                self.sbox_net_dns4.setValue(0)
                self.cbox_net_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_DHCP)
            else:
                ip_string = self.cbox_net_intf.itemData(idx, INTERFACE_TYPE_WIRED_IP_USER_ROLE).toString()
                ip_array = ip_string.split('.')
                mask_string = self.cbox_net_intf.itemData(idx, INTERFACE_TYPE_WIRED_MASK_USER_ROLE).toString()
                mask_array = mask_string.split('.')
                gw_string = self.cbox_net_intf.itemData(idx, INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE).toString()
                gw_array = gw_string.split('.')
                dns_string = self.cbox_net_intf.itemData(idx, INTERFACE_TYPE_WIRED_DNS_USER_ROLE).toString()
                dns_array = dns_string.split('.')

                if ip_string:
                    self.sbox_net_ip1.setValue(int(ip_array[0]))
                    self.sbox_net_ip2.setValue(int(ip_array[1]))
                    self.sbox_net_ip3.setValue(int(ip_array[2]))
                    self.sbox_net_ip4.setValue(int(ip_array[3]))
    
                if ip_string:
                    self.sbox_net_mask1.setValue(int(mask_array[0]))
                    self.sbox_net_mask2.setValue(int(mask_array[1]))
                    self.sbox_net_mask3.setValue(int(mask_array[2]))
                    self.sbox_net_mask4.setValue(int(mask_array[3]))
    
                if ip_string:
                    self.sbox_net_gw1.setValue(int(gw_array[0]))
                    self.sbox_net_gw2.setValue(int(gw_array[1]))
                    self.sbox_net_gw3.setValue(int(gw_array[2]))
                    self.sbox_net_gw4.setValue(int(gw_array[3]))
                
                if ip_string:
                    self.sbox_net_dns1.setValue(int(dns_array[0]))
                    self.sbox_net_dns2.setValue(int(dns_array[1]))
                    self.sbox_net_dns3.setValue(int(dns_array[2]))
                    self.sbox_net_dns4.setValue(int(dns_array[3]))
                self.cbox_net_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_STATIC)

    def slot_cbox_net_wireless_ap_current_idx_changed(self, idx):
        channel = self.cbox_net_wireless_ap.itemData(idx, AP_CHANNEL_USER_ROLE).toString()
        encryption = self.cbox_net_wireless_ap.itemData(idx, AP_ENCRYPTION_USER_ROLE).toString()
        encryption_method = self.cbox_net_wireless_ap.itemData(idx, AP_ENCRYPTION_METHOD_USER_ROLE).toString()
        key = self.cbox_net_wireless_ap.itemData(idx, AP_KEY_USER_ROLE).toString()
        address_conf = self.cbox_net_wireless_ap.itemData(idx, AP_ADDRESS_CONF_USER_ROLE).toInt()[0]
        ip_string = self.cbox_net_wireless_ap.itemData(idx, AP_IP_USER_ROLE).toString()
        mask_string = self.cbox_net_wireless_ap.itemData(idx, AP_MASK_USER_ROLE).toString()
        gw_string = self.cbox_net_wireless_ap.itemData(idx, AP_GATEWAY_USER_ROLE).toString()
        dns_string = self.cbox_net_wireless_ap.itemData(idx, AP_DNS_USER_ROLE).toString()
        ip_array = ip_string.split('.')
        mask_array = mask_string.split('.')
        gw_array = gw_string.split('.')
        dns_array = dns_string.split('.')
        
        self.label_net_wireless_channel.setText(channel)

        if encryption == 'On':
            self.ledit_net_wireless_key.setEnabled(True)
            self.label_net_wireless_enctype.setText(encryption_method)
        elif encryption == 'Off':
            self.label_net_wireless_enctype.setText('Open')
            self.ledit_net_wireless_key.setEnabled(False)
        else:
            self.label_net_wireless_enctype.setText(encryption_method)
            self.ledit_net_wireless_key.setEnabled(False)

        self.ledit_net_wireless_key.setText(unicode(key))
                
        if ip_string:
            self.sbox_net_ip1.setValue(int(ip_array[0]))
            self.sbox_net_ip2.setValue(int(ip_array[1]))
            self.sbox_net_ip3.setValue(int(ip_array[2]))
            self.sbox_net_ip4.setValue(int(ip_array[3]))

        if mask_string:
            self.sbox_net_mask1.setValue(int(mask_array[0]))
            self.sbox_net_mask2.setValue(int(mask_array[1]))
            self.sbox_net_mask3.setValue(int(mask_array[2]))
            self.sbox_net_mask4.setValue(int(mask_array[3]))

        if gw_string:
            self.sbox_net_gw1.setValue(int(gw_array[0]))
            self.sbox_net_gw2.setValue(int(gw_array[1]))
            self.sbox_net_gw3.setValue(int(gw_array[2]))
            self.sbox_net_gw4.setValue(int(gw_array[3]))

        if dns_string:
            self.sbox_net_dns1.setValue(int(dns_array[0]))
            self.sbox_net_dns2.setValue(int(dns_array[1]))
            self.sbox_net_dns3.setValue(int(dns_array[2]))
            self.sbox_net_dns4.setValue(int(dns_array[3]))
        
        self.frame_net_conftype.show()
        
        if address_conf == CBOX_NET_CONTYPE_INDEX_DHCP:
            self.cbox_net_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_DHCP)
        elif address_conf == CBOX_NET_CONTYPE_INDEX_STATIC:
            self.cbox_net_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_STATIC)
        else:
            self.cbox_net_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_DHCP)

    def slot_net_wireless_key_show_state_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.ledit_net_wireless_key.setEchoMode(QtGui.QLineEdit.Normal)
        else:
            self.ledit_net_wireless_key.setEchoMode(QtGui.QLineEdit.Password)

    def slot_cbox_net_conftype_current_idx_changed(self, idx):
        if idx == CBOX_NET_CONTYPE_INDEX_STATIC:
            self.frame_static_ip_conf.show()
        else:
            self.frame_static_ip_conf.hide()

    def slot_network_settings_changed(self):
        self.network_button_save_enabled(True)

    def brickd_settings_changed(self, value):
        self.brickd_button_save_enabled(True)

    # ======== date/time settings =========

    def time_utc_offset(self):
        if time.localtime(time.time()).tm_isdst and time.daylight:
            return -time.altzone/(60*60)
        
        return -time.timezone/(60*60)
    
    def time_start(self):
        self.time_sync_button.setEnabled(False)

        def cb_red_brick_time(result):
            try:
                if result != None and result.stderr == '':
                    self.time_red_old, tz = map(int, result.stdout.split('\n')[:2])
                    if tz < 0:
                        tz_str_red = 'UTC' + str(tz)
                    else:
                        tz_str_red = 'UTC+' + str(tz)
                    self.time_timezone_red.setText(tz_str_red)
                    
                    self.time_local_old = int(time.time())
                    tz = self.time_utc_offset()
                    if tz < 0:
                        tz_str_local = 'UTC' + str(tz)
                    else:
                        tz_str_local = 'UTC+' + str(tz)
                    
                    self.time_timezone_local.setText(tz_str_local)
                    self.time_update_gui()
                    
                    self.time_refresh_timer.start()
                    
                    if (self.time_red_old == self.time_local_old) and (tz_str_local == tz_str_red):
                        self.time_sync_button.setEnabled(False)
                    else:
                        self.time_sync_button.setEnabled(True)
                        
                    return
                else:
                    # TODO: Error popup for user?
                    print 'time_start cb_red_brick_time', result.stderr
            except:
                # TODO: Error popup for user?
                traceback.print_exc()
            
            self.time_sync_button.setEnabled(True)
        
        self.script_manager.execute_script('settings_time_get',
                                           cb_red_brick_time,
                                           [])
    
    def time_stop(self):
        try:
            self.time_refresh_timer.stop()
        except:
            traceback.print_exc()
            
    def time_refresh(self):
        self.time_local_old += 1
        self.time_red_old += 1
        
        self.time_update_gui()
        
    def time_update_gui(self):
        t = QtCore.QDateTime.fromTime_t(self.time_local_old)
        self.time_date_local.setDateTime(t)
        self.time_time_local.setDateTime(t)
        
        t = QtCore.QDateTime.fromTime_t(self.time_red_old)
        self.time_date_red.setDateTime(t)
        self.time_time_red.setDateTime(t)
        
    def time_sync_clicked(self):
        def state_changed(process, t, p):
            if p.state == REDProcess.STATE_ERROR:
                # TODO: Error popup for user?
                process.release()
            elif p.state == REDProcess.STATE_EXITED:
                if t == 0: #timezone
                    self.time_timezone_red.setText(self.time_timezone_local.text())
                elif t == 1: #time
                    self.time_red_old = self.time_local_old
                    
                process.release()
                
            if (self.time_red_old == self.time_local_old) and (self.time_timezone_red.text() == self.time_timezone_local.text()):
                self.time_sync_button.setEnabled(False)
            else:
                self.time_sync_button.setEnabled(True)

        tz = -self.time_utc_offset() # Use posix timezone definition
        if tz < 0:
            tz_str = str(tz)
        else:
            tz_str = '+' + str(tz)
            
        set_tz_str = ('/bin/ln -sf /usr/share/zoneinfo/Etc/GMT' + tz_str + ' /etc/localtime').split(' ')
        red_process_tz = REDProcess(self.session)
        red_process_tz.state_changed_callback = lambda x: state_changed(red_process_tz, 0, x)
        red_process_tz.spawn(set_tz_str[0], set_tz_str[1:], [], '/', 0, 0, self.script_manager.devnull, self.script_manager.devnull, self.script_manager.devnull)

        set_t_str = ('/bin/date +%s -u -s @' + str(int(time.time()))).split(' ')
        red_process_t = REDProcess(self.session)
        red_process_t.state_changed_callback = lambda x: state_changed(red_process_t, 1, x)
        red_process_t.spawn(set_t_str[0], set_t_str[1:], [], '/', 0, 0, self.script_manager.devnull, self.script_manager.devnull, self.script_manager.devnull)

