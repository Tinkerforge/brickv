# -*- coding: utf-8 -*-
"""
Master Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

wifi2_status.py: Wifi2Status for Master Plugin implementation

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

from PyQt4.QtGui import QDialog

from brickv.plugin_system.plugins.master.ui_wifi2_status import Ui_Wifi2Status
from brickv.async_call import async_call
from brickv.utils import get_modeless_dialog_flags

def disable_group(group):
    for t in group:
        t[0].setEnabled(False)
        
def enable_group(group):
    for t in group:
        t[0].setEnabled(True)

class Wifi2Status(QDialog, Ui_Wifi2Status):
    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())

        self.setupUi(self)

        self.parent = parent
        self.master = self.parent.master
        self.client_group = [
            (self.wifi_client_status_status, self.wifi_client_status_status_label),
            (self.wifi_client_status_signal_strength, self.wifi_client_status_signal_strength_label),
            (self.wifi_client_status_ip, self.wifi_client_status_ip_label),
            (self.wifi_client_status_subnet_mask, self.wifi_client_status_subnet_mask_label),
            (self.wifi_client_status_gateway, self.wifi_client_status_gateway_label),
            (self.wifi_client_status_mac_address, self.wifi_client_status_mac_address_label),
            (self.wifi_client_status_rx, self.wifi_client_status_rx_label),
            (self.wifi_client_status_tx, self.wifi_client_status_tx_label),
        ]
        
        self.ap_group = [
            (self.wifi_ap_status_connected_count, self.wifi_ap_status_connected_count_label),
            (self.wifi_ap_status_ip, self.wifi_ap_status_ip_label),
            (self.wifi_ap_status_subnet_mask, self.wifi_ap_status_subnet_mask_label),
            (self.wifi_ap_status_gateway, self.wifi_ap_status_gateway_label),
            (self.wifi_ap_status_mac_address, self.wifi_ap_status_mac_address_label),
            (self.wifi_ap_status_rx, self.wifi_ap_status_rx_label),
            (self.wifi_ap_status_tx, self.wifi_ap_status_tx_label),
        ]

        self.wifi_status_button_close.clicked.connect(self.close)
        self.update_status()

    def update_status_async(self, s):
        if s.client_enabled:
            enable_group(self.client_group)
            client_enabled = 'Yes'
        else:
            disable_group(self.client_group)
            client_enabled = 'No'
        
        if s.client_status == 0:
            client_status = 'Idle'
        elif s.client_status == 1:
            client_status = 'Connecting'
        elif s.client_status == 2:
            client_status = 'Wrong Password'
        elif s.client_status == 3:
            client_status = 'No AP Found'
        elif s.client_status == 4:
            client_status = 'Connect Failed'
        elif s.client_status == 5:
            client_status = 'Got IP'
        else:
            client_status = 'Unknown'
        
        self.wifi_client_status_enabled.setText(client_enabled)
        self.wifi_client_status_status.setText(client_status)
        self.wifi_client_status_ip.setText("%d.%d.%d.%d" % s.client_ip)
        self.wifi_client_status_subnet_mask.setText("%d.%d.%d.%d" % s.client_subnet_mask)
        self.wifi_client_status_gateway.setText("%d.%d.%d.%d" % s.client_gateway)
        self.wifi_client_status_mac_address.setText("%2.2x:%2.2x:%2.2x:%2.2x:%2.2x:%2.2x" % s.client_mac_address)
        self.wifi_client_status_rx.setText(str(s.client_rx_count))
        self.wifi_client_status_tx.setText(str(s.client_tx_count))
        self.wifi_client_status_signal_strength.setText(str(s.client_rssi) + 'dB')

        if s.ap_enabled:
            enable_group(self.ap_group)
            ap_enabled = 'Yes'
        else:
            disable_group(self.ap_group)
            ap_enabled = 'No'
        
        self.wifi_ap_status_enabled.setText(ap_enabled)
        self.wifi_ap_status_ip.setText("%d.%d.%d.%d" % s.ap_ip)
        self.wifi_ap_status_subnet_mask.setText("%d.%d.%d.%d" % s.ap_subnet_mask)
        self.wifi_ap_status_gateway.setText("%d.%d.%d.%d" % s.ap_gateway)
        self.wifi_ap_status_mac_address.setText("%2.2x:%2.2x:%2.2x:%2.2x:%2.2x:%2.2x" % s.ap_mac_address)
        self.wifi_ap_status_rx.setText(str(s.ap_rx_count))
        self.wifi_ap_status_tx.setText(str(s.ap_tx_count))
        self.wifi_ap_status_connected_count.setText(str(s.ap_connected_count) + ' Clients')

    def update_status(self):
        async_call(self.master.get_wifi2_status, None, self.update_status_async, self.parent.parent.increase_error_count)
