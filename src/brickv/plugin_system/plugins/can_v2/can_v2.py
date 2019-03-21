# -*- coding: utf-8 -*-
"""
CAN V2 Plugin
Copyright (C) 2018 Matthias Bolte <matthias@tinkerforge.com>

can_v2.py: CAN V2 Plugin Implementation

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

import os

from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem, QAction

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_can_v2 import BrickletCANV2, GetReadFilterConfiguration
from brickv.plugin_system.plugins.can_v2.ui_can_v2 import Ui_CANV2
from brickv.async_call import async_call
from brickv.hex_validator import HexValidator
from brickv.utils import get_main_window, get_home_path, get_save_file_name

class CANV2(COMCUPluginBase, Ui_CANV2):
    qtcb_frame_read = pyqtSignal(int, int, object)

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletCANV2, *args)

        self.setupUi(self)

        self.can = self.device

        self.qtcb_frame_read.connect(self.cb_frame_read)
        self.can.register_callback(self.can.CALLBACK_FRAME_READ,
                                   self.qtcb_frame_read.emit)

        self.last_filename = os.path.join(get_home_path(), 'can_bricklet_v2_history.log')

        self.frame_read_callback_was_enabled = False

        self.tree_frames.header().resizeSection(0, 150)
        self.tree_frames.header().resizeSection(1, 170)
        self.tree_frames.header().resizeSection(2, 300)
        self.tree_frames.header().resizeSection(3, 100)

        self.edit_data.setValidator(HexValidator(max_bytes=8))

        self.combo_frame_type.currentIndexChanged.connect(self.frame_type_changed)
        self.spin_baud_rate.valueChanged.connect(self.transceiver_configuration_changed)
        self.spin_sample_point.valueChanged.connect(self.transceiver_configuration_changed)
        self.combo_transceiver_mode.currentIndexChanged.connect(self.transceiver_configuration_changed)

        self.spin_write_buffer_size.valueChanged.connect(self.queue_configuration_changed)
        self.spin_write_buffer_timeout.valueChanged.connect(self.queue_configuration_changed)
        self.spin_write_backlog_size.valueChanged.connect(self.queue_configuration_changed)
        self.edit_read_buffer_sizes.textEdited.connect(self.queue_configuration_changed)
        self.spin_read_backlog_size.valueChanged.connect(self.queue_configuration_changed)

        for i in range(32):
            self.combo_filter_buffer.addItem(str(i))

        self.combo_filter_buffer.currentIndexChanged.connect(self.read_filter_buffer_changed)
        self.combo_filter_mode.currentIndexChanged.connect(self.read_filter_mode_changed)
        self.spin_filter_mask.valueChanged.connect(self.read_filter_configuration_changed)
        self.spin_filter_identifier.valueChanged.connect(self.read_filter_configuration_changed)

        self.button_write_frame.clicked.connect(self.write_frame)
        self.button_clear_history.clicked.connect(self.tree_frames.clear)
        self.button_save_history.clicked.connect(self.save_history)
        self.button_save_transceiver_configuration.clicked.connect(self.save_transceiver_configuration)
        self.button_reset_transceiver_configuration.clicked.connect(self.reset_transceiver_configuration)
        self.button_save_queue_configuration.clicked.connect(self.save_queue_configuration)
        self.button_reset_queue_configuration.clicked.connect(self.reset_queue_configuration)
        self.button_save_read_filter_configuration.clicked.connect(self.save_read_filter_configuration)
        self.button_reset_read_filter_configuration.clicked.connect(self.reset_read_filter_configuration)

        self.error_log_timer = QTimer(self)
        self.error_log_timer.timeout.connect(self.update_error_log)
        self.error_log_timer.setInterval(1000)

        self.frame_type_changed()
        self.read_filter_buffer_changed()
        self.read_filter_mode_changed()
        self.read_filter_configuration_changed()

        self.com_led_off_action = QAction('Off', self)
        self.com_led_off_action.triggered.connect(lambda: self.can.set_communication_led_config(BrickletCANV2.COMMUNICATION_LED_CONFIG_OFF))
        self.com_led_on_action = QAction('On', self)
        self.com_led_on_action.triggered.connect(lambda: self.can.set_communication_led_config(BrickletCANV2.COMMUNICATION_LED_CONFIG_ON))
        self.com_led_show_heartbeat_action = QAction('Show Heartbeat', self)
        self.com_led_show_heartbeat_action.triggered.connect(lambda: self.can.set_communication_led_config(BrickletCANV2.COMMUNICATION_LED_CONFIG_SHOW_HEARTBEAT))
        self.com_led_show_communication_action = QAction('Show Com', self)
        self.com_led_show_communication_action.triggered.connect(lambda: self.can.set_communication_led_config(BrickletCANV2.COMMUNICATION_LED_CONFIG_SHOW_COMMUNICATION))

        self.extra_configs += [(1, 'Com LED:', [self.com_led_off_action,
                                                self.com_led_on_action,
                                                self.com_led_show_heartbeat_action,
                                                self.com_led_show_communication_action])]

        self.error_led_off_action = QAction('Off', self)
        self.error_led_off_action.triggered.connect(lambda: self.can.set_error_led_config(BrickletCANV2.ERROR_LED_CONFIG_OFF))
        self.error_led_on_action = QAction('On', self)
        self.error_led_on_action.triggered.connect(lambda: self.can.set_error_led_config(BrickletCANV2.ERROR_LED_CONFIG_ON))
        self.error_led_show_heartbeat_action = QAction('Show Heartbeat', self)
        self.error_led_show_heartbeat_action.triggered.connect(lambda: self.can.set_error_led_config(BrickletCANV2.ERROR_LED_CONFIG_SHOW_HEARTBEAT))
        self.error_led_show_transceiver_state_action = QAction('Show Transceiver State', self)
        self.error_led_show_transceiver_state_action.triggered.connect(lambda: self.can.set_error_led_config(BrickletCANV2.ERROR_LED_CONFIG_SHOW_TRANSCEIVER_STATE))
        self.error_led_show_error_action = QAction('Show Error', self)
        self.error_led_show_error_action.triggered.connect(lambda: self.can.set_error_led_config(BrickletCANV2.ERROR_LED_CONFIG_SHOW_ERROR))

        self.extra_configs += [(1, 'Error LED:', [self.error_led_off_action,
                                                  self.error_led_on_action,
                                                  self.error_led_show_heartbeat_action,
                                                  self.error_led_show_transceiver_state_action,
                                                  self.error_led_show_error_action])]

    def start(self):
        async_call(self.can.get_communication_led_config, None, self.get_communication_led_config_async, self.increase_error_count)
        async_call(self.can.get_error_led_config, None, self.get_error_led_config_async, self.increase_error_count)

        self.frame_read_callback_was_enabled = False

        async_call(self.can.get_frame_read_callback_configuration, None, self.get_frame_read_callback_configuration_async, self.increase_error_count)
        async_call(self.can.get_transceiver_configuration, None, self.get_transceiver_configuration_async, self.increase_error_count)
        async_call(self.can.get_queue_configuration, None, self.get_queue_configuration_async, self.increase_error_count)

        def make_get_read_filter_configuration_async_lambda(i):
            return lambda config: self.get_read_filter_configuration_async(i, config)

        for i in range(32):
            async_call(self.can.get_read_filter_configuration, i, make_get_read_filter_configuration_async_lambda(i), self.increase_error_count)

        self.update_error_log()
        self.error_log_timer.start()

    def stop(self):
        self.error_log_timer.stop()

        if not self.frame_read_callback_was_enabled:
            try:
                self.can.set_response_expected(self.can.FUNCTION_SET_FRAME_READ_CALLBACK_CONFIGURATION, False)
                self.can.set_frame_read_callback_configuration(False)
                self.can.set_response_expected(self.can.FUNCTION_SET_FRAME_READ_CALLBACK_CONFIGURATION, True)
            except ip_connection.Error:
                pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletCANV2.DEVICE_IDENTIFIER

    def get_communication_led_config_async(self, config):
        if config == BrickletCANV2.COMMUNICATION_LED_CONFIG_OFF:
            self.com_led_off_action.trigger()
        elif config == BrickletCANV2.COMMUNICATION_LED_CONFIG_ON:
            self.com_led_on_action.trigger()
        elif config == BrickletCANV2.COMMUNICATION_LED_CONFIG_SHOW_HEARTBEAT:
            self.com_led_show_heartbeat_action.trigger()
        elif config == BrickletCANV2.COMMUNICATION_LED_CONFIG_SHOW_COMMUNICATION:
            self.com_led_show_communication_action.trigger()

    def get_error_led_config_async(self, config):
        if config == BrickletCANV2.ERROR_LED_CONFIG_OFF:
            self.error_led_off_action.trigger()
        elif config == BrickletCANV2.ERROR_LED_CONFIG_ON:
            self.error_led_on_action.trigger()
        elif config == BrickletCANV2.ERROR_LED_CONFIG_SHOW_HEARTBEAT:
            self.error_led_show_heartbeat_action.trigger()
        elif config == BrickletCANV2.ERROR_LED_CONFIG_SHOW_TRANSCEIVER_STATE:
            self.error_led_show_transceiver_state_action.trigger()
        elif config == BrickletCANV2.ERROR_LED_CONFIG_SHOW_ERROR:
            self.error_led_show_error_action.trigger()

    def cb_frame_read(self, frame_type, identifier, data):
        length = len(data)
        parts = []
        max_length = 0

        if frame_type == self.can.FRAME_TYPE_STANDARD_DATA:
            parts.append('Standard Data')
            max_length = 8
        elif frame_type == self.can.FRAME_TYPE_STANDARD_REMOTE:
            parts.append('Standard Remote')
        elif frame_type == self.can.FRAME_TYPE_EXTENDED_DATA:
            parts.append('Extended Data')
            max_length = 8
        elif frame_type == self.can.FRAME_TYPE_EXTENDED_REMOTE:
            parts.append('Extended Remote')
        else:
            parts.append('Unknown')

        parts.append(self.spin_identifier.textFromValue(identifier))
        parts.append(' '.join(['%02X' % c for c in data[:min(length, max_length)]]))
        parts.append(str(length))

        scroll_bar = self.tree_frames.verticalScrollBar()
        at_bottom = scroll_bar.value() == scroll_bar.maximum()

        self.tree_frames.addTopLevelItem(QTreeWidgetItem(parts))

        if at_bottom:
            self.tree_frames.scrollToBottom()

    def get_frame_read_callback_configuration_async(self, enabled):
        self.frame_read_callback_was_enabled = enabled
        self.can.set_frame_read_callback_configuration(True)

    def get_transceiver_configuration_async(self, config):
        self.spin_baud_rate.setValue(config.baud_rate)
        self.spin_sample_point.setValue(config.sample_point / 10.0)
        self.combo_transceiver_mode.setCurrentIndex(config.transceiver_mode)
        self.button_save_transceiver_configuration.setEnabled(False)

    def get_queue_configuration_async(self, config):
        self.spin_write_buffer_size.setValue(config.write_buffer_size)
        self.spin_write_buffer_timeout.setValue(config.write_buffer_timeout)
        self.spin_write_backlog_size.setValue(config.write_backlog_size)
        self.edit_read_buffer_sizes.setText(','.join(map(str, config.read_buffer_sizes)))
        self.spin_read_backlog_size.setValue(config.read_backlog_size)
        self.button_save_queue_configuration.setEnabled(False)

    def get_read_filter_configuration_async(self, buffer_index, config):
        self.combo_filter_buffer.setItemData(buffer_index, config)
        self.read_filter_buffer_changed()
        self.button_save_read_filter_configuration.setEnabled(False)

    def get_error_log_async(self, errors):
        if errors.transceiver_state == BrickletCANV2.TRANSCEIVER_STATE_ACTIVE:
            self.label_transceiver_state.setText('Active')
        elif errors.transceiver_state == BrickletCANV2.TRANSCEIVER_STATE_PASSIVE:
            self.label_transceiver_state.setText('Passive')
        else:
            self.label_transceiver_state.setText('Disabled')

        self.label_transceiver_write_error_level.setText(str(errors.transceiver_write_error_level))
        self.label_transceiver_read_error_level.setText(str(errors.transceiver_read_error_level))
        self.label_transceiver_stuffing_errors.setText(str(errors.transceiver_stuffing_error_count))
        self.label_transceiver_format_errors.setText(str(errors.transceiver_format_error_count))
        self.label_transceiver_ack_errors.setText(str(errors.transceiver_ack_error_count))
        self.label_transceiver_bit1_errors.setText(str(errors.transceiver_bit1_error_count))
        self.label_transceiver_bit0_errors.setText(str(errors.transceiver_bit0_error_count))
        self.label_transceiver_crc_errors.setText(str(errors.transceiver_crc_error_count))
        self.label_write_buffer_timeouts.setText(str(errors.write_buffer_timeout_error_count))
        self.label_read_buffer_overflows.setText(str(errors.read_buffer_overflow_error_count) + ' [' + \
                                                 ''.join(map(lambda b: '1' if b else '0', errors.read_buffer_overflow_error_occurred)) + ']')
        self.label_read_backlog_overflows.setText(str(errors.read_backlog_overflow_error_count))

    def frame_type_changed(self):
        frame_type = self.combo_frame_type.currentIndex()
        extended = frame_type in [self.can.FRAME_TYPE_EXTENDED_DATA, self.can.FRAME_TYPE_EXTENDED_REMOTE]
        remote = frame_type in [self.can.FRAME_TYPE_STANDARD_REMOTE, self.can.FRAME_TYPE_EXTENDED_REMOTE]

        if extended:
            self.spin_identifier.setMaximum((1 << 29) - 1)
        else:
            self.spin_identifier.setMaximum((1 << 11) - 1)

        self.edit_data.setEnabled(not remote)
        self.spin_length.setEnabled(remote)

    def transceiver_configuration_changed(self):
        self.button_save_transceiver_configuration.setEnabled(True)

    def queue_configuration_changed(self):
        self.button_save_queue_configuration.setEnabled(True)

    def read_filter_buffer_changed(self):
        buffer_index = self.combo_filter_buffer.currentIndex()

        if buffer_index < 0 or self.combo_filter_buffer.itemData(buffer_index) == None:
            self.combo_filter_mode.setCurrentIndex(0)
            self.spin_filter_mask.setValue(0)
            self.spin_filter_identifier.setValue(0)
        else:
            config = self.combo_filter_buffer.itemData(buffer_index)

            self.combo_filter_mode.setCurrentIndex(config.filter_mode)
            self.spin_filter_mask.setValue(config.filter_mask)
            self.spin_filter_identifier.setValue(config.filter_identifier)

        self.read_filter_configuration_changed()
        self.button_save_read_filter_configuration.setEnabled(False)

    def read_filter_mode_changed(self):
        mode = self.combo_filter_mode.currentIndex()

        if mode == self.can.FILTER_MODE_MATCH_STANDARD_ONLY:
            self.spin_filter_mask.setMaximum((1 << 11) - 1)
            self.spin_filter_identifier.setMaximum((1 << 11) - 1)
        else:
            self.spin_filter_mask.setMaximum((1 << 29) - 1)
            self.spin_filter_identifier.setMaximum((1 << 11) - 1)

        self.spin_filter_mask.setEnabled(mode != self.can.FILTER_MODE_ACCEPT_ALL)
        self.spin_filter_identifier.setEnabled(mode != self.can.FILTER_MODE_ACCEPT_ALL)
        self.button_save_read_filter_configuration.setEnabled(True)

    def read_filter_configuration_changed(self):
        self.button_save_read_filter_configuration.setEnabled(True)

    def update_error_log(self):
        async_call(self.can.get_error_log, None, self.get_error_log_async, self.increase_error_count)

    def write_frame(self):
        frame_type = self.combo_frame_type.currentIndex()
        remote = frame_type in [self.can.FRAME_TYPE_STANDARD_REMOTE, self.can.FRAME_TYPE_EXTENDED_REMOTE]
        identifier = self.spin_identifier.value()
        data_str = self.edit_data.text().replace(' ', '')

        if remote:
            data = [0] * self.spin_length.value()
        else:
            data = []

            while len(data_str) > 0:
                data.append(int(data_str[:2], 16))
                data_str = data_str[2:]

            data = data[:15]

        self.button_write_frame.setEnabled(False)
        async_call(self.can.write_frame, (frame_type, identifier, data), self.write_frame_async, self.write_frame_error)

    def write_frame_async(self, success):
        self.button_write_frame.setEnabled(True)

        if not success:
            QMessageBox.critical(get_main_window(), 'Write Frame', 'Could not write frame due to write buffer/backlog overflow.', QMessageBox.Ok)

    def write_frame_error(self):
        self.button_write_frame.setEnabled(True)
        self.increase_error_count()

    def save_history(self):
        filename = get_save_file_name(get_main_window(), 'Save History', self.last_filename)

        if len(filename) == 0:
            return

        self.last_filename = filename

        try:
            f = open(filename, 'w')
        except OSError as e:
            QMessageBox.critical(get_main_window(), 'Save History Error',
                                 'Could not open {0} for writing:\n\n{1}'.format(filename, e))
            return

        root = self.tree_frames.invisibleRootItem()
        content = ['Frame Type;Identifier [Hex];Data [Hex];Length\n']

        for i in range(root.childCount()):
            child = root.child(i)
            row = []

            for c in range(child.columnCount()):
                row.append(child.text(c))

            content.append(';'.join(row) + '\n')

        try:
            # FIXME: add progress dialog if content is bigger than some megabytes
            f.write(''.join(content))
        except Exception as e:
            QMessageBox.critical(get_main_window(), 'Save History Error',
                                 'Could not write to {0}:\n\n{1}'.format(filename, e))

        f.close()

    def save_transceiver_configuration(self):
        baud_rate = self.spin_baud_rate.value()
        sample_point = int(self.spin_sample_point.value() * 10)
        transceiver_mode = self.combo_transceiver_mode.currentIndex()

        # FIXME: add validation
        self.can.set_transceiver_configuration(baud_rate, sample_point, transceiver_mode)
        self.button_save_transceiver_configuration.setEnabled(False)

    def reset_transceiver_configuration(self):
        self.spin_baud_rate.setValue(125000)
        self.spin_sample_point.setValue(62.5)
        self.combo_transceiver_mode.setCurrentIndex(0)

    def save_queue_configuration(self):
        write_buffer_size = self.spin_write_buffer_size.value()
        write_buffer_timeout = self.spin_write_buffer_timeout.value()
        write_backlog_size = self.spin_write_backlog_size.value()
        read_buffer_sizes_str = self.edit_read_buffer_sizes.text().replace(' ', '')
        read_backlog_size = self.spin_read_backlog_size.value()

        if len(read_buffer_sizes_str) == 0:
            read_buffer_sizes = []
        else:
            try:
                read_buffer_sizes = list(map(int, read_buffer_sizes_str.split(',')))
            except:
                QMessageBox.critical(get_main_window(), 'Save Queue Configuration Error',
                                     'Read Buffer Sizes could not be parsed as comma-separated list of integers.')
                return

            if len(read_buffer_sizes) > 32:
                QMessageBox.critical(get_main_window(), 'Save Queue Configuration Error',
                                     'More than 32 Read Buffer Sizes specified.')
                return

            for read_buffer_size in read_buffer_sizes:
                if read_buffer_size == 0:
                    QMessageBox.critical(get_main_window(), 'Save Queue Configuration Error',
                                         'Read Buffer Sizes cannot be 0.')
                    return

                if read_buffer_size < -32 or read_buffer_size > 32:
                    QMessageBox.critical(get_main_window(), 'Save Queue Configuration Error',
                                         'Read Buffer Sizes must be in [-32..+32] range.')
                    return

            if write_buffer_size + sum(map(abs, read_buffer_sizes)) > 32:
                QMessageBox.critical(get_main_window(), 'Save Queue Configuration Error',
                                     'More than 32 buffers used in total.')
                return

            if write_backlog_size + read_backlog_size > 768:
                QMessageBox.critical(get_main_window(), 'Save Queue Configuration Error',
                                     'Backlog cannot be longer than 768 frames in total.')
                return

        # FIXME: add validation
        self.can.set_queue_configuration(write_buffer_size, write_buffer_timeout, write_backlog_size, read_buffer_sizes, read_backlog_size)
        self.button_save_queue_configuration.setEnabled(False)

    def reset_queue_configuration(self):
        self.spin_write_buffer_size.setValue(8)
        self.spin_write_buffer_timeout.setValue(0)
        self.spin_write_backlog_size.setValue(384)
        self.edit_read_buffer_sizes.setText('16,-8')
        self.spin_read_backlog_size.setValue(384)

    def save_read_filter_configuration(self):
        buffer_index = self.combo_filter_buffer.currentIndex()
        mode = self.combo_filter_mode.currentIndex()
        mask = self.spin_filter_mask.value()
        identifier = self.spin_filter_identifier.value()

        self.combo_filter_buffer.setItemData(buffer_index, GetReadFilterConfiguration(mode, mask, identifier))

        # FIXME: add validation
        self.can.set_read_filter_configuration(buffer_index, mode, mask, identifier)
        self.button_save_read_filter_configuration.setEnabled(False)

    def reset_read_filter_configuration(self):
        self.combo_filter_mode.setCurrentIndex(0)
        self.spin_filter_mask.setValue(0)
        self.spin_filter_identifier.setValue(0)
