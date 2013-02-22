# -*- coding: utf-8 -*-
"""
Master Plugin
Copyright (C) 2010-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012-2013 Matthias Bolte <matthias@tinkerforge.com>

chibi.py: Chibi for Master Plugin implementation

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

from PyQt4.QtGui import QWidget

from ui_chibi import Ui_Chibi

from async_call import async_call
import infos

class Chibi(QWidget, Ui_Chibi):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.setupUi(self)

        self.parent = parent
        self.master = parent.master

        if parent.version >= (1, 1, 0):
            self.update_generator = self.init_update()
            self.update_generator.next()

    def init_update(self):
        self.update_address = 0
        self.update_chibi_slave_address = 0
        self.update_chibi_master_address = 0
        self.update_chibi_frequency = 0
        self.update_chibi_channel = 0

        def get_chibi_address_async(address_async):
            self.update_address = address_async
            self.update_generator.next()

        def get_chibi_slave_address_async(chibi_slave_address_async):
            self.update_chibi_slave_address = chibi_slave_address_async
            self.update_generator.next()

        def get_chibi_master_address_async(chibi_master_address_async):
            self.update_chibi_master_address = chibi_master_address_async
            self.update_generator.next()

        def get_chibi_frequency_async(chibi_frequency_async):
            self.update_chibi_frequency = chibi_frequency_async
            self.update_generator.next()

        def get_chibi_channel_async(chibi_channel_async):
            self.update_chibi_channel = chibi_channel_async
            self.update_generator.next()

        async_call(self.master.get_chibi_address, None, get_chibi_address_async, self.parent.increase_error_count)
        yield

        address_slave = []
        for i in range(32):
            async_call(self.master.get_chibi_slave_address, i, get_chibi_slave_address_async, self.parent.increase_error_count)
            yield

            if self.update_chibi_slave_address == 0:
                break
            else:
                address_slave.append(str(self.update_chibi_slave_address))

        address_slave_text = ', '.join(address_slave)

        async_call(self.master.get_chibi_master_address, None, get_chibi_master_address_async, self.parent.increase_error_count)
        yield
        async_call(self.master.get_chibi_frequency, None, get_chibi_frequency_async, self.parent.increase_error_count)
        yield
        async_call(self.master.get_chibi_channel, None, get_chibi_channel_async, self.parent.increase_error_count)
        yield

        typ = 0
        if self.update_address == self.update_chibi_master_address:
            typ = 1

            # trigger enumerate for chibi slaves
            if infos.infos[self.parent.uid].enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED:
                self.parent.ipcon.enumerate()

        self.lineedit_slave_address.setText(address_slave_text)
        self.address_spinbox.setValue(self.update_address)
        self.master_address_spinbox.setValue(self.update_chibi_master_address)
        self.chibi_frequency.setCurrentIndex(self.update_chibi_frequency)
        self.chibi_channel.setCurrentIndex(self.update_chibi_channel)

        self.save_button.pressed.connect(self.save_pressed)
        self.chibi_type.currentIndexChanged.connect(self.chibi_type_changed)
        self.chibi_frequency.currentIndexChanged.connect(self.chibi_frequency_changed)
        self.chibi_channel.currentIndexChanged.connect(self.chibi_channel_changed)

        self.chibi_type.setCurrentIndex(typ)
        self.chibi_type_changed(typ)
        self.new_max_count()

    def popup_ok(self):
        QMessageBox.information(self, "Configuration", "Successfully saved configuration", QMessageBox.Ok)

    def popup_fail(self):
        QMessageBox.critical(self, "Configuration", "Could not save configuration", QMessageBox.Ok)

    def new_max_count(self):
        channel = int(self.chibi_channel.currentText())
        self.chibi_channel.currentIndexChanged.disconnect(self.chibi_channel_changed)

        for i in range(12):
            self.chibi_channel.removeItem(0)

        index = self.chibi_frequency.currentIndex()

        if index == 0:
            self.chibi_channel.addItem("0")
            if channel != 0:
                channel = 0
        elif index in (1, 3):
            channel -= 1
            self.chibi_channel.addItem("1")
            self.chibi_channel.addItem("2")
            self.chibi_channel.addItem("3")
            self.chibi_channel.addItem("4")
            self.chibi_channel.addItem("5")
            self.chibi_channel.addItem("6")
            self.chibi_channel.addItem("7")
            self.chibi_channel.addItem("8")
            self.chibi_channel.addItem("9")
            self.chibi_channel.addItem("10")
            if not channel in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
                channel = 0
        elif index == 2:
            self.chibi_channel.addItem("0")
            self.chibi_channel.addItem("1")
            self.chibi_channel.addItem("2")
            self.chibi_channel.addItem("3")
            if not channel in (0, 1, 2, 3):
                channel = 0

        self.chibi_channel.setCurrentIndex(channel)
        self.chibi_channel.currentIndexChanged.connect(self.chibi_channel_changed)

    def save_pressed(self):
        typ = self.chibi_type.currentIndex()
        frequency = self.chibi_frequency.currentIndex()
        channel = self.chibi_channel.currentIndex()
        if frequency in (1, 3):
            channel += 1
        address = self.address_spinbox.value()
        address_master = self.master_address_spinbox.value()
        address_slave_text = str(self.lineedit_slave_address.text().replace(' ', ''))
        if address_slave_text == '':
            address_slave = []
        else:
            address_slave = map(int, address_slave_text.split(','))
            address_slave.append(0)

        self.master.set_chibi_frequency(frequency)
        self.master.set_chibi_channel(channel)
        self.master.set_chibi_address(address)
        if typ == 0:
            self.master.set_chibi_master_address(address_master)
        else:
            self.master.set_chibi_master_address(address)
            for i in range(len(address_slave)):
                self.master.set_chibi_slave_address(i, address_slave[i])

        new_frequency = self.master.get_chibi_frequency()
        new_channel = self.master.get_chibi_channel()
        new_address = self.master.get_chibi_address()
        if typ == 0:
            new_address_master = self.master.get_chibi_master_address()
            if new_frequency == frequency and \
               new_channel == channel and \
               new_address == address and \
               new_address_master == address_master:
                self.popup_ok()
            else:
                self.popup_fail()
        else:
            new_address_master = self.master.get_chibi_master_address()
            new_address_slave = []
            for i in range(len(address_slave)):
                new_address_slave.append(self.master.get_chibi_slave_address(i))
            if new_frequency == frequency and \
               new_channel == channel and \
               new_address == address and \
               new_address_master == address and \
               new_address_slave == address_slave:
                self.popup_ok()
            else:
                self.popup_fail()

    def index_changed_async(self, addr):
        self.slave_address_spinbox.setValue(addr)

    def index_changed(self, index):
        async_call(self.master.get_chibi_slave_address, index, self.index_changed_async, self.parent.increase_error_count)

    def chibi_frequency_changed(self, index):
        self.new_max_count()

    def chibi_channel_changed(self, index):
        channel = int(self.chibi_channel.itemText(index))

    def chibi_type_changed(self, index):
        if index == 0:
            self.label_slave_address.hide()
            self.lineedit_slave_address.hide()
            self.label_master_address.show()
            self.master_address_spinbox.show()
        else:
            self.label_master_address.hide()
            self.master_address_spinbox.hide()
            self.label_slave_address.show()
            self.lineedit_slave_address.show()

    def signal_strength_update(self, ss):
        ss_str = "%g dBm"  % (ss,)
        self.signal_strength_label.setText(ss_str)

    def update_data(self):
        async_call(self.master.get_chibi_signal_strength, None, self.signal_strength_update, self.parent.increase_error_count)
