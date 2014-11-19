# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

red_tab_extension.py: RED extension configuration

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

from PyQt4 import Qt, QtCore, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_extension import Ui_REDTabExtension
from brickv.plugin_system.plugins.red.api import *

from brickv.async_call import async_call
import struct
import time

from PyQt4.QtGui import QWidget, QMessageBox
from brickv.plugin_system.plugins.master.ui_rs485 import Ui_RS485
from brickv.plugin_system.plugins.master.ethernet import SpinBoxHex
from brickv.plugin_system.plugins.red.ui_red_tab_extension_ethernet import Ui_Ethernet

from brickv.plugin_system.plugins.red import config_parser

def popup_ok(msg):
    QMessageBox.information(None, 'Configuration', msg, QMessageBox.Ok)

def popup_fail(msg):
    QMessageBox.critical(None, 'Configuration', msg, QMessageBox.Ok)

class RS485(QWidget, Ui_RS485):
    def __init__(self, parent, extension, config):
        QWidget.__init__(self)

        self.setupUi(self)

        self.save_button.setDisabled(True)
        self.save_button.setText("Wait for Extension discovery to finish...")

        self.parent = parent
        self.session = parent.session
        self.extension = extension
        self.config = config

    def start(self):
        self.rs485_type.currentIndexChanged.connect(self.rs485_type_changed)
        self.save_button.pressed.connect(self.save_pressed)

        # Master address
        address = int(self.config['address'])
        self.address_spinbox.setValue(address)
        if address == 0:
            self.rs485_type.setCurrentIndex(1)
        else:
            self.rs485_type.setCurrentIndex(0)

        # Baudrate
        baudrate = int(self.config['baudrate'])
        self.speed_spinbox.setValue(baudrate)

        # Parity
        parity = self.config['parity']
        if parity == 'e':
            self.parity_combobox.setCurrentIndex(1)
        elif parity == 'o':
            self.parity_combobox.setCurrentIndex(2)
        else:
            self.parity_combobox.setCurrentIndex(0)

        # Stopbits
        stopbits = int(self.config['stopbits'])
        self.stopbits_spinbox.setValue(stopbits)

        # Slave addresses
        slave_address = self.slave_text_to_int(self.config['slave_address'])
        self.lineedit_slave_address.setText(', '.join(map(str, slave_address)))

    def save_pressed(self):
        new_config = {}

        new_config['baudrate'] = self.speed_spinbox.value()

        parity_index = self.parity_combobox.currentIndex()
        new_config['parity'] = 'n'
        if parity_index == 1:
            new_config['parity'] = 'e'
        elif parity_index == 2:
            new_config['parity'] = 'o'

        new_config['stopbits'] = self.stopbits_spinbox.value()

        if self.rs485_type.currentIndex() == 0:
            new_config['address'] = self.address_spinbox.value()
        else:
            new_config['address'] = 0

        new_config['slave_address'] = self.slave_text_to_int(self.lineedit_slave_address.text())
        new_config['slave_address'].append(0)
        new_config['type'] = 2
        new_config['extension'] = self.extension

        self.save_button.setDisabled(True)
        self.save_button.setText("Save RS485 Configuration (saving)")

        new_config['eeprom_file'] = REDFile(self.session)

        def cb_file_open_error(new_config):
            self.rs485_type_changed(self.rs485_type.currentIndex())
            popup_fail('Could not open file on RED Brick')

        async_call(new_config['eeprom_file'].open, ('/tmp/new_eeprom_extension_' + str(new_config['extension']) + ".conf", REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_TRUNCATE, 0555, 0, 0), lambda x: self.upload_eeprom_data(new_config, x), lambda: cb_file_open_error(new_config))

    def upload_eeprom_data(self, new_config, result):
        if not isinstance(result, REDFile):
            self.rs485_type_changed(self.rs485_type.currentIndex())
            popup_fail('Could not open file on RED Brick')
            return

        eeprom = [0]*512

        # Type
        data = struct.pack('I', new_config['type'])
        eeprom[0] = ord(data[0])
        eeprom[1] = ord(data[1])
        eeprom[2] = ord(data[2])
        eeprom[3] = ord(data[3])

        # Slave address
        for i, slave in enumerate(new_config['slave_address']):
            data = struct.pack('I', slave)
            eeprom[100 + i*4] = ord(data[0])
            eeprom[101 + i*4] = ord(data[1])
            eeprom[102 + i*4] = ord(data[2])
            eeprom[103 + i*4] = ord(data[3])

        # Baudrate
        data = struct.pack('I', new_config['baudrate'])
        eeprom[400] = ord(data[0])
        eeprom[401] = ord(data[1])
        eeprom[402] = ord(data[2])
        eeprom[403] = ord(data[3])

        # Parity
        eeprom[404] = ord(new_config['parity'])
        eeprom[405] = int(new_config['stopbits'])

        # Add start address
        data = [0, 0]
        data.extend(eeprom)

        def cb_error(new_config, error):
            new_config['eeprom_file'].release()
            if error is not None:
                self.rs485_type_changed(self.rs485_type.currentIndex())
                popup_fail('Could not write file on RED Brick: ' + str(error))
            else:
                self.save_button.setText("Configuration saved. Brick Viewer should reconnect now.")
                self.parent.script_manager.execute_script('restart_brickd', None)
                popup_ok('Saved configuration successfully, restarting brickd.')

        new_config['eeprom_file'].write_async(map(chr, data), lambda x: cb_error(new_config, x), None)

    def rs485_type_changed(self, index):
        if index == 0:
            self.label_slave_address.hide()
            self.lineedit_slave_address.hide()
            self.label.show()
            self.address_spinbox.show()
            self.save_button.setDisabled(True)
            self.save_button.setText("RS485 Slave currently not supported on RED Brick")
        else:
            self.label_slave_address.show()
            self.lineedit_slave_address.show()
            self.label.hide()
            self.address_spinbox.hide()
            self.save_button.setDisabled(False)
            self.save_button.setText("Save RS485 Configuration")

    def slave_text_to_int(self, slave_text):
        slave_text = slave_text.replace(' ', '')
        if slave_text == '':
            address_slave = []
        else:
            address_slave = map(int, slave_text.split(','))

        return address_slave

class Ethernet(QWidget, Ui_Ethernet):
    def __init__(self, parent, extension, config):
        QWidget.__init__(self)

        self.setupUi(self)

        self.parent = parent
        self.session = parent.session
        self.extension = extension
        self.config = config

        self.ethernet_mac6 = SpinBoxHex()
        self.ethernet_mac5 = SpinBoxHex()
        self.ethernet_mac4 = SpinBoxHex()
        self.ethernet_mac3 = SpinBoxHex()
        self.ethernet_mac2 = SpinBoxHex()
        self.ethernet_mac1 = SpinBoxHex()
        self.mac_layout.addWidget(self.ethernet_mac6)
        self.mac_layout.addWidget(QtGui.QLabel(':'))
        self.mac_layout.addWidget(self.ethernet_mac5)
        self.mac_layout.addWidget(QtGui.QLabel(':'))
        self.mac_layout.addWidget(self.ethernet_mac4)
        self.mac_layout.addWidget(QtGui.QLabel(':'))
        self.mac_layout.addWidget(self.ethernet_mac3)
        self.mac_layout.addWidget(QtGui.QLabel(':'))
        self.mac_layout.addWidget(self.ethernet_mac2)
        self.mac_layout.addWidget(QtGui.QLabel(':'))
        self.mac_layout.addWidget(self.ethernet_mac1)

    def start(self):
        mac = map(lambda x: int(x, 16), self.config['mac'].split(':'))
        self.ethernet_mac6.setValue(mac[0])
        self.ethernet_mac5.setValue(mac[1])
        self.ethernet_mac4.setValue(mac[2])
        self.ethernet_mac3.setValue(mac[3])
        self.ethernet_mac2.setValue(mac[4])
        self.ethernet_mac1.setValue(mac[5])

        self.ethernet_save.pressed.connect(self.save_pressed)

    def save_pressed(self):
        new_config = {}
        new_config['type'] = 4
        new_config['extension'] = self.extension
        new_config['eeprom_file'] = REDFile(self.session)

        def cb_file_open_error(new_config):
            popup_fail('Could not open file on RED Brick')

        async_call(new_config['eeprom_file'].open, ('/tmp/new_eeprom_extension_' + str(new_config['extension']) + ".conf", REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_TRUNCATE, 0555, 0, 0), lambda x: self.upload_eeprom_data(new_config, x), lambda: cb_file_open_error(new_config))

    def upload_eeprom_data(self, new_config, result):
        if not isinstance(result, REDFile):
            popup_fail('Could not open file on RED Brick')
            return

        eeprom = [self.ethernet_mac6.value(),
                  self.ethernet_mac5.value(),
                  self.ethernet_mac4.value(),
                  self.ethernet_mac3.value(),
                  self.ethernet_mac2.value(),
                  self.ethernet_mac1.value()]

        # Add start address
        data = [32*4, 0]
        data.extend(eeprom)

        def cb_error(new_config, error):
            new_config['eeprom_file'].release()
            if error is not None:
                popup_fail('Could not write file on RED Brick: ' + str(error))
            else:
                self.ethernet_save.setText("Configuration saved. Brick Viewer should reconnect now.")
                self.parent.script_manager.execute_script('restart_brickd', None)
                popup_ok('Saved configuration successfully, restarting brickd.')

        new_config['eeprom_file'].write_async(map(chr, data), lambda x: cb_error(new_config, x), None)

class REDTabExtension(QtGui.QWidget, Ui_REDTabExtension):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session        = None # set from RED after construction
        self.script_manager = None # set from RED after construction

        self.red_file = [None, None]
        self.extensions_found = 0
        self.extensions = []

    def set_extension_label(self):
        if len(self.extensions) == 0:
            self.extension_label.setText('Could not find any Master Extensions on RED Brick stack.')
        else:
            self.extension_label.setText('Found ' + ' and '.join(self.extensions) + ' on RED Brick stack.')

        for i in range(self.extension_layout.count()):
            self.extension_layout.itemAt(i).widget().start()

    def set_not_present_extension(self, extension):
        # TODO: Give the user an options to change the extension type here?
        pass

    def set_rs485_extension(self, extension, config):
        self.extensions.append('RS485 Extension')
        self.extension_layout.addWidget(RS485(self, extension, config))

    def set_ethernet_extension(self, extension, config):
        self.extensions.append('Ethernet Extension')
        self.extension_layout.addWidget(Ethernet(self, extension, config))

    def cb_file_read(self, extension, result):
        self.red_file[extension].release()

        if result.error == None:
            config = config_parser.parse(result.data.decode('utf-8'))
            try:
                t = int(config['type'])
            except:
                t = 0

            if t == 2:
                self.set_rs485_extension(extension, config)
            elif t == 4:
                self.set_ethernet_extension(extension, config)
            else:
                self.set_not_present_extension(extension)

        self.extensions_found += 1
        if self.extensions_found == 2:
            self.set_extension_label()

    def cb_file_open_error(self, extension):
        self.set_not_present_extension(extension)

        self.extensions_found += 1
        if self.extensions_found == 2:
            self.set_extension_label()

    def cb_file_open(self, extension, result):
        if not isinstance(result, REDFile):
            return

        self.red_file[extension] = result
        self.red_file[extension].read_async(self.red_file[extension].length, lambda x: self.cb_file_read(extension, x), None)

    def tab_on_focus(self):
        self.extensions_found = 0
        self.extensions = []
        for i in reversed(range(self.extension_layout.count())): 
            self.extension_layout.itemAt(i).widget().setParent(None)

        self.red_file[0] = REDFile(self.session)
        async_call(self.red_file[0].open, ("/tmp/extension_position_0.conf", REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0), lambda x: self.cb_file_open(0, x), lambda: self.cb_file_open_error(0))

        self.red_file[1] = REDFile(self.session)
        async_call(self.red_file[1].open, ("/tmp/extension_position_1.conf", REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0), lambda x: self.cb_file_open(1, x), lambda: self.cb_file_open_error(1))

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        pass
