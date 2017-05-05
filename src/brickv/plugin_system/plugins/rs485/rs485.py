# -*- coding: utf-8 -*-
"""
RS485 Plugin
Copyright (C) 2016 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2017 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

rs485.py: RS485 Plugin Implementation

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

import random

from PyQt4.QtGui import QTextCursor, QAction, QMessageBox
from PyQt4.QtCore import pyqtSignal

from brickv.bindings.bricklet_rs485 import BrickletRS485
from brickv.plugin_system.plugins.rs485.ui_rs485 import Ui_RS485
from brickv.async_call import async_call
from brickv.hex_validator import HexValidator
from brickv.callback_emulator import CallbackEmulator
from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.rs485.qhexedit import QHexeditWidget
from brickv.utils import get_main_window

MODE_RS485 = 0
MODE_MODBUS_SLAVE_RTU = 1
MODE_MODBUS_MASTER_RTU = 2

MODBUS_F_IDX_READ_COILS = 0
MODBUS_F_IDX_READ_HOLDING_REGISTERS = 1
MODBUS_F_IDX_WRITE_SINGLE_COIL = 2
MODBUS_F_IDX_WRITE_SINGLE_REGISTER = 3
MODBUS_F_IDX_WRITE_MULTIPLE_COILS = 4
MODBUS_F_IDX_WRITE_MULTIPLE_REGISTERS = 5
MODBUS_F_IDX_READ_DISCRETE_INPUTS = 6
MODBUS_F_IDX_READ_INPUT_REGISTERS = 7

MSG_ERR_REQUEST_PROCESS = "Failed to process the request"
MSG_ERR_NOT_MODBUS_MASTER = "The Bricklet needs to be in Modbus master mode to perform this operation"

class RS485(COMCUPluginBase, Ui_RS485):
    qtcb_read = pyqtSignal(int, object)

    # Modbus specific.
    qtcb_modbus_slave_read_coils_request = pyqtSignal(int, int, int)
    qtcb_modbus_master_read_coils_response = pyqtSignal(int, int, object)
    qtcb_modbus_slave_read_holding_registers_request = pyqtSignal(int, int, int)
    qtcb_modbus_master_read_holding_registers_response = pyqtSignal(int, int, object)
    qtcb_modbus_slave_write_single_coil_request = pyqtSignal(int, int, int)
    qtcb_modbus_master_write_single_coil_response = pyqtSignal(int, int)
    qtcb_modbus_slave_write_single_register_request = pyqtSignal(int, int, int)
    qtcb_modbus_master_write_single_register_response = pyqtSignal(int, int)
    qtcb_modbus_slave_write_multiple_coils_request = pyqtSignal(int, int, int, object)
    qtcb_modbus_master_write_multiple_coils_response = pyqtSignal(int, int)
    qtcb_modbus_slave_write_multiple_registers_request = pyqtSignal(int, int, int, object)
    qtcb_modbus_master_write_multiple_registers_response = pyqtSignal(int, int)
    qtcb_modbus_slave_read_discrete_inputs_request = pyqtSignal(int, int, int)
    qtcb_modbus_master_read_discrete_inputs_response = pyqtSignal(int, int, object)
    qtcb_modbus_slave_read_input_registers_request = pyqtSignal(int, int, int)
    qtcb_modbus_master_read_input_registers_response = pyqtSignal(int, int, object)

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletRS485, *args)

        self.setupUi(self)
        self.text.setReadOnly(True)

        self.rs485 = self.device
        self.cbe_error_count = CallbackEmulator(self.rs485.get_error_count,
                                                self.cb_error_count,
                                                self.increase_error_count)

        self.cbe_error_count_modbus = CallbackEmulator(self.rs485.get_modbus_common_error_count,
                                                       self.cb_error_count_modbus,
                                                       self.increase_error_count)

        self.read_callback_was_enabled = False

        self.qtcb_read.connect(self.cb_read)

        # Modbus specific.
        self.qtcb_modbus_slave_read_coils_request.connect(self.cb_modbus_slave_read_coils_request)
        self.qtcb_modbus_master_read_coils_response.connect(self.cb_modbus_master_read_coils_response)
        self.qtcb_modbus_slave_read_holding_registers_request.connect(self.cb_modbus_slave_read_holding_registers_request)
        self.qtcb_modbus_master_read_holding_registers_response.connect(self.cb_modbus_master_read_holding_registers_response)
        self.qtcb_modbus_slave_write_single_coil_request.connect(self.cb_modbus_slave_write_single_coil_request)
        self.qtcb_modbus_master_write_single_coil_response.connect(self.cb_modbus_master_write_single_coil_response)
        self.qtcb_modbus_slave_write_single_register_request.connect(self.cb_modbus_slave_write_single_register_request)
        self.qtcb_modbus_master_write_single_register_response.connect(self.cb_modbus_master_write_single_register_response)
        self.qtcb_modbus_slave_write_multiple_coils_request.connect(self.cb_modbus_slave_write_multiple_coils_request)
        self.qtcb_modbus_master_write_multiple_coils_response.connect(self.cb_modbus_master_write_multiple_coils_response)
        self.qtcb_modbus_slave_write_multiple_registers_request.connect(self.cb_modbus_slave_write_multiple_registers_request)
        self.qtcb_modbus_master_write_multiple_registers_response.connect(self.cb_modbus_master_write_multiple_registers_response)
        self.qtcb_modbus_slave_read_discrete_inputs_request.connect(self.cb_modbus_slave_read_discrete_inputs_request)
        self.qtcb_modbus_master_read_discrete_inputs_response.connect(self.cb_modbus_master_read_discrete_inputs_response)
        self.qtcb_modbus_slave_read_input_registers_request.connect(self.cb_modbus_slave_read_input_registers_request)
        self.qtcb_modbus_master_read_input_registers_response.connect(self.cb_modbus_master_read_input_registers_response)

        self.rs485.register_callback(self.rs485.CALLBACK_READ,
                                     self.qtcb_read.emit)

        # Modbus specific.
        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_SLAVE_READ_COILS_REQUEST,
                                     self.qtcb_modbus_slave_read_coils_request.emit)

        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_MASTER_READ_COILS_RESPONSE,
                                     self.qtcb_modbus_master_read_coils_response.emit)

        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_SLAVE_READ_HOLDING_REGISTERS_REQUEST,
                                     self.qtcb_modbus_slave_read_holding_registers_request.emit)

        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_MASTER_READ_HOLDING_REGISTERS_RESPONSE,
                                     self.qtcb_modbus_master_read_holding_registers_response.emit)

        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_SLAVE_WRITE_SINGLE_COIL_REQUEST,
                                     self.qtcb_modbus_slave_write_single_coil_request.emit)

        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_MASTER_WRITE_SINGLE_COIL_RESPONSE,
                                     self.qtcb_modbus_master_write_single_coil_response.emit)

        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_SLAVE_WRITE_SINGLE_REGISTER_REQUEST,
                                     self.qtcb_modbus_slave_write_single_register_request.emit)

        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_MASTER_WRITE_SINGLE_REGISTER_RESPONSE,
                                     self.qtcb_modbus_master_write_single_register_response.emit)

        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_SLAVE_WRITE_MULTIPLE_COILS_REQUEST,
                                     self.qtcb_modbus_slave_write_multiple_coils_request.emit)

        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_MASTER_WRITE_MULTIPLE_COILS_RESPONSE,
                                     self.qtcb_modbus_master_write_multiple_coils_response.emit)

        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_SLAVE_WRITE_MULTIPLE_REGISTERS_REQUEST,
                                     self.qtcb_modbus_slave_write_multiple_registers_request.emit)

        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_MASTER_WRITE_MULTIPLE_REGISTERS_RESPONSE,
                                     self.qtcb_modbus_master_write_multiple_registers_response.emit)

        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_SLAVE_READ_DISCRETE_INPUTS_REQUEST,
                                     self.qtcb_modbus_slave_read_discrete_inputs_request.emit)

        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_MASTER_READ_DISCRETE_INPUTS_RESPONSE,
                                     self.qtcb_modbus_master_read_discrete_inputs_response.emit)

        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_SLAVE_READ_INPUT_REGISTERS_REQUEST,
                                     self.qtcb_modbus_slave_read_input_registers_request.emit)

        self.rs485.register_callback(self.rs485.CALLBACK_MODBUS_MASTER_READ_INPUT_REGISTERS_RESPONSE,
                                     self.qtcb_modbus_master_read_input_registers_response.emit)

        self.rs485_input_combobox.addItem("")
        self.rs485_input_combobox.lineEdit().returnPressed.connect(self.input_changed)

        self.rs485_input_line_ending_lineedit.setValidator(HexValidator())
        self.rs485_input_line_ending_combobox.currentIndexChanged.connect(self.line_ending_changed)
        self.rs485_input_line_ending_lineedit.editingFinished.connect(self.line_ending_changed)

        self.mode_combobox.currentIndexChanged.connect(self.mode_changed)
        self.baudrate_spinbox.valueChanged.connect(self.configuration_changed)
        self.parity_combobox.currentIndexChanged.connect(self.configuration_changed)
        self.stopbits_spinbox.valueChanged.connect(self.configuration_changed)
        self.wordlength_spinbox.valueChanged.connect(self.configuration_changed)
        self.duplex_combobox.currentIndexChanged.connect(self.configuration_changed)
        self.text_type_combobox.currentIndexChanged.connect(self.text_type_changed)

        # Modbus specific.
        self.modbus_slave_address_spinbox.valueChanged.connect(self.configuration_changed)
        self.modbus_master_param2_spinbox.valueChanged.connect(self.modbus_master_param2_changed)
        self.modbus_master_function_combobox.currentIndexChanged.connect(self.modbus_master_function_changed)

        self.hextext = QHexeditWidget(self.text.font())
        self.hextext.hide()
        self.layout().insertWidget(2, self.hextext)

        self.button_clear_text.clicked.connect(lambda: self.text.setPlainText(""))
        self.button_clear_text.clicked.connect(self.hextext.clear)

        self.modbus_master_send_button.clicked.connect(self.master_send_clicked)
        self.apply_button.clicked.connect(self.apply_clicked)

        self.error_overrun = 0
        self.error_parity = 0
        self.error_stream_oos = 0
        self.last_char = ''

        self.modbus_master_function_combobox.setCurrentIndex(-1)
        self.modbus_master_function_combobox.setCurrentIndex(0)

        self.gui_group_rs485 = [self.label_error_overrun_name,
                                self.label_error_overrun,
                                self.label_error_parity_name,
                                self.label_error_parity,
                                self.label_error_stream_name,
                                self.label_error_stream,
                                self.rs485_input_label,
                                self.rs485_input_combobox,
                                self.rs485_input_line_ending_combobox,
                                self.rs485_input_line_ending_lineedit]

        self.gui_group_modbus_master = [self.label_error_overrun_name,
                                        self.label_error_overrun,
                                        self.label_error_parity_name,
                                        self.label_error_parity,
                                        self.label_error_stream_name,
                                        self.label_error_stream,
                                        self.label_error_modbus_timeout_name,
                                        self.label_error_modbus_timeout,
                                        self.label_error_modbus_checksum_name,
                                        self.label_error_modbus_checksum,
                                        self.label_error_modbus_frame_size_name,
                                        self.label_error_modbus_frame_size,
                                        self.label_error_modbus_illegal_function_name,
                                        self.label_error_modbus_illegal_function,
                                        self.label_error_modbus_illegal_data_address_name,
                                        self.label_error_modbus_illegal_data_address,
                                        self.label_error_modbus_illegal_data_value_name,
                                        self.label_error_modbus_illegal_data_value,
                                        self.label_error_modbus_slave_device_failure_name,
                                        self.label_error_modbus_slave_device_failure,
                                        self.modbus_master_function_label,
                                        self.modbus_master_function_combobox,
                                        self.modbus_master_slave_address_label,
                                        self.modbus_master_slave_address_spinbox,
                                        self.modbus_master_param1_label,
                                        self.modbus_master_param1_spinbox,
                                        self.modbus_master_param2_label,
                                        self.modbus_master_param2_spinbox,
                                        self.modbus_master_request_timeout_label,
                                        self.modbus_master_request_timeout_spinbox,
                                        self.modbus_master_send_button]

        self.gui_group_modbus_slave = [self.label_error_overrun_name,
                                       self.label_error_overrun,
                                       self.label_error_parity_name,
                                       self.label_error_parity,
                                       self.label_error_stream_name,
                                       self.label_error_stream,
                                       self.label_error_modbus_timeout_name,
                                       self.label_error_modbus_timeout,
                                       self.label_error_modbus_checksum_name,
                                       self.label_error_modbus_checksum,
                                       self.label_error_modbus_frame_size_name,
                                       self.label_error_modbus_frame_size,
                                       self.label_error_modbus_illegal_function_name,
                                       self.label_error_modbus_illegal_function,
                                       self.label_error_modbus_illegal_data_address_name,
                                       self.label_error_modbus_illegal_data_address,
                                       self.label_error_modbus_illegal_data_value_name,
                                       self.label_error_modbus_illegal_data_value,
                                       self.label_error_modbus_slave_device_failure_name,
                                       self.label_error_modbus_slave_device_failure,
                                       self.modbus_slave_address_label,
                                       self.modbus_slave_address_spinbox]

        self.mode_changed(0)

        self.com_led_off_action = QAction('Off', self)
        self.com_led_off_action.triggered.connect(lambda: self.rs485.set_communication_led_config(BrickletRS485.COMMUNICATION_LED_CONFIG_OFF))
        self.com_led_on_action = QAction('On', self)
        self.com_led_on_action.triggered.connect(lambda: self.rs485.set_communication_led_config(BrickletRS485.COMMUNICATION_LED_CONFIG_ON))
        self.com_led_show_heartbeat_action = QAction('Show Heartbeat', self)
        self.com_led_show_heartbeat_action.triggered.connect(lambda: self.rs485.set_communication_led_config(BrickletRS485.COMMUNICATION_LED_CONFIG_SHOW_HEARTBEAT))
        self.com_led_show_communication_action = QAction('Show Com', self)
        self.com_led_show_communication_action.triggered.connect(lambda: self.rs485.set_communication_led_config(BrickletRS485.COMMUNICATION_LED_CONFIG_SHOW_COMMUNICATION))

        self.extra_configs += [(1, 'Com LED:', [self.com_led_off_action,
                                                self.com_led_on_action,
                                                self.com_led_show_heartbeat_action,
                                                self.com_led_show_communication_action])]

        self.error_led_off_action = QAction('Off', self)
        self.error_led_off_action.triggered.connect(lambda: self.rs485.set_error_led_config(BrickletRS485.ERROR_LED_CONFIG_OFF))
        self.error_led_on_action = QAction('On', self)
        self.error_led_on_action.triggered.connect(lambda: self.rs485.set_error_led_config(BrickletRS485.ERROR_LED_CONFIG_ON))
        self.error_led_show_heartbeat_action = QAction('Show Heartbeat', self)
        self.error_led_show_heartbeat_action.triggered.connect(lambda: self.rs485.set_error_led_config(BrickletRS485.ERROR_LED_CONFIG_SHOW_HEARTBEAT))
        self.error_led_show_error_action = QAction('Show Error', self)
        self.error_led_show_error_action.triggered.connect(lambda: self.rs485.set_error_led_config(BrickletRS485.ERROR_LED_CONFIG_SHOW_ERROR))

        self.extra_configs += [(1, 'Error LED:', [self.error_led_off_action,
                                                  self.error_led_on_action,
                                                  self.error_led_show_heartbeat_action,
                                                  self.error_led_show_error_action])]

    def append_text(self, text):
        self.text.moveCursor(QTextCursor.End)
        self.text.insertPlainText(text)
        self.text.moveCursor(QTextCursor.End)

    def popup_ok(self, msg):
        QMessageBox.information(get_main_window(), self.device_info.name, msg)

    def popup_fail(self, msg):
        QMessageBox.critical(get_main_window(), self.device_info.name, msg)

    def toggle_gui_group(self, group, toggle):
        for e in group:
            if toggle:
                e.show()
            else:
                e.hide()

    def modbus_master_param2_changed(self, value):
        if self.mode_combobox.currentIndex() == MODE_MODBUS_MASTER_RTU and \
           self.modbus_master_function_combobox.currentIndex() == MODBUS_F_IDX_WRITE_SINGLE_COIL:
                if value > 0:
                    self.modbus_master_param2_spinbox.setValue(65280)

    def master_send_clicked(self):
        if self.rs485.get_mode() != self.rs485.MODE_MODBUS_MASTER_RTU:
            self.popup_fail(MSG_ERR_NOT_MODBUS_MASTER)

            return

        if self.modbus_master_function_combobox.currentIndex() == MODBUS_F_IDX_READ_COILS:
            try:
                rid = self.rs485.modbus_master_read_coils(self.modbus_master_slave_address_spinbox.value(),
                                                          self.modbus_master_param1_spinbox.value(),
                                                          self.modbus_master_param2_spinbox.value())
            except Exception as e:
                self.popup_fail(str(e))
                self.modbus_master_send_button.setEnabled(True)

                return

            if rid == 0:
                self.popup_fail(MSG_ERR_REQUEST_PROCESS)

            self.modbus_master_send_button.setEnabled(False)

        elif self.modbus_master_function_combobox.currentIndex() == MODBUS_F_IDX_READ_HOLDING_REGISTERS:
            try:
                rid = self.rs485.modbus_master_read_holding_registers(self.modbus_master_slave_address_spinbox.value(),
                                                                      self.modbus_master_param1_spinbox.value(),
                                                                      self.modbus_master_param2_spinbox.value())
            except Exception as e:
                self.popup_fail(str(e))
                self.modbus_master_send_button.setEnabled(True)

                return

            if rid == 0:
                self.popup_fail(MSG_ERR_REQUEST_PROCESS)

            self.modbus_master_send_button.setEnabled(False)

        elif self.modbus_master_function_combobox.currentIndex() == MODBUS_F_IDX_WRITE_SINGLE_COIL:
            if self.modbus_master_param2_spinbox.value() > 0:
                param2 = True
            else:
                param2 = False

            try:
                rid = self.rs485.modbus_master_write_single_coil(self.modbus_master_slave_address_spinbox.value(),
                                                                 self.modbus_master_param1_spinbox.value(),
                                                                 param2)
            except Exception as e:
                self.popup_fail(str(e))
                self.modbus_master_send_button.setEnabled(True)

                return

            if rid == 0:
                self.popup_fail(MSG_ERR_REQUEST_PROCESS)

            self.modbus_master_send_button.setEnabled(False)

        elif self.modbus_master_function_combobox.currentIndex() == MODBUS_F_IDX_WRITE_SINGLE_REGISTER:
            try:
                rid = self.rs485.modbus_master_write_single_register(self.modbus_master_slave_address_spinbox.value(),
                                                                     self.modbus_master_param1_spinbox.value(),
                                                                     self.modbus_master_param2_spinbox.value())
            except Exception as e:
                self.popup_fail(str(e))
                self.modbus_master_send_button.setEnabled(True)

                return

            if rid == 0:
                self.popup_fail(MSG_ERR_REQUEST_PROCESS)

            self.modbus_master_send_button.setEnabled(False)

        elif self.modbus_master_function_combobox.currentIndex() == MODBUS_F_IDX_WRITE_MULTIPLE_COILS:
            data = []

            for i in range(self.modbus_master_param2_spinbox.value()):
                data.append(random.randint(0, 1) == 1)

            try:
                rid = self.rs485.modbus_master_write_multiple_coils(self.modbus_master_slave_address_spinbox.value(),
                                                                    self.modbus_master_param1_spinbox.value(),
                                                                    data)
            except Exception as e:
                self.popup_fail(str(e))
                self.modbus_master_send_button.setEnabled(True)

                return

            if rid == 0:
                self.popup_fail(MSG_ERR_REQUEST_PROCESS)

            self.modbus_master_send_button.setEnabled(False)

        elif self.modbus_master_function_combobox.currentIndex() == MODBUS_F_IDX_WRITE_MULTIPLE_REGISTERS:
            data = []

            for i in range(self.modbus_master_param2_spinbox.value()):
                data.append(random.randint(0, 65535))

            try:
                rid = self.rs485.modbus_master_write_multiple_registers(self.modbus_master_slave_address_spinbox.value(),
                                                                        self.modbus_master_param1_spinbox.value(),
                                                                        data)
            except Exception as e:
                self.popup_fail(str(e))
                self.modbus_master_send_button.setEnabled(True)

                return

            if rid == 0:
                self.popup_fail(MSG_ERR_REQUEST_PROCESS)

            self.modbus_master_send_button.setEnabled(False)

        elif self.modbus_master_function_combobox.currentIndex() == MODBUS_F_IDX_READ_DISCRETE_INPUTS:
            try:
                rid = self.rs485.modbus_master_read_discrete_inputs(self.modbus_master_slave_address_spinbox.value(),
                                                                    self.modbus_master_param1_spinbox.value(),
                                                                    self.modbus_master_param2_spinbox.value())
            except Exception as e:
                self.popup_fail(str(e))
                self.modbus_master_send_button.setEnabled(True)

                return

            if rid == 0:
                self.popup_fail(MSG_ERR_REQUEST_PROCESS)

            self.modbus_master_send_button.setEnabled(False)

        elif self.modbus_master_function_combobox.currentIndex() == MODBUS_F_IDX_READ_INPUT_REGISTERS:
            try:
                rid = self.rs485.modbus_master_read_input_registers(self.modbus_master_slave_address_spinbox.value(),
                                                                    self.modbus_master_param1_spinbox.value(),
                                                                    self.modbus_master_param2_spinbox.value())
            except Exception as e:
                self.popup_fail(str(e))
                self.modbus_master_send_button.setEnabled(True)

                return

            if rid == 0:
                self.popup_fail(MSG_ERR_REQUEST_PROCESS)

            self.modbus_master_send_button.setEnabled(False)

    def modbus_master_function_changed(self, function):
        if function == MODBUS_F_IDX_READ_COILS:
            self.modbus_master_param1_label.setText('Starting Address:')
            self.modbus_master_param1_spinbox.setMinimum(0)
            self.modbus_master_param1_spinbox.setMaximum(65535)
            self.modbus_master_param2_label.setText('Number of Coils:')
            self.modbus_master_param2_spinbox.setMinimum(1)
            self.modbus_master_param2_spinbox.setMaximum(2000)

        elif function == MODBUS_F_IDX_READ_HOLDING_REGISTERS:
            self.modbus_master_param1_label.setText('Starting Address:')
            self.modbus_master_param1_spinbox.setMinimum(0)
            self.modbus_master_param1_spinbox.setMaximum(65535)
            self.modbus_master_param2_label.setText('Number of Registers:')
            self.modbus_master_param2_spinbox.setMinimum(1)
            self.modbus_master_param2_spinbox.setMaximum(125)

        elif function == MODBUS_F_IDX_WRITE_SINGLE_COIL:
            self.modbus_master_param1_label.setText('Coil Address:')
            self.modbus_master_param1_spinbox.setMinimum(0)
            self.modbus_master_param1_spinbox.setMaximum(65535)
            self.modbus_master_param2_label.setText('Coil Value:')
            self.modbus_master_param2_spinbox.setMinimum(0)
            self.modbus_master_param2_spinbox.setMaximum(1)
            self.modbus_master_param2_spinbox.setValue(0)

        elif function == MODBUS_F_IDX_WRITE_SINGLE_REGISTER:
            self.modbus_master_param1_label.setText('Register Address:')
            self.modbus_master_param1_spinbox.setMinimum(0)
            self.modbus_master_param1_spinbox.setMaximum(65535)
            self.modbus_master_param2_label.setText('Register Value:')
            self.modbus_master_param2_spinbox.setMinimum(0)
            self.modbus_master_param2_spinbox.setMaximum(65535)

        elif function == MODBUS_F_IDX_WRITE_MULTIPLE_COILS:
            self.modbus_master_param1_label.setText('Starting Address:')
            self.modbus_master_param1_spinbox.setMinimum(0)
            self.modbus_master_param1_spinbox.setMaximum(65535)
            self.modbus_master_param2_label.setText('Number of Coils:')
            self.modbus_master_param2_spinbox.setMinimum(1)
            self.modbus_master_param2_spinbox.setMaximum(1968)

        elif function == MODBUS_F_IDX_WRITE_MULTIPLE_REGISTERS:
            self.modbus_master_param1_label.setText('Starting Address:')
            self.modbus_master_param1_spinbox.setMinimum(0)
            self.modbus_master_param1_spinbox.setMaximum(65535)
            self.modbus_master_param2_label.setText('Number of Registers:')
            self.modbus_master_param2_spinbox.setMinimum(1)
            self.modbus_master_param2_spinbox.setMaximum(123)

        elif function == MODBUS_F_IDX_READ_DISCRETE_INPUTS:
            self.modbus_master_param1_label.setText('Starting Address:')
            self.modbus_master_param1_spinbox.setMinimum(0)
            self.modbus_master_param1_spinbox.setMaximum(65535)
            self.modbus_master_param2_label.setText('Number of Coils:')
            self.modbus_master_param2_spinbox.setMinimum(1)
            self.modbus_master_param2_spinbox.setMaximum(2000)

        elif function == MODBUS_F_IDX_READ_INPUT_REGISTERS:
            self.modbus_master_param1_label.setText('Starting Address:')
            self.modbus_master_param1_spinbox.setMinimum(0)
            self.modbus_master_param1_spinbox.setMaximum(65535)
            self.modbus_master_param2_label.setText('Number of Registers:')
            self.modbus_master_param2_spinbox.setMinimum(1)
            self.modbus_master_param2_spinbox.setMaximum(125)

    def mode_changed(self, mode):
        if mode == MODE_RS485:
            self.toggle_gui_group(self.gui_group_modbus_slave, False)
            self.toggle_gui_group(self.gui_group_modbus_master, False)
            self.toggle_gui_group(self.gui_group_rs485, True)

        elif mode == MODE_MODBUS_SLAVE_RTU:
            self.toggle_gui_group(self.gui_group_rs485, False)
            self.toggle_gui_group(self.gui_group_modbus_master, False)
            self.toggle_gui_group(self.gui_group_modbus_slave, True)

        elif mode == MODE_MODBUS_MASTER_RTU:
            self.toggle_gui_group(self.gui_group_rs485, False)
            self.toggle_gui_group(self.gui_group_modbus_slave, False)
            self.toggle_gui_group(self.gui_group_modbus_master, True)

        self.configuration_changed()

    def cb_read(self, message):
        if message == None:
            # Increase stream error counter
            self.error_stream_oos = self.error_stream_oos + 1
            self.label_error_stream.setText(str(self.error_stream_oos))

            return

        s = ''.join(message)

        self.hextext.appendData(s)

        # check if a \r\n or \n\r was split into two messages. the first one
        # ended with \r or \n and the next one starts with \n or \r
        if len(s) > 0:
            if s[0] != self.last_char and self.last_char in ['\r', '\n'] and s[0] in ['\r', '\n']:
                s = s[1:]

            if len(s) > 0:
                self.last_char = s[-1]
            else:
                self.last_char = ''

        # QTextEdit breaks lines at \r and \n
        s = s.replace('\n\r', '\n').replace('\r\n', '\n')

        ascii = ''

        for c in s:
            if (ord(c) < 32 or ord(c) > 126) and not (ord(c) in (10, 13)):
                ascii += '.'
            else:
                ascii += c

        self.append_text(ascii)

    def cb_modbus_slave_read_coils_request(self, request_id, starting_address, count):
        a = 'READ COILS REQUEST: ' + \
            'REQUEST ID=' + \
            str(request_id) + \
            ', STARTING ADDRESS=' + \
            str(starting_address) + \
            ', COUNT=' + \
            str(count) + \
            '\n\n'

        data = []

        for i in range(count):
            data.append(random.randint(0, 1) == 1)

        self.rs485.modbus_slave_answer_read_coils_request(request_id, data)
        self.append_text(a)

    def cb_modbus_master_read_coils_response(self,
                                             request_id,
                                             exception_code,
                                             coils):
        if coils == None:
            # Increase stream error counter
            self.error_stream_oos = self.error_stream_oos + 1
            self.label_error_stream.setText(str(self.error_stream_oos))

            a = 'READ COILS RESPONSE: ' + \
                'STREAM OUT OF SYNC' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_TIMEOUT:
            a = 'READ COILS RESPONSE: ' + \
                'REQUEST TIMEOUT' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_FUNCTION:
            a = 'READ COILS RESPONSE: ' + \
                'RECEIVED ILLEGAL FUNCTION CODE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_ADDRESS:
            a = 'READ COILS RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA ADDRESS' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_VALUE:
            a = 'READ COILS RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA VALUE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_SLAVE_DEVICE_FAILURE:
            a = 'READ COILS RESPONSE: ' + \
                'SLAVE DEVICE FAILURE' + \
                '\n\n'
        else:
            a = 'READ COILS RESPONSE: ' + \
                'REQUEST ID=' + \
                str(request_id) + \
                ', EXCEPTION CODE=' + \
                str(exception_code) + \
                ', COILS=' + \
                str(coils) + \
                '\n\n'

        self.append_text(a)
        self.modbus_master_send_button.setEnabled(True)

    def cb_modbus_slave_read_holding_registers_request(self,
                                                       request_id,
                                                       starting_address,
                                                       count):
        a = 'READ HOLDING REGISTERS REQUEST: ' + \
            'REQUEST ID=' + \
            str(request_id) + \
            ', STARTING ADDRESS=' + \
            str(starting_address) + \
            ', COUNT=' + \
            str(count) + \
            '\n\n'

        data = []

        for i in range(count):
            data.append(random.randint(0, 65535))

        self.rs485.modbus_slave_answer_read_holding_registers_request(request_id, data)
        self.append_text(a)

    def cb_modbus_master_read_holding_registers_response(self,
                                                         request_id,
                                                         exception_code,
                                                         holding_registers):
        if holding_registers == None:
            # Increase stream error counter
            self.error_stream_oos = self.error_stream_oos + 1
            self.label_error_stream.setText(str(self.error_stream_oos))

            a = 'READ HOLDING REGISTERS RESPONSE: ' + \
                'STREAM OUT OF SYNC' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_TIMEOUT:
            a = 'READ HOLDING REGISTERS RESPONSE: ' + \
                'REQUEST TIMEOUT' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_FUNCTION:
            a = 'READ HOLDING REGISTERS RESPONSE: ' + \
                'RECEIVED ILLEGAL FUNCTION CODE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_ADDRESS:
            a = 'READ HOLDING REGISTERS RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA ADDRESS' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_VALUE:
            a = 'READ HOLDING REGISTERS RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA VALUE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_SLAVE_DEVICE_FAILURE:
            a = 'READ HOLDING REGISTERS RESPONSE: ' + \
                'SLAVE DEVICE FAILURE' + \
                '\n\n'
        else:
            a = 'READ HOLDING REGISTERS RESPONSE: ' + \
                'REQUEST ID=' + \
                str(request_id) + \
                ', EXCEPTION CODE=' + \
                str(exception_code) + \
                ', HOLDING REGISTERS=' + \
                str(holding_registers) + \
                '\n\n'

        self.append_text(a)
        self.modbus_master_send_button.setEnabled(True)

    def cb_modbus_slave_write_single_coil_request(self,
                                                  request_id,
                                                  coil_address,
                                                  coil_value):
        a = 'WRITE SINGLE COIL REQUEST: ' + \
            'REQUEST ID=' + \
            str(request_id) + \
            ', COIL ADDRESS=' + \
            str(coil_address) + \
            ', COIL VALUE=' + \
            str(coil_value) + \
            '\n\n'

        self.rs485.modbus_slave_answer_write_single_coil_request(request_id)
        self.append_text(a)

    def cb_modbus_master_write_single_coil_response(self,
                                                    request_id,
                                                    exception_code):
        if exception_code == self.rs485.EXCEPTION_CODE_TIMEOUT:
            a = 'WRITE SINGLE COIL RESPONSE: ' + \
                'REQUEST TIMEOUT' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_FUNCTION:
            a = 'WRITE SINGLE COIL RESPONSE: ' + \
                'RECEIVED ILLEGAL FUNCTION CODE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_ADDRESS:
            a = 'WRITE SINGLE COIL RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA ADDRESS' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_VALUE:
            a = 'WRITE SINGLE COIL RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA VALUE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_SLAVE_DEVICE_FAILURE:
            a = 'WRITE SINGLE COIL RESPONSE: ' + \
                'SLAVE DEVICE FAILURE' + \
                '\n\n'
        else:
            a = 'WRITE SINGLE COIL RESPONSE: ' + \
                'REQUEST ID=' + \
                str(request_id) + \
                ', EXCEPTION CODE=' + \
                str(exception_code) + \
                '\n\n'

        self.append_text(a)
        self.modbus_master_send_button.setEnabled(True)

    def cb_modbus_slave_write_single_register_request(self,
                                                      request_id,
                                                      register_address,
                                                      register_value):
        a = 'WRITE SINGLE REGISTER REQUEST: ' + \
            'REQUEST ID=' + \
            str(request_id) + \
            ', REGISTER ADDRESS=' + \
            str(register_address) + \
            ', REGISTER VALUE=' + \
            str(register_value) + \
            '\n\n'

        self.rs485.modbus_slave_answer_write_single_register_request(request_id)
        self.append_text(a)

    def cb_modbus_master_write_single_register_response(self,
                                                        request_id,
                                                        exception_code):
        if exception_code == self.rs485.EXCEPTION_CODE_TIMEOUT:
            a = 'WRITE SINGLE REGISTER RESPONSE: ' + \
                'REQUEST TIMEOUT' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_FUNCTION:
            a = 'WRITE SINGLE REGISTER RESPONSE: ' + \
                'RECEIVED ILLEGAL FUNCTION CODE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_ADDRESS:
            a = 'WRITE SINGLE REGISTER RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA ADDRESS' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_VALUE:
            a = 'WRITE SINGLE REGISTER RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA VALUE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_SLAVE_DEVICE_FAILURE:
            a = 'WRITE SINGLE REGISTER RESPONSE: ' + \
                'SLAVE DEVICE FAILURE' + \
                '\n\n'
        else:
            a = 'WRITE SINGLE REGISTER RESPONSE: ' + \
                'REQUEST ID=' + \
                str(request_id) + \
                ', EXCEPTION CODE=' + \
                str(exception_code) + \
                '\n\n'

        self.append_text(a)
        self.modbus_master_send_button.setEnabled(True)

    def cb_modbus_slave_write_multiple_coils_request(self,
                                                     request_id,
                                                     starting_address,
                                                     count,
                                                     coils):
        if coils == None:
            # Increase stream error counter
            self.error_stream_oos = self.error_stream_oos + 1
            self.label_error_stream.setText(str(self.error_stream_oos))

            a = 'WRITE MULTIPLE COILS REQUEST: ' + \
                'STREAM OUT OF SYNC' + \
                '\n\n'
        else:
            a = 'WRITE MULTIPLE COILS REQUEST: ' + \
                'REQUEST ID=' + \
                str(request_id) + \
                ', STARTING ADDRESS=' + \
                str(starting_address) + \
                ', COUNT=' + \
                str(count) + \
                ', COILS=' + \
                str(coils) + \
                '\n\n'

        self.rs485.modbus_slave_answer_write_multiple_coils_request(request_id)
        self.append_text(a)

    def cb_modbus_master_write_multiple_coils_response(self,
                                                       request_id,
                                                       exception_code):
        if exception_code == self.rs485.EXCEPTION_CODE_TIMEOUT:
            a = 'WRITE MULTIPLE COILS RESPONSE: ' + \
                'REQUEST TIMEOUT' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_FUNCTION:
            a = 'WRITE MULTIPLE COILS RESPONSE: ' + \
                'RECEIVED ILLEGAL FUNCTION CODE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_ADDRESS:
            a = 'WRITE MULTIPLE COILS RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA ADDRESS' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_VALUE:
            a = 'WRITE MULTIPLE COILS RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA VALUE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_SLAVE_DEVICE_FAILURE:
            a = 'WRITE MULTIPLE COILS RESPONSE: ' + \
                'SLAVE DEVICE FAILURE' + \
                '\n\n'
        else:
            a = 'WRITE MULTIPLE COILS RESPONSE: ' + \
                'REQUEST ID=' + \
                str(request_id) + \
                ', EXCEPTION CODE=' + \
                str(exception_code) + \
                '\n\n'

        self.append_text(a)
        self.modbus_master_send_button.setEnabled(True)

    def cb_modbus_slave_write_multiple_registers_request(self,
                                                         request_id,
                                                         starting_address,
                                                         count,
                                                         registers):
        if registers == None:
            # Increase stream error counter
            self.error_stream_oos = self.error_stream_oos + 1
            self.label_error_stream.setText(str(self.error_stream_oos))

            a = 'WRITE MULTIPLE REGISTERS REQUEST: ' + \
                'STREAM OUT OF SYNC' + \
                '\n\n'
        else:
            a = 'WRITE MULTIPLE REGISTERS REQUEST: ' + \
                'REQUEST ID=' + \
                str(request_id) + \
                ', STARTING ADDRESS=' + \
                str(starting_address) + \
                ', COUNT=' + \
                str(count) + \
                ', REGISTERS=' + \
                str(registers) + \
                '\n\n'

        self.rs485.modbus_slave_answer_write_multiple_registers_request(request_id)
        self.append_text(a)

    def cb_modbus_master_write_multiple_registers_response(self,
                                                           request_id,
                                                           exception_code):
        if exception_code == self.rs485.EXCEPTION_CODE_TIMEOUT:
            a = 'WRITE MULTIPLE REGISTERS RESPONSE: ' + \
                'REQUEST TIMEOUT' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_FUNCTION:
            a = 'WRITE MULTIPLE REGISTERS RESPONSE: ' + \
                'RECEIVED ILLEGAL FUNCTION CODE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_ADDRESS:
            a = 'WRITE MULTIPLE REGISTERS RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA ADDRESS' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_VALUE:
            a = 'WRITE MULTIPLE REGISTERS RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA VALUE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_SLAVE_DEVICE_FAILURE:
            a = 'WRITE MULTIPLE REGISTERS RESPONSE: ' + \
                'SLAVE DEVICE FAILURE' + \
                '\n\n'
        else:
            a = 'WRITE MULTIPLE REGISTERS RESPONSE: ' + \
                'REQUEST ID=' + \
                str(request_id) + \
                ', EXCEPTION CODE=' + \
                str(exception_code) + \
                '\n\n'

        self.append_text(a)
        self.modbus_master_send_button.setEnabled(True)

    def cb_modbus_slave_read_discrete_inputs_request(self,
                                                     request_id,
                                                     starting_address,
                                                     count):
        a = 'READ DISCRETE INPUTS REQUEST: ' + \
            'REQUEST ID=' + \
            str(request_id) + \
            ', STARTING ADDRESS=' + \
            str(starting_address) + \
            ', COUNT=' + \
            str(count) + \
            '\n\n'

        data = []

        for i in range(count):
            data.append(random.randint(0, 1) == 1)

        self.rs485.modbus_slave_answer_read_discrete_inputs_request(request_id, data)
        self.append_text(a)

    def cb_modbus_master_read_discrete_inputs_response(self,
                                                       request_id,
                                                       exception_code,
                                                       discrete_inputs):
        if discrete_inputs == None:
            # Increase stream error counter
            self.error_stream_oos = self.error_stream_oos + 1
            self.label_error_stream.setText(str(self.error_stream_oos))

            a = 'READ DISCRETE INPUTS RESPONSE: ' + \
                'STREAM OUT OF SYNC' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_TIMEOUT:
            a = 'READ DISCRETE INPUTS RESPONSE: ' + \
                'REQUEST TIMEOUT' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_FUNCTION:
            a = 'READ DISCRETE INPUTS RESPONSE: ' + \
                'RECEIVED ILLEGAL FUNCTION CODE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_ADDRESS:
            a = 'READ DISCRETE INPUTS RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA ADDRESS' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_VALUE:
            a = 'READ DISCRETE INPUTS RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA VALUE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_SLAVE_DEVICE_FAILURE:
            a = 'READ DISCRETE INPUTS RESPONSE: ' + \
                'SLAVE DEVICE FAILURE' + \
                '\n\n'
        else:
            a = 'READ DISCRETE INPUTS RESPONSE: ' + \
                'REQUEST ID=' + \
                str(request_id) + \
                ', EXCEPTION CODE=' + \
                str(exception_code) + \
                ', DISCRETE INPUTS=' + \
                str(discrete_inputs) + \
                '\n\n'

        self.append_text(a)
        self.modbus_master_send_button.setEnabled(True)

    def cb_modbus_slave_read_input_registers_request(self,
                                                     request_id,
                                                     starting_address,
                                                     count):
        a = 'READ INPUT REGISTERS REQUEST: ' + \
            'REQUEST ID=' + \
            str(request_id) + \
            ', STARTING ADDRESS=' + \
            str(starting_address) + \
            ', COUNT=' + \
            str(count) + \
            '\n\n'

        data = []

        for i in range(count):
            data.append(random.randint(0, 65535))

        self.rs485.modbus_slave_answer_read_input_registers_request(request_id, data)
        self.append_text(a)

    def cb_modbus_master_read_input_registers_response(self,
                                                       request_id,
                                                       exception_code,
                                                       input_registers):
        if input_registers == None:
            # Increase stream error counter
            self.error_stream_oos = self.error_stream_oos + 1
            self.label_error_stream.setText(str(self.error_stream_oos))

            a = 'READ INPUT REGISTERS RESPONSE: ' + \
                'STREAM OUT OF SYNC' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_TIMEOUT:
            a = 'READ INPUT REGISTERS RESPONSE: ' + \
                'REQUEST TIMEOUT' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_FUNCTION:
            a = 'READ INPUT REGISTERS RESPONSE: ' + \
                'RECEIVED ILLEGAL FUNCTION CODE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_ADDRESS:
            a = 'READ INPUT REGISTERS RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA ADDRESS' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_VALUE:
            a = 'READ INPUT REGISTERS RESPONSE: ' + \
                'RECEIVED ILLEGAL DATA VALUE' + \
                '\n\n'
        elif exception_code == self.rs485.EXCEPTION_CODE_SLAVE_DEVICE_FAILURE:
            a = 'READ INPUT REGISTERS RESPONSE: ' + \
                'SLAVE DEVICE FAILURE' + \
                '\n\n'
        else:
            a = 'READ INPUT REGISTERS RESPONSE: ' + \
                'REQUEST ID=' + \
                str(request_id) + \
                ', EXCEPTION CODE=' + \
                str(exception_code) + \
                ', INPUT REGISTERS=' + \
                str(input_registers) + \
                '\n\n'

        self.append_text(a)
        self.modbus_master_send_button.setEnabled(True)

    def line_ending_changed(self):
        selected_line_ending = self.rs485_input_line_ending_combobox.currentText()
        self.rs485_input_line_ending_lineedit.setEnabled( (selected_line_ending == 'Hex:' ))

    def get_line_ending(self):
        selected_line_ending = self.rs485_input_line_ending_combobox.currentText()

        if selected_line_ending == '\\n':
            hex_le = '0A'
        elif selected_line_ending == '\\r':
            hex_le = '0D'
        elif selected_line_ending == '\\r\\n':
            hex_le = '0D0A'
        elif selected_line_ending == '\\n\\r':
            hex_le = '0A0D'
        elif selected_line_ending == '\\0':
            hex_le = "00"
        elif selected_line_ending == 'Hex:':
            hex_le = self.rs485_input_line_ending_lineedit.text()
        else:
            hex_le = ''

        try:
            line_ending = hex_le.decode('hex')
        except TypeError:
            # TODO: Handle Error!
            # Should never happen, because LineEdit has a validator applied
            line_ending = ''

        return line_ending

    def input_changed(self):
        text = self.rs485_input_combobox.currentText().encode('utf-8') + self.get_line_ending()
        c = ['\0']*len(text)
        for i, t in enumerate(text):
            c[i] = t

        self.rs485.write(c)
        self.rs485_input_combobox.setCurrentIndex(0)

    def get_rs485_configuration_async(self, conf):
        self.baudrate_spinbox.setValue(conf.baudrate)
        self.parity_combobox.setCurrentIndex(conf.parity)
        self.stopbits_spinbox.setValue(conf.stopbits)
        self.wordlength_spinbox.setValue(conf.wordlength)
        self.duplex_combobox.setCurrentIndex(conf.duplex)
        self.apply_button.setEnabled(False)

    def get_modbus_configuration_async(self, conf):
        self.modbus_slave_address_spinbox.setValue(conf.slave_address)
        self.modbus_master_request_timeout_spinbox.setValue(conf.master_request_timeout)
        self.apply_button.setEnabled(False)

    def get_mode_async(self, mode):
        self.mode_combobox.setCurrentIndex(mode)
        self.apply_button.setEnabled(False)

    def text_type_changed(self):
        if self.text_type_combobox.currentIndex() == 0:
            self.hextext.hide()
            self.text.show()
        else:
            self.text.hide()
            self.hextext.show()

    def configuration_changed(self):
        self.apply_button.setEnabled(True)

    def apply_clicked(self):
        mode = self.mode_combobox.currentIndex()
        baudrate = self.baudrate_spinbox.value()
        parity = self.parity_combobox.currentIndex()
        stopbits = self.stopbits_spinbox.value()
        wordlength = self.wordlength_spinbox.value()
        duplex = self.duplex_combobox.currentIndex()
        modbus_slave_address = self.modbus_slave_address_spinbox.value()
        modbus_master_request_timeout = self.modbus_master_request_timeout_spinbox.value()

        self.rs485.set_rs485_configuration(baudrate,
                                           parity,
                                           stopbits,
                                           wordlength,
                                           duplex)

        self.rs485.set_modbus_configuration(modbus_slave_address,
                                            modbus_master_request_timeout)

        self.rs485.set_mode(mode)

        self.apply_button.setEnabled(False)

    def is_read_callback_enabled_async(self, enabled):
        self.read_callback_was_enabled = enabled
        self.rs485.enable_read_callback()

    def cb_error_count(self, error):
        self.label_error_overrun.setText(str(error.overrun_error_count))
        self.label_error_parity.setText(str(error.parity_error_count))

    def cb_error_count_modbus(self, error):
        self.label_error_modbus_timeout.setText(str(error.timeout_error_count))
        self.label_error_modbus_checksum.setText(str(error.checksum_error_count))
        self.label_error_modbus_frame_size.setText(str(error.frame_too_big_error_count))
        self.label_error_modbus_illegal_function.setText(str(error.illegal_function_error_count))
        self.label_error_modbus_illegal_data_address.setText(str(error.illegal_data_address_error_count))
        self.label_error_modbus_illegal_data_value.setText(str(error.illegal_data_value_error_count))
        self.label_error_modbus_slave_device_failure.setText(str(error.slave_device_failure_error_count))

    def get_communication_led_config_async(self, config):
        if config == BrickletRS485.COMMUNICATION_LED_CONFIG_OFF:
            self.com_led_off_action.trigger()
        elif config == BrickletRS485.COMMUNICATION_LED_CONFIG_ON:
            self.com_led_on_action.trigger()
        elif config == BrickletRS485.COMMUNICATION_LED_CONFIG_SHOW_HEARTBEAT:
            self.com_led_show_heartbeat_action.trigger()
        elif config == BrickletRS485.COMMUNICATION_LED_CONFIG_SHOW_COMMUNICATION:
            self.com_led_show_communication_action.trigger()

    def get_error_led_config_async(self, config):
        if config == BrickletRS485.ERROR_LED_CONFIG_OFF:
            self.error_led_off_action.trigger()
        elif config == BrickletRS485.ERROR_LED_CONFIG_ON:
            self.error_led_on_action.trigger()
        elif config == BrickletRS485.ERROR_LED_CONFIG_SHOW_HEARTBEAT:
            self.error_led_show_heartbeat_action.trigger()
        elif config == BrickletRS485.ERROR_LED_CONFIG_SHOW_ERROR:
            self.error_led_show_error_action.trigger()

    def start(self):
        async_call(self.rs485.get_communication_led_config, None, self.get_communication_led_config_async, self.increase_error_count)
        async_call(self.rs485.get_error_led_config, None, self.get_error_led_config_async, self.increase_error_count)

        self.read_callback_was_enabled = False

        async_call(self.rs485.is_read_callback_enabled, None, self.is_read_callback_enabled_async, self.increase_error_count)
        async_call(self.rs485.get_rs485_configuration, None, self.get_rs485_configuration_async, self.increase_error_count)
        async_call(self.rs485.get_modbus_configuration, None, self.get_modbus_configuration_async, self.increase_error_count)
        async_call(self.rs485.get_mode, None, self.get_mode_async, self.increase_error_count)
        self.cbe_error_count.set_period(250)
        self.cbe_error_count_modbus.set_period(250)

    def stop(self):
        self.cbe_error_count.set_period(0)
        self.cbe_error_count_modbus.set_period(0)
        if not self.read_callback_was_enabled:
            try:
                async_call(self.rs485.disable_read_callback, None, None, None)
            except:
                pass

    def destroy(self):
        pass

    def get_url_part(self):
        return 'rs485'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRS485.DEVICE_IDENTIFIER
