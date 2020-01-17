# -*- coding: utf-8 -*-
"""
Master Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

wifi2.py: Wifi 2.0 for Master Plugin implementation

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

from PyQt5.QtWidgets import QWidget, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from brickv.plugin_system.plugins.master.wifi2_status import Wifi2Status
from brickv.plugin_system.plugins.master.ui_wifi2 import Ui_Wifi2
from brickv.async_call import async_call
from brickv.utils import get_main_window
from brickv.load_pixmap import load_pixmap
from brickv.infos import get_version_string

def show_group(group):
    for widget in group:
        widget.setVisible(True)

def hide_group(group):
    for widget in group:
        widget.setVisible(False)

class Wifi2(QWidget, Ui_Wifi2):
    def __init__(self, wifi2_firmware_version, parent):
        QWidget.__init__(self)

        self.setupUi(self)

        self.parent = parent
        self.master = parent.master

        self.wifi2_status = None

        if parent.firmware_version < (2, 4, 0):
            # This should not be possible
            return

        self.wifi2_firmware_version = wifi2_firmware_version

        self.wifi_update_firmware_button.setIcon(QIcon(load_pixmap('update-icon-normal.png')))
        self.wifi_update_firmware_button.clicked.connect(lambda: get_main_window().show_extension_update(parent.device_info.uid))
        self.wifi_update_firmware_button.hide()

        self.wifi_firmware_version_label.setText(get_version_string(wifi2_firmware_version, replace_unknown='Waiting for WIFI Extension 2.0 FW Version...'))

        self.general_group = [self.wifi_port_label, self.wifi_port, self.wifi_websocket_port_label,
                              self.wifi_websocket_port, self.wifi_website_port_label, self.wifi_website_port,
                              self.wifi_disable_web_interface, self.wifi_phy_mode_label, self.wifi_phy_mode,
                              self.wifi_use_auth, self.wifi_secret_label, self.wifi_secret, self.wifi_show_characters]

        self.authentication_group = [self.wifi_secret_label, self.wifi_secret, self.wifi_show_characters]

        self.client_ip_group = [self.wifi_client_ip_label, self.wifi_client_sub_label, self.wifi_client_gw_label,
                                self.wifi_client_ip4, self.wifi_client_ip3, self.wifi_client_ip2, self.wifi_client_ip1,
                                self.wifi_client_sub4, self.wifi_client_sub3, self.wifi_client_sub2, self.wifi_client_sub1,
                                self.wifi_client_gw4, self.wifi_client_gw3, self.wifi_client_gw2, self.wifi_client_gw1,
                                self.wifi_client_dot1, self.wifi_client_dot2, self.wifi_client_dot3,
                                self.wifi_client_dot4, self.wifi_client_dot5, self.wifi_client_dot6,
                                self.wifi_client_dot7, self.wifi_client_dot8, self.wifi_client_dot9]
        self.client_bssid_group = [self.wifi_client_bssid_label,
                                   self.wifi_client_bssid6, self.wifi_client_bssid5, self.wifi_client_bssid4,
                                   self.wifi_client_bssid3, self.wifi_client_bssid2, self.wifi_client_bssid1,
                                   self.wifi_client_bssid_dot1, self.wifi_client_bssid_dot2, self.wifi_client_bssid_dot3,
                                   self.wifi_client_bssid_dot4, self.wifi_client_bssid_dot5]
        self.client_mac_group = [self.wifi_client_mac_label,
                                 self.wifi_client_mac6, self.wifi_client_mac5, self.wifi_client_mac4,
                                 self.wifi_client_mac3, self.wifi_client_mac2, self.wifi_client_mac1,
                                 self.wifi_client_mac_dot1, self.wifi_client_mac_dot2, self.wifi_client_mac_dot3,
                                 self.wifi_client_mac_dot4, self.wifi_client_mac_dot5]
        self.client_enc_group = [self.wifi_client_password_label,
                                 self.wifi_client_change_password,
                                 self.wifi_client_password,
                                 self.wifi_client_password_show]

        self.ap_ip_group = [self.wifi_ap_ip_label, self.wifi_ap_sub_label, self.wifi_ap_gw_label,
                            self.wifi_ap_ip4, self.wifi_ap_ip3, self.wifi_ap_ip2, self.wifi_ap_ip1,
                            self.wifi_ap_sub4, self.wifi_ap_sub3, self.wifi_ap_sub2, self.wifi_ap_sub1,
                            self.wifi_ap_gw4, self.wifi_ap_gw3, self.wifi_ap_gw2, self.wifi_ap_gw1,
                            self.wifi_ap_dot1, self.wifi_ap_dot2, self.wifi_ap_dot3,
                            self.wifi_ap_dot4, self.wifi_ap_dot5, self.wifi_ap_dot6,
                            self.wifi_ap_dot7, self.wifi_ap_dot8, self.wifi_ap_dot9]
        self.ap_mac_group = [self.wifi_ap_mac_label,
                             self.wifi_ap_mac6, self.wifi_ap_mac5, self.wifi_ap_mac4,
                             self.wifi_ap_mac3, self.wifi_ap_mac2, self.wifi_ap_mac1,
                             self.wifi_ap_mac_dot1, self.wifi_ap_mac_dot2, self.wifi_ap_mac_dot3,
                             self.wifi_ap_mac_dot4, self.wifi_ap_mac_dot5]
        self.ap_enc_group = [self.wifi_ap_password_label,
                             self.wifi_ap_change_password,
                             self.wifi_ap_password,
                             self.wifi_ap_password_show]

        self.mesh_router_enc_group = [self.wifi_mesh_router_password_label,
                                      self.wifi_mesh_router_change_password,
                                      self.wifi_mesh_router_password,
                                      self.wifi_mesh_router_password_show]
        self.mesh_root_static_ip_group = [self.wifi_mesh_root_ip_label,
                                          self.wifi_mesh_root_sub_label,
                                          self.wifi_mesh_root_gw_label,
                                          self.wifi_mesh_root_ip1,
                                          self.wifi_mesh_root_ip2,
                                          self.wifi_mesh_root_ip3,
                                          self.wifi_mesh_root_ip4,
                                          self.wifi_mesh_root_sub1,
                                          self.wifi_mesh_root_sub2,
                                          self.wifi_mesh_root_sub3,
                                          self.wifi_mesh_root_sub4,
                                          self.wifi_mesh_root_gw1,
                                          self.wifi_mesh_root_gw2,
                                          self.wifi_mesh_root_gw3,
                                          self.wifi_mesh_root_gw4,
                                          self.wifi_mesh_dot1,
                                          self.wifi_mesh_dot2,
                                          self.wifi_mesh_dot3,
                                          self.wifi_mesh_dot4,
                                          self.wifi_mesh_dot5,
                                          self.wifi_mesh_dot6,
                                          self.wifi_mesh_dot7,
                                          self.wifi_mesh_dot8,
                                          self.wifi_mesh_dot9]
        self.mesh_router_bssid_group = [self.wifi_mesh_router_bssid_label,
                                        self.wifi_mesh_router_bssid1,
                                        self.wifi_mesh_router_bssid2,
                                        self.wifi_mesh_router_bssid3,
                                        self.wifi_mesh_router_bssid4,
                                        self.wifi_mesh_router_bssid5,
                                        self.wifi_mesh_router_bssid6,
                                        self.wifi_mesh_colon1,
                                        self.wifi_mesh_colon2,
                                        self.wifi_mesh_colon3,
                                        self.wifi_mesh_colon4,
                                        self.wifi_mesh_colon5]

        # Enable/disable web interface
        self.wifi_disable_web_interface.stateChanged.connect(self.wifi_disable_web_interface_state_changed)

        # Passwords
        self.wifi_secret_show_state_changed(Qt.Unchecked)
        self.wifi_client_show_state_changed(Qt.Unchecked)
        self.wifi_mesh_router_password_show_state_change(Qt.Unchecked)
        self.wifi_ap_password_show_state_changed(Qt.Unchecked)
        self.wifi_show_characters.stateChanged.connect(self.wifi_secret_show_state_changed)
        self.wifi_client_password_show.stateChanged.connect(self.wifi_client_show_state_changed)
        self.wifi_ap_password_show.stateChanged.connect(self.wifi_ap_password_show_state_changed)
        self.wifi_mesh_router_password_show.stateChanged.connect(self.wifi_mesh_router_password_show_state_change)
        self.wifi_client_change_password.stateChanged.connect(self.wifi_client_change_password_changed)
        self.wifi_ap_change_password.stateChanged.connect(self.wifi_ap_change_password_changed)
        self.wifi_mesh_router_change_password.stateChanged.connect(self.wifi_mesh_router_change_password_changed)

        # Use passwords
        self.wifi_client_encryption_changed(1)
        self.wifi_ap_encryption_changed(3)
        self.wifi_mesh_router_encryption_changed(1)

        self.wifi_use_auth_state_changed(Qt.Unchecked)
        self.wifi_mesh_router_encryption_changed(0)
        self.wifi_client_encryption.currentIndexChanged.connect(self.wifi_client_encryption_changed)
        self.wifi_ap_encryption.currentIndexChanged.connect(self.wifi_ap_encryption_changed)
        self.wifi_use_auth.stateChanged.connect(self.wifi_use_auth_state_changed)
        self.wifi_mesh_router_encryption.currentIndexChanged.connect(self.wifi_mesh_router_encryption_changed)

        # MACs
        self.wifi_client_use_bssid_state_changed(Qt.Unchecked)
        self.wifi_client_use_mac_state_changed(Qt.Unchecked)
        self.wifi_ap_use_mac_state_changed(Qt.Unchecked)
        self.wifi_client_use_bssid.stateChanged.connect(self.wifi_client_use_bssid_state_changed)
        self.wifi_client_use_mac.stateChanged.connect(self.wifi_client_use_mac_state_changed)
        self.wifi_ap_use_mac.stateChanged.connect(self.wifi_ap_use_mac_state_changed)
        self.wifi_mesh_use_router_bssid_state_changed(Qt.Unchecked)
        self.wifi_mesh_router_use_bssid.stateChanged.connect(self.wifi_mesh_use_router_bssid_state_changed)

        # IP Configuration
        self.wifi_client_ip_configuration_changed(0)
        self.wifi_ap_ip_configuration_changed(0)
        self.wifi_mesh_root_ip_configuration_changed(0)
        self.wifi_client_ip_configuration.currentIndexChanged.connect(self.wifi_client_ip_configuration_changed)
        self.wifi_ap_ip_configuration.currentIndexChanged.connect(self.wifi_ap_ip_configuration_changed)
        self.wifi_mesh_root_ip_configuration.currentIndexChanged.connect(self.wifi_mesh_root_ip_configuration_changed)

        # Mode
        self.wifi_mode_changed(0)
        self.wifi_mode.currentIndexChanged.connect(self.wifi_mode_changed)

        # Save/Status
        self.wifi_save.clicked.connect(self.save_clicked)
        self.wifi_show_status.clicked.connect(self.show_status_clicked)

        self.client_enable = False
        self.ap_enable = False
        self.mesh_enable = False

        # Check if the master brick and WIFI extension 2 firmware versions
        # support mesh networking feature
        if self.wifi2_firmware_version >= (2, 1, 0) and  self.parent.firmware_version >= (2, 4, 2):
            self.wifi_mode.addItem('Mesh')
            self.label_mesh_hint.hide()

    def start(self):
        # Get Current state of WIFI Extension 2.0
        async_call(self.master.get_wifi2_authentication_secret, None,
                   self.get_wifi2_authentication_secret_async, self.parent.increase_error_count)

        async_call(self.master.get_wifi2_configuration, None,
                   self.get_wifi2_configuration_async, self.parent.increase_error_count)

        async_call(self.master.get_wifi2_client_configuration, None,
                   self.get_wifi2_client_configuration_async, self.parent.increase_error_count)

        async_call(self.master.get_wifi2_client_hostname, None,
                   self.get_wifi2_client_hostname_async, self.parent.increase_error_count)

        if self.wifi2_firmware_version >= (2, 1, 4):
            # FW >= 2.1.4 reports a fake password to allow checking if encryption
            # is enabled instead of always reporting an empty password
            async_call(self.master.get_wifi2_client_password, None,
                       self.get_wifi2_client_password_async, self.parent.increase_error_count)

        async_call(self.master.get_wifi2_ap_configuration, None,
                   self.get_wifi2_ap_configuration_async, self.parent.increase_error_count)

        if self.parent.firmware_version >= (2, 4, 2) and self.wifi2_firmware_version >= (2, 1, 0):
            async_call(self.master.get_wifi2_mesh_configuration, None,
                       self.get_wifi2_mesh_configuration_async, self.parent.increase_error_count)

            async_call(self.master.get_wifi2_mesh_router_password, None,
                       self.get_wifi2_mesh_router_password_async, self.parent.increase_error_count)

            async_call(self.master.get_wifi2_mesh_router_ssid, None,
                       self.get_wifi2_mesh_router_ssid_async, self.parent.increase_error_count)

    def destroy(self):
        if self.wifi2_status:
            self.wifi2_status.close()

    def check_ap_client_mesh(self):
        if not self.client_enable and not self.ap_enable and not self.mesh_enable:
            self.wifi_mode.setCurrentIndex(2)
        else:
            if self.client_enable and not self.ap_enable and not self.mesh_enable:
                self.wifi_mode.setCurrentIndex(0)
            elif self.ap_enable and not self.client_enable and not self.mesh_enable:
                self.wifi_mode.setCurrentIndex(1)
            elif self.client_enable and self.ap_enable and not self.mesh_enable:
                self.wifi_mode.setCurrentIndex(2)
            elif not self.client_enable and not self.ap_enable and self.mesh_enable:
                self.wifi_mode.setCurrentIndex(3)
            else:
                self.wifi_mode.setCurrentIndex(2)

    def get_wifi2_authentication_secret_async(self, data):
        if len(data) == 0:
            self.wifi_secret.setText('')
            self.wifi_use_auth.setChecked(False)
        else:
            self.wifi_secret.setText(data)
            self.wifi_use_auth.setChecked(True)

    def get_wifi2_configuration_async(self, data):
        self.wifi_port.setValue(data.port)
        self.wifi_phy_mode.setCurrentIndex(data.phy_mode)
        self.wifi_websocket_port.setValue(data.websocket_port)

        if self.wifi2_firmware_version >= (2, 1, 0):
            if data.website == 1:
                self.wifi_website_port.setValue(data.website_port)
                self.wifi_disable_web_interface.setChecked(False)
            else:
                self.wifi_website_port.setValue(80)
                self.wifi_disable_web_interface.setChecked(True)
        else:
            if data.website_port < 2 or data.website_port > 65534:
                self.wifi_website_port.setValue(80)
                self.wifi_disable_web_interface.setChecked(True)
            else:
                self.wifi_website_port.setValue(data.website_port)
                self.wifi_disable_web_interface.setChecked(False)

    def get_wifi2_client_configuration_async(self, data):
        self.client_enable = data.enable
        self.wifi_client_ssid.setText(data.ssid)

        if data.ip == (0, 0, 0, 0):
            self.wifi_client_ip_configuration.setCurrentIndex(0)
        else:
            self.wifi_client_ip_configuration.setCurrentIndex(1)

        self.wifi_client_ip1.setValue(data.ip[3])
        self.wifi_client_ip2.setValue(data.ip[2])
        self.wifi_client_ip3.setValue(data.ip[1])
        self.wifi_client_ip4.setValue(data.ip[0])
        self.wifi_client_sub1.setValue(data.subnet_mask[3])
        self.wifi_client_sub2.setValue(data.subnet_mask[2])
        self.wifi_client_sub3.setValue(data.subnet_mask[1])
        self.wifi_client_sub4.setValue(data.subnet_mask[0])
        self.wifi_client_gw1.setValue(data.gateway[3])
        self.wifi_client_gw2.setValue(data.gateway[2])
        self.wifi_client_gw3.setValue(data.gateway[1])
        self.wifi_client_gw4.setValue(data.gateway[0])

        if data.mac_address == (0, 0, 0, 0, 0, 0):
            self.wifi_client_use_mac.setChecked(False)
        else:
            self.wifi_client_use_mac.setChecked(True)
            self.wifi_client_mac1.setValue(data.mac_address[5])
            self.wifi_client_mac2.setValue(data.mac_address[4])
            self.wifi_client_mac3.setValue(data.mac_address[3])
            self.wifi_client_mac4.setValue(data.mac_address[2])
            self.wifi_client_mac5.setValue(data.mac_address[1])
            self.wifi_client_mac6.setValue(data.mac_address[0])

        if data.bssid == (0, 0, 0, 0, 0, 0):
            self.wifi_client_use_bssid.setChecked(False)
        else:
            self.wifi_client_use_bssid.setChecked(True)
            self.wifi_client_bssid1.setValue(data.bssid[5])
            self.wifi_client_bssid2.setValue(data.bssid[4])
            self.wifi_client_bssid3.setValue(data.bssid[3])
            self.wifi_client_bssid4.setValue(data.bssid[2])
            self.wifi_client_bssid5.setValue(data.bssid[1])
            self.wifi_client_bssid6.setValue(data.bssid[0])

        self.check_ap_client_mesh()

    def get_wifi2_client_hostname_async(self, data):
        self.wifi_client_hostname.setText(data)

    def get_wifi2_client_password_async(self, data):
        if len(data) == 0:
            self.wifi_client_encryption.setCurrentIndex(0)
        else:
            self.wifi_client_encryption.setCurrentIndex(1)

    def get_wifi2_ap_configuration_async(self, data):
        self.ap_enable = data.enable
        self.wifi_ap_ssid.setText(data.ssid)

        if data.ip == (0, 0, 0, 0):
            self.wifi_ap_ip_configuration.setCurrentIndex(0)
        else:
            self.wifi_ap_ip_configuration.setCurrentIndex(1)

        self.wifi_ap_ip1.setValue(data.ip[3])
        self.wifi_ap_ip2.setValue(data.ip[2])
        self.wifi_ap_ip3.setValue(data.ip[1])
        self.wifi_ap_ip4.setValue(data.ip[0])
        self.wifi_ap_sub1.setValue(data.subnet_mask[3])
        self.wifi_ap_sub2.setValue(data.subnet_mask[2])
        self.wifi_ap_sub3.setValue(data.subnet_mask[1])
        self.wifi_ap_sub4.setValue(data.subnet_mask[0])
        self.wifi_ap_gw1.setValue(data.gateway[3])
        self.wifi_ap_gw2.setValue(data.gateway[2])
        self.wifi_ap_gw3.setValue(data.gateway[1])
        self.wifi_ap_gw4.setValue(data.gateway[0])

        if data.encryption == 0:
            self.wifi_ap_encryption.setCurrentIndex(0)
        elif data.encryption == 1:
            self.wifi_ap_encryption.setCurrentIndex(3)
        else:
            self.wifi_ap_encryption.setCurrentIndex(data.encryption - 1)

        self.wifi_ap_hide_ssid.setChecked(data.hidden)
        self.wifi_ap_channel.setValue(data.channel)

        if data.mac_address == (0, 0, 0, 0, 0, 0):
            self.wifi_ap_use_mac.setChecked(False)
        else:
            self.wifi_ap_use_mac.setChecked(True)
            self.wifi_ap_mac1.setValue(data.mac_address[5])
            self.wifi_ap_mac2.setValue(data.mac_address[4])
            self.wifi_ap_mac3.setValue(data.mac_address[3])
            self.wifi_ap_mac4.setValue(data.mac_address[2])
            self.wifi_ap_mac5.setValue(data.mac_address[1])
            self.wifi_ap_mac6.setValue(data.mac_address[0])

        self.check_ap_client_mesh()

    def get_wifi2_mesh_configuration_async(self, data):
        self.mesh_enable = data.enable

        self.wifi_mesh_root_ip1.setValue(data.root_ip[0])
        self.wifi_mesh_root_ip2.setValue(data.root_ip[1])
        self.wifi_mesh_root_ip3.setValue(data.root_ip[2])
        self.wifi_mesh_root_ip4.setValue(data.root_ip[3])

        self.wifi_mesh_root_sub1.setValue(data.root_subnet_mask[0])
        self.wifi_mesh_root_sub2.setValue(data.root_subnet_mask[1])
        self.wifi_mesh_root_sub3.setValue(data.root_subnet_mask[2])
        self.wifi_mesh_root_sub4.setValue(data.root_subnet_mask[3])

        self.wifi_mesh_root_gw1.setValue(data.root_gateway[0])
        self.wifi_mesh_root_gw2.setValue(data.root_gateway[1])
        self.wifi_mesh_root_gw3.setValue(data.root_gateway[2])
        self.wifi_mesh_root_gw4.setValue(data.root_gateway[3])

        self.wifi_mesh_router_bssid1.setValue(data.router_bssid[0])
        self.wifi_mesh_router_bssid2.setValue(data.router_bssid[1])
        self.wifi_mesh_router_bssid3.setValue(data.router_bssid[2])
        self.wifi_mesh_router_bssid4.setValue(data.router_bssid[3])
        self.wifi_mesh_router_bssid5.setValue(data.router_bssid[4])
        self.wifi_mesh_router_bssid6.setValue(data.router_bssid[5])

        self.wifi_mesh_group_id1.setValue(data.group_id[0])
        self.wifi_mesh_group_id2.setValue(data.group_id[1])
        self.wifi_mesh_group_id3.setValue(data.group_id[2])
        self.wifi_mesh_group_id4.setValue(data.group_id[3])
        self.wifi_mesh_group_id5.setValue(data.group_id[4])
        self.wifi_mesh_group_id6.setValue(data.group_id[5])

        self.wifi_mesh_group_ssid_prefix.setText(data.group_ssid_prefix)

        self.wifi_mesh_gateway_ip1.setValue(data.gateway_ip[0])
        self.wifi_mesh_gateway_ip2.setValue(data.gateway_ip[1])
        self.wifi_mesh_gateway_ip3.setValue(data.gateway_ip[2])
        self.wifi_mesh_gateway_ip4.setValue(data.gateway_ip[3])

        self.wifi_mesh_gateway_port.setValue(data.gateway_port)

        if data.root_ip == (0, 0, 0, 0):
            self.wifi_mesh_root_ip_configuration.setCurrentIndex(0)
        else:
            self.wifi_mesh_root_ip_configuration.setCurrentIndex(1)

        if data.router_bssid == (0, 0, 0, 0, 0, 0):
            self.wifi_mesh_router_use_bssid.setChecked(False)
        else:
            self.wifi_mesh_router_use_bssid.setChecked(True)

        self.check_ap_client_mesh()

    def get_wifi2_mesh_router_password_async(self, data):
        if len(data) == 0:
            self.wifi_mesh_router_encryption.setCurrentIndex(0)
        else:
            self.wifi_mesh_router_encryption.setCurrentIndex(1)

    def get_wifi2_mesh_router_ssid_async(self, data):
        self.wifi_mesh_router_ssid.setText(data)

    def save_clicked(self):
        try:
            self.wifi_secret.text().encode('ascii')
        except:
            self.popup_fail('Secret cannot contain non-ASCII characters')
            return

        try:
            self.wifi_client_hostname.text().encode('ascii')
        except:
            self.popup_fail('Client hostname cannot contain non-ASCII characters')
            return

        try:
            self.wifi_client_ssid.text().encode('ascii')
        except:
            self.popup_fail('Client SSID cannot contain non-ASCII characters')
            return

        try:
            self.wifi_client_password.text().encode('ascii')
        except:
            self.popup_fail('Client password cannot contain non-ASCII characters')
            return

        try:
            self.wifi_ap_ssid.text().encode('ascii')
        except:
            self.popup_fail('Access point SSID cannot contain non-ASCII characters')
            return

        try:
            tmp_pw = self.wifi_ap_password.text().encode('ascii')
        except:
            self.popup_fail('Access point password cannot contain non-ASCII characters')
            return

        if self.wifi_ap_change_password.isChecked() and len(tmp_pw) < 8:
            self.popup_fail('Access point password must contain at least 8 characters')
            return

        try:
            self.wifi_mesh_router_ssid.text().encode('ascii')
        except:
            self.popup_fail('Mesh router SSID cannot contain non-ASCII characters')
            return

        try:
            self.wifi_mesh_router_password.text().encode('ascii')
        except:
            self.popup_fail('Mesh router password cannot contain non-ASCII characters')
            return

        try:
            self.wifi_mesh_group_ssid_prefix.text().encode('ascii')
        except:
            self.popup_fail('Mesh SSID prefix cannot contain non-ASCII characters')
            return

        # Get current configuration
        general_port           = self.wifi_port.value()
        general_websocket_port = self.wifi_websocket_port.value()
        general_website        = 0

        if self.wifi2_firmware_version >= (2, 1, 0):
            if self.wifi_disable_web_interface.isChecked():
                general_website      = 0
                general_website_port = 1
            else:
                general_website      = 1
                general_website_port = self.wifi_website_port.value()
        else:
            if self.wifi_disable_web_interface.isChecked():
                general_website_port = 1
            else:
                general_website_port = self.wifi_website_port.value()

        general_phy_mode = self.wifi_phy_mode.currentIndex()
        general_use_auth = self.wifi_use_auth.isChecked()

        if general_use_auth:
            general_secret = self.wifi_secret.text()
        else:
            general_secret = ''

        # FIXME: Mesh mode is added to the mode combobox dynamically from master,
        # after master and WIFI2 extension firmware versions are verified which is
        # done from an async callback from the master brick tab. We assume in this
        # case that the mesh entry will have index 3 because until now nothing else
        # is added to the combobox dynamically. In future if more items are dynamically
        # being added to this combobox form async calls depending on this index
        # assumtion may fail.
        general_mode = self.wifi_mode.currentIndex()

        if general_mode == 3:
            client_enable = False
        else:
            client_enable = general_mode in (0, 2)

        client_hostname = self.wifi_client_hostname.text()
        client_ip_conf  = self.wifi_client_ip_configuration.currentIndex()

        if client_ip_conf == 1:
            client_ip  = (self.wifi_client_ip4.value(), self.wifi_client_ip3.value(), self.wifi_client_ip2.value(), self.wifi_client_ip1.value())
            client_sub = (self.wifi_client_sub4.value(), self.wifi_client_sub3.value(), self.wifi_client_sub2.value(), self.wifi_client_sub1.value())
            client_gw  = (self.wifi_client_gw4.value(), self.wifi_client_gw3.value(), self.wifi_client_gw2.value(), self.wifi_client_gw1.value())
        else:
            client_ip  = (0, 0, 0, 0)
            client_sub = (0, 0, 0, 0)
            client_gw  = (0, 0, 0, 0)

        client_ssid       = self.wifi_client_ssid.text()
        client_encryption = self.wifi_client_encryption.currentIndex()
        client_password   = None

        if client_encryption == 0:
            client_password = ''
        elif self.wifi_client_change_password.isChecked():
            client_password = self.wifi_client_password.text()

        client_use_bssid = self.wifi_client_use_bssid.isChecked()

        if client_use_bssid:
            client_bssid = (self.wifi_client_bssid6.value(), self.wifi_client_bssid5.value(), self.wifi_client_bssid4.value(), self.wifi_client_bssid3.value(), self.wifi_client_bssid2.value(), self.wifi_client_bssid1.value())
        else:
            client_bssid = (0, 0, 0, 0, 0, 0)

        client_use_mac = self.wifi_client_use_mac.isChecked()

        if client_use_mac:
            client_mac = (self.wifi_client_mac6.value(), self.wifi_client_mac5.value(), self.wifi_client_mac4.value(), self.wifi_client_mac3.value(), self.wifi_client_mac2.value(), self.wifi_client_mac1.value())
        else:
            client_mac = (0, 0, 0, 0, 0, 0)

        if general_mode == 3:
            ap_enable = False
        else:
            ap_enable = general_mode in (1, 2)

        ap_ip_conf = self.wifi_ap_ip_configuration.currentIndex()

        if ap_ip_conf == 1:
            ap_ip  = (self.wifi_ap_ip4.value(), self.wifi_ap_ip3.value(), self.wifi_ap_ip2.value(), self.wifi_ap_ip1.value())
            ap_sub = (self.wifi_ap_sub4.value(), self.wifi_ap_sub3.value(), self.wifi_ap_sub2.value(), self.wifi_ap_sub1.value())
            ap_gw  = (self.wifi_ap_gw4.value(), self.wifi_ap_gw3.value(), self.wifi_ap_gw2.value(), self.wifi_ap_gw1.value())
        else:
            ap_ip  = (0, 0, 0, 0)
            ap_sub = (0, 0, 0 ,0)
            ap_gw  = (0, 0, 0, 0)

        ap_ssid       = self.wifi_ap_ssid.text()
        ap_encryption = self.wifi_ap_encryption.currentIndex()

        if ap_encryption > 0:
            ap_encryption = ap_encryption + 1

        ap_password  = self.wifi_ap_password.text()
        ap_hide_ssid = self.wifi_ap_hide_ssid.isChecked()
        ap_channel   = self.wifi_ap_channel.value()
        ap_use_mac   = self.wifi_ap_use_mac.isChecked()

        if ap_use_mac:
            ap_mac = (self.wifi_ap_mac6.value(), self.wifi_ap_mac5.value(), self.wifi_ap_mac4.value(), self.wifi_ap_mac3.value(), self.wifi_ap_mac2.value(), self.wifi_ap_mac1.value())
        else:
            ap_mac = (0, 0, 0, 0, 0, 0)

        if self.parent.firmware_version >= (2, 4, 2) and self.wifi2_firmware_version >= (2, 1, 0):
            # Get current mesh configuration.
            if general_mode == 3:
                mesh_enable = True
                client_enable = False
                ap_enable = False
            else:
                mesh_enable = False

            mesh_router_ssid = self.wifi_mesh_router_ssid.text()

            if self.wifi_mesh_router_use_bssid.isChecked():
                mesh_router_bssid = (self.wifi_mesh_router_bssid1.value(),
                                     self.wifi_mesh_router_bssid2.value(),
                                     self.wifi_mesh_router_bssid3.value(),
                                     self.wifi_mesh_router_bssid4.value(),
                                     self.wifi_mesh_router_bssid5.value(),
                                     self.wifi_mesh_router_bssid6.value())
            else:
                mesh_router_bssid = (0, 0, 0, 0, 0, 0)

            mesh_router_encryption = self.wifi_mesh_router_encryption.currentIndex()
            mesh_router_password = None

            if mesh_router_encryption == 0:
                mesh_router_password = ''
            elif self.wifi_mesh_router_change_password.isChecked():
                mesh_router_password = self.wifi_mesh_router_password.text()

            if self.wifi_mesh_root_ip_configuration.currentIndex() == 1:
                mesh_root_ip  = (self.wifi_mesh_root_ip1.value(),
                                 self.wifi_mesh_root_ip2.value(),
                                 self.wifi_mesh_root_ip3.value(),
                                 self.wifi_mesh_root_ip4.value())
                mesh_root_sub = (self.wifi_mesh_root_sub1.value(),
                                 self.wifi_mesh_root_sub2.value(),
                                 self.wifi_mesh_root_sub3.value(),
                                 self.wifi_mesh_root_sub4.value())
                mesh_root_gw  = (self.wifi_mesh_root_gw1.value(),
                                 self.wifi_mesh_root_gw2.value(),
                                 self.wifi_mesh_root_gw3.value(),
                                 self.wifi_mesh_root_gw4.value())
            else:
                mesh_root_ip  = (0, 0, 0, 0)
                mesh_root_sub = (0, 0, 0, 0)
                mesh_root_gw  = (0, 0, 0, 0)

            mesh_group_ssid_prefix = self.wifi_mesh_group_ssid_prefix.text()

            mesh_group_id     = (self.wifi_mesh_group_id1.value(),
                                 self.wifi_mesh_group_id2.value(),
                                 self.wifi_mesh_group_id3.value(),
                                 self.wifi_mesh_group_id4.value(),
                                 self.wifi_mesh_group_id5.value(),
                                 self.wifi_mesh_group_id6.value())
            mesh_gateway_ip   = (self.wifi_mesh_gateway_ip1.value(),
                                 self.wifi_mesh_gateway_ip2.value(),
                                 self.wifi_mesh_gateway_ip3.value(),
                                 self.wifi_mesh_gateway_ip4.value())
            mesh_gateway_port = self.wifi_mesh_gateway_port.value()

        self.master.set_response_expected(self.master.FUNCTION_SET_WIFI2_AUTHENTICATION_SECRET, True)
        self.master.set_response_expected(self.master.FUNCTION_SET_WIFI2_CONFIGURATION,         True)
        self.master.set_response_expected(self.master.FUNCTION_SET_WIFI2_CLIENT_CONFIGURATION,  True)
        self.master.set_response_expected(self.master.FUNCTION_SET_WIFI2_CLIENT_HOSTNAME,       True)
        self.master.set_response_expected(self.master.FUNCTION_SET_WIFI2_CLIENT_PASSWORD,       True)
        self.master.set_response_expected(self.master.FUNCTION_SET_WIFI2_AP_CONFIGURATION,      True)
        self.master.set_response_expected(self.master.FUNCTION_SET_WIFI2_AP_PASSWORD,           True)

        if self.parent.firmware_version >= (2, 4, 2) and self.wifi2_firmware_version >= (2, 1, 0):
            self.master.set_response_expected(self.master.FUNCTION_SET_WIFI2_MESH_CONFIGURATION,    True)
            self.master.set_response_expected(self.master.FUNCTION_SET_WIFI2_MESH_ROUTER_PASSWORD,  True)
            self.master.set_response_expected(self.master.FUNCTION_SET_WIFI2_MESH_ROUTER_SSID,      True)

        to_write = [
            (self.master.set_wifi2_authentication_secret, general_secret),
            (self.master.set_wifi2_configuration, general_port, general_websocket_port, general_website_port, general_phy_mode, 0, general_website), # TODO: Sleep Mode?
            (self.master.set_wifi2_client_configuration, client_enable, client_ssid, client_ip, client_sub, client_gw, client_mac, client_bssid),
            (self.master.set_wifi2_client_hostname, client_hostname),
            (self.master.set_wifi2_ap_configuration, ap_enable, ap_ssid, ap_ip, ap_sub, ap_gw, ap_encryption, ap_hide_ssid, ap_channel, ap_mac),
        ]

        if client_password != None:
            to_write.append((self.master.set_wifi2_client_password, client_password))

        if self.wifi_ap_change_password.isChecked():
            to_write.append((self.master.set_wifi2_ap_password, ap_password))

        if self.parent.firmware_version >= (2, 4, 2) and self.wifi2_firmware_version >= (2, 1, 0):
            to_write.append((self.master.set_wifi2_mesh_configuration,
                             mesh_enable, mesh_root_ip,
                             mesh_root_sub, mesh_root_gw, mesh_router_bssid, mesh_group_id,
                             mesh_group_ssid_prefix, mesh_gateway_ip, mesh_gateway_port))

            if mesh_router_password != None:
                to_write.append((self.master.set_wifi2_mesh_router_password, mesh_router_password))

            to_write.append((self.master.set_wifi2_mesh_router_ssid, mesh_router_ssid))

        try:
            for setter, *args in to_write:
                setter(*args)
        except Exception as e:
            self.popup_fail("Could not save Wifi configuration: Error Code 1:\n\n" + str(e))
            return

        # All done, now save configuration.
        try:
            ok = self.master.save_wifi2_configuration()
        except Exception as e:
            self.popup_fail("Could not save Wifi configuration: Error Code 2:\n\n" + str(e))
            return

        if ok != 0:
            self.popup_fail("Could not save Wifi configuration. Error Code 3:\n\n Bricklet reported error " + str(ok))
            return

        def check(setter, *args):
            if setter.__name__ in ['set_wifi2_client_password', 'set_wifi2_ap_password'] and self.wifi2_firmware_version >= (2, 1, 3):
                return True

            if setter.__name__ == 'set_wifi2_mesh_router_password' and self.wifi2_firmware_version >= (2, 1, 4):
                return True

            getter = getattr(self.master, 'g' + setter.__name__[1:])
            g = getter()

            # convert named tuples to tuples
            if hasattr(g, '_fields'):
                g = tuple(g)

            # some getters return only a single value
            if not isinstance(g, tuple):
                g = (g,)

            return args == g

        try:
            for setter, *args in to_write:
                if not check(setter, *args):
                    self.popup_fail("Could not save Wifi configuration: Error Code 4.")
                    return
        except Exception as e:
            self.popup_fail("Could not save Wifi configuration: " + str(e))
            return

        self.popup_ok()

    def wifi_disable_web_interface_state_changed(self, state):
        if state == Qt.Checked:
            self.wifi_website_port.setDisabled(True)
        else:
            self.wifi_website_port.setDisabled(False)

    def wifi_mode_changed(self, index):
        if index == 0:
            show_group(self.general_group)

            if self.wifi_use_auth.isChecked():
                show_group(self.authentication_group)
            else:
                hide_group(self.authentication_group)

            self.wifi_groupbox_ap.setVisible(False)
            self.wifi_groupbox_client.setVisible(True)
            self.wifi_groupbox_mesh.setVisible(False)
        elif index == 1:
            show_group(self.general_group)

            if self.wifi_use_auth.isChecked():
                show_group(self.authentication_group)
            else:
                hide_group(self.authentication_group)

            self.wifi_groupbox_client.setVisible(False)
            self.wifi_groupbox_ap.setVisible(True)
            self.wifi_groupbox_mesh.setVisible(False)
        elif index == 2:
            show_group(self.general_group)

            if self.wifi_use_auth.isChecked():
                show_group(self.authentication_group)
            else:
                hide_group(self.authentication_group)

            self.wifi_groupbox_client.setVisible(True)
            self.wifi_groupbox_ap.setVisible(True)
            self.wifi_groupbox_mesh.setVisible(False)
        elif index == 3:
            hide_group(self.general_group)
            self.wifi_groupbox_client.setVisible(False)
            self.wifi_groupbox_ap.setVisible(False)
            self.wifi_groupbox_mesh.setVisible(True)

        phy_mode_index = self.wifi_phy_mode.currentIndex()

        if index == 0:
            if self.wifi_phy_mode.count() == 2:
                self.wifi_phy_mode.addItem('N')
        else:
            if phy_mode_index == 2:
                self.wifi_phy_mode.setCurrentIndex(1)

            if self.wifi_phy_mode.count() == 3:
                self.wifi_phy_mode.removeItem(2)

    def wifi_client_encryption_changed(self, index):
        if index == 0:
            hide_group(self.client_enc_group)
        else:
            show_group(self.client_enc_group)

    def wifi_ap_encryption_changed(self, index):
        if index == 0:
            hide_group(self.ap_enc_group)
        else:
            show_group(self.ap_enc_group)

    def wifi_mesh_router_encryption_changed(self, index):
        if index == 0:
            hide_group(self.mesh_router_enc_group)
        else:
            show_group(self.mesh_router_enc_group)

    def wifi_use_auth_state_changed(self, state):
        if state == Qt.Checked:
            show_group(self.authentication_group)
        else:
            hide_group(self.authentication_group)

    def wifi_client_ip_configuration_changed(self, index):
        if index == 0:
            hide_group(self.client_ip_group)
        else:
            show_group(self.client_ip_group)

    def wifi_ap_ip_configuration_changed(self, index):
        if index == 0:
            hide_group(self.ap_ip_group)
        else:
            show_group(self.ap_ip_group)

    def wifi_client_use_bssid_state_changed(self, state):
        if state == Qt.Checked:
            show_group(self.client_bssid_group)
        else:
            hide_group(self.client_bssid_group)

    def wifi_client_use_mac_state_changed(self, state):
        if state == Qt.Checked:
            show_group(self.client_mac_group)
        else:
            hide_group(self.client_mac_group)

    def wifi_ap_use_mac_state_changed(self, state):
        if state == Qt.Checked:
            show_group(self.ap_mac_group)
        else:
            hide_group(self.ap_mac_group)

    def wifi_mesh_use_router_bssid_state_changed(self, state):
        if state == Qt.Checked:
            show_group(self.mesh_router_bssid_group)
        else:
            hide_group(self.mesh_router_bssid_group)

    def wifi_client_change_password_changed(self, state):
        if state == Qt.Checked:
            self.wifi_client_password.setEnabled(True)
            self.wifi_client_password_show.setEnabled(True)
        else:
            self.wifi_client_password.setEnabled(False)
            self.wifi_client_password_show.setEnabled(False)

    def wifi_ap_change_password_changed(self, state):
        if state == Qt.Checked:
            self.wifi_ap_password.setEnabled(True)
            self.wifi_ap_password_show.setEnabled(True)
        else:
            self.wifi_ap_password.setEnabled(False)
            self.wifi_ap_password_show.setEnabled(False)

    def wifi_mesh_router_change_password_changed(self, state):
        if state == Qt.Checked:
            self.wifi_mesh_router_password.setEnabled(True)
            self.wifi_mesh_router_password_show.setEnabled(True)
        else:
            self.wifi_mesh_router_password.setEnabled(False)
            self.wifi_mesh_router_password_show.setEnabled(False)

    def wifi_secret_show_state_changed(self, state):
        if state == Qt.Checked:
            self.wifi_secret.setEchoMode(QLineEdit.Normal)
        else:
            self.wifi_secret.setEchoMode(QLineEdit.Password)

    def wifi_client_show_state_changed(self, state):
        if state == Qt.Checked:
            self.wifi_client_password.setEchoMode(QLineEdit.Normal)
        else:
            self.wifi_client_password.setEchoMode(QLineEdit.Password)

    def wifi_mesh_router_password_show_state_change(self, state):
        if state == Qt.Checked:
            self.wifi_mesh_router_password.setEchoMode(QLineEdit.Normal)
        else:
            self.wifi_mesh_router_password.setEchoMode(QLineEdit.Password)

    def wifi_ap_password_show_state_changed(self, state):
        if state == Qt.Checked:
            self.wifi_ap_password.setEchoMode(QLineEdit.Normal)
        else:
            self.wifi_ap_password.setEchoMode(QLineEdit.Password)

    def wifi_mesh_root_ip_configuration_changed(self, index):
        if index == 0:
            hide_group(self.mesh_root_static_ip_group)
        else:
            show_group(self.mesh_root_static_ip_group)

    def show_status_clicked(self):
        if self.wifi2_status is None:
            self.wifi2_status = Wifi2Status(self)

        self.wifi2_status.show()
        self.wifi2_status.update_status()

    def update_data(self):
        if self.wifi2_status is not None:
            if self.wifi2_status.isVisible():
                self.wifi2_status.update_status()

    def popup_ok(self, message='Successfully saved configuration.\nNew configuration will be used after reset of the Master Brick.'):
        QMessageBox.information(get_main_window(), 'Configuration', message, QMessageBox.Ok)

    def popup_fail(self, message='Could not save configuration.'):
        QMessageBox.critical(get_main_window(), 'Configuration', message, QMessageBox.Ok)
