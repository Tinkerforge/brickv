# -*- coding: utf-8 -*-
"""
Master Plugin
Copyright (C) 2010-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012-2013 Matthias Bolte <matthias@tinkerforge.com>

rs485.py: RS485 for Master Plugin implementation

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

from bindings.ip_connection import IPConnection

from PyQt4.QtGui import QWidget, QMessageBox
from ui_rs485 import Ui_RS485

from async_call import async_call
import infos

class RS485(QWidget, Ui_RS485):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.setupUi(self)

        self.parent = parent
        self.master = parent.master

        if parent.version >= (1, 2, 0):
            async_call(self.master.get_rs485_configuration, None, self.get_rs485_configuration_async, self.parent.increase_error_count)
            self.update_generator = self.update_addresses()
            self.update_generator.next()

    def update_addresses(self):
        self.update_address = 0
        self.update_address_slave = 0

        def get_rs485_address_async(address_async):
            self.update_address = address_async
            self.update_generator.next()

        def get_rs485_slave_address_async(update_address_slave_async):
            self.update_address_slave = update_address_slave_async
            self.update_generator.next()

        async_call(self.master.get_rs485_address, None, get_rs485_address_async, self.parent.increase_error_count)
        yield

        address_slave = []
        for i in range(32):
            async_call(self.master.get_rs485_slave_address, i, get_rs485_slave_address_async, self.parent.increase_error_count)
            yield

            if self.update_address_slave == 0:
                break
            else:
                address_slave.append(str(self.update_address_slave))

        address_slave_text = ', '.join(address_slave)

        typ = 0
        if self.update_address == 0:
            typ = 1

            # trigger enumerate for rs485 slaves
            if infos.infos[self.parent.uid].enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED:
                self.parent.ipcon.enumerate()

        self.lineedit_slave_address.setText(address_slave_text)
        self.address_spinbox.setValue(self.update_address)

        self.save_button.pressed.connect(self.save_pressed)
        self.rs485_type.currentIndexChanged.connect(self.rs485_type_changed)

        self.rs485_type.setCurrentIndex(typ)
        self.rs485_type_changed(typ)

    def get_rs485_configuration_async(self, configuration):
        speed, parity, stopbits = configuration
        self.speed_spinbox.setValue(speed)
        if parity == 'e':
            self.parity_combobox.setCurrentIndex(1)
        elif parity == 'o':
            self.parity_combobox.setCurrentIndex(2)
        else:
            self.parity_combobox.setCurrentIndex(0)
        self.stopbits_spinbox.setValue(stopbits)


    def destroy(self):
        pass

    def popup_ok(self):
        QMessageBox.information(self, "Configuration", "Successfully saved configuration", QMessageBox.Ok)

    def popup_fail(self):
        QMessageBox.critical(self, "Configuration", "Could not save configuration", QMessageBox.Ok)

    def save_pressed(self):
        speed = self.speed_spinbox.value()
        parity_index = self.parity_combobox.currentIndex()
        parity = 'n'
        if parity_index == 1:
            parity = 'e'
        elif parity_index == 2:
            parity = 'o'
        stopbits = self.stopbits_spinbox.value()

        self.master.set_rs485_configuration(speed, parity, stopbits)

        typ = self.rs485_type.currentIndex()
        if typ == 0:
            address = self.address_spinbox.value()
        else:
            address = 0

        address_slave_text = str(self.lineedit_slave_address.text().replace(' ', ''))
        if address_slave_text == '':
            address_slave = []
        else:
            address_slave = map(int, address_slave_text.split(','))
            address_slave.append(0)

        self.master.set_rs485_address(address)
        if typ == 1:
            for i in range(len(address_slave)):
                self.master.set_rs485_slave_address(i, address_slave[i])

        new_address = self.master.get_rs485_address()
        if typ == 0:
            if new_address == address:
                self.popup_ok()
            else:
                self.popup_fail()
        else:
            new_address_slave = []
            for i in range(len(address_slave)):
                new_address_slave.append(self.master.get_rs485_slave_address(i))
            if new_address == 0 and new_address_slave == address_slave:
                self.popup_ok()
            else:
                self.popup_fail()

    def rs485_type_changed(self, index):
        if index == 0:
            self.label_slave_address.hide()
            self.lineedit_slave_address.hide()
            self.label.show()
            self.address_spinbox.show()
        else:
            self.label_slave_address.show()
            self.lineedit_slave_address.show()
            self.label.hide()
            self.address_spinbox.hide()

    def update_data(self):
        pass
