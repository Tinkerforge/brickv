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

from PyQt4.QtGui import QWidget, QMessageBox, QLineEdit
from PyQt4.QtCore import Qt

from brickv.plugin_system.plugins.master.ui_wifi2 import Ui_Wifi2
from brickv.async_call import async_call

def show_group(group):
    for widget in group:
        widget.setVisible(True)
        
def hide_group(group):
    for widget in group:
        widget.setVisible(False)

class Wifi2(QWidget, Ui_Wifi2):
    def __init__(self, parent):
        QWidget.__init__(self)

        self.setupUi(self)

        self.parent = parent
        self.master = parent.master

        self.update_data_counter = 0
        self.connection = 0

        if parent.firmware_version < (2, 4, 0):
            # This should not be possible
            return

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
        self.client_enc_group = [self.wifi_client_password_label, self.wifi_client_password, self.wifi_client_password_show]

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
        self.ap_enc_group = [self.wifi_ap_password_label, self.wifi_ap_password, self.wifi_ap_password_show]

        # Passwords
        self.wifi_secret_show_state_changed(Qt.Unchecked)
        self.wifi_client_show_state_changed(Qt.Unchecked)
        self.wifi_ap_show_state_changed(Qt.Unchecked)
        self.wifi_show_characters.stateChanged.connect(self.wifi_secret_show_state_changed)
        self.wifi_client_password_show.stateChanged.connect(self.wifi_client_show_state_changed)
        self.wifi_ap_password_show.stateChanged.connect(self.wifi_ap_show_state_changed)

        # Use passwords
        self.wifi_client_encryption_changed(1)
        self.wifi_ap_encryption_changed(4)
        self.wifi_use_auth_state_changed(Qt.Unchecked)
        self.wifi_client_encryption.currentIndexChanged.connect(self.wifi_client_encryption_changed)
        self.wifi_ap_encryption.currentIndexChanged.connect(self.wifi_ap_encryption_changed)
        self.wifi_use_auth.stateChanged.connect(self.wifi_use_auth_state_changed)
        
        # MACs
        self.wifi_client_use_bssid_state_changed(Qt.Unchecked)
        self.wifi_client_use_mac_state_changed(Qt.Unchecked)
        self.wifi_ap_use_mac_state_changed(Qt.Unchecked)
        self.wifi_client_use_bssid.stateChanged.connect(self.wifi_client_use_bssid_state_changed)
        self.wifi_client_use_mac.stateChanged.connect(self.wifi_client_use_mac_state_changed)
        self.wifi_ap_use_mac.stateChanged.connect(self.wifi_ap_use_mac_state_changed)
        
        # IP Configuration
        self.wifi_client_ip_configuration_changed(0)
        self.wifi_ap_ip_configuration_changed(0)
        self.wifi_client_ip_configuration.currentIndexChanged.connect(self.wifi_client_ip_configuration_changed)
        self.wifi_ap_ip_configuration.currentIndexChanged.connect(self.wifi_ap_ip_configuration_changed)
        
        # Mode
        self.wifi_mode_changed(0)
        self.wifi_mode.currentIndexChanged.connect(self.wifi_mode_changed)

    def wifi_mode_changed(self, index):
        if index == 0:
            self.wifi_groupbox_ap.setVisible(False)
            self.wifi_groupbox_client.setVisible(True)
        elif index == 1:
            self.wifi_groupbox_client.setVisible(False)
            self.wifi_groupbox_ap.setVisible(True)
        elif index == 2:
            self.wifi_groupbox_client.setVisible(True)
            self.wifi_groupbox_ap.setVisible(True)
            
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
            
    def wifi_ap_show_state_changed(self, state):
        if state == Qt.Checked:
            self.wifi_ap_password.setEchoMode(QLineEdit.Normal)
        else:
            self.wifi_ap_password.setEchoMode(QLineEdit.Password)
        
    def destroy(self):
        pass
#        if self.wifi_status:
#            self.wifi_status.close()

    def update_data(self):
        pass
    