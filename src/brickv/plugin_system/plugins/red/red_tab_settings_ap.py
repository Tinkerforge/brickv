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
from PyQt4 import QtCore, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_settings_ap import Ui_REDTabSettingsAP
from brickv.plugin_system.plugins.red.red_tab_settings_ap_dhcp_leases_dialog import REDTabSettingsAPDhcpLeasesDialog
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import TextFile
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
        self.pbutton_ap_show_dhcp_leases.hide()
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
        self.pbutton_ap_show_dhcp_leases.clicked.connect(self.slot_pbutton_ap_show_dhcp_leases_clicked)

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

        self.pbutton_ap_show_dhcp_leases.setVisible(dhcp_visible)

        self.line2.setVisible(has_interface)

    def slot_cbox_ap_interface_current_index_changed(self, index):
        ip = self.cbox_ap_interface.itemData(index, AP_INTERFACE_IP_USER_ROLE)
        mask = self.cbox_ap_interface.itemData(index, AP_INTERFACE_MASK_USER_ROLE)

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
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Access Point',
                                           'Error saving access point settings:\n\n' + result.stderr,
                                           QtGui.QMessageBox.Ok)

        apply_dict = {'interface'       : None,
                      'interface_ip'    : None,
                      'interface_mask'  : None,
                      'ssid'            : None,
                      'ssid_hidden'     : None,
                      'wpa_key'         : None,
                      'channel'         : None,
                      'enabled_dns_dhcp': None,
                      'domain'          : None,
                      'dhcp_start'      : None,
                      'dhcp_end'        : None,
                      'dhcp_mask'       : None}

        def check_ascii(text, message):
            try:
                text.encode('ascii')
                return True
            except:
                self.label_working_wait.hide()
                self.pbar_working_wait.hide()
                self.saving = False
                self.sarea_ap.show()
                self.update_button_text_state(BUTTON_STATE_DEFAULT)

                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Access Point',
                                           message,
                                           QtGui.QMessageBox.Ok)
                return False

        if not check_ascii(self.ledit_ap_ssid.text(),
                           'SSID must not contain non-ASCII characters'):
            return

        if not check_ascii(self.ledit_ap_wpa_key.text(),
                           'WPA key not contain non-ASCII characters'):
            return

        if not check_ascii(self.ledit_ap_domain.text(),
                           'DNS domain not contain non-ASCII characters'):
            return

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

            elif not domain:
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Access Point',
                                           'DNS Domain empty.',
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
            apply_dict['domain']           = domain
            apply_dict['dhcp_start']       = dhcp_start
            apply_dict['dhcp_end']         = dhcp_end
            apply_dict['dhcp_mask']        = dhcp_mask

            self.label_working_wait.show()
            self.pbar_working_wait.show()
            self.saving = True
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

            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Access Point',
                                       'Error occured while processing input data:\n\n' + str(e),
                                       QtGui.QMessageBox.Ok)

    def slot_pbutton_ap_show_dhcp_leases_clicked(self):
        leases_dialog = REDTabSettingsAPDhcpLeasesDialog(self, self.session)
        leases_dialog.setModal(True)
        leases_dialog.show()

    def read_config_files(self):
        def cb_hostapd_conf_content(content):
            if not self.is_tab_on_focus or len(content) == 0:
                return

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
                                                               ap_mode_interfaces[intf]['ip'],
                                                               AP_INTERFACE_IP_USER_ROLE)
                        else:
                            self.cbox_ap_interface.setItemData(current_item_index,
                                                               '192.168.42.1',
                                                               AP_INTERFACE_IP_USER_ROLE)

                        if ap_mode_interfaces[intf]['mask']:
                            self.cbox_ap_interface.setItemData(current_item_index,
                                                               ap_mode_interfaces[intf]['mask'],
                                                               AP_INTERFACE_MASK_USER_ROLE)

                        else:
                            self.cbox_ap_interface.setItemData(current_item_index,
                                                               '255.255.255.0',
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
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Access Point',
                                               'Error getting access point interfaces:\n\n' + result.stderr,
                                               QtGui.QMessageBox.Ok)

                self.update_ui_state()

            try:
                lines       = content.splitlines()
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
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Access Point',
                                           'Error parsing hostapd.conf file:\n\n' + unicode(e),
                                           QtGui.QMessageBox.Ok)

            self.update_ui_state()

        def cb_dnsmasq_conf_content(content):
            if not self.is_tab_on_focus or len(content) == 0:
                return

            try:
                lines               = content.splitlines()
                dns_dhcp_enabled    = True
                dhcp_range_start    = '192.168.42.50'
                dhcp_range_end      = '192.168.42.254'
                domain              = 'red-brick-ap'
                dhcp_option_netmask = '255.255.255.0'

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

                    elif l_split[0].strip(' ') == 'domain':
                        domain= l_split[1].strip(' ')

                    elif l_split[0].strip(' ') == 'dhcp-option':
                        dhcp_option = l_split[1].strip(' ').split(',')
                        if len(dhcp_option) == 2:
                            if dhcp_option[0].strip(' ') == 'option:netmask':
                                dhcp_option_netmask = dhcp_option[1]

                self.chkbox_ap_enable_dns_dhcp.setChecked(dns_dhcp_enabled)

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
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Access Point',
                                           'Error parsing dnsmasq.conf file:\n\n' + unicode(e),
                                           QtGui.QMessageBox.Ok)

            self.update_ui_state()

        def cb_text_file_error(title, kind, error):
            self.update_ui_state()

            kind_text = {
            TextFile.ERROR_KIND_OPEN: 'opening',
            TextFile.ERROR_KIND_READ: 'reading',
            TextFile.ERROR_KIND_UTF8: 'decoding'
            }

            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Access Point',
                                       'Error {0} {1} file:\n\n{2}'.format(kind_text[kind], title, unicode(error)),
                                       QtGui.QMessageBox.Ok)

        TextFile.read_async(self.session, HOSTAPD_CONF_PATH,
                            cb_hostapd_conf_content,
                            lambda kind, error: cb_text_file_error('hostapd.conf', kind, error))

        TextFile.read_async(self.session, DNSMASQ_CONF_PATH,
                            cb_dnsmasq_conf_content,
                            lambda kind, error: cb_text_file_error('hostapd.conf', kind, error))
