# -*- coding: utf-8 -*-
"""
CAN Plugin
Copyright (C) 2016-2017 Matthias Bolte <matthias@tinkerforge.com>

can.py: CAN Plugin Implementation

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

from PyQt4.QtCore import pyqtSignal, QTimer
from PyQt4.QtGui import QMessageBox, QTreeWidgetItem

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_can import BrickletCAN
from brickv.plugin_system.plugins.can.ui_can import Ui_CAN
from brickv.async_call import async_call
from brickv.hex_validator import HexValidator
from brickv.utils import get_main_window, get_home_path, get_save_file_name

class CAN(PluginBase, Ui_CAN):
    qtcb_frame_read = pyqtSignal(int, int, object, int)

    def __init__(self, *args):
        PluginBase.__init__(self, BrickletCAN, *args)

        self.setupUi(self)

        self.can = self.device

        self.qtcb_frame_read.connect(self.cb_frame_read)
        self.can.register_callback(self.can.CALLBACK_FRAME_READ,
                                   self.qtcb_frame_read.emit)

        self.last_filename = os.path.join(get_home_path(), 'can_bricklet_history.log')

        self.filter_mask = 0
        self.filter1 = 0
        self.filter2 = 0

        self.frame_read_callback_was_enabled = False

        self.tree_frames.header().resizeSection(0, 150)
        self.tree_frames.header().resizeSection(1, 135)
        self.tree_frames.header().resizeSection(2, 135)
        self.tree_frames.header().resizeSection(3, 300)
        self.tree_frames.header().resizeSection(4, 100)

        self.edit_data.setValidator(HexValidator(max_bytes=8))

        self.combo_frame_type.currentIndexChanged.connect(self.frame_type_changed)
        self.combo_baud_rate.currentIndexChanged.connect(self.configuration_changed)
        self.combo_transceiver_mode.currentIndexChanged.connect(self.configuration_changed)
        self.spin_write_timeout.valueChanged.connect(self.configuration_changed)

        self.combo_filter_mode.currentIndexChanged.connect(self.filter_mode_changed)
        self.spin_filter_mask_extended.valueChanged.connect(self.mask_or_filter_changed)
        self.spin_filter_mask_standard.valueChanged.connect(self.mask_or_filter_changed)
        self.spin_filter_mask_data1.valueChanged.connect(self.mask_or_filter_changed)
        self.spin_filter_mask_data2.valueChanged.connect(self.mask_or_filter_changed)
        self.spin_filter1_extended.valueChanged.connect(self.mask_or_filter_changed)
        self.spin_filter1_standard.valueChanged.connect(self.mask_or_filter_changed)
        self.spin_filter1_data1.valueChanged.connect(self.mask_or_filter_changed)
        self.spin_filter1_data2.valueChanged.connect(self.mask_or_filter_changed)
        self.spin_filter2_extended.valueChanged.connect(self.mask_or_filter_changed)
        self.spin_filter2_standard.valueChanged.connect(self.mask_or_filter_changed)
        self.spin_filter2_data1.valueChanged.connect(self.mask_or_filter_changed)
        self.spin_filter2_data2.valueChanged.connect(self.mask_or_filter_changed)

        self.button_write_frame.clicked.connect(self.write_frame)
        self.button_clear_history.clicked.connect(self.tree_frames.clear)
        self.button_save_history.clicked.connect(self.save_history)
        self.button_save_configuration.clicked.connect(self.save_configuration)
        self.button_save_read_filter.clicked.connect(self.save_read_filter)

        self.error_log_timer = QTimer(self)
        self.error_log_timer.timeout.connect(self.update_error_log)
        self.error_log_timer.setInterval(1000)

        self.frame_type_changed()
        self.filter_mode_changed()

    def start(self):
        self.frame_read_callback_was_enabled = False

        async_call(self.can.is_frame_read_callback_enabled, None, self.is_frame_read_callback_enabled_async, self.increase_error_count)
        async_call(self.can.get_configuration, None, self.get_configuration_async, self.increase_error_count)
        async_call(self.can.get_read_filter, None, self.get_read_filter_async, self.increase_error_count)

        self.update_error_log()
        self.error_log_timer.start()

    def stop(self):
        self.error_log_timer.stop()

        if not self.frame_read_callback_was_enabled:
            try:
                self.can.disable_frame_read_callback()
            except:
                pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletCAN.DEVICE_IDENTIFIER

    def cb_frame_read(self, frame_type, identifier, data, length):
        parts = []
        max_length = 0
        extended = False

        if frame_type == self.can.FRAME_TYPE_STANDARD_DATA:
            parts.append('Standard Data')
            max_length = 8
        elif frame_type == self.can.FRAME_TYPE_STANDARD_REMOTE:
            parts.append('Standard Remote')
        elif frame_type == self.can.FRAME_TYPE_EXTENDED_DATA:
            parts.append('Extended Data')
            max_length = 8
            extended = True
        elif frame_type == self.can.FRAME_TYPE_EXTENDED_REMOTE:
            parts.append('Extended Remote')
            extended = True
        else:
            parts.append('Unknown')

        if extended:
            parts.append(self.spin_identifier_extended.textFromValue((identifier >> 11) & 0x3FFFF))
        else:
            parts.append('')

        parts.append(self.spin_identifier_standard.textFromValue(identifier & 0x7FF))
        parts.append(' '.join(['%02X' % c for c in data[:min(length, max_length)]]))
        parts.append(str(length))

        scroll_bar = self.tree_frames.verticalScrollBar()
        at_bottom = scroll_bar.value() == scroll_bar.maximum()

        self.tree_frames.addTopLevelItem(QTreeWidgetItem(parts))

        if at_bottom:
            self.tree_frames.scrollToBottom()

    def is_frame_read_callback_enabled_async(self, enabled):
        self.frame_read_callback_was_enabled = enabled
        self.can.enable_frame_read_callback()

    def get_configuration_async(self, conf):
        self.combo_baud_rate.setCurrentIndex(conf.baud_rate)
        self.combo_transceiver_mode.setCurrentIndex(conf.transceiver_mode)
        self.spin_write_timeout.setValue(conf.write_timeout)
        self.button_save_configuration.setEnabled(False)

    def get_read_filter_async(self, read_filter):
        self.combo_filter_mode.setCurrentIndex(read_filter.mode)

        self.spin_filter_mask_extended.setValue((read_filter.mask >> 11) & 0x3FFFF)
        self.spin_filter_mask_standard.setValue(read_filter.mask & 0x7FF)
        self.spin_filter_mask_data1.setValue((read_filter.mask >> 19) & 0xFF)
        self.spin_filter_mask_data2.setValue((read_filter.mask >> 11) & 0xFF)

        self.spin_filter1_extended.setValue((read_filter.filter1 >> 11) & 0x3FFFF)
        self.spin_filter1_standard.setValue(read_filter.filter1 & 0x7FF)
        self.spin_filter1_data1.setValue((read_filter.filter1 >> 19) & 0xFF)
        self.spin_filter1_data2.setValue((read_filter.filter1 >> 11) & 0xFF)

        self.spin_filter2_extended.setValue((read_filter.filter2 >> 11) & 0x3FFFF)
        self.spin_filter2_standard.setValue(read_filter.filter2 & 0x7FF)
        self.spin_filter2_data1.setValue((read_filter.filter2 >> 19) & 0xFF)
        self.spin_filter2_data2.setValue((read_filter.filter2 >> 11) & 0xFF)

        self.button_save_read_filter.setEnabled(False)

    def get_error_log_async(self, log):
        self.label_write_error_level.setText(str(log.write_error_level))
        self.label_read_error_level.setText(str(log.read_error_level))

        if log.transceiver_disabled:
            self.label_transceiver_status.setText('Disabled by Error')
        else:
            self.label_transceiver_status.setText('Active')

        self.label_write_timeouts.setText(str(log.write_timeout_count))
        self.label_read_register_overflows.setText(str(log.read_register_overflow_count))
        self.label_read_buffer_overflows.setText(str(log.read_buffer_overflow_count))

    def frame_type_changed(self):
        frame_type = self.combo_frame_type.currentIndex()
        extended = frame_type in [self.can.FRAME_TYPE_EXTENDED_DATA, self.can.FRAME_TYPE_EXTENDED_REMOTE]
        remote = frame_type in [self.can.FRAME_TYPE_STANDARD_REMOTE, self.can.FRAME_TYPE_EXTENDED_REMOTE]

        self.spin_identifier_extended.setEnabled(extended)
        self.edit_data.setDisabled(remote)

    def configuration_changed(self):
        self.button_save_configuration.setEnabled(True)

    def filter_mode_changed(self):
        index = self.combo_filter_mode.currentIndex()
        disabled = index == self.can.FILTER_MODE_DISABLED
        accept_all = index == self.can.FILTER_MODE_ACCEPT_ALL
        match_standard_and_data = index == self.can.FILTER_MODE_MATCH_STANDARD_AND_DATA
        match_extended = index == self.can.FILTER_MODE_MATCH_EXTENDED

        self.spin_filter_mask_extended.setDisabled(disabled or accept_all)
        self.spin_filter_mask_standard.setDisabled(disabled or accept_all)
        self.spin_filter_mask_data1.setDisabled(disabled or accept_all)
        self.spin_filter_mask_data2.setDisabled(disabled or accept_all)

        self.spin_filter1_extended.setDisabled(disabled or accept_all)
        self.spin_filter1_standard.setDisabled(disabled or accept_all)
        self.spin_filter1_data1.setDisabled(disabled or accept_all)
        self.spin_filter1_data2.setDisabled(disabled or accept_all)

        self.spin_filter2_extended.setDisabled(disabled or accept_all)
        self.spin_filter2_standard.setDisabled(disabled or accept_all)
        self.spin_filter2_data1.setDisabled(disabled or accept_all)
        self.spin_filter2_data2.setDisabled(disabled or accept_all)

        self.spin_filter_mask_extended.setVisible(match_extended)
        self.spin_filter_mask_data1.setVisible(match_standard_and_data)
        self.spin_filter_mask_data2.setVisible(match_standard_and_data)

        self.spin_filter1_extended.setVisible(match_extended)
        self.spin_filter1_data1.setVisible(match_standard_and_data)
        self.spin_filter1_data2.setVisible(match_standard_and_data)

        self.spin_filter2_extended.setVisible(match_extended)
        self.spin_filter2_data1.setVisible(match_standard_and_data)
        self.spin_filter2_data2.setVisible(match_standard_and_data)

        self.button_save_read_filter.setEnabled(True)

    def mask_or_filter_changed(self):
        self.button_save_read_filter.setEnabled(True)

    def update_error_log(self):
        async_call(self.can.get_error_log, None, self.get_error_log_async, self.increase_error_count)

    def write_frame(self):
        frame_type = self.combo_frame_type.currentIndex()
        extended = frame_type in [self.can.FRAME_TYPE_EXTENDED_DATA, self.can.FRAME_TYPE_EXTENDED_REMOTE]
        identifier = self.spin_identifier_standard.value()

        if extended:
            identifier |= self.spin_identifier_extended.value() << 11

        data_str = self.edit_data.text().replace(' ', '')
        data = []

        while len(data_str) > 0:
            data.append(int(data_str[:2], 16))
            data_str = data_str[2:]

        data += [0] * max(8 - len(data), 0)
        data = data[:8]
        length = self.spin_length.value()

        async_call(self.can.write_frame, (frame_type, identifier, data, length), self.write_frame_async, self.write_frame_error)

    def write_frame_async(self, success):
        if not success:
            QMessageBox.critical(get_main_window(), 'Write Frame', 'Could not write frame due to write buffer overflow.', QMessageBox.Ok)

    def write_frame_error(self):
        self.increase_error_count()
        self.button_write_frame.setEnabled(True)

    def save_history(self):
        filename = get_save_file_name(get_main_window(), 'Save History', self.last_filename)

        if len(filename) == 0:
            return

        self.last_filename = filename

        try:
            f = open(filename, 'wb')
        except Exception as e:
            QMessageBox.critical(get_main_window(), 'Save History Error',
                                 u'Could not open {0} for writing:\n\n{1}'.format(filename, e))
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
            f.write(''.join(content).encode('utf-8'))
        except Exception as e:
            QMessageBox.critical(get_main_window(), 'Save History Error',
                                 u'Could not write to {0}:\n\n{1}'.format(filename, e))

        f.close()

    def save_configuration(self):
        baud_rate = self.combo_baud_rate.currentIndex()
        transceiver_mode = self.combo_transceiver_mode.currentIndex()
        write_timeout = self.spin_write_timeout.value()

        # FIXME: add validation
        self.can.set_configuration(baud_rate, transceiver_mode, write_timeout)
        self.button_save_configuration.setEnabled(False)

    def save_read_filter(self):
        mode = self.combo_filter_mode.currentIndex()
        mask = 0
        filter1 = 0
        filter2 = 2

        if mode == self.can.FILTER_MODE_MATCH_STANDARD:
            mask = self.spin_filter_mask_standard.value()
            filter1 = self.spin_filter1_standard.value()
            filter2 = self.spin_filter2_standard.value()
        elif mode == self.can.FILTER_MODE_MATCH_STANDARD_AND_DATA:
            mask = (self.spin_filter_mask_data1.value() << 19) | (self.spin_filter_mask_data2.value() << 11) | self.spin_filter_mask_standard.value()
            filter1 = (self.spin_filter1_data1.value() << 19) | (self.spin_filter1_data2.value() << 11) | self.spin_filter1_standard.value()
            filter2 = (self.spin_filter2_data1.value() << 19) | (self.spin_filter2_data2.value() << 11) | self.spin_filter2_standard.value()
        elif mode == self.can.FILTER_MODE_MATCH_EXTENDED:
            mask = (self.spin_filter_mask_extended.value() << 11) | self.spin_filter_mask_standard.value()
            filter1 = (self.spin_filter1_extended.value() << 11) | self.spin_filter1_standard.value()
            filter2 = (self.spin_filter2_extended.value() << 11) | self.spin_filter2_standard.value()

        # FIXME: add validation
        self.can.set_read_filter(mode, mask, filter1, filter2)
        self.button_save_read_filter.setEnabled(False)
