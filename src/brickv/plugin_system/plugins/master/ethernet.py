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

from PyQt4.QtGui import QWidget, QMessageBox, QSpinBox, QRegExpValidator, QLabel, QLineEdit
from PyQt4.QtCore import QRegExp, QString, Qt

from brickv.plugin_system.plugins.master.ui_ethernet import Ui_Ethernet

from brickv.async_call import async_call

class SpinBoxHex(QSpinBox):
    def __init__(self, parent=None):
        super(SpinBoxHex, self).__init__(parent)
        self.validator = QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,2}"), self)
        self.setRange(0, 255)

    def fixCase(self, text):
        self.lineEdit().setText(text.toUpper())


    def validate(self, text, pos):
        return self.validator.validate(text, pos)

    def valueFromText(self, text):
        return text.toInt(16)[0]

    def textFromValue(self, value):
        s = QString.number(value, base=16).toUpper()
        if len(s) == 1:
            s = '0' + s
            
        return s

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
        self.last_port = 4223
        self.last_websocket_port = 4225

        if parent.version >= (2, 1, 0):
            async_call(self.master.get_ethernet_configuration, None, self.get_ethernet_configuration_async, self.parent.increase_error_count)
            async_call(self.master.get_ethernet_status, None, self.get_ethernet_status_init_async, self.parent.increase_error_count)
            self.ethernet_connection.currentIndexChanged.connect(self.connection_changed)
            self.ethernet_save.pressed.connect(self.save_pressed)
            self.ethernet_mac6 = SpinBoxHex()
            self.ethernet_mac5 = SpinBoxHex()
            self.ethernet_mac4 = SpinBoxHex()
            self.ethernet_mac3 = SpinBoxHex()
            self.ethernet_mac2 = SpinBoxHex()
            self.ethernet_mac1 = SpinBoxHex()
            self.mac_layout.addWidget(self.ethernet_mac6)
            self.mac_layout.addWidget(QLabel(':'))
            self.mac_layout.addWidget(self.ethernet_mac5)
            self.mac_layout.addWidget(QLabel(':'))
            self.mac_layout.addWidget(self.ethernet_mac4)
            self.mac_layout.addWidget(QLabel(':'))
            self.mac_layout.addWidget(self.ethernet_mac3)
            self.mac_layout.addWidget(QLabel(':'))
            self.mac_layout.addWidget(self.ethernet_mac2)
            self.mac_layout.addWidget(QLabel(':'))
            self.mac_layout.addWidget(self.ethernet_mac1)
        if parent.version >= (2, 2, 0):
            async_call(self.master.get_ethernet_websocket_configuration, None, self.get_ethernet_websocket_configuration_async, self.parent.increase_error_count)
            self.ethernet_socket_connections.valueChanged.connect(self.socket_connections_changed)
            self.ethernet_websocket_connections.valueChanged.connect(self.websocket_connections_changed)

            self.ethernet_port.valueChanged.connect(self.ethernet_port_changed)
            self.ethernet_websocket_port.valueChanged.connect(self.ethernet_websocket_port_changed)

            self.ethernet_use_auth.stateChanged.connect(self.ethernet_auth_changed)
            self.ethernet_show_characters.stateChanged.connect(self.ethernet_show_characters_changed)

            self.ethernet_show_characters.hide()
            self.ethernet_secret_label.hide()
            self.ethernet_secret.hide()

            async_call(self.master.get_ethernet_authentication_secret, None, self.get_ethernet_authentication_secret_async, self.parent.increase_error_count)
        else:
            self.ethernet_use_auth.setText("Use Authentication (FW Version >= 2.2.0 required)")
            self.ethernet_use_auth.setDisabled(True)
            self.ethernet_show_characters.hide()
            self.ethernet_secret_label.hide()
            self.ethernet_secret.hide()
            self.ethernet_websocket_port.setEnabled(False)
            self.ethernet_socket_connections.setEnabled(False)
            self.ethernet_websocket_connections.setEnabled(False)

    def destroy(self):
        pass

    def get_ethernet_authentication_secret_async(self, secret):
        self.ethernet_secret.setText(secret)
        if secret == '':
            self.ethernet_show_characters.hide()
            self.ethernet_secret_label.hide()
            self.ethernet_secret.hide()
            self.ethernet_use_auth.setChecked(Qt.Unchecked)
        else:
            self.ethernet_show_characters.show()
            self.ethernet_secret_label.show()
            self.ethernet_secret.show()
            self.ethernet_use_auth.setChecked(Qt.Checked)
            if self.ethernet_show_characters.isChecked():
                self.ethernet_secret.setEchoMode(QLineEdit.Normal)
            else:
                self.ethernet_secret.setEchoMode(QLineEdit.Password)
            
    def ethernet_auth_changed(self, state):
        if state == Qt.Checked:
            self.ethernet_show_characters.show()
            self.ethernet_secret_label.show()
            self.ethernet_secret.show()
            if self.ethernet_show_characters.isChecked():
                self.ethernet_secret.setEchoMode(QLineEdit.Normal)
            else:
                self.ethernet_secret.setEchoMode(QLineEdit.Password)
        else:
            self.ethernet_show_characters.hide()
            self.ethernet_secret_label.hide()
            self.ethernet_secret.hide()
            self.ethernet_secret.setText('')
        
    def ethernet_show_characters_changed(self, state):
        if state == Qt.Checked:
            self.ethernet_secret.setEchoMode(QLineEdit.Normal)
        else:
            self.ethernet_secret.setEchoMode(QLineEdit.Password)
            
    def ethernet_port_changed(self, value):
        if self.parent.version < (2, 2, 0):
            return
        
        if self.ethernet_websocket_port.value() == value:
            if self.last_port < value:
                value += 1
            else:
                value -= 1
            
            if value < 0:
                value = 1
            if value > 0xFFFF:
                value = 0xFFFE
                
            self.ethernet_port.setValue(value)
            
        self.last_port = value
             
    def ethernet_websocket_port_changed(self, value):
        if self.ethernet_port.value() == value:
            if self.last_websocket_port < value:
                value += 1
            else:
                value -= 1
                
            if value < 0:
                value = 1
            if value > 0xFFFF:
                value = 0xFFFE
                
            self.ethernet_websocket_port.setValue(value)
            
        self.last_websocket_port = value
            
    def socket_connections_changed(self, value):
        self.ethernet_websocket_connections.setValue(7 - value)
    
    def websocket_connections_changed(self, value):
        self.ethernet_socket_connections.setValue(7 - value)
            
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
        
    def get_ethernet_websocket_configuration_async(self, ws_conf):
        self.ethernet_websocket_port.setValue(ws_conf.port)
        self.ethernet_socket_connections.setValue(7 - ws_conf.sockets)
        self.ethernet_websocket_connections.setValue(ws_conf.sockets)

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
        
        self.ethernet_mac1.setValue(status.mac_address[5])
        self.ethernet_mac2.setValue(status.mac_address[4])
        self.ethernet_mac3.setValue(status.mac_address[3])
        self.ethernet_mac4.setValue(status.mac_address[2])
        self.ethernet_mac5.setValue(status.mac_address[1])
        self.ethernet_mac6.setValue(status.mac_address[0])
        
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
        
        mac = (self.ethernet_mac6.value(), self.ethernet_mac5.value(), self.ethernet_mac4.value(), self.ethernet_mac3.value(), self.ethernet_mac2.value(), self.ethernet_mac1.value())
            
        self.master.set_ethernet_configuration(connection, ip, sub, gw, port)
        self.master.set_ethernet_hostname(hostname)
        self.master.set_ethernet_mac_address(mac)
        
        if self.parent.version >= (2, 2, 0):
            port_websocket = self.ethernet_websocket_port.value()
            websocket_connections = self.ethernet_websocket_connections.value()
            secret = self.ethernet_secret.text()
            self.master.set_ethernet_authentication_secret(str(secret))
            
            self.master.set_ethernet_websocket_configuration(websocket_connections, port_websocket)
        
        saved_conf = self.master.get_ethernet_configuration()
        if saved_conf.ip == ip and saved_conf.gateway == gw and saved_conf.subnet_mask == sub and saved_conf.connection == connection and saved_conf.port == port:
            self.popup_ok()
        else:
            self.popup_fail()
        

    def update_data(self):
        self.update_data_counter += 1
        if self.update_data_counter == 10:
            self.update_data_counter = 0
            async_call(self.master.get_ethernet_status, None, self.get_ethernet_status_async, self.parent.increase_error_count)
            
    def popup_ok(self, message='Successfully saved configuration.\nNew configuration will be used after reset of the Master Brick.'):
        QMessageBox.information(self, "Configuration", message, QMessageBox.Ok)

    def popup_fail(self, message='Could not save configuration'):
        QMessageBox.critical(self, "Configuration", message, QMessageBox.Ok)
