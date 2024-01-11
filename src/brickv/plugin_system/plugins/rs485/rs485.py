# -*- coding: utf-8 -*-
"""
RS485 Plugin
Copyright (C) 2016 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2017 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2022 Erik Fleckstein <erik@tinkerforge.com>

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

from collections import namedtuple
import re
import time

from PyQt5.QtWidgets import QAction, QMessageBox, QTreeWidgetItem
from PyQt5.QtGui import QTextCursor, QColor, QBrush, QPalette
from PyQt5.QtCore import pyqtSignal, Qt, QTimer

from brickv.bindings.bricklet_rs485 import BrickletRS485
from brickv.plugin_system.plugins.rs485.ui_rs485 import Ui_RS485
from brickv.async_call import async_call
from brickv.hex_validator import HexValidator
from brickv.bin_validator import BinValidator
from brickv.callback_emulator import CallbackEmulator
from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.qhexedit import QHexeditWidget
from brickv.utils import get_main_window

from brickv.bindings.ip_connection import Error

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
MSG_ERR_NOT_RS485 = "The Bricklet needs to be in RS485 mode to perform this operation"

EXCEPTION_CODE_STREAM_OUT_OF_SYNC = -2
EXCEPTION_CODE_DEVICE_TIMEOUT = -2

ModbusEvent = namedtuple('ModbusEvent', ['is_request', 'time', 'request_id', 'slave_address', 'function', 'address', 'count', 'data', 'exception_code'])

class RS485(COMCUPluginBase, Ui_RS485):
    qtcb_read = pyqtSignal(object)

    # Modbus specific.
    qtcb_modbus_slave_read_coils_request = pyqtSignal(int, int, int)
    qtcb_modbus_master_read_coils_response = pyqtSignal(int, int, object)
    qtcb_modbus_slave_read_holding_registers_request = pyqtSignal(int, int, int)
    qtcb_modbus_master_read_holding_registers_response = pyqtSignal(int, int, object)
    qtcb_modbus_slave_write_single_coil_request = pyqtSignal(int, int, bool)
    qtcb_modbus_master_write_single_coil_response = pyqtSignal(int, int)
    qtcb_modbus_slave_write_single_register_request = pyqtSignal(int, int, int)
    qtcb_modbus_master_write_single_register_response = pyqtSignal(int, int)
    qtcb_modbus_slave_write_multiple_coils_request = pyqtSignal(int, int, object)
    qtcb_modbus_master_write_multiple_coils_response = pyqtSignal(int, int)
    qtcb_modbus_slave_write_multiple_registers_request = pyqtSignal(int, int, object)
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

        self.modbus_errors = {
            self.rs485.EXCEPTION_CODE_TIMEOUT: 'Request timeout',
            self.rs485.EXCEPTION_CODE_SUCCESS: 'Request succeeded',
            self.rs485.EXCEPTION_CODE_ILLEGAL_FUNCTION: 'Received illegal function code',
            self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_ADDRESS: 'Received illegal data address',
            self.rs485.EXCEPTION_CODE_ILLEGAL_DATA_VALUE: 'Received illegal data value',
            self.rs485.EXCEPTION_CODE_SLAVE_DEVICE_FAILURE: 'Slave device failure',

            self.rs485.EXCEPTION_CODE_ACKNOWLEDGE: 'Slave device acknowledged',
            self.rs485.EXCEPTION_CODE_SLAVE_DEVICE_BUSY: 'Slave device busy',
            self.rs485.EXCEPTION_CODE_MEMORY_PARITY_ERROR: 'Slave device detected memory parity error',
            self.rs485.EXCEPTION_CODE_GATEWAY_PATH_UNAVAILABLE: 'Gateway path unavailable',
            self.rs485.EXCEPTION_CODE_GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND: 'Gateway target device failed to respond',
        }

        # A modbus timeout is reported as -1, this is not in the protocol, but an addition for communicating between the bindings and the bricklet.
        # Add -2 for a stream out of sync error, which simplifies the error handling further down.
        # As the bindings could add another error code in the future, check if this is a good idea.
        assert EXCEPTION_CODE_STREAM_OUT_OF_SYNC not in self.modbus_errors, "-2 was already in the modbus_errors dictionary. This is a bug in the Brick Viewer."
        assert EXCEPTION_CODE_DEVICE_TIMEOUT not in self.modbus_errors, "-3 was already in the modbus_errors dictionary. This is a bug in the Brick Viewer."
        self.modbus_errors[EXCEPTION_CODE_STREAM_OUT_OF_SYNC] = 'Stream out of sync.'
        self.modbus_errors[EXCEPTION_CODE_DEVICE_TIMEOUT] = 'Bricklet communication timeout.'

        self.cbe_error_count = CallbackEmulator(self,
                                                self.rs485.get_error_count,
                                                None,
                                                self.cb_error_count,
                                                self.increase_error_count)

        self.cbe_error_count_modbus = CallbackEmulator(self,
                                                       self.rs485.get_modbus_common_error_count,
                                                       None,
                                                       self.cb_modbus_common_error_count,
                                                       self.increase_error_count)

        self.read_callback_was_enabled = None

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

        self.combo_input.addItem("")
        self.combo_input.lineEdit().setMaxLength(65533)
        self.combo_input.lineEdit().returnPressed.connect(self.do_write)
        self.button_write.clicked.connect(self.do_write)

        self.rs485_input_line_ending_lineedit.setValidator(HexValidator())
        self.rs485_input_line_ending_combobox.currentIndexChanged.connect(self.line_ending_changed)
        self.rs485_input_line_ending_lineedit.editingFinished.connect(self.line_ending_changed)


        self.baudrate_spinbox.valueChanged.connect(self.configuration_changed)
        self.parity_combobox.currentIndexChanged.connect(self.configuration_changed)
        self.stopbits_spinbox.valueChanged.connect(self.configuration_changed)
        self.wordlength_spinbox.valueChanged.connect(self.configuration_changed)
        self.duplex_combobox.currentIndexChanged.connect(self.configuration_changed)
        self.text_type_combobox.currentIndexChanged.connect(self.text_type_changed)

        # Modbus specific.
        self.modbus_master_request_timeout_spinbox.valueChanged.connect(self.configuration_changed)
        self.modbus_slave_address_spinbox.valueChanged.connect(self.configuration_changed)
        self.modbus_master_function_combobox.currentIndexChanged.connect(self.modbus_master_function_changed)

        self.hextext = QHexeditWidget(self.text.font())
        self.hextext.hide()
        self.layout().insertWidget(1, self.hextext, stretch=1)

        self.button_clear_text.clicked.connect(lambda: self.text.setPlainText(""))
        self.button_clear_text.clicked.connect(self.hextext.clear)
        self.button_clear_text.clicked.connect(self.modbus_master_tree.clear)
        self.button_clear_text.clicked.connect(self.modbus_slave_tree.clear)


        self.modbus_master_send_button.clicked.connect(self.master_send_clicked)
        self.apply_button.clicked.connect(self.apply_clicked)

        self.error_overrun = 0
        self.error_parity = 0
        self.error_stream_oos = 0
        self.last_char = ''

        self.modbus_master_function_combobox.setCurrentIndex(-1)
        self.modbus_master_function_combobox.setCurrentIndex(0)

        self.modbus_master_param2_hex_spinbox.enable_hex_mode(digit_block_size=4)

        self.gui_group_rs485 = [self.label_show_text_as,
                                self.text_type_combobox,
                                self.button_clear_text,
                                self.text,
                                self.hextext,
                                self.line_3,
                                self.button_write,
                                self.label_error_overrun_name,
                                self.label_error_overrun,
                                self.label_error_parity_name,
                                self.label_error_parity,
                                self.label_error_stream_name,
                                self.label_error_stream,
                                self.rs485_input_label,
                                self.combo_input,
                                self.rs485_input_line_ending_combobox,
                                self.rs485_input_line_ending_lineedit]

        self.gui_group_modbus_master = [self.modbus_master_tree,
                                        self.button_clear_text,
                                        self.line_3,
                                        self.label_error_overrun_name,
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
                                        self.modbus_master_param2_dec_spinbox,
                                        self.modbus_master_param2_hex_spinbox,
                                        self.modbus_master_param2_bool_combobox,
                                        self.modbus_master_param2_combobox,
                                        self.modbus_master_request_timeout_label,
                                        self.modbus_master_request_timeout_spinbox,
                                        self.modbus_master_send_button]

        self.gui_group_modbus_slave = [self.modbus_slave_tree,
                                       self.button_clear_text,
                                       self.line_3,
                                       self.label_error_overrun_name,
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
                                       self.modbus_slave_address_spinbox,
                                       self.modbus_slave_behaviour_combobox,
                                       self.modbus_slave_behaviour_label]

        self.gui_group_empty = [self.text,
                                self.button_clear_text,
                                self.line_3,
                                self.label_error_overrun_name,
                                self.label_error_overrun,
                                self.label_error_parity_name,
                                self.label_error_parity,
                                self.label_error_stream_name,
                                self.label_error_stream]

        item = ['00:00:00', '123', '123', 'Write Multiple Registers Response', '12345', '123', '0000 0000 0000 0000']
        self.modbus_master_tree.addTopLevelItem(QTreeWidgetItem(item))
        for i in range(len(item)):
            self.modbus_master_tree.resizeColumnToContents(i)
        self.modbus_master_tree.clear()

        item = ['00:00:00', '123', 'Write Multiple Registers Response', '12345', '123', '0000 0000 0000 0000']
        self.modbus_slave_tree.addTopLevelItem(QTreeWidgetItem(item))
        for i in range(len(item)):
            self.modbus_slave_tree.resizeColumnToContents(i)
        self.modbus_slave_tree.clear()

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

        self.modbus_log = []
        self.modbus_master_answer_timer = QTimer(self)
        self.modbus_master_answer_timer.setSingleShot(True)

        self.configured_mode = None
        self.mode_changed(self.configured_mode)
        self.mode_combobox.insertItem(0, "Querying...")
        self.mode_combobox.setCurrentIndex(0)

        self.mode_combobox.currentIndexChanged.connect(self.mode_changed)

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

    def master_send_clicked(self):
        if self.configured_mode != self.rs485.MODE_MODBUS_MASTER_RTU:
            self.popup_fail(MSG_ERR_NOT_MODBUS_MASTER)
            return

        request_fn_dict = {
            MODBUS_F_IDX_READ_COILS: self.rs485.modbus_master_read_coils,
            MODBUS_F_IDX_READ_HOLDING_REGISTERS: self.rs485.modbus_master_read_holding_registers,
            MODBUS_F_IDX_WRITE_SINGLE_COIL: self.rs485.modbus_master_write_single_coil,
            MODBUS_F_IDX_WRITE_SINGLE_REGISTER: self.rs485.modbus_master_write_single_register,
            MODBUS_F_IDX_WRITE_MULTIPLE_COILS: self.rs485.modbus_master_write_multiple_coils,
            MODBUS_F_IDX_WRITE_MULTIPLE_REGISTERS: self.rs485.modbus_master_write_multiple_registers,
            MODBUS_F_IDX_READ_DISCRETE_INPUTS: self.rs485.modbus_master_read_discrete_inputs,
            MODBUS_F_IDX_READ_INPUT_REGISTERS: self.rs485.modbus_master_read_input_registers
        }

        request_fn_idx = self.modbus_master_function_combobox.currentIndex()
        request_fn_name = re.sub(" \(Function Code \d*\)", "", self.modbus_master_function_combobox.currentText())
        request_fn = request_fn_dict[request_fn_idx]

        slave_address = self.modbus_master_slave_address_spinbox.value()

        address = self.modbus_master_param1_spinbox.value()

        if request_fn_idx == MODBUS_F_IDX_WRITE_SINGLE_REGISTER:
            arg2 = self.modbus_master_param2_hex_spinbox.value()
        elif request_fn_idx == MODBUS_F_IDX_WRITE_SINGLE_COIL:
            arg2 = self.modbus_master_param2_bool_combobox.currentText() == 'True'
        elif request_fn_idx == MODBUS_F_IDX_WRITE_MULTIPLE_COILS:
            text = self.modbus_master_param2_combobox.currentText()
            if len(text) == 0:
                return

            arg2 = [i == '1' for i in text]
        elif request_fn_idx == MODBUS_F_IDX_WRITE_MULTIPLE_REGISTERS:
            text = self.modbus_master_param2_combobox.currentText()
            if len(text) == 0:
                return

            arg2 = [int(i, 16) for i in text.split(' ')]
        else:
            arg2 = self.modbus_master_param2_dec_spinbox.value()

        count = 1

        if request_fn_idx == MODBUS_F_IDX_WRITE_SINGLE_COIL:
            arg2_string = str(arg2)
        elif request_fn_idx == MODBUS_F_IDX_WRITE_SINGLE_REGISTER:
            arg2_string = "{:04X}".format(arg2)
        elif request_fn_idx == MODBUS_F_IDX_WRITE_MULTIPLE_COILS:
            arg2_string = ' '.join(str(a) for a in arg2)
        elif request_fn_idx == MODBUS_F_IDX_WRITE_MULTIPLE_REGISTERS:
            arg2_string = ' '.join("{:04X}".format(i) for i in arg2)
        else:
            count = arg2
            arg2_string = ''

        try:
            # Use address without coil/register type prefix
            rid = request_fn(slave_address, address % 100000, arg2)
        except Exception as e:
            if isinstance(e, Error) and e.value == Error.TIMEOUT:
                self.modbus_log_add(ModbusEvent(True, time.localtime(), rid, slave_address, request_fn_name, address, count, arg2_string, EXCEPTION_CODE_DEVICE_TIMEOUT))
                self.increase_error_count()
            else:
                self.popup_fail(str(e))
            return

        if rid == 0:
            self.popup_fail(MSG_ERR_REQUEST_PROCESS)
            return

        self.modbus_log_add(ModbusEvent(True, time.localtime(), rid, slave_address, request_fn_name, address, count, arg2_string, BrickletRS485.EXCEPTION_CODE_SUCCESS))
        self.modbus_master_send_button.setEnabled(False)
        self.modbus_master_answer_timer.setInterval(self.modbus_master_request_timeout_spinbox.value() + 2600)

        def timeout():
            self.modbus_log_add(ModbusEvent(False, time.localtime(), rid, slave_address, request_fn_name, address, count, arg2_string, EXCEPTION_CODE_DEVICE_TIMEOUT))
            self.modbus_master_send_button.setEnabled(True)
            self.modbus_master_send_button.setDefault(True)

        try:
            self.modbus_master_answer_timer.timeout.disconnect()
        except: # This raises an exception if no slots are connected.
            pass
        self.modbus_master_answer_timer.timeout.connect(timeout)
        self.modbus_master_answer_timer.start()

    def modbus_log_add(self, event):
        self.modbus_log.append(event)

        entry = [time.strftime("%H:%M:%S", event.time),
                 str(event.request_id),
                 str(event.slave_address),
                 event.function + ' ' + ('Request' if event.is_request else 'Response'),
                 '{:06d}'.format(event.address) if event.address is not None else None,
                 str(event.count),
                 event.data if event.exception_code == BrickletRS485.EXCEPTION_CODE_SUCCESS else self.modbus_errors[event.exception_code]]

        # None marks unknown values except in the data field.
        for i, e in enumerate(entry):
            if e is None or e == 'None':
                entry[i] = '?' if i != len(entry) - 1 else ''

        if self.configured_mode == self.rs485.MODE_MODBUS_SLAVE_RTU:
            entry = entry[:2] + entry[3:]

        item = QTreeWidgetItem(entry)

        color = None
        if event.exception_code != BrickletRS485.EXCEPTION_CODE_SUCCESS:
            color = QBrush(QColor(0xFF, 0x7F, 0x7F))
        elif (self.configured_mode == self.rs485.MODE_MODBUS_MASTER_RTU and event.is_request) or \
             (self.configured_mode == self.rs485.MODE_MODBUS_SLAVE_RTU and not event.is_request):
            color = QBrush(QColor(self.palette().color(QPalette.Background)))

        if color is not None:
            for i in range(len(entry)):
                item.setData(i, Qt.BackgroundRole, color)

        if self.configured_mode == self.rs485.MODE_MODBUS_SLAVE_RTU:
            self.modbus_slave_tree.addTopLevelItem(item)
        else:
            self.modbus_master_tree.addTopLevelItem(item)

    def modbus_master_function_changed(self, function):
        d = {
            MODBUS_F_IDX_READ_COILS:               ('First Coil Number:',     'Number of Coils:',      None,                    1,    2000,  self.modbus_master_param2_dec_spinbox,   1,      65536),
            MODBUS_F_IDX_READ_HOLDING_REGISTERS:   ('First Register Number:', 'Number of Registers:',  None,                    1,    125,   self.modbus_master_param2_dec_spinbox,   400001, 465536),
            MODBUS_F_IDX_WRITE_SINGLE_COIL:        ('Coil Number:',           'Coil Value:',           None,                    None, None,  self.modbus_master_param2_bool_combobox, 1,      65536),
            MODBUS_F_IDX_WRITE_SINGLE_REGISTER:    ('Register Number:',       'Register Value [Hex]:', None,                    0,    65535, self.modbus_master_param2_hex_spinbox,   400001, 465536),
            MODBUS_F_IDX_WRITE_MULTIPLE_COILS:     ('First Coil Number:',     'Coil Values [0 or 1]',  BinValidator(1968, 1),   None, None,  self.modbus_master_param2_combobox,      1,      65536),
            MODBUS_F_IDX_WRITE_MULTIPLE_REGISTERS: ('First Register Number:', 'Register Values [Hex]', HexValidator(123*2, 4),  None, None,  self.modbus_master_param2_combobox,      400001, 465536),
            MODBUS_F_IDX_READ_DISCRETE_INPUTS:     ('First Input Number:',    'Number of Inputs:',     None,                    1,    2000,  self.modbus_master_param2_dec_spinbox,   100001, 165536),
            MODBUS_F_IDX_READ_INPUT_REGISTERS:     ('First Input Number:',    'Number of Inputs:',     None,                    1,    125,   self.modbus_master_param2_dec_spinbox,   300001, 365536)
        }
        if function not in d:
            return
        text1, text2, param2_validator, spin_min, spin_max, spin, number_min, number_max = d[function]
        self.modbus_master_param1_spinbox.setMinimum(number_min)
        self.modbus_master_param1_spinbox.setMaximum(number_max)
        self.modbus_master_param1_spinbox.setValue(number_min)
        self.modbus_master_param1_label.setText(text1)
        self.modbus_master_param2_label.setText(text2)

        self.modbus_master_param2_combobox.setValidator(param2_validator)
        if function == MODBUS_F_IDX_WRITE_MULTIPLE_REGISTERS or function == MODBUS_F_IDX_WRITE_MULTIPLE_COILS:
            self.modbus_master_param2_combobox.clearEditText()
            self.modbus_master_param2_combobox.clear()

        if spin_min is not None and spin_max is not None:
            spin.setMinimum(spin_min)
            spin.setMaximum(spin_max)

        if number_min == 1:
            self.modbus_master_param1_spinbox.use_leading_zeros(6)
        else:
            self.modbus_master_param1_spinbox.use_leading_zeros(0)

        self.modbus_master_param2_dec_spinbox.hide()
        self.modbus_master_param2_hex_spinbox.hide()
        self.modbus_master_param2_bool_combobox.hide()
        self.modbus_master_param2_combobox.hide()
        spin.show()


    def mode_changed(self, mode):
        if mode == self.rs485.MODE_RS485:
            self.toggle_gui_group(self.gui_group_modbus_slave, False)
            self.toggle_gui_group(self.gui_group_modbus_master, False)
            self.toggle_gui_group(self.gui_group_rs485, True)
            self.text_type_changed()

        elif mode == self.rs485.MODE_MODBUS_SLAVE_RTU:
            self.toggle_gui_group(self.gui_group_rs485, False)
            self.toggle_gui_group(self.gui_group_modbus_master, False)
            self.toggle_gui_group(self.gui_group_modbus_slave, True)

        elif mode == self.rs485.MODE_MODBUS_MASTER_RTU:
            self.toggle_gui_group(self.gui_group_rs485, False)
            self.toggle_gui_group(self.gui_group_modbus_slave, False)
            self.toggle_gui_group(self.gui_group_modbus_master, True)
            self.modbus_master_function_changed(self.modbus_master_function_combobox.currentIndex())
            self.modbus_master_send_button.setDefault(True)
        else:
            self.toggle_gui_group(self.gui_group_rs485, False)
            self.toggle_gui_group(self.gui_group_modbus_slave, False)
            self.toggle_gui_group(self.gui_group_modbus_master, False)
            self.toggle_gui_group(self.gui_group_empty, True)


        self.configuration_changed()

    def cb_read(self, message):
        if self.check_stream_sync(message) != BrickletRS485.EXCEPTION_CODE_SUCCESS:
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

        ascii_ = ''

        for c in s:
            if (ord(c) < 32 or ord(c) > 126) and ord(c) not in (10, 13):
                ascii_ += '.'
            else:
                ascii_ += c

        self.append_text(ascii_)

    def check_stream_sync(self, item, exception_code=BrickletRS485.EXCEPTION_CODE_SUCCESS):
        if item == None:
            self.error_stream_oos = self.error_stream_oos + 1
            self.label_error_stream.setText(str(self.error_stream_oos))
            return EXCEPTION_CODE_STREAM_OUT_OF_SYNC
        return exception_code

    def modbus_master_response_received(self, function_name, request_id, exception_code, data=None, streamed=False):
        self.modbus_master_answer_timer.stop()
        if streamed:
            exception_code = self.check_stream_sync(data, exception_code)

        request = None
        for item in self.modbus_log:
            if item.is_request and item.request_id == request_id:
                request = item
        if request is not None:
            self.modbus_log_add(ModbusEvent(False, time.localtime(), request_id, request.slave_address, function_name, request.address, request.count, data, exception_code))
            self.modbus_log.remove(request)
        else:
            self.modbus_log_add(ModbusEvent(False, time.localtime(), request_id, 'Master (self)', function_name, None, None, data, exception_code))

        self.modbus_master_send_button.setEnabled(True)
        self.modbus_master_send_button.setDefault(True)

    def modbus_slave_request_received(self, function_name, request_id, starting_address, count, data=None, streamed=False):
        exception_code = self.check_stream_sync(data) if streamed else BrickletRS485.EXCEPTION_CODE_SUCCESS
        self.modbus_log_add(ModbusEvent(True, time.localtime(), request_id, str(self.modbus_master_slave_address_spinbox.value()) + ' (self)', function_name, starting_address, count, data, exception_code))

    def modbus_slave_answer_request_async(self, answer_fn, answer_fn_args, log_fn_args):
        if self.modbus_slave_behaviour_combobox.currentIndex() == 0:
            return

        def modbus_slave_response_sent(function_name, request_id, starting_address, count, data=None, exception_code=BrickletRS485.EXCEPTION_CODE_SUCCESS):
            self.modbus_log_add(ModbusEvent(False, time.localtime(), request_id, 'Master', function_name, starting_address, count, data, exception_code))

        def modbus_slave_response_sent_error(e, *args):
            if isinstance(e, Error) and e.value == Error.TIMEOUT:
                self.increase_error_count()
                modbus_slave_response_sent(*args, exception_code=EXCEPTION_CODE_DEVICE_TIMEOUT)
            else:
                self.popup_fail(e)

        async_call(answer_fn, answer_fn_args,
                   lambda: modbus_slave_response_sent(*log_fn_args),
                   lambda error: modbus_slave_response_sent_error(error, *log_fn_args))

    def cb_modbus_slave_read_coils_request(self, request_id, starting_address, count):
        self.modbus_slave_request_received('Read Coils', request_id, starting_address, count)

        data = [i % 2 == 0 for i in range(count)]

        self.modbus_slave_answer_request_async(
            self.rs485.modbus_slave_answer_read_coils_request, (request_id, data),
            ('Read Coils', request_id, starting_address, count, ' '.join(str(b) for b in data)))

    def cb_modbus_master_read_coils_response(self,
                                             request_id,
                                             exception_code,
                                             coils):
        self.modbus_master_response_received('Read Coils', request_id, exception_code, ' '.join(str(b) for b in coils), streamed=True)

    def cb_modbus_slave_read_holding_registers_request(self,
                                                       request_id,
                                                       starting_address,
                                                       count):
        starting_address += 400000
        self.modbus_slave_request_received('Read Holding Registers', request_id, starting_address, count)

        data = list(range(1, count+1))

        self.modbus_slave_answer_request_async(
            self.rs485.modbus_slave_answer_read_holding_registers_request, (request_id, data),
            ('Read Holding Registers', request_id, starting_address, count, ' '.join("{:04X}".format(i) for i in data)))

    def cb_modbus_master_read_holding_registers_response(self,
                                                         request_id,
                                                         exception_code,
                                                         holding_registers):
        self.modbus_master_response_received('Read Holding Registers', request_id, exception_code, ' '.join("{:04X}".format(i) for i in holding_registers), streamed=True)

    def cb_modbus_slave_write_single_coil_request(self,
                                                  request_id,
                                                  coil_address,
                                                  coil_value):
        self.modbus_slave_request_received('Write Single Coil', request_id, coil_address, 1, str(coil_value))

        self.modbus_slave_answer_request_async(
            self.rs485.modbus_slave_answer_write_single_coil_request, (request_id),
            ('Write Single Coil', request_id, coil_address, 1))

    def cb_modbus_master_write_single_coil_response(self,
                                                    request_id,
                                                    exception_code):
        self.modbus_master_response_received('Write Single Coil', request_id, exception_code)

    def cb_modbus_slave_write_single_register_request(self,
                                                      request_id,
                                                      register_address,
                                                      register_value):
        register_address += 400000
        self.modbus_slave_request_received('Write Single Register', request_id, register_address, 1, '{:04X}'.format(register_value))

        self.modbus_slave_answer_request_async(
            self.rs485.modbus_slave_answer_write_single_register_request, (request_id),
            ('Write Single Register', request_id, register_address, 1))

    def cb_modbus_master_write_single_register_response(self,
                                                        request_id,
                                                        exception_code):
        self.modbus_master_response_received('Write Single Register', request_id, exception_code)

    def cb_modbus_slave_write_multiple_coils_request(self,
                                                     request_id,
                                                     starting_address,
                                                     coils):
        self.modbus_slave_request_received('Write Multiple Coils', request_id, starting_address, len(coils), ' '.join(str(c) for c in coils), streamed=True)

        self.modbus_slave_answer_request_async(
            self.rs485.modbus_slave_answer_write_multiple_coils_request, (request_id),
            ('Write Multiple Coils', request_id, starting_address, len(coils)))

    def cb_modbus_master_write_multiple_coils_response(self,
                                                       request_id,
                                                       exception_code):
        self.modbus_master_response_received('Write Multiple Coils', request_id, exception_code)

    def cb_modbus_slave_write_multiple_registers_request(self,
                                                         request_id,
                                                         starting_address,
                                                         registers):
        starting_address += 400000
        self.modbus_slave_request_received('Write Multiple Registers', request_id, starting_address, len(registers), ' '.join("{:04X}".format(i) for i in registers), streamed=True)

        self.modbus_slave_answer_request_async(
            self.rs485.modbus_slave_answer_write_multiple_registers_request, (request_id),
            ('Write Multiple Registers', request_id, starting_address, len(registers)))

    def cb_modbus_master_write_multiple_registers_response(self,
                                                           request_id,
                                                           exception_code):
        self.modbus_master_response_received('Write Multiple Registers', request_id, exception_code)

    def cb_modbus_slave_read_discrete_inputs_request(self,
                                                     request_id,
                                                     starting_address,
                                                     count):
        starting_address += 100000
        self.modbus_slave_request_received('Read Discrete Inputs', request_id, starting_address, count)

        data = [i % 2 == 0 for i in range(count)]

        self.modbus_slave_answer_request_async(
            self.rs485.modbus_slave_answer_read_discrete_inputs_request, (request_id, data),
            ('Read Discrete Inputs', request_id, starting_address, count, ' '.join(str(c) for c in data)))

    def cb_modbus_master_read_discrete_inputs_response(self,
                                                       request_id,
                                                       exception_code,
                                                       discrete_inputs):
        self.modbus_master_response_received('Read Discrete Inputs', request_id, exception_code, ' '.join(str(c) for c in discrete_inputs), streamed=True)

    def cb_modbus_slave_read_input_registers_request(self,
                                                     request_id,
                                                     starting_address,
                                                     count):
        starting_address += 300000
        self.modbus_slave_request_received('Read Input Registers', request_id, starting_address, count)

        data = list(range(1, count+1))

        self.modbus_slave_answer_request_async(
            self.rs485.modbus_slave_answer_read_input_registers_request, (request_id, data),
            ('Read Input Registers', request_id, starting_address, count, ' '.join("{:04X}".format(i) for i in data)))

    def cb_modbus_master_read_input_registers_response(self,
                                                       request_id,
                                                       exception_code,
                                                       input_registers):
        self.modbus_master_response_received('Read Input Registers', request_id, exception_code, ' '.join("{:04X}".format(i) for i in input_registers), streamed=True)

    def line_ending_changed(self):
        selected_line_ending = self.rs485_input_line_ending_combobox.currentText()
        self.rs485_input_line_ending_lineedit.setEnabled(selected_line_ending == 'Hex:')

    def get_line_ending(self):
        selected_line_ending = self.rs485_input_line_ending_combobox.currentText()

        d = {
            '\\n': '0A',
            '\\r': '0D',
            '\\r\\n':'0D0A',
            '\\n\\r':'0A0D',
            '\\0': '00',
            'Hex:': self.rs485_input_line_ending_lineedit.text()
        }

        hex_le = d.get(selected_line_ending, '')

        try:
            line_ending = bytes.fromhex(hex_le)
        except TypeError:
            # TODO: Handle Error!
            # Should never happen, because LineEdit has a validator applied
            line_ending = bytes()

        return line_ending

    def do_write(self):
        if self.configured_mode != self.rs485.MODE_RS485:
            self.popup_fail(MSG_ERR_NOT_RS485)
            return

        pos = 0
        written = 0
        text = self.combo_input.currentText()
        attempts_without_progress = 0

        if self.text_type_combobox.currentIndex() == 0:
            bytes_ = text.encode('utf-8') + self.get_line_ending()
        else:
            bytes_ = bytes.fromhex(text)

        while pos < len(bytes_):
            written = self.rs485.write(bytes_[pos:])
            pos = pos + written

            if written == 0:
                attempts_without_progress += 1
            else:
                attempts_without_progress = 0

            if attempts_without_progress == 100:
                self.popup_fail("Could not write. Made no progress after {} attempts.".format(attempts_without_progress))
                return

        entries = [self.combo_input.itemText(i) for i in range(self.combo_input.count())]

        if text not in entries:
            self.combo_input.addItem(text)

        self.combo_input.setCurrentIndex(self.combo_input.count() - 1)

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
        if self.mode_combobox.itemText(0) == 'Querying...':
            self.mode_combobox.removeItem(0)

        self.mode_combobox.setCurrentIndex(mode)
        self.configured_mode = mode
        self.apply_button.setEnabled(False)

    def text_type_changed(self):
        if self.text_type_combobox.currentIndex() == 0:
            self.hextext.hide()
            self.text.show()
            self.combo_input.setValidator(None)
            self.rs485_input_line_ending_lineedit.show()
            self.rs485_input_line_ending_combobox.show()
        else:
            self.text.hide()
            self.hextext.show()
            self.combo_input.setValidator(HexValidator())
            self.rs485_input_line_ending_lineedit.hide()
            self.rs485_input_line_ending_combobox.hide()

        self.combo_input.clearEditText()
        self.combo_input.clear()

    def configuration_changed(self):
        self.apply_button.setEnabled(True)

    def error_get_mode_async(self):
        self.popup_fail("Could not set mode.")
        self.apply_button.setEnabled(True)

    def apply_clicked(self):
        mode = self.mode_combobox.currentIndex()
        baudrate = self.baudrate_spinbox.value()
        parity = self.parity_combobox.currentIndex()
        stopbits = self.stopbits_spinbox.value()
        wordlength = self.wordlength_spinbox.value()
        duplex = self.duplex_combobox.currentIndex()

        self.rs485.set_rs485_configuration(baudrate,
                                           parity,
                                           stopbits,
                                           wordlength,
                                           duplex)

        self.rs485.set_mode(mode)

        if mode == self.rs485.MODE_MODBUS_MASTER_RTU or mode == self.rs485.MODE_MODBUS_SLAVE_RTU:
            self.rs485.set_modbus_configuration(self.modbus_slave_address_spinbox.value(),
                                                self.modbus_master_request_timeout_spinbox.value())
        async_call(self.rs485.get_mode, None, self.get_mode_async, self.error_get_mode_async)

        self.apply_button.setEnabled(False)

    def is_read_callback_enabled_async(self, enabled):
        self.read_callback_was_enabled = enabled

        if not enabled:
            async_call(self.rs485.enable_read_callback, None, None, self.increase_error_count)

    def cb_error_count(self, error_count):
        self.label_error_overrun.setText(str(error_count.overrun_error_count))
        self.label_error_parity.setText(str(error_count.parity_error_count))

    def cb_modbus_common_error_count(self, error_count):
        self.label_error_modbus_timeout.setText(str(error_count.timeout_error_count))
        self.label_error_modbus_checksum.setText(str(error_count.checksum_error_count))
        self.label_error_modbus_frame_size.setText(str(error_count.frame_too_big_error_count))
        self.label_error_modbus_illegal_function.setText(str(error_count.illegal_function_error_count))
        self.label_error_modbus_illegal_data_address.setText(str(error_count.illegal_data_address_error_count))
        self.label_error_modbus_illegal_data_value.setText(str(error_count.illegal_data_value_error_count))
        self.label_error_modbus_slave_device_failure.setText(str(error_count.slave_device_failure_error_count))

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
        self.read_callback_was_enabled = None

        async_call(self.rs485.is_read_callback_enabled, None, self.is_read_callback_enabled_async, self.increase_error_count)
        async_call(self.rs485.get_communication_led_config, None, self.get_communication_led_config_async, self.increase_error_count)
        async_call(self.rs485.get_error_led_config, None, self.get_error_led_config_async, self.increase_error_count)
        async_call(self.rs485.get_rs485_configuration, None, self.get_rs485_configuration_async, self.increase_error_count)
        async_call(self.rs485.get_modbus_configuration, None, self.get_modbus_configuration_async, self.increase_error_count)
        async_call(self.rs485.get_mode, None, self.get_mode_async, self.increase_error_count)

        self.cbe_error_count.set_period(250)
        self.cbe_error_count_modbus.set_period(250)

    def stop(self):
        self.modbus_master_answer_timer.stop()
        self.cbe_error_count.set_period(0)
        self.cbe_error_count_modbus.set_period(0)

        if self.read_callback_was_enabled == False: # intentionally check for False to distinguish from None
            async_call(self.rs485.disable_read_callback, None, None, self.increase_error_count)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRS485.DEVICE_IDENTIFIER
