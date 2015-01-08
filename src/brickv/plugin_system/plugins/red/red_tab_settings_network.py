# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

red_tab_settings_network.py: RED settings network tab implementation

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
from brickv.plugin_system.plugins.red.ui_red_tab_settings_network import Ui_REDTabSettingsNetwork
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red import config_parser
from brickv.async_call import async_call
from brickv.utils import get_main_window

# Constants
NETWORK_STAT_REFRESH_INTERVAL = 3000 # in milliseconds
MANAGER_SETTINGS_CONF_PATH = '/etc/wicd/manager-settings.conf'
WIRELESS_SETTINGS_CONF_PATH = '/etc/wicd/wireless-settings.conf'
WIRED_SETTINGS_CONF_PATH = '/etc/wicd/wired-settings.conf'
TAB_INDEX_NETWORK_GENERAL = 0
TAB_INDEX_NETWORK_WIRELESS = 1
TAB_INDEX_NETWORK_WIRED = 2
CBOX_NET_CONTYPE_INDEX_DHCP = 0
CBOX_NET_CONTYPE_INDEX_STATIC = 1

INTERFACE_TYPE_WIRELESS = 1
INTERFACE_TYPE_WIRED = 2
INTERFACE_STATE_ACTIVE = 1
INTERFACE_STATE_INACTIVE = 2
AP_STATUS_ASSOCIATED = 1
AP_STATUS_NOT_ASSOCIATED = 2
AP_STATUS_NONE = 3
AP_ENC_METHOD_WPA1 = 1
AP_ENC_METHOD_WPA2 = 2
AP_ENC_METHOD_UNSUPPORTED = 3
AP_COL = 4

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
AP_COL_USER_ROLE = QtCore.Qt.UserRole + 14

WORKING_STATE_REFRESH = 1
WORKING_STATE_SCAN = 2
WORKING_STATE_DONE = 3
WORKING_STATE_SAVE = 4

AP_NAME_COL_WIDTH = 300
AP_CHANNEL_COL_WIDTH = 100
AP_SECURITY_COL_WIDTH = 100

class REDTabSettingsNetwork(QtGui.QWidget, Ui_REDTabSettingsNetwork):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        
        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings

        self.is_tab_on_focus = False

        self.network_stat_refresh_timer = Qt.QTimer(self)

        self.network_refresh_tasks_remaining = -1
        self.network_refresh_tasks_error_occured = False
        self.work_in_progress = False
        self.network_stat_work_in_progress = False

        self.network_all_data = {'status': None,
                                 'interfaces': None,
                                 'scan_result': None,
                                 'scan_result_cache': None,
                                 'manager_settings': None,
                                 'wireless_settings': None,
                                 'wired_settings': None}
        

        self.ap_tree_model = QtGui.QStandardItemModel(0, 3)

        self.ap_tree_model.setHorizontalHeaderItem(0, QtGui.QStandardItem("Access Point"))
        self.ap_tree_model.setHorizontalHeaderItem(1, QtGui.QStandardItem("Channel"))
        self.ap_tree_model.setHorizontalHeaderItem(2, QtGui.QStandardItem("Security"))

        self.tree_net_wireless_ap.setModel(self.ap_tree_model)

        self.tree_net_wireless_ap.header().resizeSection(0, AP_NAME_COL_WIDTH)
        self.tree_net_wireless_ap.header().resizeSection(1, AP_CHANNEL_COL_WIDTH)
        self.tree_net_wireless_ap.header().resizeSection(2, AP_SECURITY_COL_WIDTH)

        self.network_stat_refresh_timer.timeout.connect(self.cb_network_stat_refresh)

        # Signals/slots
        self.pbutton_net_wireless_scan.clicked.connect(self.slot_pbutton_net_wireless_scan_clicked)
        self.pbutton_net_conf_refresh.clicked.connect(self.slot_network_conf_refresh_clicked)
        self.pbutton_net_connect.clicked.connect(self.slot_network_connect_clicked)

        # Network fields
        self.address_configuration_gui(False)
        self.static_ip_configuration_gui(False)
        self.frame_working_please_wait.hide()
        self.cbox_net_intf.currentIndexChanged.connect(self.slot_cbox_net_intf_current_idx_changed)
        self.cbox_net_conftype.currentIndexChanged.connect(self.slot_cbox_net_conftype_current_idx_changed)
        QtCore.QObject.connect(self.tree_net_wireless_ap.selectionModel(),
                               QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'),
                               self.slot_tree_net_wireless_ap_selection_changed)
        self.ledit_net_wireless_key.setEchoMode(QtGui.QLineEdit.Password)
        self.chkbox_net_wireless_key_show.stateChanged.connect(self.slot_net_wireless_key_show_state_changed)

    def tab_on_focus(self):
        self.is_tab_on_focus = True
        
        self.manager_settings_conf_rfile = REDFile(self.session)
        self.wired_settings_conf_rfile = REDFile(self.session)
        self.wireless_settings_conf_rfile = REDFile(self.session)
        
        if not self.network_stat_work_in_progress:
            self.cb_network_stat_refresh()
        if not self.work_in_progress:
            self.slot_network_conf_refresh_clicked()

    def tab_off_focus(self):
        self.is_tab_on_focus = False
        self.network_stat_refresh_timer.stop()

    def tab_destroy(self):
        pass

    def ap_tree_model_clear_add_item(self, item):
        self.ap_tree_model.removeRows(0, self.ap_tree_model.rowCount())
        if item:
            self.ap_tree_model.appendRow([item])

    def cb_settings_network_status(self, result):
        self.network_stat_refresh_timer.stop()
        self.network_stat_work_in_progress = False

        #check if the tab is still on view or not
        if not self.is_tab_on_focus:
            return

        if result and result.stdout and not result.stderr and result.exit_code == 0:
            self.network_all_data['status'] = json.loads(result.stdout)

            # Populating the current network status section and hostname
            if self.network_all_data['status'] is not None:
                self.label_net_hostname.setText(self.network_all_data['status']['cstat_hostname'])

                self.label_net_gen_cstat_status.setText(unicode(self.network_all_data['status']['cstat_status']))

                if self.network_all_data['status']['cstat_intf_active']['name'] is not None:
                    if self.network_all_data['status']['cstat_intf_active']['type'] == INTERFACE_TYPE_WIRELESS:
                        intf_stat_str = unicode(self.network_all_data['status']['cstat_intf_active']['name']) + ' : Wireless'
                        self.label_net_gen_cstat_intf.setText(intf_stat_str)
                    else:
                        intf_stat_str = unicode(self.network_all_data['status']['cstat_intf_active']['name']) + ' : Wired'
                        self.label_net_gen_cstat_intf.setText(intf_stat_str)

                    self.label_net_gen_cstat_ip.setText(self.network_all_data['status']['cstat_intf_active']['ip'])
                    self.label_net_gen_cstat_mask.setText(self.network_all_data['status']['cstat_intf_active']['mask'])
                else:
                    self.label_net_gen_cstat_intf.setText('-')
                    self.label_net_gen_cstat_ip.setText('-')
                    self.label_net_gen_cstat_mask.setText('-')

                if self.network_all_data['status']['cstat_gateway'] is not None:
                    self.label_net_gen_cstat_gateway.setText(self.network_all_data['status']['cstat_gateway'])
                else:
                    self.label_net_gen_cstat_gateway.setText('-')

                if self.network_all_data['status']['cstat_dns'] is not None:
                    self.label_net_gen_cstat_dns.setText(self.network_all_data['status']['cstat_dns'].strip())
                else:
                    self.label_net_gen_cstat_dns.setText('-')
            else:
                self.label_net_hostname.setText('')
                self.label_net_gen_cstat_intf.setText('-')
                self.label_net_gen_cstat_ip.setText('-')
                self.label_net_gen_cstat_mask.setText('-')
                self.label_net_gen_cstat_gateway.setText('-')
                self.label_net_gen_cstat_dns.setText('-')

        self.network_stat_refresh_timer.start(NETWORK_STAT_REFRESH_INTERVAL)

    def cb_network_stat_refresh(self):
        self.network_stat_refresh_timer.stop()
        if not self.network_stat_work_in_progress and self.is_tab_on_focus:
            self.network_stat_work_in_progress = True
            self.script_manager.execute_script('settings_network_status',
                                               self.cb_settings_network_status)

    def static_ip_configuration_gui(self, show):
        if show:
            self.label_ip.show()
            self.label_mask.show()
            self.label_gw.show()
            self.label_dns.show()
            self.sbox_net_ip1.show()
            self.sbox_net_ip2.show()
            self.sbox_net_ip3.show()
            self.sbox_net_ip4.show()
            self.sbox_net_mask1.show()
            self.sbox_net_mask2.show()
            self.sbox_net_mask3.show()
            self.sbox_net_mask4.show()
            self.sbox_net_gw1.show()
            self.sbox_net_gw2.show()
            self.sbox_net_gw3.show()
            self.sbox_net_gw4.show()
            self.sbox_net_dns1.show()
            self.sbox_net_dns2.show()
            self.sbox_net_dns3.show()
            self.sbox_net_dns4.show()
        else:
            self.label_ip.hide()
            self.label_mask.hide()
            self.label_gw.hide()
            self.label_dns.hide()
            self.sbox_net_ip1.hide()
            self.sbox_net_ip2.hide()
            self.sbox_net_ip3.hide()
            self.sbox_net_ip4.hide()
            self.sbox_net_mask1.hide()
            self.sbox_net_mask2.hide()
            self.sbox_net_mask3.hide()
            self.sbox_net_mask4.hide()
            self.sbox_net_gw1.hide()
            self.sbox_net_gw2.hide()
            self.sbox_net_gw3.hide()
            self.sbox_net_gw4.hide()
            self.sbox_net_dns1.hide()
            self.sbox_net_dns2.hide()
            self.sbox_net_dns3.hide()
            self.sbox_net_dns4.hide()

    def address_configuration_gui(self, show):
        if show:
            self.label_addrs_conf.show()
            self.cbox_net_conftype.show()
        else:
            self.label_addrs_conf.hide()
            self.cbox_net_conftype.hide()

    def wireless_configuration_gui(self, show):
        if show:
            self.label_ap.show()
            self.tree_net_wireless_ap.show()
            self.widget_scan.show()
            self.label_key.show()
            self.ledit_net_wireless_key.show()
            self.chkbox_net_wireless_key_show.setChecked(False)
            self.chkbox_net_wireless_key_show.show()
        else:
            self.label_ap.hide()
            self.tree_net_wireless_ap.hide()
            self.widget_scan.hide()
            self.label_key.hide()
            self.ledit_net_wireless_key.hide()
            self.chkbox_net_wireless_key_show.setChecked(False)
            self.chkbox_net_wireless_key_show.hide()

    def show_please_wait(self, state):
        self.frame_working_please_wait.show()
        self.gbox_net_config.setEnabled(False)
        self.network_button_refresh_enabled(False)

        if state == WORKING_STATE_REFRESH:
            self.work_in_progress = True
            self.cbox_net_intf.clear()
            self.cbox_net_intf.setEnabled(False)
            item = QtGui.QStandardItem('')
            item.setData(QtCore.QVariant(AP_STATUS_NONE),
                         AP_STATUS_USER_ROLE)
            self.ap_tree_model_clear_add_item(item)
            self.tree_net_wireless_ap.setEnabled(False)
            self.ledit_net_wireless_key.setEnabled(False)
            self.ledit_net_wireless_key.setText('')
            self.wireless_configuration_gui(False)
            self.cbox_net_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_DHCP)
            self.address_configuration_gui(False)

        elif state == WORKING_STATE_SCAN:
            self.work_in_progress = True
            item = QtGui.QStandardItem('Scanning...')
            item.setData(QtCore.QVariant(AP_STATUS_NONE),
                         AP_STATUS_USER_ROLE)
            self.ap_tree_model_clear_add_item(item)
            self.tree_net_wireless_ap.setEnabled(False)
            self.ledit_net_wireless_key.setEnabled(False)
            self.ledit_net_wireless_key.setText('')

        elif state == WORKING_STATE_SAVE:
            self.work_in_progress = True
            self.network_button_refresh_enabled(True)

        elif state == WORKING_STATE_DONE:
            self.work_in_progress = False
            self.frame_working_please_wait.hide()
            self.gbox_net_config.setEnabled(True)
            self.network_button_refresh_enabled(True)

    def update_access_points(self, scan_data):
        def ap_found():
            self.tree_net_wireless_ap.setEnabled(True)
            self.chkbox_net_wireless_key_show.setChecked(False)
        def no_ap_found():
            self.tree_net_wireless_ap.setEnabled(True)
            self.ledit_net_wireless_key.setText('')
            self.chkbox_net_wireless_key_show.setChecked(False)
            self.ap_tree_model_clear_add_item(None)
            item = QtGui.QStandardItem('No access points found. Scan again?')
            item.setData(QtCore.QVariant(AP_COL), AP_COL_USER_ROLE)
            item.setData(QtCore.QVariant(AP_STATUS_NONE), AP_STATUS_USER_ROLE)
            item.setEnabled(False)
            item.setSelectable(False)
            self.ap_tree_model_clear_add_item(item)

        if scan_data and \
           self.network_all_data['interfaces']['wireless'] and \
           self.network_all_data['interfaces']['wireless_links']:

            if len(scan_data) <= 0 or \
               len(self.network_all_data['interfaces']['wireless']) <= 0:
                no_ap_found()
                return

            self.ap_tree_model_clear_add_item(None)

            for nidx, apdict in scan_data.iteritems():
                if not unicode(apdict['essid']):
                    continue

                essid = unicode(apdict['essid'])
                bssid = unicode(apdict['bssid'])
                channel = unicode(apdict['channel'])
                encryption = unicode(apdict['encryption'])
                encryption_method = unicode(apdict['encryption_method'])

                ap_item = QtGui.QStandardItem(essid)
                ap_item.setData(QtCore.QVariant(AP_COL),
                                AP_COL_USER_ROLE)
                ap_item.setData(QtCore.QVariant(encryption),
                                AP_ENCRYPTION_USER_ROLE)
                ap_item.setData(QtCore.QVariant(essid),
                                AP_NAME_USER_ROLE)
                ap_item.setData(QtCore.QVariant(bssid),
                                AP_BSSID_USER_ROLE)
                ap_item.setData(QtCore.QVariant(nidx),
                                AP_NETWORK_INDEX_USER_ROLE)
                ap_item.setData(QtCore.QVariant(channel),
                                AP_CHANNEL_USER_ROLE)

                channel_item = QtGui.QStandardItem(channel)

                if encryption == 'Off':
                    encryption_method_item = QtGui.QStandardItem('Open')
                else:
                    if encryption_method == 'WPA1':
                        encryption_method_item = QtGui.QStandardItem('WPA1')
                        ap_item.setData(QtCore.QVariant(AP_ENC_METHOD_WPA1),
                                        AP_ENCRYPTION_METHOD_USER_ROLE)
                    elif encryption_method == 'WPA2':
                        encryption_method_item = QtGui.QStandardItem('WPA2')
                        ap_item.setData(QtCore.QVariant(AP_ENC_METHOD_WPA2),
                                        AP_ENCRYPTION_METHOD_USER_ROLE)
                    else:
                        encryption_method_item = QtGui.QStandardItem('Unsupported')
                        ap_item.setData(QtCore.QVariant(AP_ENC_METHOD_UNSUPPORTED),
                                        AP_ENCRYPTION_METHOD_USER_ROLE)

                try:
                    _key = self.network_all_data['wireless_settings'].get(bssid, 'key', '')
                    ap_item.setData(QtCore.QVariant(unicode(_key)),
                                    AP_KEY_USER_ROLE)
                except:
                    ap_item.setData(QtCore.QVariant(''),
                                    AP_KEY_USER_ROLE)

                # Checking if the access point is associated
                ap_item.setData(QtCore.QVariant(AP_STATUS_NOT_ASSOCIATED),
                                AP_STATUS_USER_ROLE)
                for key, value in self.network_all_data['interfaces']['wireless_links'].iteritems():
                    if (unicode(value['bssid']) == unicode(bssid)) and value['status']:
                        ap_item.setData(QtCore.QVariant(AP_STATUS_ASSOCIATED),
                                        AP_STATUS_USER_ROLE)
                        break
                try:
                    _ip = self.network_all_data['wireless_settings'].get(bssid, 'ip', '')
                    if _ip == '' or _ip == 'None':
                        ap_item.setData(QtCore.QVariant(CBOX_NET_CONTYPE_INDEX_DHCP),
                                        AP_ADDRESS_CONF_USER_ROLE)
                        ap_item.setData(QtCore.QVariant('0.0.0.0'),
                                        AP_IP_USER_ROLE)
                    else:
                        ap_item.setData(QtCore.QVariant(CBOX_NET_CONTYPE_INDEX_STATIC),
                                        AP_ADDRESS_CONF_USER_ROLE)
                        ap_item.setData(QtCore.QVariant(_ip),
                                        AP_IP_USER_ROLE)
                except:
                    ap_item.setData(QtCore.QVariant(CBOX_NET_CONTYPE_INDEX_DHCP),
                                    AP_ADDRESS_CONF_USER_ROLE)
                    ap_item.setData(QtCore.QVariant('0.0.0.0'),
                                    AP_IP_USER_ROLE)

                try:
                    _mask = self.network_all_data['wireless_settings'].get(bssid, 'netmask', '')
                    if _mask == '' or _ip == 'None':
                        ap_item.setData(QtCore.QVariant('0.0.0.0'),
                                        AP_MASK_USER_ROLE)
                    else:
                        ap_item.setData(QtCore.QVariant(_mask),
                                        AP_MASK_USER_ROLE)
                except:
                    ap_item.setData(QtCore.QVariant('0.0.0.0'),
                                    AP_MASK_USER_ROLE)

                try:
                    _gw = self.network_all_data['wireless_settings'].get(bssid, 'gateway', '')
                    if _gw == '' or _gw == 'None':
                        ap_item.setData(QtCore.QVariant('0.0.0.0'),
                                        AP_GATEWAY_USER_ROLE)
                    else:
                        ap_item.setData(QtCore.QVariant(_gw),
                                        AP_GATEWAY_USER_ROLE)
                except:
                    ap_item.setData(QtCore.QVariant('0.0.0.0'),
                                    AP_GATEWAY_USER_ROLE)

                try:
                    _dns = self.network_all_data['wireless_settings'].get(bssid, 'dns1', '')
                    if _dns == '' or _dns == 'None':
                        ap_item.setData(QtCore.QVariant('0.0.0.0'),
                                        AP_DNS_USER_ROLE)
                    else:
                        ap_item.setData(QtCore.QVariant(_dns),
                                        AP_DNS_USER_ROLE)
                except:
                    ap_item.setData(QtCore.QVariant('0.0.0.0'),
                                    AP_DNS_USER_ROLE)

                self.ap_tree_model.appendRow([ap_item, channel_item, encryption_method_item])

            if self.ap_tree_model.rowCount() <= 0:
                no_ap_found()
                return

            ap_found()

            # Select first associated accesspoint if not then the first item
            for i in range(self.ap_tree_model.rowCount()):
                item = self.ap_tree_model.item(i)
                ap_status = item.data(AP_STATUS_USER_ROLE).toInt()[0]
                if ap_status == AP_STATUS_ASSOCIATED:
                    self.tree_net_wireless_ap.setCurrentIndex(self.ap_tree_model.index(i, 0))
                    break
                if i == self.ap_tree_model.rowCount()- 1:
                    self.tree_net_wireless_ap.setCurrentIndex(self.ap_tree_model.index(0, 0))
        else:
            no_ap_found()

    def update_network_gui(self):
        def update_no_interface_available():
            self.cbox_net_intf.clear()
            self.cbox_net_intf.addItem('No interfaces available')
            self.cbox_net_intf.setEnabled(False)
            self.wireless_configuration_gui(False)
            self.cbox_net_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_DHCP)
            self.address_configuration_gui(False)
            self.static_ip_configuration_gui(False)

        # Populating available interfaces
        self.cbox_net_intf.clear()

        if self.network_all_data['interfaces'] is not None and \
           self.network_all_data['status'] is not None and \
           (self.network_all_data['interfaces']['wireless'] is not None or \
            self.network_all_data['interfaces']['wired'] is not None or \
            self.network_all_data['interfaces']['wireless_links'] is not None):
                # Processing wireless interfaces
                if self.network_all_data['interfaces']['wireless'] is not None and\
                   len(self.network_all_data['interfaces']['wireless']) > 0:
                        for intf in self.network_all_data['interfaces']['wireless']:
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
                                    _ip = 'None'

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
                    return
                else:
                    # Select first active interface by default if not then the first item
                    self.cbox_net_intf.setCurrentIndex(-1)
                    for i in range(self.cbox_net_intf.count()):
                        istate = self.cbox_net_intf.itemData(i, INTERFACE_STATE_USER_ROLE).toInt()[0]
                        if istate == INTERFACE_STATE_ACTIVE:
                            self.cbox_net_intf.setCurrentIndex(i)
                            iname = self.cbox_net_intf.itemData(i, INTERFACE_NAME_USER_ROLE).toString()
                            itype = self.cbox_net_intf.itemData(i, INTERFACE_TYPE_USER_ROLE).toInt()[0]
                            break
                        if i == self.cbox_net_intf.count() - 1:
                            self.cbox_net_intf.setCurrentIndex(0)

                self.cbox_net_intf.setEnabled(True)

        elif self.network_all_data['interfaces']['wireless'] is None and \
             self.network_all_data['interfaces']['wired'] is None:
            update_no_interface_available()

        elif self.network_all_data['interfaces']['wireless'] is not None and \
             self.network_all_data['interfaces']['wired'] is not None:
            if len(self.network_all_data['interfaces']['wireless']) <= 0 and \
               len(self.network_all_data['interfaces']['wired']) <= 0:
                update_no_interface_available()

    def network_button_refresh_enabled(self, state):
        self.pbutton_net_conf_refresh.setEnabled(state)

        if state:
            self.pbutton_net_conf_refresh.setText('Refresh')
        else:
            self.pbutton_net_conf_refresh.setText('Refreshing...')

    def network_button_connect_enabled(self, state):
        self.pbutton_net_connect.setEnabled(state)

        if state:
            self.pbutton_net_connect.setText('Connect')
        else:
            self.pbutton_net_connect.setText('Connecting...')

    def slot_pbutton_net_wireless_scan_clicked(self):
        cbox_cidx = self.cbox_net_intf.currentIndex()
        interface_name = self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_NAME_USER_ROLE).toString()
        interface_type = self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_TYPE_USER_ROLE).toInt()[0]

        if interface_type == INTERFACE_TYPE_WIRELESS:
            def cb_settings_network_wireless_scan(result):
                self.show_please_wait(WORKING_STATE_DONE)
                if not self.is_tab_on_focus:
                    return
                if result and result.stdout and not result.stderr and result.exit_code == 0:
                    self.network_all_data['scan_result'] = json.loads(result.stdout)
                    self.update_access_points(self.network_all_data['scan_result'])
                    QtGui.QMessageBox.information(get_main_window(),
                                               'Settings | Network',
                                               'Scan finished',
                                               QtGui.QMessageBox.Ok)
                else:
                    err_msg = 'Wireless scan failed\n\n'+unicode(result.stderr)
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               err_msg,
                                               QtGui.QMessageBox.Ok)
            try:
                # Saving currently configured wireless interface
                wlintf_restore_to = unicode(self.network_all_data['manager_settings'].get('Settings', 'wireless_interface', ''))
            except Exception as e:
                err_msg = 'Wireless scan failed\n\n'+unicode(e)
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Network',
                                           err_msg,
                                           QtGui.QMessageBox.Ok)
                return

            self.show_please_wait(WORKING_STATE_SCAN)

            self.script_manager.execute_script('settings_network_wireless_scan',
                                               cb_settings_network_wireless_scan,
                                               [interface_name, wlintf_restore_to])

        else:
            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Network',
                                       'Scan only possible for wireless interfaces.',
                                       QtGui.QMessageBox.Ok)

    def slot_network_conf_refresh_clicked(self):
        def network_refresh_tasks_done(refresh_all_ok):
            self.show_please_wait(WORKING_STATE_DONE)
            self.network_refresh_tasks_remaining = -1
            self.network_refresh_tasks_error_occured = False
            if refresh_all_ok:
                self.update_network_gui()

        def cb_settings_network_status(result):
            if not self.is_tab_on_focus:
                self.show_please_wait(WORKING_STATE_DONE)
                return
            self.network_refresh_tasks_remaining -= 1
            if result and result.stdout and not result.stderr and result.exit_code == 0 and \
               not self.network_refresh_tasks_error_occured:
                self.network_all_data['status'] = json.loads(result.stdout)
                if self.network_refresh_tasks_remaining == 0:
                    network_refresh_tasks_done(True)
            else:
                if self.network_refresh_tasks_remaining == 0:
                    network_refresh_tasks_done(False)
                else:
                    self.network_refresh_tasks_error_occured = True

                if result and result.stderr:
                    err_msg = 'Error executing network status script.\n\n'+unicode(result.stderr)
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               err_msg,
                                               QtGui.QMessageBox.Ok)

        def cb_settings_network_get_interfaces(result):
            if not self.is_tab_on_focus:
                self.show_please_wait(WORKING_STATE_DONE)
                return
            self.network_refresh_tasks_remaining -= 1
            if result and result.stdout and not result.stderr and result.exit_code == 0 and \
               not self.network_refresh_tasks_error_occured:
                self.network_all_data['interfaces'] = json.loads(result.stdout)
                self.script_manager.execute_script('settings_network_wireless_scan_cache',
                                                   cb_settings_network_wireless_scan_cache)
            else:
                self.network_refresh_tasks_error_occured = True
                if result and result.stderr:
                    err_msg = 'Error executing network get interfaces script.\n\n'+unicode(result.stderr)
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               err_msg,
                                               QtGui.QMessageBox.Ok)

        def cb_settings_network_wireless_scan_cache(result):
            if not self.is_tab_on_focus:
                self.show_please_wait(WORKING_STATE_DONE)
                return
            self.network_refresh_tasks_remaining -= 1
            if result and result.stdout and not result.stderr and result.exit_code == 0 and \
               not self.network_refresh_tasks_error_occured:
                self.network_all_data['scan_result_cache'] = json.loads(result.stdout)
                self.update_access_points(self.network_all_data['scan_result_cache'])
                if self.network_refresh_tasks_remaining == 0:
                    network_refresh_tasks_done(True)
            else:
                if self.network_refresh_tasks_remaining == 0:
                    network_refresh_tasks_done(False)
                else:
                    self.network_refresh_tasks_error_occured = True

                if result and result.stderr:
                    err_msg = 'Error executing wireless scan cache script.\n\n'+unicode(result.stderr)
                    QtGui.QMessageBox.critical(None,
                                               'Settings | Network',
                                               err_msg,
                                               QtGui.QMessageBox.Ok)

        def cb_open_manager_settings(red_file):
            if not self.is_tab_on_focus:
                self.show_please_wait(WORKING_STATE_DONE)
                return
            def cb_read(red_file, result):
                if not self.is_tab_on_focus:
                    self.show_please_wait(WORKING_STATE_DONE)
                    return
                self.network_refresh_tasks_remaining -= 1

                red_file.release()

                if result and result.data is not None and result.error is None and \
                   not self.network_refresh_tasks_error_occured:
                    self.network_all_data['manager_settings'] = config_parser.parse_no_fake(result.data.decode('utf-8'))
                    if self.network_refresh_tasks_remaining == 0:
                        network_refresh_tasks_done(True)
                else:
                    if self.network_refresh_tasks_remaining == 0:
                        network_refresh_tasks_done(False)
                    else:
                        self.network_refresh_tasks_error_occured = True

                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               'Error reading wired settings file.',
                                               QtGui.QMessageBox.Ok)

            red_file.read_async(4096, lambda x: cb_read(red_file, x))

        def cb_open_error_manager_settings():
            if not self.is_tab_on_focus:
                self.show_please_wait(WORKING_STATE_DONE)
                return
            self.network_refresh_tasks_remaining -= 1
            if self.network_refresh_tasks_remaining == 0:
                network_refresh_tasks_done(False)
            else:
                self.network_refresh_tasks_error_occured = True

            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Network',
                                       'Error opening manager settings file.',
                                       QtGui.QMessageBox.Ok)

        def cb_open_wireless_settings(red_file):
            if not self.is_tab_on_focus:
                self.show_please_wait(WORKING_STATE_DONE)
                return
            def cb_read(red_file, result):
                if not self.is_tab_on_focus:
                    self.show_please_wait(WORKING_STATE_DONE)
                    return
                self.network_refresh_tasks_remaining -= 1

                red_file.release()

                if result and result.data is not None and result.error is None and \
                   not self.network_refresh_tasks_error_occured:
                    self.network_all_data['wireless_settings'] = config_parser.parse_no_fake(result.data.decode('utf-8'))
                    if self.network_refresh_tasks_remaining == 0:
                        network_refresh_tasks_done(True)
                else:
                    if self.network_refresh_tasks_remaining == 0:
                        network_refresh_tasks_done(False)
                    else:
                        self.network_refresh_tasks_error_occured = True

                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               'Error reading wireless settings file.',
                                               QtGui.QMessageBox.Ok)

            red_file.read_async(4096, lambda x: cb_read(red_file, x))

        def cb_open_error_wireless_settings():
            if not self.is_tab_on_focus:
                self.show_please_wait(WORKING_STATE_DONE)
                return
            self.network_refresh_tasks_remaining -= 1
            if self.network_refresh_tasks_remaining == 0:
                network_refresh_tasks_done(False)
            else:
                self.network_refresh_tasks_error_occured = True

            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Network',
                                       'Error opening wireless settings file.',
                                       QtGui.QMessageBox.Ok)

        def cb_open_wired_settings(red_file):
            if not self.is_tab_on_focus:
                self.show_please_wait(WORKING_STATE_DONE)
                return
            def cb_read(red_file, result):
                if not self.is_tab_on_focus:
                    self.show_please_wait(WORKING_STATE_DONE)
                    return
                self.network_refresh_tasks_remaining -= 1

                red_file.release()

                if result and result.data is not None and result.error is None and \
                   not self.network_refresh_tasks_error_occured:
                    self.network_all_data['wired_settings'] = config_parser.parse_no_fake(result.data.decode('utf-8'))
                    if self.network_refresh_tasks_remaining == 0:
                        network_refresh_tasks_done(True)
                else:
                    if self.network_refresh_tasks_remaining == 0:
                        network_refresh_tasks_done(False)
                    else:
                        self.network_refresh_tasks_error_occured = True

                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               'Error reading wired settings file.',
                                               QtGui.QMessageBox.Ok)

            red_file.read_async(4096, lambda x: cb_read(red_file, x))

        def cb_open_error_wired_settings():
            if not self.is_tab_on_focus:
                self.show_please_wait(WORKING_STATE_DONE)
                return
            self.network_refresh_tasks_remaining -= 1
            if self.network_refresh_tasks_remaining == 0:
                network_refresh_tasks_done(False)
            else:
                self.network_refresh_tasks_error_occured = True

            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Network',
                                       'Error opening wired settings file.',
                                       QtGui.QMessageBox.Ok)

        self.show_please_wait(WORKING_STATE_REFRESH)

        self.network_refresh_tasks_remaining = 6
        self.network_refresh_tasks_error_occured = False

        self.script_manager.execute_script('settings_network_status',
                                           cb_settings_network_status)

        self.script_manager.execute_script('settings_network_get_interfaces',
                                           cb_settings_network_get_interfaces)

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

    def slot_network_connect_clicked(self):
        cbox_cidx = self.cbox_net_intf.currentIndex()

        iname = self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_NAME_USER_ROLE).toString()
        itype = self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_TYPE_USER_ROLE).toInt()[0]

        # Wireless
        if itype == INTERFACE_TYPE_WIRELESS:
            self.show_please_wait(WORKING_STATE_SAVE)

            index_list = self.tree_net_wireless_ap.selectedIndexes()

            ap_item = None
            for i in range(len(index_list)):
                item = self.ap_tree_model.itemFromIndex(index_list[i])
                try:
                    ap_col = item.data(AP_COL_USER_ROLE)
                    if ap_col == AP_COL:
                        ap_item = item
                        break
                except:
                    continue

            if ap_item:
                apname = ap_item.data(AP_NAME_USER_ROLE).toString()
                enc_method = ap_item.data(AP_ENCRYPTION_METHOD_USER_ROLE).toInt()[0]
                enc = ap_item.data(AP_ENCRYPTION_USER_ROLE).toString()
                key = self.ledit_net_wireless_key.text()

            if not apname:
                self.show_please_wait(WORKING_STATE_DONE)
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Network',
                                           'Configure an access point first.',
                                           QtGui.QMessageBox.Ok)
                return
            elif enc_method == AP_ENC_METHOD_UNSUPPORTED:
                self.show_please_wait(WORKING_STATE_DONE)
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Network',
                                           'Encryption method not supported.',
                                           QtGui.QMessageBox.Ok)
                return
            elif enc == 'On' and not key:
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Network',
                                           'Please provide a secret key.',
                                           QtGui.QMessageBox.Ok)
                return
            else:
                address_conf = self.cbox_net_conftype.currentIndex()
                netidx = ap_item.data(AP_NETWORK_INDEX_USER_ROLE).toString()
                essid = apname
                bssid = ap_item.data(AP_BSSID_USER_ROLE).toString()

                iname_previous = self.network_all_data['manager_settings'].get('Settings', 'wireless_interface', 'None')
                self.network_all_data['manager_settings'].set('Settings', 'wireless_interface', iname)

                # Check BSSID section
                if not self.network_all_data['wireless_settings'].has_section(bssid):
                    self.network_all_data['wireless_settings'].add_section(bssid)

                self.network_all_data['wireless_settings'].set(bssid, 'automatic', 'True')
                self.network_all_data['wireless_settings'].set(bssid, 'essid', essid)
                self.network_all_data['wireless_settings'].set(bssid, 'bssid', bssid)
                self.network_all_data['wireless_settings'].set(bssid, 'use_static_dns', 'False')

                self.network_all_data['wireless_settings'].set(bssid, 'broadcast', 'None')
                self.network_all_data['wireless_settings'].set(bssid, 'search_domain', 'None')
                self.network_all_data['wireless_settings'].set(bssid, 'dns_domain', 'None')
                self.network_all_data['wireless_settings'].set(bssid, 'dns2', 'None')
                self.network_all_data['wireless_settings'].set(bssid, 'dns3', 'None')

                # Wireless DHCP config
                if address_conf == CBOX_NET_CONTYPE_INDEX_DHCP:
                    self.network_all_data['wireless_settings'].set(bssid, 'ip', 'None')
                    self.network_all_data['wireless_settings'].set(bssid, 'netmask', 'None')
                    self.network_all_data['wireless_settings'].set(bssid, 'gateway', 'None')
                    self.network_all_data['wireless_settings'].set(bssid, 'dns1', 'None')
                # Wireless static config
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

                    self.network_all_data['wireless_settings'].set(bssid, 'ip', ip)
                    self.network_all_data['wireless_settings'].set(bssid, 'netmask', mask)
                    self.network_all_data['wireless_settings'].set(bssid, 'gateway', gw)
                    self.network_all_data['wireless_settings'].set(bssid, 'dns1', dns)
                    self.network_all_data['wireless_settings'].set(bssid, 'use_static_dns', 'True')


                if enc == 'On':
                    self.network_all_data['wireless_settings'].set(bssid, 'encryption', 'True')
                    self.network_all_data['wireless_settings'].set(bssid, 'enctype', 'wpa')
                    self.network_all_data['wireless_settings'].set(bssid, 'key', key)

                    if enc_method == AP_ENC_METHOD_WPA1:
                        self.network_all_data['wireless_settings'].set(bssid, 'encryption_method', 'WPA1')
                    else:
                        self.network_all_data['wireless_settings'].set(bssid, 'encryption_method', 'WPA2')
                else:
                    self.network_all_data['wireless_settings'].remove_option(bssid, 'encryption')
                    self.network_all_data['wireless_settings'].remove_option(bssid, 'enctype')
                    self.network_all_data['wireless_settings'].remove_option(bssid, 'encryption_method')
                    self.network_all_data['wireless_settings'].remove_option(bssid, 'key')

                def cb_settings_network_apply(result):
                    self.show_please_wait(WORKING_STATE_DONE)
                    if result and not result.stderr and result.exit_code == 0:
                        self.slot_network_conf_refresh_clicked()
                        QtGui.QMessageBox.information(get_main_window(),
                                                      'Settings | Network',
                                                      'Configuration saved.',
                                                      QtGui.QMessageBox.Ok)
                    else:
                        err_msg = 'Error saving configuration.\n\n'+unicode(result.stderr)
                        QtGui.QMessageBox.critical(get_main_window(),
                                                   'Settings | Network',
                                                   err_msg,
                                                   QtGui.QMessageBox.Ok)

                def cb_open(config, write_wireless_settings, red_file, iname_previous):
                    def cb_write(red_file, write_wireless_settings, result, iname_previous):
                        red_file.release()
                        if result is not None:
                            self.show_please_wait(WORKING_STATE_DONE)
                            QtGui.QMessageBox.critical(get_main_window(),
                                                       'Settings | Network',
                                                       'Error saving configuration.',
                                                       QtGui.QMessageBox.Ok)
                        else:
                            if write_wireless_settings:
                                self.script_manager.execute_script('settings_network_apply',
                                                                   cb_settings_network_apply,
                                                                   [iname, iname_previous, 'wireless', netidx])
                            else:
                                config = config_parser.to_string_no_fake(self.network_all_data['wireless_settings'])
                                write_wireless_settings = True
                                async_call(self.wired_settings_conf_rfile.open,
                                           (WIRELESS_SETTINGS_CONF_PATH,
                                           REDFile.FLAG_WRITE_ONLY |
                                           REDFile.FLAG_CREATE |
                                           REDFile.FLAG_NON_BLOCKING |
                                           REDFile.FLAG_TRUNCATE, 0o500, 0, 0),
                                           lambda x: cb_open(config, write_wireless_settings, x, iname_previous),
                                           cb_open_error)

                    red_file.write_async(config, lambda x: cb_write(red_file, write_wireless_settings, x, iname_previous), None)

                def cb_open_error():
                    self.show_please_wait(WORKING_STATE_DONE)

                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               'Error saving configuration.',
                                               QtGui.QMessageBox.Ok)

                config = config_parser.to_string_no_fake(self.network_all_data['manager_settings'])
                write_wireless_settings = False

                async_call(self.manager_settings_conf_rfile.open,
                           (MANAGER_SETTINGS_CONF_PATH,
                           REDFile.FLAG_WRITE_ONLY |
                           REDFile.FLAG_CREATE |
                           REDFile.FLAG_NON_BLOCKING |
                           REDFile.FLAG_TRUNCATE, 0o500, 0, 0),
                           lambda x: cb_open(config, write_wireless_settings, x, iname_previous),
                           cb_open_error)

        # Wired
        else:
            iname_previous = self.network_all_data['manager_settings'].get('Settings', 'wired_interface', '')

            # Check default wired profile section
            if not self.network_all_data['wired_settings'].has_section('wired-default'):
                self.network_all_data['wired_settings'].add_section('wired-default')

            if self.cbox_net_conftype.currentIndex() == CBOX_NET_CONTYPE_INDEX_DHCP:
                # Save wired DHCP config
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
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               'Error saving configuration.',
                                               QtGui.QMessageBox.Ok)
                    return
            else:
                # Save wired static config
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
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               'Error saving configuration.',
                                               QtGui.QMessageBox.Ok)
                    return

            def cb_settings_network_apply(result):
                self.show_please_wait(WORKING_STATE_DONE)
                if result and not result.stderr and result.exit_code == 0:
                    self.slot_network_conf_refresh_clicked()
                    QtGui.QMessageBox.information(get_main_window(),
                                                  'Settings | Network',
                                                  'Configuration saved.',
                                                  QtGui.QMessageBox.Ok)
                else:
                    err_msg = 'Error saving configuration.\n\n'+unicode(result.stderr)
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               err_msg,
                                               QtGui.QMessageBox.Ok)

            def cb_open(config, write_wired_settings, red_file, iname_previous):
                def cb_write(red_file, write_wired_settings, result, iname_previous):
                    red_file.release()
                    if result is not None:
                        self.show_please_wait(WORKING_STATE_DONE)
                        QtGui.QMessageBox.critical(get_main_window(),
                                                   'Settings | Network',
                                                   'Error saving configuration.',
                                                   QtGui.QMessageBox.Ok)
                    else:
                        if write_wired_settings:
                            self.script_manager.execute_script('settings_network_apply',
                                                               cb_settings_network_apply,
                                                               [iname, iname_previous, 'wired'])
                        else:
                            config = config_parser.to_string_no_fake(self.network_all_data['wired_settings'])
                            write_wired_settings = True
                            async_call(self.wired_settings_conf_rfile.open,
                                       (WIRED_SETTINGS_CONF_PATH,
                                       REDFile.FLAG_WRITE_ONLY |
                                       REDFile.FLAG_CREATE |
                                       REDFile.FLAG_NON_BLOCKING |
                                       REDFile.FLAG_TRUNCATE, 0o500, 0, 0),
                                       lambda x: cb_open(config, write_wired_settings, x, iname_previous),
                                       cb_open_error)

                red_file.write_async(config, lambda x: cb_write(red_file, write_wired_settings, x, iname_previous), None)

            def cb_open_error():
                self.show_please_wait(WORKING_STATE_DONE)

                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Network',
                                           'Error saving configuration.',
                                           QtGui.QMessageBox.Ok)

            config = config_parser.to_string_no_fake(self.network_all_data['manager_settings'])
            write_wired_settings = False

            async_call(self.manager_settings_conf_rfile.open,
                       (MANAGER_SETTINGS_CONF_PATH,
                       REDFile.FLAG_WRITE_ONLY |
                       REDFile.FLAG_CREATE |
                       REDFile.FLAG_NON_BLOCKING |
                       REDFile.FLAG_TRUNCATE, 0o500, 0, 0),
                       lambda x: cb_open(config, write_wired_settings, x, iname_previous),
                       cb_open_error)

    def slot_cbox_net_intf_current_idx_changed(self, idx):
        interface_name = self.cbox_net_intf.itemData(idx, INTERFACE_NAME_USER_ROLE).toString()
        interface_type = self.cbox_net_intf.itemData(idx, INTERFACE_TYPE_USER_ROLE).toInt()[0]

        if interface_type == INTERFACE_TYPE_WIRELESS:
            self.wireless_configuration_gui(True)

            if self.ap_tree_model.rowCount() > 0:
                self.address_configuration_gui(True)
            else:
                self.address_configuration_gui(False)
        elif interface_type == INTERFACE_TYPE_WIRED:
            self.address_configuration_gui(True)
            self.wireless_configuration_gui(False)

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
                    self.cbox_net_conftype.setCurrentIndex(-1)
                self.cbox_net_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_STATIC)

    def slot_tree_net_wireless_ap_selection_changed(self, current_is, previous_is):
        index_list = current_is.indexes()
        for i in range(len(index_list)):
            item = self.ap_tree_model.itemFromIndex(index_list[i])
            try:
                ap_col = item.data(AP_COL_USER_ROLE)
                if ap_col == AP_COL:
                    enc = item.data(AP_ENCRYPTION_USER_ROLE).toString()
                    if enc == 'On':
                        self.ledit_net_wireless_key.setEnabled(True)
                        ap_key = item.data(AP_KEY_USER_ROLE).toString()
                        self.ledit_net_wireless_key.setText(unicode(ap_key))
                    else:
                        self.ledit_net_wireless_key.setText('')
                        self.ledit_net_wireless_key.setEnabled(False)

                    address_conf = item.data(AP_ADDRESS_CONF_USER_ROLE).toInt()[0]

                    encryption_method = item.data(AP_ENCRYPTION_METHOD_USER_ROLE).toInt()[0]
                    channel = item.data(AP_CHANNEL_USER_ROLE).toString()
                    encryption = item.data(AP_ENCRYPTION_USER_ROLE).toString()
                    key = item.data(AP_KEY_USER_ROLE).toString()
                    ip_string = item.data(AP_IP_USER_ROLE).toString()
                    mask_string = item.data(AP_MASK_USER_ROLE).toString()
                    gw_string = item.data(AP_GATEWAY_USER_ROLE).toString()
                    dns_string = item.data(AP_DNS_USER_ROLE).toString()
                    ip_array = ip_string.split('.')
                    mask_array = mask_string.split('.')
                    gw_array = gw_string.split('.')
                    dns_array = dns_string.split('.')

                    if encryption == 'On':
                        if encryption_method == AP_ENC_METHOD_WPA1:
                            self.ledit_net_wireless_key.setEnabled(True)
                            self.ledit_net_wireless_key.setText(unicode(key))
                        elif encryption_method == AP_ENC_METHOD_WPA2:
                            self.ledit_net_wireless_key.setEnabled(True)
                            self.ledit_net_wireless_key.setText(unicode(key))
                        else:
                            self.ledit_net_wireless_key.setEnabled(False)
                            self.ledit_net_wireless_key.setText('')
                    elif encryption == 'Off':
                        self.ledit_net_wireless_key.setEnabled(False)
                        self.ledit_net_wireless_key.setText('')

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

                    if address_conf == CBOX_NET_CONTYPE_INDEX_STATIC:
                        self.cbox_net_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_STATIC)
                    else:
                        self.cbox_net_conftype.setCurrentIndex(CBOX_NET_CONTYPE_INDEX_DHCP)
                    self.address_configuration_gui(True)

                    break
            except:
                continue

    def slot_net_wireless_key_show_state_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.ledit_net_wireless_key.setEchoMode(QtGui.QLineEdit.Normal)
        else:
            self.ledit_net_wireless_key.setEchoMode(QtGui.QLineEdit.Password)

    def slot_cbox_net_conftype_current_idx_changed(self, idx):
        if idx == CBOX_NET_CONTYPE_INDEX_STATIC:
            self.static_ip_configuration_gui(True)
        else:
            self.static_ip_configuration_gui(False)
