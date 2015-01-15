# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

red_tab_settings_ap.py: RED settings access point tab implementation

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
from brickv.plugin_system.plugins.red.ui_red_tab_settings_ap import Ui_REDTabSettingsAP
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red import config_parser
from brickv.async_call import async_call
from brickv.utils import get_main_window

BUTTON_STATE_DEFAULT = 1
BUTTON_STATE_REFRESH = 2
BUTTON_STATE_SAVE    = 3

AP_INTERFACE_IP_USER_ROLE = QtCore.Qt.UserRole + 1
AP_INTERFACE_MASK_USER_ROLE = QtCore.Qt.UserRole + 2

HOSTAPD_CONF_PATH = '/etc/hostapd/hostapd.conf'
DNSMASQ_CONF_PATH = '/etc/dnsmasq.conf'

class REDTabSettingsAP(QtGui.QWidget, Ui_REDTabSettingsAP):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.setupUi(self)

        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings
        self.image_version  = None # Set from REDTabSettings
        self.service_state  = None # Set from REDTabSettings

        self.is_tab_on_focus = False

        self.saving = False
        self.label_ap_unsupported.hide()
        self.label_ap_disabled.hide()
        self.label_working_wait.hide()
        self.pbar_working_wait.hide()
        self.sarea_ap.hide()

        self.cbox_ap_interface.currentIndexChanged.connect(self.slot_cbox_ap_interface_current_index_changed)
        self.chkbox_ap_wpa_key_show.stateChanged.connect(self.slot_chkbox_ap_wpa_key_show_state_changed)
        self.chkbox_ap_enable_dns_dhcp.stateChanged.connect(self.update_ui_state)
        self.pbutton_ap_refresh.clicked.connect(self.slot_pbutton_ap_refresh_clicked)
        self.pbutton_ap_save.clicked.connect(self.slot_pbutton_ap_save_clicked)

    def tab_on_focus(self):
        self.is_tab_on_focus = True

        self.update_ui_state()

        if self.saving:
            return

        if self.image_version.number < (1, 4):
            self.label_ap_unsupported.show()
        elif not self.service_state.ap:
            self.label_ap_disabled.show()
        else:
            self.sarea_ap.show()
            self.slot_pbutton_ap_refresh_clicked()

    def tab_off_focus(self):
        self.is_tab_on_focus = False

    def tab_destroy(self):
        pass

    def update_button_text_state(self, state):
        if state == BUTTON_STATE_DEFAULT:
            self.pbutton_ap_refresh.setEnabled(True)
            self.pbutton_ap_refresh.setText('Refresh')
            self.pbutton_ap_save.setText('Save')

        elif state == BUTTON_STATE_REFRESH:
            self.pbutton_ap_refresh.setText('Refreshing...')
            self.pbutton_ap_refresh.setEnabled(False)
            self.pbutton_ap_save.setText('Save')

        else:
            self.pbutton_ap_refresh.setText('Refresh')
            self.pbutton_ap_save.setText('Saving...')

    def update_ui_state(self):
        has_interface = self.cbox_ap_interface.count() > 0
        dhcp_visible = has_interface and self.chkbox_ap_enable_dns_dhcp.isChecked()

        self.label_interface.setVisible(has_interface)
        self.cbox_ap_interface.setVisible(has_interface)

        self.label_ip.setVisible(has_interface)
        self.sbox_ap_intf_ip1.setVisible(has_interface)
        self.sbox_ap_intf_ip2.setVisible(has_interface)
        self.sbox_ap_intf_ip3.setVisible(has_interface)
        self.sbox_ap_intf_ip4.setVisible(has_interface)

        self.label_subnet_mask.setVisible(has_interface)
        self.sbox_ap_intf_mask1.setVisible(has_interface)
        self.sbox_ap_intf_mask2.setVisible(has_interface)
        self.sbox_ap_intf_mask3.setVisible(has_interface)
        self.sbox_ap_intf_mask4.setVisible(has_interface)

        self.label_ssid.setVisible(has_interface)
        self.ledit_ap_ssid.setVisible(has_interface)
        self.chkbox_ap_ssid_hidden.setVisible(has_interface)

        self.label_wpa_key.setVisible(has_interface)
        self.ledit_ap_wpa_key.setVisible(has_interface)
        self.chkbox_ap_wpa_key_show.setVisible(has_interface)

        self.label_channel.setVisible(has_interface)
        self.sbox_ap_channel.setVisible(has_interface)

        self.line.setVisible(has_interface)
        self.chkbox_ap_enable_dns_dhcp.setVisible(has_interface)

        self.label_ap_server_name.setVisible(dhcp_visible)
        self.ledit_ap_server_name.setVisible(dhcp_visible)
        self.label_ap_domain.setVisible(dhcp_visible)
        self.ledit_ap_domain.setVisible(dhcp_visible)
        self.label_ap_pool_start.setVisible(dhcp_visible)
        self.sbox_ap_pool_start1.setVisible(dhcp_visible)
        self.sbox_ap_pool_start2.setVisible(dhcp_visible)
        self.sbox_ap_pool_start3.setVisible(dhcp_visible)
        self.sbox_ap_pool_start4.setVisible(dhcp_visible)

        self.label_ap_pool_end.setVisible(dhcp_visible)
        self.sbox_ap_pool_end1.setVisible(dhcp_visible)
        self.sbox_ap_pool_end2.setVisible(dhcp_visible)
        self.sbox_ap_pool_end3.setVisible(dhcp_visible)
        self.sbox_ap_pool_end4.setVisible(dhcp_visible)

        self.label_ap_pool_mask.setVisible(dhcp_visible)
        self.sbox_ap_pool_mask1.setVisible(dhcp_visible)
        self.sbox_ap_pool_mask2.setVisible(dhcp_visible)
        self.sbox_ap_pool_mask3.setVisible(dhcp_visible)
        self.sbox_ap_pool_mask4.setVisible(dhcp_visible)

        self.line2.setVisible(has_interface)

    def slot_cbox_ap_interface_current_index_changed(self, index):
        ip = self.cbox_ap_interface.itemData(index, AP_INTERFACE_IP_USER_ROLE).toString()
        mask = self.cbox_ap_interface.itemData(index, AP_INTERFACE_MASK_USER_ROLE).toString()

        if ip and mask:
            ip_list = ip.split('.')
            ip1 = ip_list[0]
            ip2 = ip_list[1]
            ip3 = ip_list[2]
            ip4 = ip_list[3]

            mask_list = mask.split('.')
            mask1 = mask_list[0]
            mask2 = mask_list[1]
            mask3 = mask_list[2]
            mask4 = mask_list[3]

            self.sbox_ap_intf_ip1.setValue(int(ip1))
            self.sbox_ap_intf_ip2.setValue(int(ip2))
            self.sbox_ap_intf_ip3.setValue(int(ip3))
            self.sbox_ap_intf_ip4.setValue(int(ip4))

            self.sbox_ap_intf_mask1.setValue(int(mask1))
            self.sbox_ap_intf_mask2.setValue(int(mask2))
            self.sbox_ap_intf_mask3.setValue(int(mask3))
            self.sbox_ap_intf_mask4.setValue(int(mask4))

    def slot_chkbox_ap_wpa_key_show_state_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.ledit_ap_wpa_key.setEchoMode(QtGui.QLineEdit.Normal)
        else:
            self.ledit_ap_wpa_key.setEchoMode(QtGui.QLineEdit.Password)

    def slot_pbutton_ap_refresh_clicked(self):
        def cb_settings_network_apmode_status(result):
            self.update_button_text_state(BUTTON_STATE_DEFAULT)
            self.label_working_wait.hide()
            self.pbar_working_wait.hide()
            self.sarea_ap.setEnabled(True)

            if not self.is_tab_on_focus:
                return

            if result and not result.stderr and result.exit_code == 0:
                ap_mode_status = json.loads(result.stdout)

                if ap_mode_status is None or \
                   ap_mode_status['ap_first_time'] is None or \
                   ap_mode_status['ap_incomplete_config'] is None or \
                   ap_mode_status['ap_hardware_or_config_problem'] is None:
                    self.label_ap_status.setText('-')
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Access Point',
                                               'Error checking access point mode.',
                                               QtGui.QMessageBox.Ok)
                elif not ap_mode_status['ap_incomplete_config'] and \
                     not ap_mode_status['ap_hardware_or_config_problem']:
                        self.label_ap_status.setText('Active')
                elif ap_mode_status['ap_first_time']:
                    self.label_ap_status.setText('Inactive - Select an interface and click save')
                elif ap_mode_status['ap_incomplete_config']:
                    self.label_ap_status.setText('Inactive - Incomplete configuration, check your configuration and click save')
                elif ap_mode_status['ap_hardware_or_config_problem']:
                    self.label_ap_status.setText('Inactive - Hardware not supported or wrong configuration')

                self.update_ui_state()
                self.read_config_files()
            else:
                self.label_ap_status.setText('-')
                err_msg = 'Error checking access point mode\n\n'+unicode(result.stderr)
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Access Point',
                                           err_msg,
                                           QtGui.QMessageBox.Ok)

        self.update_button_text_state(BUTTON_STATE_REFRESH)
        self.label_working_wait.show()
        self.pbar_working_wait.show()
        self.sarea_ap.setEnabled(False)

        self.script_manager.execute_script('settings_network_apmode_status',
                                           cb_settings_network_apmode_status)

    def slot_pbutton_ap_save_clicked(self):
        def cb_settings_network_apmode_apply(result):
            self.label_working_wait.hide()
            self.pbar_working_wait.hide()
            self.saving = False
            self.sarea_ap.setEnabled(True)
            self.update_button_text_state(BUTTON_STATE_DEFAULT)

            if result and result.exit_code == 0:
                self.slot_pbutton_ap_refresh_clicked()

                QtGui.QMessageBox.information(get_main_window(),
                                              'Settings | Access Point',
                                              'Access point settings saved.',
                                              QtGui.QMessageBox.Ok)
            else:
                err_msg = 'Error saving access point settings.\n\n' + result.stderr
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Access Point',
                                           err_msg,
                                           QtGui.QMessageBox.Ok)

        apply_dict = {'interface'       : None,
                      'interface_ip'    : None,
                      'interface_mask'  : None,
                      'ssid'            : None,
                      'ssid_hidden'     : None,
                      'wpa_key'         : None,
                      'channel'         : None,
                      'enabled_dns_dhcp': None,
                      'server_name'     : None,
                      'domain'          : None,
                      'dhcp_start'      : None,
                      'dhcp_end'        : None,
                      'dhcp_mask'       : None}
        try:
            interface = self.cbox_ap_interface.currentText()
            
            interface_ip_list = []
            interface_ip_list.append(unicode(self.sbox_ap_intf_ip1.value()))
            interface_ip_list.append(unicode(self.sbox_ap_intf_ip2.value()))
            interface_ip_list.append(unicode(self.sbox_ap_intf_ip3.value()))
            interface_ip_list.append(unicode(self.sbox_ap_intf_ip4.value()))
            interface_ip = '.'.join(interface_ip_list)

            interface_mask_list = []
            interface_mask_list.append(unicode(self.sbox_ap_intf_mask1.value()))
            interface_mask_list.append(unicode(self.sbox_ap_intf_mask2.value()))
            interface_mask_list.append(unicode(self.sbox_ap_intf_mask3.value()))
            interface_mask_list.append(unicode(self.sbox_ap_intf_mask4.value()))
            interface_mask = '.'.join(interface_mask_list)

            ssid = self.ledit_ap_ssid.text()
            ssid_hidden = self.chkbox_ap_ssid_hidden.isChecked()
            wpa_key = self.ledit_ap_wpa_key.text()
            channel = unicode(self.sbox_ap_channel.value())
            enabled_dns_dhcp = self.chkbox_ap_enable_dns_dhcp.isChecked()
            server_name = self.ledit_ap_server_name.text()
            domain = self.ledit_ap_domain.text()

            dhcp_start_list = []
            dhcp_start_list.append(unicode(self.sbox_ap_pool_start1.value()))
            dhcp_start_list.append(unicode(self.sbox_ap_pool_start2.value()))
            dhcp_start_list.append(unicode(self.sbox_ap_pool_start3.value()))
            dhcp_start_list.append(unicode(self.sbox_ap_pool_start4.value()))
            dhcp_start = '.'.join(dhcp_start_list)

            dhcp_end_list = []
            dhcp_end_list.append(unicode(self.sbox_ap_pool_end1.value()))
            dhcp_end_list.append(unicode(self.sbox_ap_pool_end2.value()))
            dhcp_end_list.append(unicode(self.sbox_ap_pool_end3.value()))
            dhcp_end_list.append(unicode(self.sbox_ap_pool_end4.value()))
            dhcp_end = '.'.join(dhcp_end_list)

            dhcp_mask_list = []
            dhcp_mask_list.append(unicode(self.sbox_ap_pool_mask1.value()))
            dhcp_mask_list.append(unicode(self.sbox_ap_pool_mask2.value()))
            dhcp_mask_list.append(unicode(self.sbox_ap_pool_mask3.value()))
            dhcp_mask_list.append(unicode(self.sbox_ap_pool_mask4.value()))
            dhcp_mask = '.'.join(dhcp_mask_list)

            if not interface:
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Access Point',
                                           'Interface empty.',
                                           QtGui.QMessageBox.Ok)
                return

            elif not ssid:
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Access Point',
                                           'SSID empty.',
                                           QtGui.QMessageBox.Ok)
                return

            elif not wpa_key:
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Access Point',
                                           'WPA key empty.',
                                           QtGui.QMessageBox.Ok)
                return

            elif not server_name:
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Access Point',
                                           'Server name empty.',
                                           QtGui.QMessageBox.Ok)
                return

            elif not domain:
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Access Point',
                                           'Domain empty.',
                                           QtGui.QMessageBox.Ok)
                return

            apply_dict['interface']        = interface
            apply_dict['interface_ip']     = interface_ip
            apply_dict['interface_mask']   = interface_mask
            apply_dict['ssid']             = ssid
            apply_dict['ssid_hidden']      = ssid_hidden
            apply_dict['wpa_key']          = wpa_key
            apply_dict['channel']          = channel
            apply_dict['enabled_dns_dhcp'] = enabled_dns_dhcp
            apply_dict['server_name']      = server_name
            apply_dict['domain']           = domain
            apply_dict['dhcp_start']       = dhcp_start
            apply_dict['dhcp_end']         = dhcp_end
            apply_dict['dhcp_mask']        = dhcp_mask

            self.saving = True
            self.label_working_wait.show()
            self.pbar_working_wait.show()
            self.sarea_ap.setEnabled(False)
            self.update_button_text_state(BUTTON_STATE_SAVE)

            self.script_manager.execute_script('settings_network_apmode_apply',
                                               cb_settings_network_apmode_apply,
                                               [json.dumps(apply_dict)])

        except Exception as e:
            self.label_working_wait.hide()
            self.pbar_working_wait.hide()
            self.saving = False
            self.sarea_ap.show()
            self.update_button_text_state(BUTTON_STATE_DEFAULT)
            err_msg = 'Error occured while processing input data.\n\n' + str(e)

            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Access Point',
                                       err_msg,
                                       QtGui.QMessageBox.Ok)

    def read_config_files(self):
        self.hostapd_conf_rfile = REDFile(self.session)
        self.dnsmasq_conf_rfile = REDFile(self.session)
        self.interfaces_conf_rfile = REDFile(self.session)

        def cb_open_hostapd_conf(red_file):
            def cb_read(red_file, result):
                red_file.release()

                if not self.is_tab_on_focus:
                    return

                if result and result.data and not result.error:
                    try:
                        def cb_settings_network_apmode_get_interfaces(result):
                            if not self.is_tab_on_focus:
                                return

                            if result and not result.stderr and result.exit_code == 0:
                                ap_mode_interfaces = json.loads(result.stdout)

                                if len(ap_mode_interfaces) <= 0:
                                    self.label_ap_status.setText('Inactive - No wireless interface available')
                                    self.cbox_ap_interface.clear()
                                    self.pbutton_ap_save.setEnabled(False)
                                    self.update_ui_state()
                                    return

                                self.pbutton_ap_save.setEnabled(True)
                                self.cbox_ap_interface.clear()

                                self.cbox_ap_interface.currentIndexChanged.disconnect()

                                for intf in ap_mode_interfaces:
                                    self.cbox_ap_interface.addItem(intf)
                                    current_item_index = self.cbox_ap_interface.count() - 1

                                    if ap_mode_interfaces[intf]['ip']:
                                        self.cbox_ap_interface.setItemData(current_item_index,
                                                                           QtCore.QVariant(ap_mode_interfaces[intf]['ip']),
                                                                           AP_INTERFACE_IP_USER_ROLE)
                                    else:
                                        self.cbox_ap_interface.setItemData(current_item_index,
                                                                           QtCore.QVariant('192.168.42.1'),
                                                                           AP_INTERFACE_IP_USER_ROLE)

                                    if ap_mode_interfaces[intf]['mask']:
                                        self.cbox_ap_interface.setItemData(current_item_index,
                                                                           QtCore.QVariant(ap_mode_interfaces[intf]['mask']),
                                                                           AP_INTERFACE_MASK_USER_ROLE)

                                    else:
                                        self.cbox_ap_interface.setItemData(current_item_index,
                                                                           QtCore.QVariant('255.255.255.0'),
                                                                           AP_INTERFACE_MASK_USER_ROLE)
                                self.cbox_ap_interface.setCurrentIndex(-1)
                                self.cbox_ap_interface.currentIndexChanged.connect(self.slot_cbox_ap_interface_current_index_changed)

                                if not interface:
                                    self.cbox_ap_interface.setCurrentIndex(0)

                                elif not interface and self.cbox_ap_interface.count() > 0:
                                    self.cbox_ap_interface.setCurrentIndex(0)

                                else:
                                    broke = False
                                    for i in range(0, self.cbox_ap_interface.count()):
                                        if self.cbox_ap_interface.itemText(i) == interface:
                                            self.cbox_ap_interface.setCurrentIndex(i)
                                            broke = True
                                            break

                                    if not broke:
                                        self.cbox_ap_interface.setCurrentIndex(0)
                            else:
                                err_msg = 'Error getting access point interfaces.\n\n' + result.stderr
                                QtGui.QMessageBox.critical(get_main_window(),
                                                           'Settings | Access Point',
                                                           err_msg,
                                                           QtGui.QMessageBox.Ok)

                            self.update_ui_state()

                        hostapd_conf = result.data.decode('utf-8')

                        if hostapd_conf:
                            lines = hostapd_conf.splitlines()

                            interface   = ''
                            ssid        = ''
                            channel     = 1
                            ssid_hidden = '0'
                            wpa_key     = ''

                            for l in lines:
                                l_split = l.strip().split('=')

                                if len(l_split) != 2:
                                    continue

                                if l_split[0].strip(' ') == 'interface':
                                    interface = l_split[1].strip(' ')

                                elif l_split[0].strip(' ') == 'ssid':
                                    ssid = l_split[1].strip(' ')

                                elif l_split[0].strip(' ') == 'channel':
                                    channel = l_split[1].strip(' ')

                                elif l_split[0].strip(' ') == 'ignore_broadcast_ssid':
                                    ssid_hidden = l_split[1].strip(' ')

                                elif l_split[0].strip(' ') == 'wpa_passphrase':
                                    wpa_key = l_split[1]

                            self.script_manager.execute_script('settings_network_apmode_get_interfaces',
                                                               cb_settings_network_apmode_get_interfaces)
                            self.ledit_ap_ssid.setText(ssid)
                            self.chkbox_ap_ssid_hidden.setChecked(ssid_hidden != '0')

                            self.sbox_ap_channel.setValue(int(channel))
                            self.ledit_ap_wpa_key.setText(wpa_key)

                    except Exception as e:
                        err_msg = 'Error parsing hostapd.conf\n\n' + str(e)
                        QtGui.QMessageBox.critical(get_main_window(),
                                                   'Settings | Access Point',
                                                   err_msg,
                                                   QtGui.QMessageBox.Ok)
                else:
                    err_msg = 'Error reading hostapd.conf\n\n'+result.error
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Access Point',
                                               err_msg,
                                               QtGui.QMessageBox.Ok)

                self.update_ui_state()

            red_file.read_async(4096, lambda x: cb_read(red_file, x))

        def cb_open_error_hostapd_conf():
            err_msg = 'Error opening hostapd.conf'
            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Access Point',
                                       err_msg,
                                       QtGui.QMessageBox.Ok)

            self.update_ui_state()

        def cb_open_dnsmasq_conf(red_file):
            def cb_read(red_file, result):
                red_file.release()

                if not self.is_tab_on_focus:
                    return

                if result and result.data and not result.error:
                    try:
                        dnsmasq_conf = result.data.decode('utf-8')
                        if dnsmasq_conf:
                            dns_dhcp_enabled = True
                            dhcp_range_start = '192.168.42.50'
                            dhcp_range_end = '192.168.42.254'
                            server_name = 'red-brick'
                            domain = 'tf.local'
                            dhcp_option_netmask = '255.255.255.0'

                            lines = dnsmasq_conf.splitlines()

                            for l in lines:
                                if l.strip().strip(' ') == '#Enabled':
                                    dns_dhcp_enabled = True
                                elif l.strip().strip(' ') == '#Disabled':
                                    dns_dhcp_enabled = False

                                l_split = l.strip().split('=')

                                if len(l_split) != 2:
                                    continue

                                if l_split[0].strip(' ') == 'dhcp-range':
                                    dhcp_range = l_split[1].strip(' ').split(',')
                                    dhcp_range_start = dhcp_range[0]
                                    dhcp_range_end = dhcp_range[1]

                                elif l_split[0].strip(' ') == 'address':
                                    l_split1 = l_split[1].split('/')
                                    if len(l_split1) == 3:
                                        server_name = l_split1[1]

                                elif l_split[0].strip(' ') == 'domain':
                                    domain= l_split[1].strip(' ')

                                elif l_split[0].strip(' ') == 'dhcp-option':
                                    dhcp_option = l_split[1].strip(' ').split(',')
                                    if len(dhcp_option) == 2:
                                        if dhcp_option[0].strip(' ') == 'option:netmask':
                                            dhcp_option_netmask = dhcp_option[1]

                            self.chkbox_ap_enable_dns_dhcp.setChecked(dns_dhcp_enabled)

                            if server_name:
                                self.ledit_ap_server_name.setText(server_name)

                            if domain:
                                self.ledit_ap_domain.setText(domain)

                            dhcp_range_start_list = dhcp_range_start.split('.')
                            dhcp_range_end_list = dhcp_range_end.split('.')
                            dhcp_option_netmask_list = dhcp_option_netmask.split('.')

                            self.sbox_ap_pool_start1.setValue(int(dhcp_range_start_list[0]))
                            self.sbox_ap_pool_start2.setValue(int(dhcp_range_start_list[1]))
                            self.sbox_ap_pool_start3.setValue(int(dhcp_range_start_list[2]))
                            self.sbox_ap_pool_start4.setValue(int(dhcp_range_start_list[3]))

                            self.sbox_ap_pool_end1.setValue(int(dhcp_range_end_list[0]))
                            self.sbox_ap_pool_end2.setValue(int(dhcp_range_end_list[1]))
                            self.sbox_ap_pool_end3.setValue(int(dhcp_range_end_list[2]))
                            self.sbox_ap_pool_end4.setValue(int(dhcp_range_end_list[3]))

                            self.sbox_ap_pool_mask1.setValue(int(dhcp_option_netmask_list[0]))
                            self.sbox_ap_pool_mask2.setValue(int(dhcp_option_netmask_list[1]))
                            self.sbox_ap_pool_mask3.setValue(int(dhcp_option_netmask_list[2]))
                            self.sbox_ap_pool_mask4.setValue(int(dhcp_option_netmask_list[3]))

                    except Exception as e:
                        err_msg = 'Error parsing dnsmasq.conf\n\n' + str(e)
                        QtGui.QMessageBox.critical(get_main_window(),
                                                   'Settings | Access Point',
                                                   err_msg,
                                                   QtGui.QMessageBox.Ok)
                else:
                    err_msg = 'Error reading dnsmasq.conf\n\n'+result.error
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Access Point',
                                               err_msg,
                                               QtGui.QMessageBox.Ok)

                self.update_ui_state()

            red_file.read_async(4096, lambda x: cb_read(red_file, x))

        def cb_open_error_dnsmasq_conf():
            err_msg = 'Error opening dnsmasq.conf'
            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Access Point',
                                       err_msg,
                                       QtGui.QMessageBox.Ok)

            self.update_ui_state()

        async_call(self.hostapd_conf_rfile.open,
                   (HOSTAPD_CONF_PATH, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open_hostapd_conf,
                   cb_open_error_hostapd_conf)

        async_call(self.dnsmasq_conf_rfile.open,
                   (DNSMASQ_CONF_PATH, REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   cb_open_dnsmasq_conf,
                   cb_open_error_dnsmasq_conf)
