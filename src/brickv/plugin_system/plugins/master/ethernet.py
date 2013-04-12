# -*- coding: utf-8 -*-
"""
Master Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>

ethernet.py: Ethernet for Master Plugin implementation

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

from PyQt4.QtGui import QWidget, QMessageBox

from ui_ethernet import Ui_Ethernet

from async_call import async_call
import infos

class Ethernet(QWidget, Ui_Ethernet):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.setupUi(self)
        self.parent = parent
        self.master = parent.master

        self.update_data_counter = 0
        self.connection = 0
        self.update_data_counter = 0
        self.last_status = None
        self.last_configuration = None

        if parent.version >= (2, 1, 0):
            async_call(self.master.get_ethernet_configuration, None, self.get_ethernet_configuration_async, self.parent.increase_error_count)
            async_call(self.master.get_ethernet_status, None, self.get_ethernet_status_init_async, self.parent.increase_error_count)
            self.ethernet_connection.currentIndexChanged.connect(self.connection_changed)
            self.ethernet_save.pressed.connect(self.save_pressed)
            
    def connection_changed(self, index):
        if index == 0:
            self.disable_ips()
        else:
            self.enable_ips()

    def disable_ips(self):
        self.ethernet_ip1.setEnabled(False)
        self.ethernet_ip2.setEnabled(False)
        self.ethernet_ip3.setEnabled(False)
        self.ethernet_ip4.setEnabled(False)
        self.ethernet_sub1.setEnabled(False)
        self.ethernet_sub2.setEnabled(False)
        self.ethernet_sub3.setEnabled(False)
        self.ethernet_sub4.setEnabled(False)
        self.ethernet_gw1.setEnabled(False)
        self.ethernet_gw2.setEnabled(False)
        self.ethernet_gw3.setEnabled(False)
        self.ethernet_gw4.setEnabled(False)
        
    def enable_ips(self):
        self.ethernet_ip1.setEnabled(True)
        self.ethernet_ip2.setEnabled(True)
        self.ethernet_ip3.setEnabled(True)
        self.ethernet_ip4.setEnabled(True)
        self.ethernet_sub1.setEnabled(True)
        self.ethernet_sub2.setEnabled(True)
        self.ethernet_sub3.setEnabled(True)
        self.ethernet_sub4.setEnabled(True)
        self.ethernet_gw1.setEnabled(True)
        self.ethernet_gw2.setEnabled(True)
        self.ethernet_gw3.setEnabled(True)
        self.ethernet_gw4.setEnabled(True)

    def get_ethernet_configuration_async(self, configuration):
        self.last_configuration = configuration
        self.ethernet_connection.setCurrentIndex(configuration.connection)
        if configuration.connection == 0:
            self.disable_ips()
        else:
            self.enable_ips()
        self.ethernet_port.setValue(configuration.port)

    def get_ethernet_status_init_async(self, status):
        self.ethernet_ip1.setValue(status.ip[3])
        self.ethernet_ip2.setValue(status.ip[2])
        self.ethernet_ip3.setValue(status.ip[1])
        self.ethernet_ip4.setValue(status.ip[0])
        self.ethernet_sub1.setValue(status.subnet_mask[3])
        self.ethernet_sub2.setValue(status.subnet_mask[2])
        self.ethernet_sub3.setValue(status.subnet_mask[1])
        self.ethernet_sub4.setValue(status.subnet_mask[0])
        self.ethernet_gw1.setValue(status.gateway[3])
        self.ethernet_gw2.setValue(status.gateway[2])
        self.ethernet_gw3.setValue(status.gateway[1])
        self.ethernet_gw4.setValue(status.gateway[0])
        self.ethernet_hostname.setText(status.hostname)
        
        self.get_ethernet_status_async(status)
        
    def get_ethernet_status_async(self, status):
        if self.ethernet_connection.currentIndex() == 0:
            self.ethernet_ip1.setValue(status.ip[3])
            self.ethernet_ip2.setValue(status.ip[2])
            self.ethernet_ip3.setValue(status.ip[1])
            self.ethernet_ip4.setValue(status.ip[0])
            self.ethernet_sub1.setValue(status.subnet_mask[3])
            self.ethernet_sub2.setValue(status.subnet_mask[2])
            self.ethernet_sub3.setValue(status.subnet_mask[1])
            self.ethernet_sub4.setValue(status.subnet_mask[0])
            self.ethernet_gw1.setValue(status.gateway[3])
            self.ethernet_gw2.setValue(status.gateway[2])
            self.ethernet_gw3.setValue(status.gateway[1])
            self.ethernet_gw4.setValue(status.gateway[0])

        self.last_status = status
        sl = []
        for m in status.mac_address:
            s = str(hex(m)).replace('0x', '')
            if len(s) == 1:
                s = '0' + s
            sl.append(s)
            
        self.ethernet_mac.setText('MAC Address: ' + ':'.join(sl))
        
        self.ethernet_count_rx.setText('Count RX: ' + str(status.rx_count))
        self.ethernet_count_tx.setText('Count TX: ' + str(status.tx_count))
        
    def save_pressed(self):
        port = self.ethernet_port.value()
        hostname = str(self.ethernet_hostname.text())
        connection = self.ethernet_connection.currentIndex()
        if connection == 0:
            ip = (0, 0, 0, 0)
            gw = (0, 0, 0, 0)
            sub = (0, 0, 0, 0)
        else:
            ip = (self.ethernet_ip4.value(), self.ethernet_ip3.value(), self.ethernet_ip2.value(), self.ethernet_ip1.value())
            gw = (self.ethernet_gw4.value(), self.ethernet_gw3.value(), self.ethernet_gw2.value(), self.ethernet_gw1.value())
            sub = (self.ethernet_sub4.value(), self.ethernet_sub3.value(), self.ethernet_sub2.value(), self.ethernet_sub1.value())
            
        self.master.set_ethernet_configuration(connection, ip, sub, gw, port)
        self.master.set_ethernet_hostname(hostname)
        
        saved_conf = self.master.get_ethernet_configuration()
        print saved_conf
        if saved_conf.ip == ip and saved_conf.gateway == gw and saved_conf.subnet_mask == sub and saved_conf.connection == connection and saved_conf.port == port:
            self.popup_ok()
        else:
            self.popup_fail()
        

    def update_data(self):
        self.update_data_counter += 1
        if self.update_data_counter == 10:
            self.update_data_counter = 0
            async_call(self.master.get_ethernet_status, None, self.get_ethernet_status_async, self.parent.increase_error_count)
            
    def popup_ok(self, message="Successfully saved configuration"):
        QMessageBox.information(self, "Configuration", message, QMessageBox.Ok)

    def popup_fail(self, message="Could not save configuration"):
        QMessageBox.critical(self, "Configuration", message, QMessageBox.Ok)