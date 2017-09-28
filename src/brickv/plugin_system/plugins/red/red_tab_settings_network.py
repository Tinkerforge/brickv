# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2017 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
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
import socket
import struct

from PyQt4 import Qt, QtCore, QtGui

from brickv.plugin_system.plugins.red.ui_red_tab_settings_network import Ui_REDTabSettingsNetwork
from brickv.plugin_system.plugins.red.ui_red_tab_settings_network_wireless_connect_hidden \
    import Ui_REDTabSettingsNetworkWirelessConnectHidden
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import TextFile
from brickv.plugin_system.plugins.red import config_parser
from brickv.async_call import async_call
from brickv.utils import get_main_window

# Constants
NETWORK_STAT_REFRESH_INTERVAL = 3000 # in milliseconds
MANAGER_SETTINGS_CONF_PATH = '/etc/wicd/manager-settings.conf'
WIRELESS_SETTINGS_CONF_PATH = '/etc/wicd/wireless-settings.conf'
WIRED_SETTINGS_CONF_PATH = '/etc/wicd/wired-settings.conf'
MANAGER_SETTINGS_CONF_PATH_NM = '/etc/NetworkManager/NetworkManager.conf'
WIRELESS_SETTINGS_CONF_PATH_NM = '/etc/NetworkManager/system-connections/_tf_brickv_wifi'
WIRED_SETTINGS_CONF_PATH_NM = '/etc/NetworkManager/system-connections/_tf_brickv_ethernet'
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
AP_QUALITY_USER_ROLE = QtCore.Qt.UserRole + 15

WORKING_STATE_REFRESH = 1
WORKING_STATE_SCAN = 2
WORKING_STATE_DONE = 3
WORKING_STATE_CONNECT = 4
WORKING_STATE_CHANGE_HOSTNAME = 5

AP_NAME_COL_WIDTH = 300
AP_CHANNEL_COL_WIDTH = 100
AP_SECURITY_COL_WIDTH = 100
AP_QUALITY_COL_WIDTH = 100

CONNECTION_CONFIG_WIFI_DICT = \
    {
        'connection':
        {
            'id': '_tf_brickv_wifi',
            'interface-name': None,
            'type': '802-11-wireless',
            'autoconnect': True
        },

        '802-11-wireless':
        {
            'ssid': None,
            'bssid': None,
            'hidden': None
        },

        'ipv4':
        {
            'method': None,
            'dns': None,
            'address-data': None,
            'gateway': None,
            'dhcp-send-hostname': True
        }
    }

CONNECTION_CONFIG_ETHERNET_DICT = \
    {
        'connection':
        {
            'id': '_tf_brickv_ethernet',
            'interface-name': None,
            'type': '802-3-ethernet',
            'autoconnect': True
        },

        '802-3-ethernet':
        {
            'auto-negotiate': True
        },

        'ipv4':
        {
            'method': None,
            'dns': None,
            'address-data': None,
            'gateway': None,
            'dhcp-send-hostname': True
        }
    }

class REDTabSettingsNetworkWirelessConnectHidden(QtGui.QDialog,
                                                 Ui_REDTabSettingsNetworkWirelessConnectHidden):
    def __init__(self, parent, parameters):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)

        self.parameters = parameters

        self.ui_group_encryption = [self.label_wpa_key,
                                    self.ledit_wpa_key,
                                    self.chkbox_wpa_key_show]

        self.ui_group_static_ip = [self.label_ip,
                                   self.label_subnet_mask,
                                   self.label_gateway,
                                   self.label_dns,
                                   self.sbox_ip_0,
                                   self.sbox_ip_1,
                                   self.sbox_ip_2,
                                   self.sbox_ip_3,
                                   self.sbox_netmask_0,
                                   self.sbox_netmask_1,
                                   self.sbox_netmask_2,
                                   self.sbox_netmask_3,
                                   self.sbox_gw_0,
                                   self.sbox_gw_1,
                                   self.sbox_gw_2,
                                   self.sbox_gw_3,
                                   self.sbox_dns_0,
                                   self.sbox_dns_1,
                                   self.sbox_dns_2,
                                   self.sbox_dns_3,
                                   self.label_15,
                                   self.label_16,
                                   self.label_17,
                                   self.label_18,
                                   self.label_19,
                                   self.label_20,
                                   self.label_21,
                                   self.label_22,
                                   self.label_23,
                                   self.label_24,
                                   self.label_25,
                                   self.label_26]

        self.slot_cbox_address_current_idx_changed(0)
        self.slot_chkbox_wpa_key_show_state_changed(False)
        self.slot_cbox_encryption_current_idx_changed(self.cbox_encryption.currentIndex())

        self.pbutton_cancel.clicked.connect(self.slot_pbutton_cancel_clicked)
        self.pbutton_connect.clicked.connect(self.slot_pbutton_connect_clicked)
        self.cbox_address.currentIndexChanged.connect(self.slot_cbox_address_current_idx_changed)
        self.chkbox_wpa_key_show.stateChanged.connect(self.slot_chkbox_wpa_key_show_state_changed)
        self.cbox_encryption.currentIndexChanged.connect(self.slot_cbox_encryption_current_idx_changed)

    def do_verify(self):
        if self.ledit_ssid.text() == '':
            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Network',
                                       'Please provide access point name.')
            return False

        if self.cbox_encryption.currentIndex() > 0 \
           and self.ledit_wpa_key.text() == '':
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Network',
                                           'Please provide WPA key.')
                return False

        return True

    def ui_group_toggle(self, ui_group, show):
        if show:
            for ui_element in ui_group:
                ui_element.show()
        else:
            for ui_element in ui_group:
                ui_element.hide()

    def slot_cbox_encryption_current_idx_changed(self, idx):
        if idx == 0:
            self.ui_group_toggle(self.ui_group_encryption, False)
        else:
            self.ui_group_toggle(self.ui_group_encryption, True)

    def slot_cbox_address_current_idx_changed(self, idx):
        if(idx == CBOX_NET_CONTYPE_INDEX_STATIC):
            self.ui_group_toggle(self.ui_group_static_ip, True)
        else:
            self.ui_group_toggle(self.ui_group_static_ip, False)

    def slot_chkbox_wpa_key_show_state_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.ledit_wpa_key.setEchoMode(QtGui.QLineEdit.Normal)
        else:
            self.ledit_wpa_key.setEchoMode(QtGui.QLineEdit.Password)

    def slot_pbutton_cancel_clicked(self):
        self.done(0)

    def slot_pbutton_connect_clicked(self):
        if self.do_verify():
            self.parameters['bssid'] = ':'.join((str('{:02X}'.format(self.sbox_bssid_0.value())),
                                                 str('{:02X}'.format(self.sbox_bssid_1.value())),
                                                 str('{:02X}'.format(self.sbox_bssid_2.value())),
                                                 str('{:02X}'.format(self.sbox_bssid_3.value())),
                                                 str('{:02X}'.format(self.sbox_bssid_4.value())),
                                                 str('{:02X}'.format(self.sbox_bssid_5.value()))))

            self.parameters['essid'] = self.ledit_ssid.text()
            self.parameters['key'] = self.ledit_wpa_key.text()
            self.parameters['address_conf_type'] = self.cbox_address.currentIndex()

            self.parameters['ip'] = '.'.join((str(self.sbox_ip_0.value()),
                                           str(self.sbox_ip_1.value()),
                                           str(self.sbox_ip_2.value()),
                                           str(self.sbox_ip_3.value())))

            self.parameters['netmask'] = '.'.join((str(self.sbox_netmask_0.value()),
                                                str(self.sbox_netmask_1.value()),
                                                str(self.sbox_netmask_2.value()),
                                                str(self.sbox_netmask_3.value())))

            self.parameters['gw'] = '.'.join((str(self.sbox_gw_0.value()),
                                           str(self.sbox_gw_1.value()),
                                           str(self.sbox_gw_2.value()),
                                           str(self.sbox_gw_3.value())))

            self.parameters['dns'] = '.'.join((str(self.sbox_dns_0.value()),
                                            str(self.sbox_dns_1.value()),
                                            str(self.sbox_dns_2.value()),
                                            str(self.sbox_dns_3.value())))

            self.parameters['encryption_method'] = self.cbox_encryption.currentIndex()

            self.done(1)

class REDTabSettingsNetwork(QtGui.QWidget, Ui_REDTabSettingsNetwork):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings
        self.image_version  = None # Set from REDTabSettings
        self.service_state  = None # Set from REDTabSettings

        self.is_tab_on_focus = False

        self.image_version_lt_1_10 = True

        self.network_stat_refresh_timer = Qt.QTimer(self)

        self.network_refresh_tasks_remaining = -1
        self.network_refresh_tasks_error_occured = False
        self.work_in_progress = False
        self.network_stat_work_in_progress = False
        self.ap_mode = False

        self.is_connecting = False

        self.label_net_disabled.hide()
        self.sarea_net.hide()

        self.network_all_data = {'status': None,
                                 'interfaces': None,
                                 'scan_result': None,
                                 'scan_result_cache': None,
                                 'manager_settings': None,
                                 'wireless_settings': None,
                                 'wired_settings': None}


        self.ap_tree_model = QtGui.QStandardItemModel(0, 4)

        self.ap_tree_model.setHorizontalHeaderItem(0, QtGui.QStandardItem('SSID'))
        self.ap_tree_model.setHorizontalHeaderItem(1, QtGui.QStandardItem('Channel'))
        self.ap_tree_model.setHorizontalHeaderItem(2, QtGui.QStandardItem('Security'))
        self.ap_tree_model.setHorizontalHeaderItem(3, QtGui.QStandardItem('Signal Quality'))

        self.tree_net_wireless_ap.setModel(self.ap_tree_model)

        self.tree_net_wireless_ap.header().resizeSection(0, AP_NAME_COL_WIDTH)
        self.tree_net_wireless_ap.header().resizeSection(1, AP_CHANNEL_COL_WIDTH)
        self.tree_net_wireless_ap.header().resizeSection(2, AP_SECURITY_COL_WIDTH)
        self.tree_net_wireless_ap.header().resizeSection(3, AP_QUALITY_COL_WIDTH)

        self.network_stat_refresh_timer.timeout.connect(self.cb_network_stat_refresh)

        # Signals/slots
        self.pbutton_net_wireless_scan.clicked.connect(self.slot_pbutton_net_wireless_scan_clicked)
        self.pbutton_net_conf_refresh.clicked.connect(self.slot_network_conf_refresh_clicked)
        self.pbutton_net_connect.clicked.connect(self.slot_network_connect_clicked)
        self.pbutton_net_conf_change_hostname.clicked.connect(self.slot_change_hostname_clicked)
        self.pbutton_net_wireless_connect_hidden.clicked.connect(self.slot_wireless_connect_hidden_clicked)

        # Network fields
        self.address_configuration_gui(False)
        self.static_ip_configuration_gui(False)
        self.widget_working_please_wait.hide()
        self.cbox_net_intf.currentIndexChanged.connect(self.slot_cbox_net_intf_current_idx_changed)
        self.cbox_net_conftype.currentIndexChanged.connect(self.slot_cbox_net_conftype_current_idx_changed)
        QtCore.QObject.connect(self.tree_net_wireless_ap.selectionModel(),
                               QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'),
                               self.slot_tree_net_wireless_ap_selection_changed)
        self.ledit_net_wireless_key.setEchoMode(QtGui.QLineEdit.Password)
        self.chkbox_net_wireless_key_show.stateChanged.connect(self.slot_net_wireless_key_show_state_changed)

    def tab_on_focus(self):
        self.is_tab_on_focus = True

        # python-reconfigure is available since image version 1.7
        self.pbutton_net_conf_change_hostname.setDisabled(self.image_version.number < (1, 7))
        self.label_net_conf_change_hostname_hint.setVisible(self.image_version.number < (1, 7))

        if not self.image_version:
            self.image_version_lt_1_10 = True
        else:
            self.image_version_lt_1_10 = self.image_version.number < (1, 10)

        if not self.image_version_lt_1_10:
            item_channel = self.ap_tree_model.takeHorizontalHeaderItem(1)
            item_channel.setText('Channel (MHz)')
            self.ap_tree_model.setHorizontalHeaderItem(1, item_channel)

        if self.image_version.number < (1, 4) or not self.service_state.ap:
            self.ap_mode_disabled()
        else:
            self.ap_mode_enabled()

    def tab_off_focus(self):
        self.is_tab_on_focus = False
        self.network_stat_refresh_timer.stop()

    def tab_destroy(self):
        pass

    def cidr_to_netmask(self, cidr):
        host_bits = 32 - int(cidr)
        return socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))

    def netmask_to_cidr(self, netmask):
        return sum([bin(int(x)).count('1') for x in netmask.split('.')])

    def save_and_apply(self, iname, iname_previous):
        def cb_settings_network_apply(result):
            self.is_connecting = False
            self.update_gui(WORKING_STATE_DONE)
            if result and result.stderr == '' and result.exit_code == 0:
                QtGui.QMessageBox.information(get_main_window(),
                                              'Settings | Network',
                                              'Configuration saved.')
                self.slot_network_conf_refresh_clicked()
            else:
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Network',
                                           'Error saving configuration:\n\n' + result.stderr)

        def cb_open(config, stage, red_file, iname_previous):
            def cb_write(red_file, stage, result, iname_previous):
                red_file.release()

                if result is not None:
                    self.is_connecting = False
                    self.update_gui(WORKING_STATE_DONE)
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               'Error saving configuration.')
                else:
                    stage = stage + 1

                    if stage == 2:
                        config = config_parser.to_string_no_fake(self.network_all_data['wireless_settings'])
                        async_call(self.wired_settings_conf_rfile.open,
                                   (WIRELESS_SETTINGS_CONF_PATH,
                                   REDFile.FLAG_WRITE_ONLY |
                                   REDFile.FLAG_CREATE |
                                   REDFile.FLAG_NON_BLOCKING |
                                   REDFile.FLAG_TRUNCATE, 0o500, 0, 0),
                                   lambda x: cb_open(config, stage, x, iname_previous),
                                   cb_open_error)
                    elif stage == 3:
                        config = config_parser.to_string_no_fake(self.network_all_data['wired_settings'])
                        async_call(self.manager_settings_conf_rfile.open,
                                   (WIRED_SETTINGS_CONF_PATH,
                                   REDFile.FLAG_WRITE_ONLY |
                                   REDFile.FLAG_CREATE |
                                   REDFile.FLAG_NON_BLOCKING |
                                   REDFile.FLAG_TRUNCATE, 0o500, 0, 0),
                                   lambda x: cb_open(config, stage, x, iname_previous),
                                   cb_open_error)
                    elif stage == 4:
                        self.script_manager.execute_script('settings_network_apply',
                                                           cb_settings_network_apply,
                                                           [iname, iname_previous, 'wireless'])

            red_file.write_async(config, lambda x: cb_write(red_file, stage, x, iname_previous), None)

        def cb_open_error():
            self.is_connecting = False
            self.update_gui(WORKING_STATE_DONE)

            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Network',
                                       'Error saving configuration.')

        config = config_parser.to_string_no_fake(self.network_all_data['manager_settings'])
        stage = 1

        async_call(self.manager_settings_conf_rfile.open,
                   (MANAGER_SETTINGS_CONF_PATH,
                   REDFile.FLAG_WRITE_ONLY |
                   REDFile.FLAG_CREATE |
                   REDFile.FLAG_NON_BLOCKING |
                   REDFile.FLAG_TRUNCATE, 0o500, 0, 0),
                   lambda x: cb_open(config, stage, x, iname_previous),
                   cb_open_error)

        self.is_connecting = True

    def connect_wireless_hidden(self, parameters):
        def cb_settings_network_apply_nm(result):
            self.update_gui(WORKING_STATE_DONE)
            if result and result.stderr == '' and result.exit_code == 0:
                QtGui.QMessageBox.information(get_main_window(),
                                              'Settings | Network',
                                              'Configuration saved.')
                self.slot_network_conf_refresh_clicked()
            else:
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Network',
                                           'Error saving configuration:\n\n' + result.stderr)

        if self.image_version_lt_1_10:
            cbox_cidx = self.cbox_net_intf.currentIndex()
            itype = self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_TYPE_USER_ROLE)
            iname = self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_NAME_USER_ROLE)
            iname_previous = self.network_all_data['manager_settings'].get('Settings', 'wireless_interface', 'None')

            self.network_all_data['manager_settings'].set('Settings', 'wireless_interface', iname)
            self.network_all_data['wired_settings'].set('wired-default', 'default', 'False')

            if itype != INTERFACE_TYPE_WIRELESS:
                return

            self.update_gui(WORKING_STATE_CONNECT)

            sections = self.network_all_data['wireless_settings'].sections()

            # Set all existing config file AP 'automatic' parameter to be false
            for s in sections:
                self.network_all_data['wireless_settings'].set(s, 'automatic', 'False')

            bssid = parameters['bssid']
            essid = parameters['essid']
            key = parameters['key']
            address_conf_type = parameters['address_conf_type']
            ip = parameters['ip']
            netmask = parameters['netmask']
            gw = parameters['gw']
            dns = parameters['dns']
            encryption_method = parameters['encryption_method']
            key = parameters['key']

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

            # Static IP config
            if address_conf_type == CBOX_NET_CONTYPE_INDEX_STATIC:
                self.network_all_data['wireless_settings'].set(bssid, 'ip', ip)
                self.network_all_data['wireless_settings'].set(bssid, 'netmask', netmask)
                self.network_all_data['wireless_settings'].set(bssid, 'gateway', gw)
                self.network_all_data['wireless_settings'].set(bssid, 'dns1', dns)
                self.network_all_data['wireless_settings'].set(bssid, 'use_static_dns', 'True')
            # DHCP config
            else:
                self.network_all_data['wireless_settings'].set(bssid, 'ip', 'None')
                self.network_all_data['wireless_settings'].set(bssid, 'netmask', 'None')
                self.network_all_data['wireless_settings'].set(bssid, 'gateway', 'None')
                self.network_all_data['wireless_settings'].set(bssid, 'dns1', 'None')

            if encryption_method > 0:
                self.network_all_data['wireless_settings'].set(bssid, 'encryption', 'True')
                self.network_all_data['wireless_settings'].set(bssid, 'enctype', 'wpa')
                self.network_all_data['wireless_settings'].set(bssid, 'key', key)

                if encryption_method == AP_ENC_METHOD_WPA1:
                    self.network_all_data['wireless_settings'].set(bssid, 'encryption_method', 'WPA1')
                else:
                    self.network_all_data['wireless_settings'].set(bssid, 'encryption_method', 'WPA2')
            else:
                self.network_all_data['wireless_settings'].remove_option(bssid, 'encryption')
                self.network_all_data['wireless_settings'].remove_option(bssid, 'enctype')
                self.network_all_data['wireless_settings'].remove_option(bssid, 'encryption_method')
                self.network_all_data['wireless_settings'].remove_option(bssid, 'key')

            self.save_and_apply(iname, iname_previous)
        else:
            cbox_cidx = self.cbox_net_intf.currentIndex()
            itype = self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_TYPE_USER_ROLE)
            iname = self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_NAME_USER_ROLE)

            if itype != INTERFACE_TYPE_WIRELESS:
                return

            self.update_gui(WORKING_STATE_CONNECT)

            essid = parameters['essid']
            bssid = parameters['bssid']
            encryption_method = parameters['encryption_method']
            key = parameters['key']
            address_conf_type = parameters['address_conf_type']
            ip = parameters['ip']
            netmask = parameters['netmask']
            ip_gw = parameters['gw']
            ip_dns = parameters['dns']

            cidr = 0
            ip_method = 'auto'
            connection_config_dict = None

            if address_conf_type == CBOX_NET_CONTYPE_INDEX_STATIC:
                ip_method = 'manual'
                cidr = self.netmask_to_cidr(netmask)
            else:
                ip = '0'
                ip_dns = '0'
                ip_gw = '0'
                cidr = 0

            connection_config_dict = CONNECTION_CONFIG_WIFI_DICT

            connection_config_dict['connection']['interface-name'] = iname
            connection_config_dict['802-11-wireless']['ssid'] = essid
            connection_config_dict['802-11-wireless']['bssid'] = bssid
            connection_config_dict['802-11-wireless']['hidden'] = True
            connection_config_dict['ipv4']['method'] = ip_method
            connection_config_dict['ipv4']['dns'] = ip_dns
            connection_config_dict['ipv4']['address-data'] = {'address': ip, 'prefix': cidr}
            connection_config_dict['ipv4']['gateway'] = ip_gw

            if '802-11-wireless-security' in connection_config_dict:
                del connection_config_dict['802-11-wireless-security']

            if encryption_method > 0:
                connection_config_dict['802-11-wireless-security'] = {}
                connection_config_dict['802-11-wireless-security']['auth-alg'] = 'open'
                connection_config_dict['802-11-wireless-security']['key-mgmt'] = 'wpa-psk'
                connection_config_dict['802-11-wireless-security']['psk'] = key
                connection_config_dict['802-11-wireless-security']['psk-flags'] = 0

            self.script_manager.execute_script('settings_network_apply_nm',
                                               cb_settings_network_apply_nm,
                                               [json.dumps(connection_config_dict)])

    def update_connect_button_state(self):
        self.pbutton_net_connect.setEnabled(True)

        if self.ap_tree_model.rowCount() < 1:
            return

        ap_status = self.ap_tree_model.item(0).data(AP_STATUS_USER_ROLE)
        itype = self.cbox_net_intf.itemData(self.cbox_net_intf.currentIndex(),
                                            INTERFACE_TYPE_USER_ROLE)

        if itype == INTERFACE_TYPE_WIRELESS and ap_status == AP_STATUS_NONE:
            self.pbutton_net_connect.setEnabled(False)

    def ap_mode_enabled(self):
        self.ap_mode = True
        self.address_configuration_gui(False)
        self.wireless_configuration_gui(False)
        self.label_net_disabled.show()
        self.sarea_net.hide()

    def ap_mode_disabled(self):
        self.ap_mode = False
        self.label_net_disabled.hide()
        self.sarea_net.show()

        if self.image_version_lt_1_10:
            self.manager_settings_conf_rfile = REDFile(self.session)
            self.wired_settings_conf_rfile = REDFile(self.session)
            self.wireless_settings_conf_rfile = REDFile(self.session)

        if not self.network_stat_work_in_progress:
            self.cb_network_stat_refresh()
        if not self.work_in_progress:
            self.slot_network_conf_refresh_clicked()

    def ap_tree_model_clear_add_item(self, item):
        self.ap_tree_model.removeRows(0, self.ap_tree_model.rowCount())

        if not item:
            return

        list_items = [item]

        for i in range(self.ap_tree_model.columnCount() - 1):
            _item = QtGui.QStandardItem('')
            _item.setEnabled(False)
            _item.setSelectable(False)
            list_items.append(_item)

        self.ap_tree_model.appendRow(list_items)

    def cb_settings_network_status(self, result):
        self.network_stat_refresh_timer.stop()
        self.network_stat_work_in_progress = False

        # check if the tab is still on view or not
        if not self.is_tab_on_focus and self.ap_mode:
            return

        if result and result.stdout and not result.stderr and result.exit_code == 0:
            self.network_all_data['status'] = json.loads(result.stdout)

            # Populating the current network status section and hostname
            if self.is_connecting:
                self.label_net_gen_cstat_status.setText(unicode('Connecting'))
                self.label_net_gen_cstat_intf.setText('-')
                self.label_net_gen_cstat_ip.setText('-')
                self.label_net_gen_cstat_mask.setText('-')
                self.label_net_gen_cstat_gateway.setText('-')
                self.label_net_gen_cstat_dns.setText('-')
            elif self.network_all_data['status'] is not None:
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
                self.label_net_hostname.setText('-')
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

            if self.image_version_lt_1_10:
                self.script_manager.execute_script('settings_network_status',
                                                   self.cb_settings_network_status)
            else:
                self.script_manager.execute_script('settings_network_status_nm',
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
            self.label_dot_1.show()
            self.label_dot_2.show()
            self.label_dot_3.show()
            self.label_dot_4.show()
            self.label_dot_5.show()
            self.label_dot_6.show()
            self.label_dot_7.show()
            self.label_dot_8.show()
            self.label_dot_9.show()
            self.label_dot_10.show()
            self.label_dot_11.show()
            self.label_dot_12.show()
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
            self.label_dot_1.hide()
            self.label_dot_2.hide()
            self.label_dot_3.hide()
            self.label_dot_4.hide()
            self.label_dot_5.hide()
            self.label_dot_6.hide()
            self.label_dot_7.hide()
            self.label_dot_8.hide()
            self.label_dot_9.hide()
            self.label_dot_10.hide()
            self.label_dot_11.hide()
            self.label_dot_12.hide()

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
            self.pbutton_net_wireless_connect_hidden.setEnabled(True)
        else:
            self.label_ap.hide()
            self.tree_net_wireless_ap.hide()
            self.widget_scan.hide()
            self.label_key.hide()
            self.ledit_net_wireless_key.hide()
            self.chkbox_net_wireless_key_show.setChecked(False)
            self.chkbox_net_wireless_key_show.hide()
            self.pbutton_net_wireless_connect_hidden.setEnabled(False)

    def update_gui(self, state):
        def show_work_in_progress():
            self.widget_working_please_wait.show()
            self.widget_net_config.setEnabled(False)
            self.widget_net_adv_functions.setEnabled(False)

        def hide_work_in_progress():
            self.widget_working_please_wait.hide()
            self.widget_net_config.setEnabled(True)
            self.widget_net_adv_functions.setEnabled(True)

        if state == WORKING_STATE_REFRESH:
            self.work_in_progress = True
            show_work_in_progress()
            self.pbutton_net_conf_refresh.setText('Refreshing...')

        elif state == WORKING_STATE_SCAN:
            self.work_in_progress = True
            item = QtGui.QStandardItem('Scanning...')
            item.setData(AP_STATUS_NONE, AP_STATUS_USER_ROLE)
            self.ap_tree_model_clear_add_item(item)
            self.ledit_net_wireless_key.setText('')
            self.cbox_net_conftype.setCurrentIndex(0)
            self.pbutton_net_wireless_scan.setText('Scanning...')
            show_work_in_progress()

        elif state == WORKING_STATE_CONNECT:
            self.work_in_progress = True
            show_work_in_progress()
            self.pbutton_net_connect.setText('Connecting...')

        elif state == WORKING_STATE_CHANGE_HOSTNAME:
            self.work_in_progress = True
            show_work_in_progress()
            self.pbutton_net_conf_change_hostname.setText('Changing Hostname...')

        elif state == WORKING_STATE_DONE:
            self.work_in_progress = False
            hide_work_in_progress()
            self.pbutton_net_conf_change_hostname.setText('Change Hostname')
            self.pbutton_net_conf_refresh.setText('Refresh')
            self.pbutton_net_connect.setText('Connect')
            self.pbutton_net_wireless_scan.setText('Scan')

    def ap_found(self):
        self.label_key.show()
        self.ledit_net_wireless_key.show()
        self.chkbox_net_wireless_key_show.setChecked(False)
        self.chkbox_net_wireless_key_show.show()
        self.address_configuration_gui(True)
        self.chkbox_net_wireless_key_show.setChecked(False)

    def no_ap_found(self):
        self.label_key.hide()
        self.ledit_net_wireless_key.setText('')
        self.ledit_net_wireless_key.hide()
        self.chkbox_net_wireless_key_show.setChecked(False)
        self.chkbox_net_wireless_key_show.hide()
        self.cbox_net_conftype.setCurrentIndex(0)
        self.address_configuration_gui(False)

        self.ap_tree_model_clear_add_item(None)
        item = QtGui.QStandardItem('No access points found. Scan again?')
        item.setData(AP_COL, AP_COL_USER_ROLE)
        item.setData(AP_STATUS_NONE, AP_STATUS_USER_ROLE)
        item.setEnabled(False)
        item.setSelectable(False)
        self.ap_tree_model_clear_add_item(item)

    def update_access_points(self, scan_data):
        if scan_data and \
           self.network_all_data['interfaces']['wireless'] and \
           self.network_all_data['interfaces']['wireless_links']:

            if len(scan_data) <= 0 or \
               len(self.network_all_data['interfaces']['wireless']) <= 0:
                self.no_ap_found()
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
                quality = unicode(apdict['quality'])

                ap_item = QtGui.QStandardItem(essid)
                ap_item.setData(AP_COL, AP_COL_USER_ROLE)
                ap_item.setData(encryption, AP_ENCRYPTION_USER_ROLE)
                ap_item.setData(essid, AP_NAME_USER_ROLE)
                ap_item.setData(bssid, AP_BSSID_USER_ROLE)
                ap_item.setData(nidx, AP_NETWORK_INDEX_USER_ROLE)
                ap_item.setData(channel, AP_CHANNEL_USER_ROLE)

                if str(quality) == '':
                    quality = '0'
                    ap_item.setData(0, AP_QUALITY_USER_ROLE)
                else:
                    ap_item.setData(int(quality), AP_QUALITY_USER_ROLE)

                channel_item = QtGui.QStandardItem(channel)

                if encryption == 'Off':
                    encryption_method_item = QtGui.QStandardItem('Open')
                else:
                    if encryption_method == 'WPA1':
                        encryption_method_item = QtGui.QStandardItem('WPA1')
                        ap_item.setData(AP_ENC_METHOD_WPA1,
                                        AP_ENCRYPTION_METHOD_USER_ROLE)
                    elif encryption_method == 'WPA2':
                        encryption_method_item = QtGui.QStandardItem('WPA2')
                        ap_item.setData(AP_ENC_METHOD_WPA2,
                                        AP_ENCRYPTION_METHOD_USER_ROLE)
                    else:
                        encryption_method_item = QtGui.QStandardItem('Unsupported')
                        ap_item.setData(AP_ENC_METHOD_UNSUPPORTED,
                                        AP_ENCRYPTION_METHOD_USER_ROLE)

                if self.image_version_lt_1_10:
                    try:
                        _key = self.network_all_data['wireless_settings'].get(bssid, 'key', '')
                        ap_item.setData(unicode(_key), AP_KEY_USER_ROLE)
                    except:
                        ap_item.setData('', AP_KEY_USER_ROLE)
                else:
                    try:
                        if essid == self.network_all_data['wireless_settings'].get('wifi', 'ssid', ''):
                            _key = self.network_all_data['wireless_settings'].get('wifi-security', 'psk', '')
                        else:
                            _key= ''
                        ap_item.setData(unicode(_key), AP_KEY_USER_ROLE)
                    except:
                        ap_item.setData('', AP_KEY_USER_ROLE)

                # Checking if the access point is associated
                ap_item.setData(AP_STATUS_NOT_ASSOCIATED, AP_STATUS_USER_ROLE)
                for key, value in self.network_all_data['interfaces']['wireless_links'].iteritems():
                    if (unicode(value['bssid']) == unicode(bssid)) and value['status']:
                        ap_item.setData(AP_STATUS_ASSOCIATED, AP_STATUS_USER_ROLE)
                        break

                if self.image_version_lt_1_10:
                    try:
                        _ip = self.network_all_data['wireless_settings'].get(bssid, 'ip', '')
                        if _ip == '' or _ip == 'None':
                            ap_item.setData(CBOX_NET_CONTYPE_INDEX_DHCP,
                                            AP_ADDRESS_CONF_USER_ROLE)
                            ap_item.setData('0.0.0.0', AP_IP_USER_ROLE)
                        else:
                            ap_item.setData(CBOX_NET_CONTYPE_INDEX_STATIC,
                                            AP_ADDRESS_CONF_USER_ROLE)
                            ap_item.setData(_ip, AP_IP_USER_ROLE)
                    except:
                        ap_item.setData(CBOX_NET_CONTYPE_INDEX_DHCP,
                                        AP_ADDRESS_CONF_USER_ROLE)
                        ap_item.setData('0.0.0.0', AP_IP_USER_ROLE)

                    try:
                        _mask = self.network_all_data['wireless_settings'].get(bssid, 'netmask', '')
                        if _mask == '' or _ip == 'None':
                            ap_item.setData('0.0.0.0', AP_MASK_USER_ROLE)
                        else:
                            ap_item.setData(_mask, AP_MASK_USER_ROLE)
                    except:
                        ap_item.setData('0.0.0.0', AP_MASK_USER_ROLE)

                    try:
                        _gw = self.network_all_data['wireless_settings'].get(bssid, 'gateway', '')
                        if _gw == '' or _gw == 'None':
                            ap_item.setData('0.0.0.0', AP_GATEWAY_USER_ROLE)
                        else:
                            ap_item.setData(_gw, AP_GATEWAY_USER_ROLE)
                    except:
                        ap_item.setData('0.0.0.0', AP_GATEWAY_USER_ROLE)

                    try:
                        _dns = self.network_all_data['wireless_settings'].get(bssid, 'dns1', '')
                        if _dns == '' or _dns == 'None':
                            ap_item.setData('0.0.0.0', AP_DNS_USER_ROLE)
                        else:
                            ap_item.setData(_dns, AP_DNS_USER_ROLE)
                    except:
                        ap_item.setData('0.0.0.0', AP_DNS_USER_ROLE)
                else:
                    try:
                        if essid and \
                           essid != self.network_all_data['wireless_settings'].get('wifi', 'ssid', ''):
                                ap_item.setData(CBOX_NET_CONTYPE_INDEX_DHCP,
                                                AP_ADDRESS_CONF_USER_ROLE)
                                ap_item.setData('0.0.0.0', AP_IP_USER_ROLE)
                                ap_item.setData('0.0.0.0', AP_MASK_USER_ROLE)
                                ap_item.setData('0.0.0.0', AP_GATEWAY_USER_ROLE)
                                ap_item.setData('0.0.0.0', AP_DNS_USER_ROLE)
                        else:
                            _ip = None
                            _gw = None
                            _dns = None
                            _mask = None
                            _method = self.network_all_data['wireless_settings'].get('ipv4', 'method', '')
                            if _method == '' or _method == 'None':
                                ap_item.setData(CBOX_NET_CONTYPE_INDEX_DHCP,
                                                AP_ADDRESS_CONF_USER_ROLE)
                                ap_item.setData('0.0.0.0', AP_IP_USER_ROLE)
                                ap_item.setData('0.0.0.0', AP_MASK_USER_ROLE)
                                ap_item.setData('0.0.0.0', AP_GATEWAY_USER_ROLE)
                                ap_item.setData('0.0.0.0', AP_DNS_USER_ROLE)
                            elif _method == 'manual':
                                _cidr = ''
                                _address1 = self.network_all_data['wireless_settings'].get('ipv4', 'address1', '')
                                _ip, _cidr = _address1.split(',')[0].split('/')
                                _mask = self.cidr_to_netmask(_cidr)
                                _gw = _address1.split(',')[1]
                                _dns = self.network_all_data['wireless_settings'].get('ipv4', 'dns', '').split(';')[0]
                                if not _ip or not _gw or not _mask or not _dns:
                                    ap_item.setData(CBOX_NET_CONTYPE_INDEX_DHCP,
                                                    AP_ADDRESS_CONF_USER_ROLE)
                                    ap_item.setData('0.0.0.0', AP_IP_USER_ROLE)
                                    ap_item.setData('0.0.0.0', AP_MASK_USER_ROLE)
                                    ap_item.setData('0.0.0.0', AP_GATEWAY_USER_ROLE)
                                    ap_item.setData('0.0.0.0', AP_DNS_USER_ROLE)
                                else:
                                    ap_item.setData(CBOX_NET_CONTYPE_INDEX_STATIC,
                                                    AP_ADDRESS_CONF_USER_ROLE)
                                    ap_item.setData(_ip, AP_IP_USER_ROLE)
                                    ap_item.setData(_mask, AP_MASK_USER_ROLE)
                                    ap_item.setData(_gw, AP_GATEWAY_USER_ROLE)
                                    ap_item.setData(_dns, AP_DNS_USER_ROLE)
                            else:
                                ap_item.setData(CBOX_NET_CONTYPE_INDEX_DHCP,
                                                AP_ADDRESS_CONF_USER_ROLE)
                                ap_item.setData('0.0.0.0', AP_IP_USER_ROLE)
                                ap_item.setData('0.0.0.0', AP_MASK_USER_ROLE)
                                ap_item.setData('0.0.0.0', AP_GATEWAY_USER_ROLE)
                                ap_item.setData('0.0.0.0', AP_DNS_USER_ROLE)
                    except:
                        ap_item.setData(CBOX_NET_CONTYPE_INDEX_DHCP,
                                        AP_ADDRESS_CONF_USER_ROLE)
                        ap_item.setData('0.0.0.0', AP_IP_USER_ROLE)
                        ap_item.setData('0.0.0.0', AP_MASK_USER_ROLE)
                        ap_item.setData('0.0.0.0', AP_GATEWAY_USER_ROLE)
                        ap_item.setData('0.0.0.0', AP_DNS_USER_ROLE)

                quality_item = QtGui.QStandardItem(quality+'%')

                self.ap_tree_model.appendRow([ap_item, channel_item, encryption_method_item, quality_item])

                self.ap_tree_model.setSortRole(AP_QUALITY_USER_ROLE)
                self.ap_tree_model.sort(0, QtCore.Qt.DescendingOrder)

            if self.ap_tree_model.rowCount() <= 0:
                self.no_ap_found()
                return

            self.ap_found()

            self.tree_net_wireless_ap.setCurrentIndex(self.ap_tree_model.index(-1, -1))
            self.tree_net_wireless_ap.setCurrentIndex(self.ap_tree_model.index(0, 0))
        else:
            self.no_ap_found()

    def update_network_gui(self):
        def update_no_interface_available():
            self.cbox_net_intf.clear()
            self.cbox_net_intf.addItem('No interfaces available')
            self.pbutton_net_connect.setEnabled(False)
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
                                                           unicode(intf), INTERFACE_NAME_USER_ROLE)

                            self.cbox_net_intf.setItemData(self.cbox_net_intf.count() - 1,
                                                           INTERFACE_TYPE_WIRELESS, INTERFACE_TYPE_USER_ROLE)

                            if intf == self.network_all_data['status']['cstat_intf_active']['name']:
                                self.cbox_net_intf.setItemData(self.cbox_net_intf.count() - 1,
                                                               INTERFACE_STATE_ACTIVE,
                                                               INTERFACE_STATE_USER_ROLE)
                            else:
                                self.cbox_net_intf.setItemData(self.cbox_net_intf.count() - 1,
                                                               INTERFACE_STATE_INACTIVE,
                                                               INTERFACE_STATE_USER_ROLE)

                # Processing wired interfaces
                if self.network_all_data['interfaces']['wired'] is not None and\
                   len(self.network_all_data['interfaces']['wired']) > 0:
                        if self.image_version_lt_1_10:
                            try:
                                cwintf = unicode(self.network_all_data['manager_settings'].get('Settings', 'wired_interface', 'None'))
                            except:
                                cwintf = 'None'
                        else:
                            if self.network_all_data['wired_settings']:
                                try:
                                    cwintf = unicode(self.network_all_data['wired_settings'].get('connection', 'interface-name', 'None'))
                                except:
                                    cwintf = 'None'
                            else:
                                cwintf = 'None'

                        for intf in self.network_all_data['interfaces']['wired']:
                            self.cbox_net_intf.addItem(intf+' : Wired')

                            idx_cbox = self.cbox_net_intf.count() - 1

                            if intf == self.network_all_data['status']['cstat_intf_active']['name']:
                                self.cbox_net_intf.setItemData(idx_cbox, INTERFACE_STATE_ACTIVE,
                                                               INTERFACE_STATE_USER_ROLE)
                            else:
                                self.cbox_net_intf.setItemData(idx_cbox, INTERFACE_STATE_INACTIVE,
                                                               INTERFACE_STATE_USER_ROLE)

                            self.cbox_net_intf.setItemData(self.cbox_net_intf.count() - 1, unicode(intf), INTERFACE_NAME_USER_ROLE)

                            self.cbox_net_intf.setItemData(idx_cbox, INTERFACE_TYPE_WIRED, INTERFACE_TYPE_USER_ROLE)

                            # Populating wired interface fields
                            if cwintf == intf:
                                if self.image_version_lt_1_10:
                                    try:
                                        _ip = self.network_all_data['wired_settings'].get('wired-default', 'ip', 'None')
                                    except:
                                        _ip = 'None'
                                else:
                                    try:
                                        _ip = 'None'
                                        _mask = 'None'
                                        _ip_address = 'None'
                                        _method = self.network_all_data['wired_settings'].get('ipv4', 'method', 'None')
                                        if _method == 'None':
                                            _ip = 'None'
                                            _mask = 'None'
                                        elif _method == 'manual':
                                            _cidr = None
                                            _ip_address = self.network_all_data['wired_settings'].get('ipv4', 'address1', 'None')
                                            _ip_address_split = _ip_address.split(',')
                                            _ip, _cidr = _ip_address_split[0].split('/')
                                            if _ip == 'None' or not _cidr:
                                                _ip = 'None'
                                                _mask = 'None'
                                            else:
                                                _mask = self.cidr_to_netmask(_cidr)
                                        else:
                                            _ip = 'None'
                                            _mask = 'None'
                                    except:
                                        _ip = 'None'
                                        _mask = 'None'
                                if _ip == 'None':
                                    self.cbox_net_intf.setItemData(idx_cbox, CBOX_NET_CONTYPE_INDEX_DHCP,
                                                                   INTERFACE_TYPE_WIRED_ADDRESS_CONF_USER_ROLE)
                                    self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                                   INTERFACE_TYPE_WIRED_IP_USER_ROLE)
                                    self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                                   INTERFACE_TYPE_WIRED_MASK_USER_ROLE)
                                    self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                                   INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE)
                                    self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                                   INTERFACE_TYPE_WIRED_DNS_USER_ROLE)
                                else:
                                    self.cbox_net_intf.setItemData(idx_cbox, CBOX_NET_CONTYPE_INDEX_STATIC,
                                                                   INTERFACE_TYPE_WIRED_ADDRESS_CONF_USER_ROLE)
                                    self.cbox_net_intf.setItemData(idx_cbox, _ip,
                                                                   INTERFACE_TYPE_WIRED_IP_USER_ROLE)

                                    if self.image_version_lt_1_10:
                                        try:
                                            _mask = self.network_all_data['wired_settings'].get('wired-default', 'netmask', '')
                                            if _mask == '' or _mask == 'None':
                                                self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                                               INTERFACE_TYPE_WIRED_MASK_USER_ROLE)
                                            else:
                                                self.cbox_net_intf.setItemData(idx_cbox, _mask,
                                                                               INTERFACE_TYPE_WIRED_MASK_USER_ROLE)
                                        except:
                                            self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                                           INTERFACE_TYPE_WIRED_MASK_USER_ROLE)

                                        try:
                                            _gw = self.network_all_data['wired_settings'].get('wired-default', 'gateway', '')
                                            if _gw == '' or _gw == 'None':
                                                self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                                               INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE)
                                            else:
                                                self.cbox_net_intf.setItemData(idx_cbox, _gw,
                                                                               INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE)
                                        except:
                                            self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                                           INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE)

                                        try:
                                            _dns = self.network_all_data['wired_settings'].get('wired-default', 'dns1', '')
                                            if _dns == '' or _dns == 'None':
                                                self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                                               INTERFACE_TYPE_WIRED_DNS_USER_ROLE)
                                            else:
                                                self.cbox_net_intf.setItemData(idx_cbox, _dns,
                                                                               INTERFACE_TYPE_WIRED_DNS_USER_ROLE)
                                        except:
                                            self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                                           INTERFACE_TYPE_WIRED_DNS_USER_ROLE)
                                    else:
                                        if _mask == '' or _mask == 'None':
                                            self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                                           INTERFACE_TYPE_WIRED_MASK_USER_ROLE)
                                        else:
                                            self.cbox_net_intf.setItemData(idx_cbox, _mask,
                                                                           INTERFACE_TYPE_WIRED_MASK_USER_ROLE)

                                        try:
                                            _ip_address = self.network_all_data['wired_settings'].get('ipv4', 'address1', 'None')
                                            _ip_address_split = _ip_address.split(',')
                                            if len(_ip_address_split) < 2:
                                                _gw == 'None'
                                            else:
                                                _gw = _ip_address_split[1]
                                            if _gw == '' or _gw == 'None':
                                                self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                                               INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE)
                                            else:
                                                self.cbox_net_intf.setItemData(idx_cbox, _gw,
                                                                               INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE)
                                        except:
                                            self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                                           INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE)

                                        try:
                                            _dns = self.network_all_data['wired_settings'].get('ipv4', 'dns', '')
                                            if _dns == '' or _dns == 'None':
                                                self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                                               INTERFACE_TYPE_WIRED_DNS_USER_ROLE)
                                            else:
                                                _dns_split = _dns.split(';')
                                                self.cbox_net_intf.setItemData(idx_cbox, _dns_split[0],
                                                                               INTERFACE_TYPE_WIRED_DNS_USER_ROLE)
                                        except:
                                            self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                                           INTERFACE_TYPE_WIRED_DNS_USER_ROLE)
                            else:
                                self.cbox_net_intf.setItemData(idx_cbox, CBOX_NET_CONTYPE_INDEX_DHCP,
                                                               INTERFACE_TYPE_WIRED_ADDRESS_CONF_USER_ROLE)
                                self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                               INTERFACE_TYPE_WIRED_IP_USER_ROLE)
                                self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                               INTERFACE_TYPE_WIRED_MASK_USER_ROLE)
                                self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                               INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE)
                                self.cbox_net_intf.setItemData(idx_cbox, '0.0.0.0',
                                                               INTERFACE_TYPE_WIRED_DNS_USER_ROLE)

                if self.cbox_net_intf.count() <= 0:
                    update_no_interface_available()
                    return
                else:
                    # Select first active interface by default if not then the first item
                    self.cbox_net_intf.setCurrentIndex(-1)
                    self.pbutton_net_connect.setEnabled(True)
                    for i in range(self.cbox_net_intf.count()):
                        istate = self.cbox_net_intf.itemData(i, INTERFACE_STATE_USER_ROLE)
                        if istate == INTERFACE_STATE_ACTIVE:
                            self.cbox_net_intf.setCurrentIndex(i)
                            iname = self.cbox_net_intf.itemData(i, INTERFACE_NAME_USER_ROLE)
                            itype = self.cbox_net_intf.itemData(i, INTERFACE_TYPE_USER_ROLE)
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

    def slot_pbutton_net_wireless_scan_clicked(self):
        cbox_cidx = self.cbox_net_intf.currentIndex()
        interface_name = self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_NAME_USER_ROLE)
        interface_type = self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_TYPE_USER_ROLE)

        if interface_type == INTERFACE_TYPE_WIRELESS:
            def cb_settings_network_wireless_scan(result):
                self.update_gui(WORKING_STATE_DONE)
                if not self.is_tab_on_focus:
                    return
                if result and result.stdout and not result.stderr and result.exit_code == 0:
                    self.network_all_data['scan_result'] = json.loads(result.stdout)
                    self.update_access_points(self.network_all_data['scan_result'])
                    QtGui.QMessageBox.information(get_main_window(),
                                                  'Settings | Network',
                                                  'Scan finished')
                else:
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               'Wireless scan failed:\n\n' + result.stderr)
                self.update_connect_button_state()

            if self.image_version_lt_1_10:
                try:
                    # Saving currently configured wireless interface
                    wlintf_restore_to = unicode(self.network_all_data['manager_settings'].get('Settings', 'wireless_interface', ''))
                except Exception as e:
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               'Wireless scan failed:\n\n{0}'.format(e))
                    return

            self.update_gui(WORKING_STATE_SCAN)

            if self.image_version_lt_1_10:
                self.script_manager.execute_script('settings_network_wireless_scan',
                                                   cb_settings_network_wireless_scan,
                                                   [interface_name, wlintf_restore_to])
            else:
                self.script_manager.execute_script('settings_network_wireless_scan_nm',
                                                   cb_settings_network_wireless_scan)

        else:
            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Network',
                                       'Scan only possible for wireless interfaces.')

    def slot_network_conf_refresh_clicked(self):
        def network_refresh_task_done(successful):
            self.network_refresh_tasks_remaining -= 1

            self.update_connect_button_state()

            if not successful:
                self.update_gui(WORKING_STATE_DONE)

                self.network_refresh_tasks_error_occured = True
            elif self.network_refresh_tasks_remaining == 0:
                self.update_gui(WORKING_STATE_DONE)

                if not self.network_refresh_tasks_error_occured:
                    self.update_network_gui()

        def cb_settings_network_status(result):
            if not self.is_tab_on_focus:
                self.update_gui(WORKING_STATE_DONE)
                return

            if self.network_refresh_tasks_error_occured:
                return

            if result and result.stdout and not result.stderr and result.exit_code == 0:
                self.network_all_data['status'] = json.loads(result.stdout)

                network_refresh_task_done(True)
            else:
                network_refresh_task_done(False)

                if result and result.stderr:
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               'Error executing network status script:\n\n' + result.stderr)

        def cb_settings_network_get_interfaces(result):
            if not self.is_tab_on_focus:
                self.update_gui(WORKING_STATE_DONE)
                return

            if self.network_refresh_tasks_error_occured:
                return

            if result and result.stdout and not result.stderr and result.exit_code == 0:
                self.network_all_data['interfaces'] = json.loads(result.stdout)

                if self.image_version_lt_1_10:
                    self.update_gui(WORKING_STATE_SCAN)

                    self.script_manager.execute_script('settings_network_wireless_scan_cache',
                                                       cb_settings_network_wireless_scan_cache)

                    network_refresh_task_done(True)
                else:
                    self.script_manager.execute_script('settings_network_wireless_scan_nm',
                                                       cb_settings_network_wireless_scan_cache)
                    network_refresh_task_done(True)

            else:
                network_refresh_task_done(False)

                if result and result.stderr:
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               'Error executing network get interfaces script:\n\n' + result.stderr)

        def cb_settings_network_wireless_scan_cache(result):
            if not self.is_tab_on_focus:
                self.update_gui(WORKING_STATE_DONE)
                return

            if self.network_refresh_tasks_error_occured:
                return

            if result and result.stdout and not result.stderr and result.exit_code == 0:
                self.network_all_data['scan_result_cache'] = json.loads(result.stdout)
                self.update_access_points(self.network_all_data['scan_result_cache'])

                network_refresh_task_done(True)
            else:
                network_refresh_task_done(False)

                if result and result.stderr:
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Network',
                                               'Error executing wireless scan cache script:\n\n' + result.stderr)

        def cb_text_file_content(key, content):
            if not self.is_tab_on_focus:
                self.update_gui(WORKING_STATE_DONE)
                return

            if self.network_refresh_tasks_error_occured:
                return

            self.network_all_data[key] = config_parser.parse_no_fake(content)

            network_refresh_task_done(True)

        def cb_text_file_error(title, kind, error):
            if not self.is_tab_on_focus:
                self.update_gui(WORKING_STATE_DONE)
                return

            if self.network_refresh_tasks_error_occured:
                return

            if self.image_version_lt_1_10 or not self.image_version_lt_1_10 and title == 'manager settings':
                network_refresh_task_done(False)

                kind_text = {
                    TextFile.ERROR_KIND_OPEN: 'opening',
                    TextFile.ERROR_KIND_READ: 'reading',
                    TextFile.ERROR_KIND_UTF8: 'decoding'
                }

                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Network',
                                           'Error {0} {1} file:\n\n{2}'.format(kind_text[kind], title, unicode(error)))
            else:
                network_refresh_task_done(True)

        self.update_gui(WORKING_STATE_REFRESH)

        self.network_refresh_tasks_remaining = 6

        self.network_refresh_tasks_error_occured = False

        if self.image_version_lt_1_10:
            self.script_manager.execute_script('settings_network_status',
                                               cb_settings_network_status)
        else:
            self.script_manager.execute_script('settings_network_status_nm',
                                               cb_settings_network_status)

        self.script_manager.execute_script('settings_network_get_interfaces',
                                           cb_settings_network_get_interfaces)

        if self.image_version_lt_1_10:
            TextFile.read_async(self.session,
                                MANAGER_SETTINGS_CONF_PATH,
                                lambda content: cb_text_file_content('manager_settings', content),
                                lambda kind, error: cb_text_file_error('manager settings', kind, error))

            TextFile.read_async(self.session,
                                WIRELESS_SETTINGS_CONF_PATH,
                                lambda content: cb_text_file_content('wireless_settings', content),
                                lambda kind, error: cb_text_file_error('wireless settings', kind, error))

            TextFile.read_async(self.session,
                                WIRED_SETTINGS_CONF_PATH,
                                lambda content: cb_text_file_content('wired_settings', content),
                                lambda kind, error: cb_text_file_error('wired settings', kind, error))
        else:
            TextFile.read_async(self.session,
                                MANAGER_SETTINGS_CONF_PATH_NM,
                                lambda content: cb_text_file_content('manager_settings', content),
                                lambda kind, error: cb_text_file_error('manager settings', kind, error))

            TextFile.read_async(self.session,
                                WIRELESS_SETTINGS_CONF_PATH_NM,
                                lambda content: cb_text_file_content('wireless_settings', content),
                                lambda kind, error: cb_text_file_error('wireless settings', kind, error))

            TextFile.read_async(self.session,
                                WIRED_SETTINGS_CONF_PATH_NM,
                                lambda content: cb_text_file_content('wired_settings', content),
                                lambda kind, error: cb_text_file_error('wired settings', kind, error))

    def check_get_ap_item(self):
        ap_item = None
        item = self.ap_tree_model.itemFromIndex(self.tree_net_wireless_ap.selectedIndexes()[0])
        ap_col = item.data(AP_COL_USER_ROLE)

        if ap_col == AP_COL:
            ap_item = item

        if ap_item:
            apname = ap_item.data(AP_NAME_USER_ROLE)
            enc_method = ap_item.data(AP_ENCRYPTION_METHOD_USER_ROLE)
            enc = ap_item.data(AP_ENCRYPTION_USER_ROLE)
            key = self.ledit_net_wireless_key.text()

        if not apname:
            self.update_gui(WORKING_STATE_DONE)
            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Network',
                                       'Configure an access point first.')
            return False, None
        elif enc_method == AP_ENC_METHOD_UNSUPPORTED:
            self.update_gui(WORKING_STATE_DONE)
            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Network',
                                       'Encryption method not supported.')
            return False, None
        elif enc == 'On' and not key:
            self.update_gui(WORKING_STATE_DONE)
            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Network',
                                       'Please provide WPA key.')
            return False, None

        return True, ap_item

    def get_static_ip_info(self):
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

        return ip, mask, gw, dns

    def slot_network_connect_clicked(self):
        def cb_settings_network_apply_nm(result):
            self.is_connecting = False
            self.update_gui(WORKING_STATE_DONE)
            if result and result.stderr == '' and result.exit_code == 0:
                QtGui.QMessageBox.information(get_main_window(),
                                              'Settings | Network',
                                              'Configuration saved.')
                self.slot_network_conf_refresh_clicked()
            else:
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Network',
                                           'Error saving configuration:\n\n' + result.stderr)

        cbox_cidx = self.cbox_net_intf.currentIndex()
        iname = self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_NAME_USER_ROLE)
        itype = self.cbox_net_intf.itemData(cbox_cidx, INTERFACE_TYPE_USER_ROLE)

        if self.image_version_lt_1_10:
            # Set all existing config file AP 'automatic' parameter to be false
            sections = self.network_all_data['wireless_settings'].sections()

            for s in sections:
                self.network_all_data['wireless_settings'].set(s, 'automatic', 'False')

            self.network_all_data['wired_settings'].set('wired-default', 'default', 'False')

            # Wireless
            if itype == INTERFACE_TYPE_WIRELESS:
                self.update_gui(WORKING_STATE_CONNECT)

                r = False
                enc = None
                key = None
                ap_item = None
                enc_method = None
                address_conf = None

                r, ap_item = self.check_get_ap_item()

                if not r or not ap_item:
                    return

                essid = ap_item.data(AP_NAME_USER_ROLE)
                bssid = ap_item.data(AP_BSSID_USER_ROLE)
                key = self.ledit_net_wireless_key.text()
                enc = ap_item.data(AP_ENCRYPTION_USER_ROLE)
                address_conf = self.cbox_net_conftype.currentIndex()
                enc_method = ap_item.data(AP_ENCRYPTION_METHOD_USER_ROLE)

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
                    ip, mask, gw, dns = self.get_static_ip_info()

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
            # Wired
            else:
                iname_previous = self.network_all_data['manager_settings'].get('Settings', 'wired_interface', '')

                # Check default wired profile section
                if not self.network_all_data['wired_settings'].has_section('wired-default'):
                    self.network_all_data['wired_settings'].add_section('wired-default')

                if self.cbox_net_conftype.currentIndex() == CBOX_NET_CONTYPE_INDEX_DHCP:
                    # Save wired DHCP config
                    self.update_gui(WORKING_STATE_CONNECT)
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
                        self.update_gui(WORKING_STATE_DONE)
                        QtGui.QMessageBox.critical(get_main_window(),
                                                   'Settings | Network',
                                                   'Error saving configuration.')
                        return
                else:
                    # Save wired static config
                    self.update_gui(WORKING_STATE_CONNECT)
                    try:
                        self.network_all_data['manager_settings'].set('Settings', 'wired_interface', iname)
                        ip, mask, gw, dns = self.get_static_ip_info()

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
                        self.update_gui(WORKING_STATE_DONE)
                        QtGui.QMessageBox.critical(get_main_window(),
                                                   'Settings | Network',
                                                   'Error saving configuration.')
                        return

            self.save_and_apply(iname, iname_previous)
        else:
            self.update_gui(WORKING_STATE_CONNECT)

            ip = ''
            cidr = 0
            ip_gw = ''
            ip_dns = ''
            ip_method = 'auto'
            connection_config_dict = None
            address_conf = self.cbox_net_conftype.currentIndex()

            if address_conf != CBOX_NET_CONTYPE_INDEX_DHCP:
                ip_method = 'manual'
                ip, mask, ip_gw, ip_dns = self.get_static_ip_info()
                cidr = self.netmask_to_cidr(mask)

            # Wireless
            if itype == INTERFACE_TYPE_WIRELESS:
                r = False
                enc = None
                key = None
                ap_item = None

                r, ap_item = self.check_get_ap_item()

                if not r or not ap_item:
                    return

                essid = ap_item.data(AP_NAME_USER_ROLE)
                bssid = ap_item.data(AP_BSSID_USER_ROLE)
                key = self.ledit_net_wireless_key.text()
                enc = ap_item.data(AP_ENCRYPTION_USER_ROLE)
                connection_config_dict = CONNECTION_CONFIG_WIFI_DICT

                connection_config_dict['connection']['interface-name'] = iname
                connection_config_dict['802-11-wireless']['ssid'] = essid
                connection_config_dict['802-11-wireless']['bssid'] = bssid
                connection_config_dict['802-11-wireless']['hidden'] = False
                connection_config_dict['ipv4']['method'] = ip_method
                connection_config_dict['ipv4']['dns'] = ip_dns
                connection_config_dict['ipv4']['address-data'] = {'address': ip, 'prefix': cidr}
                connection_config_dict['ipv4']['gateway'] = ip_gw

                if '802-11-wireless-security' in connection_config_dict:
                    del connection_config_dict['802-11-wireless-security']

                if enc == 'On':
                    connection_config_dict['802-11-wireless-security'] = {}
                    connection_config_dict['802-11-wireless-security']['auth-alg'] = 'open'
                    connection_config_dict['802-11-wireless-security']['key-mgmt'] = 'wpa-psk'
                    connection_config_dict['802-11-wireless-security']['psk'] = key
                    connection_config_dict['802-11-wireless-security']['psk-flags'] = 0
            # Wired
            else:
                connection_config_dict = CONNECTION_CONFIG_ETHERNET_DICT

                connection_config_dict['connection']['interface-name'] = iname
                connection_config_dict['ipv4']['method'] = ip_method
                connection_config_dict['ipv4']['dns'] = ip_dns
                connection_config_dict['ipv4']['address-data'] = {'address': ip, 'prefix': cidr}
                connection_config_dict['ipv4']['gateway'] = ip_gw

            self.script_manager.execute_script('settings_network_apply_nm',
                                               cb_settings_network_apply_nm,
                                               [json.dumps(connection_config_dict)])
            self.is_connecting = True

    def slot_change_hostname_clicked(self):
        def cb_settings_network_change_hostname(result):
            self.update_gui(WORKING_STATE_DONE)

            if not self.is_tab_on_focus:
                return

            if result.exit_code != 0:
                err_msg = 'Error occured while changing hostname.'

                if result.stderr:
                    err_msg = err_msg + '\n\n' + unicode(result.stderr)

                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Network',
                                           err_msg)

            self.slot_network_conf_refresh_clicked()

        hostname_old = self.label_net_hostname.text()
        input_dialog_hostname = QtGui.QInputDialog()
        input_dialog_hostname.setInputMode(QtGui.QInputDialog.TextInput)
        hostname_new, ok = input_dialog_hostname.getText(get_main_window(),
                                                     'Change Hostname',
                                                     'Hostname:',
                                                     QtGui.QLineEdit.Normal,
                                                     self.label_net_hostname.text())
        if not ok or not hostname_new:
            return

        if hostname_old == hostname_new:
            return

        # Checking for non ASCII characters
        try:
            hostname_new.encode('ascii')
        except:
            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Network',
                                       'Hostname contains non ASCII characters.')
            return

        # Checking for blank spaces
        if ' ' in hostname_new:
            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Network',
                                       'Hostname contains blank spaces.')
            return

        self.update_gui(WORKING_STATE_CHANGE_HOSTNAME)

        self.script_manager.execute_script('settings_network_change_hostname',
                                           cb_settings_network_change_hostname,
                                           [hostname_old, hostname_new])

    def slot_wireless_connect_hidden_clicked(self):
        parameters = {'bssid': None,
                      'essid': None,
                      'key': None,
                      'address_conf_type': None,
                      'ip': None,
                      'netmask': None,
                      'gw': None,
                      'dns': None,
                      'encryption_method': None}
        qwidget_wireless_connect_hidden = REDTabSettingsNetworkWirelessConnectHidden(self, parameters)
        ret = qwidget_wireless_connect_hidden.exec_()

        if ret == 1:
            self.connect_wireless_hidden(parameters)

    def slot_cbox_net_intf_current_idx_changed(self, idx):
        interface_name = self.cbox_net_intf.itemData(idx, INTERFACE_NAME_USER_ROLE)
        interface_type = self.cbox_net_intf.itemData(idx, INTERFACE_TYPE_USER_ROLE)

        self.update_connect_button_state()

        if interface_type == INTERFACE_TYPE_WIRELESS:
            self.wireless_configuration_gui(True)
            item = self.ap_tree_model.item(0)

            if self.ap_tree_model.rowCount() > 0 \
               and item.data(AP_STATUS_USER_ROLE) != AP_STATUS_NONE:
                    self.ap_found()
                    self.tree_net_wireless_ap.setCurrentIndex(self.ap_tree_model.index(-1, -1))
                    self.tree_net_wireless_ap.setCurrentIndex(self.ap_tree_model.index(0, 0))
            else:
                self.no_ap_found()

        elif interface_type == INTERFACE_TYPE_WIRED:
            self.address_configuration_gui(True)
            self.wireless_configuration_gui(False)

            net_conf_type = self.cbox_net_intf.itemData(idx, INTERFACE_TYPE_WIRED_ADDRESS_CONF_USER_ROLE)

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
                ip_string = self.cbox_net_intf.itemData(idx, INTERFACE_TYPE_WIRED_IP_USER_ROLE)
                ip_array = ip_string.split('.')
                mask_string = self.cbox_net_intf.itemData(idx, INTERFACE_TYPE_WIRED_MASK_USER_ROLE)
                mask_array = mask_string.split('.')
                gw_string = self.cbox_net_intf.itemData(idx, INTERFACE_TYPE_WIRED_GATEWAY_USER_ROLE)
                gw_array = gw_string.split('.')
                dns_string = self.cbox_net_intf.itemData(idx, INTERFACE_TYPE_WIRED_DNS_USER_ROLE)
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
                    enc = item.data(AP_ENCRYPTION_USER_ROLE)
                    if enc == 'On':
                        self.ledit_net_wireless_key.setEnabled(True)
                        ap_key = item.data(AP_KEY_USER_ROLE)
                        self.ledit_net_wireless_key.setText(ap_key)
                    else:
                        self.ledit_net_wireless_key.setText('')
                        self.ledit_net_wireless_key.setEnabled(False)

                    address_conf = item.data(AP_ADDRESS_CONF_USER_ROLE)

                    encryption_method = item.data(AP_ENCRYPTION_METHOD_USER_ROLE)
                    channel           = item.data(AP_CHANNEL_USER_ROLE)
                    encryption        = item.data(AP_ENCRYPTION_USER_ROLE)
                    key               = item.data(AP_KEY_USER_ROLE)
                    ip_string         = item.data(AP_IP_USER_ROLE)
                    mask_string       = item.data(AP_MASK_USER_ROLE)
                    gw_string         = item.data(AP_GATEWAY_USER_ROLE)
                    dns_string        = item.data(AP_DNS_USER_ROLE)
                    ip_array          = ip_string.split('.')
                    mask_array        = mask_string.split('.')
                    gw_array          = gw_string.split('.')
                    dns_array         = dns_string.split('.')

                    if encryption == 'On':
                        if encryption_method == AP_ENC_METHOD_WPA1:
                            self.ledit_net_wireless_key.setEnabled(True)
                            self.ledit_net_wireless_key.setText(key)
                        elif encryption_method == AP_ENC_METHOD_WPA2:
                            self.ledit_net_wireless_key.setEnabled(True)
                            self.ledit_net_wireless_key.setText(key)
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
