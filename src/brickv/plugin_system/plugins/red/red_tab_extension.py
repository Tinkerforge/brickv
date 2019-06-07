# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015, 2017 Matthias Bolte <matthias@tinkerforge.com>

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

import struct

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QMessageBox

from brickv.plugin_system.plugins.red.red_tab import REDTab
from brickv.plugin_system.plugins.red.ui_red_tab_extension import Ui_REDTabExtension
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.master.ui_rs485 import Ui_RS485
from brickv.plugin_system.plugins.red.ui_red_tab_extension_ethernet import Ui_Ethernet
from brickv.plugin_system.plugins.red.ui_red_tab_extension_unsupported import Ui_Unsupported
from brickv.plugin_system.plugins.red import config_parser
from brickv.async_call import async_call
from brickv.utils import get_main_window

def popup_ok(msg):
    QMessageBox.information(get_main_window(), 'Configuration', msg)

def popup_fail(msg):
    QMessageBox.critical(get_main_window(), 'Configuration', msg)

class RS485(QWidget, Ui_RS485):
    def __init__(self, parent, extension, config):
        QWidget.__init__(self)

        self.supported_baudrates = [500000, 250000, 166666, 125000, 100000, 83333, 71428, 62500, 55555, 50000, 45454, 41666]

        self.setupUi(self)

        self.save_button.setDisabled(True)
        self.save_button.setText("Wait for Extension discovery to finish...")

        self.parent = parent
        self.session = parent.session
        self.extension = extension
        self.config = config

        self.rs485_type.currentIndexChanged.connect(self.rs485_type_changed)
        self.save_button.clicked.connect(self.save_clicked)

        # Master address
        address = int(self.config['address'])
        self.address_spinbox.setValue(address)
        if address == 0:
            self.rs485_type.setCurrentIndex(1)
            self.rs485_type_changed(1)
        else:
            self.rs485_type.setCurrentIndex(0)
            self.rs485_type_changed(0)

        # Baudrate
        baudrate = int(self.config['baudrate'])
        self.speed_spinbox.setValue(baudrate)
        self.speed_spinbox.valueChanged.connect(self.check_baudrate)
        self.check_baudrate()

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
        self.lineedit_slave_addresses.setText(', '.join(map(str, slave_address)))

        # Update data stuff
        self.red_file_crc_error_count = None
        self.update_interval_crc_error_count = 2000
        self.timer_update_crc_error_count = QTimer(self)
        self.timer_update_crc_error_count.timeout.connect(self.do_update_crc_error_count)

    def start_update_data(self):
        self.timer_update_crc_error_count.start(self.update_interval_crc_error_count)

    def stop_update_data(self):
        self.timer_update_crc_error_count.stop()

    def cb_file_read(self, result):
        self.red_file_crc_error_count.release()

        if result.error == None:
            do_update = True
            config = config_parser.parse(result.data.decode('utf-8'))

            try:
                _ = int(config['crc_errors'])
            except:
                do_update = False

            if do_update:
                self.label_crc_errors.setText(config['crc_errors'])

        self.timer_update_crc_error_count.start(self.update_interval_crc_error_count)

    def cb_file_open_error(self):
        self.label_crc_errors.setText('?')
        self.timer_update_crc_error_count.start(self.update_interval_crc_error_count)

    def cb_file_open(self, result):
        if not isinstance(result, REDFile):
            self.timer_update_crc_error_count.start(self.update_interval_crc_error_count)
            return

        self.red_file_crc_error_count = result
        self.red_file_crc_error_count.read_async(self.red_file_crc_error_count.length, self.cb_file_read)

    def do_update_crc_error_count(self):
        self.timer_update_crc_error_count.stop()
        self.red_file_crc_error_count = REDFile(self.session)

        async_call(self.red_file_crc_error_count.open,
                   ("/tmp/extension_rs485_crc_error_count.conf", REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                   self.cb_file_open,
                   self.cb_file_open_error)

    def check_baudrate(self):
        supported = self.speed_spinbox.value() in self.supported_baudrates

        self.label_speed_warning.setVisible(not supported)
        self.save_button.setEnabled(supported and self.rs485_type.currentIndex() == 1)

    def save_clicked(self):
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

        new_config['slave_address'] = self.slave_text_to_int(self.lineedit_slave_addresses.text())
        new_config['slave_address'].append(0)
        new_config['type'] = 2
        new_config['extension'] = self.extension

        self.save_button.setDisabled(True)
        self.save_button.setText("Save RS485 Configuration (saving)")

        new_config['eeprom_file'] = REDFile(self.session)

        def cb_file_open_error(new_config):
            self.rs485_type_changed(self.rs485_type.currentIndex())
            popup_fail('Could not open file on RED Brick')

        async_call(new_config['eeprom_file'].open,
                   ('/tmp/new_eeprom_extension_' + str(new_config['extension']) + ".conf",
                    REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_TRUNCATE, 0o555, 0, 0),
                   lambda x: self.upload_eeprom_data(new_config, x),
                   lambda: cb_file_open_error(new_config))

    def upload_eeprom_data(self, new_config, result):
        if not isinstance(result, REDFile):
            self.rs485_type_changed(self.rs485_type.currentIndex())
            popup_fail('Could not open file on RED Brick')
            return

        eeprom = [0]*512

        # Type
        data = struct.pack('I', new_config['type'])
        eeprom[0] = data[0]
        eeprom[1] = data[1]
        eeprom[2] = data[2]
        eeprom[3] = data[3]

        # Slave address
        for i, slave in enumerate(new_config['slave_address']):
            data = struct.pack('I', slave)
            eeprom[100 + i*4] = data[0]
            eeprom[101 + i*4] = data[1]
            eeprom[102 + i*4] = data[2]
            eeprom[103 + i*4] = data[3]

        # Baudrate
        data = struct.pack('I', new_config['baudrate'])
        eeprom[400] = data[0]
        eeprom[401] = data[1]
        eeprom[402] = data[2]
        eeprom[403] = data[3]

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

        new_config['eeprom_file'].write_async(data, lambda x: cb_error(new_config, x), None)

    def rs485_type_changed(self, index):
        if index == 0:
            self.label_type_warning.show()
            self.label_slave_addresses.hide()
            self.lineedit_slave_addresses.hide()
            self.label_slave_addresses_help.hide()
            self.label_address.show()
            self.address_spinbox.show()
            self.save_button.setEnabled(False)
        else:
            self.label_type_warning.hide()
            self.label_slave_addresses.show()
            self.lineedit_slave_addresses.show()
            self.label_slave_addresses_help.show()
            self.label_address.hide()
            self.address_spinbox.hide()
            self.save_button.setEnabled(self.speed_spinbox.value() in self.supported_baudrates)

        self.save_button.setText("Save RS485 Configuration")

    def slave_text_to_int(self, slave_text):
        slave_text = slave_text.replace(' ', '')
        if slave_text == '':
            address_slave = []
        else:
            address_slave = list(map(int, slave_text.split(',')))

        return address_slave

class Ethernet(QWidget, Ui_Ethernet):
    def __init__(self, parent, extension, config):
        QWidget.__init__(self)

        self.setupUi(self)

        self.parent = parent
        self.session = parent.session
        self.extension = extension
        self.config = config

        mac = list(map(lambda x: int(x, 16), self.config['mac'].split(':')))
        self.ethernet_mac6.setValue(mac[0])
        self.ethernet_mac5.setValue(mac[1])
        self.ethernet_mac4.setValue(mac[2])
        self.ethernet_mac3.setValue(mac[3])
        self.ethernet_mac2.setValue(mac[4])
        self.ethernet_mac1.setValue(mac[5])

        self.ethernet_save.clicked.connect(self.save_clicked)

    def start_update_data(self):
        pass

    def stop_update_data(self):
        pass

    def save_clicked(self):
        new_config = {}
        new_config['type'] = 4
        new_config['extension'] = self.extension
        new_config['eeprom_file'] = REDFile(self.session)

        def cb_file_open_error(new_config):
            popup_fail('Could not open file on RED Brick')

        async_call(new_config['eeprom_file'].open,
                   ('/tmp/new_eeprom_extension_' + str(new_config['extension']) + ".conf",
                    REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_TRUNCATE, 0o555, 0, 0),
                   lambda x: self.upload_eeprom_data(new_config, x), lambda: cb_file_open_error(new_config))

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

        new_config['eeprom_file'].write_async(data, lambda x: cb_error(new_config, x), None)

class Unsupported(QWidget, Ui_Unsupported):
    def __init__(self, parent, extension, config):
        QWidget.__init__(self)

        self.setupUi(self)

    def start_update_data(self):
        pass

    def stop_update_data(self):
        pass

class REDTabExtension(REDTab, Ui_REDTabExtension):
    def __init__(self):
        REDTab.__init__(self)

        self.setupUi(self)

        self.red_file = [None, None]
        self.config_read_counter = 0
        self.tabbed_extension_widgets = []

        self.tab_widget.hide()
        self.label_status.setText('Discovering Extensions...')
        self.label_status.show()

    def extension_query_finished(self, result):
        for i in reversed(range(self.tab_widget.count())):
             self.tab_widget.removeTab(i)

        for extension, config in result:
            if config is None:
                continue

            try:
                t = int(config['type'])
            except:
                t = 0

            if t == 2:
                self.tabbed_extension_widgets.append(RS485(self, extension, config))
                self.tab_widget.addTab(self.tabbed_extension_widgets[len(self.tabbed_extension_widgets) - 1],
                                       'RS485')
                self.tabbed_extension_widgets[len(self.tabbed_extension_widgets) - 1].start_update_data()
            elif t == 4:
                self.tabbed_extension_widgets.append(Ethernet(self, extension, config))
                self.tab_widget.addTab(self.tabbed_extension_widgets[len(self.tabbed_extension_widgets) - 1],
                                       'Ethernet')
                self.tabbed_extension_widgets[len(self.tabbed_extension_widgets) - 1].start_update_data()
            else:
                extension_name = 'Unknown Extension'

                if t == 1:
                    extension_name = 'Chibi Extension'
                elif t == 3:
                    extension_name = 'WIFI Extension'
                elif t == 5:
                    extension_name = 'WIFI Extension 2.0'

                self.tabbed_extension_widgets.append(Unsupported(self, extension, config))
                self.tab_widget.addTab(self.tabbed_extension_widgets[len(self.tabbed_extension_widgets) - 1],
                                       extension_name)
                self.tabbed_extension_widgets[len(self.tabbed_extension_widgets) - 1].start_update_data()

        self.update_ui_state()

    def update_ui_state(self):
        if self.tab_widget.count() == 0:
            self.label_status.setText('Could not find any Master Extensions on RED Brick stack.')
            self.label_status.show()
            self.tab_widget.hide()
        else:
            self.label_status.hide()
            self.tab_widget.show()

    def tab_on_focus(self):
        pass

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        pass
