# -*- coding: utf-8 -*-
"""
RS232 Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

rs232.py: RS232 Plugin Implementation

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

from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_rs232 import BrickletRS232
from brickv.bindings import ip_connection
from brickv.plugin_system.plugins.rs232.ui_rs232 import Ui_RS232
from brickv.async_call import async_call
from brickv.hex_validator import HexValidator

from brickv.qhexedit import QHexeditWidget

FLOWCONTROL_OFF = 0
FLOWCONTROL_SW = 1
FLOWCONTROL_HW = 2

class RS232(PluginBase, Ui_RS232):
    qtcb_read = pyqtSignal(object, int)
    qtcb_error = pyqtSignal(int)

    def __init__(self, *args):
        PluginBase.__init__(self, BrickletRS232, *args)

        self.setupUi(self)

        has_errors = self.firmware_version >= (2, 0, 1)

        self.text.setReadOnly(True)

        self.rs232 = self.device

        self.read_callback_was_enabled = False

        self.qtcb_read.connect(self.cb_read)
        self.rs232.register_callback(self.rs232.CALLBACK_READ,
                                     self.qtcb_read.emit)

        if has_errors:
            self.label_no_error_support.hide()
            self.qtcb_error.connect(self.cb_error)
            self.rs232.register_callback(self.rs232.CALLBACK_ERROR,
                                         self.qtcb_error.emit)
        else:
            self.widget_errors.hide()

        self.input_combobox.addItem("")
        self.input_combobox.lineEdit().setMaxLength(58)
        self.input_combobox.lineEdit().returnPressed.connect(self.input_changed)

        self.line_ending_lineedit.setValidator(HexValidator())
        self.line_ending_combobox.currentIndexChanged.connect(self.line_ending_changed)
        self.line_ending_lineedit.editingFinished.connect(self.line_ending_changed)

        self.baudrate_combobox.currentIndexChanged.connect(self.configuration_changed)
        self.parity_combobox.currentIndexChanged.connect(self.configuration_changed)
        self.stopbits_spinbox.valueChanged.connect(self.configuration_changed)
        self.wordlength_spinbox.valueChanged.connect(self.configuration_changed)
        self.flowcontrol_combobox.currentIndexChanged.connect(self.configuration_changed)
        self.text_type_combobox.currentIndexChanged.connect(self.text_type_changed)

        self.hextext = QHexeditWidget(self.text.font())
        self.hextext.hide()
        self.layout().insertWidget(2, self.hextext)

        self.button_clear_text.clicked.connect(lambda: self.text.setPlainText(""))
        self.button_clear_text.clicked.connect(self.hextext.clear)

        self.save_button.clicked.connect(self.save_clicked)

        self.error_overrun = 0
        self.error_parity = 0
        self.error_framing = 0

        self.last_char = ''

    def cb_error(self, error):
        if error & BrickletRS232.ERROR_OVERRUN:
            self.error_overrun += 1
            self.label_error_overrun.setText(str(self.error_overrun))
        if error & BrickletRS232.ERROR_PARITY:
            self.error_parity += 1
            self.label_error_parity.setText(str(self.error_parity))
        if error & BrickletRS232.ERROR_FRAMING:
            self.error_framing += 1
            self.label_error_framing.setText(str(self.error_framing))

    def cb_read(self, message, length):
        s = ''.join(message[:length])
        self.hextext.appendData(s)

        # check if a \r\n or \n\r was split into two messages. the first one
        # ended with \r or \n and the net one starts with \n or \r
        if len(s) > 0:
            if s[0] != self.last_char and self.last_char in ['\r', '\n'] and s[0] in ['\r', '\n']:
                s = s[1:]

            if len(s) > 0:
                self.last_char = s[-1]
            else:
                self.last_char = ''

        # QTextEdit breaks lines at \r and \n
        s = s.replace('\n\r', '\n').replace('\r\n', '\n')

        ascii_chars = ''
        for c in s:
            if (ord(c) < 32 or ord(c) > 126) and not ord(c) in (10, 13):
                ascii_chars += '.'
            else:
                ascii_chars += c

        self.text.moveCursor(QTextCursor.End)
        self.text.insertPlainText(ascii_chars)
        self.text.moveCursor(QTextCursor.End)

    def line_ending_changed(self):
        selected_line_ending = self.line_ending_combobox.currentText()
        self.line_ending_lineedit.setEnabled((selected_line_ending == 'Hex:'))

    def get_line_ending(self):
        selected_line_ending = self.line_ending_combobox.currentText()

        d = {
            '\\n': '0A',
            '\\r': '0D',
            '\\r\\n':'0D0A',
            '\\n\\r':'0A0D',
            '\\0': '00',
            'Hex:': self.line_ending_lineedit.text()
        }

        hex_le = d.get(selected_line_ending, '')

        try:
            line_ending = bytes.fromhex(hex_le)
        except TypeError:
            # TODO: Handle Error!
            # Should never happen, because LineEdit has a validator applied
            line_ending = bytes()

        return line_ending

    def input_changed(self):
        text = self.input_combobox.currentText().encode('utf-8') + self.get_line_ending()
        length = len(text)
        if length > 60:
            QMessageBox.critical(self, 'RS 232',
                                 'Input length was too long. Maybe you tried to send to many non-ASCII characters?\n'\
                                  + '(Got {} bytes, but only 60 are allowed)'.format(length),
                                 QMessageBox.Ok)
            return
        if length < 60:
            text += bytes([0] * (60 - length))

        written = 0
        while length != 0:
            written = self.rs232.write(text, length)
            text = text[written:]
            text = text + bytes([0]*written)
            length = length - written

        self.input_combobox.setCurrentIndex(0)

    def get_configuration_async(self, conf):
        self.baudrate_combobox.setCurrentIndex(conf.baudrate)
        self.parity_combobox.setCurrentIndex(conf.parity)
        self.stopbits_spinbox.setValue(conf.stopbits)
        self.wordlength_spinbox.setValue(conf.wordlength)

        if not conf.software_flowcontrol and not conf.hardware_flowcontrol:
            self.flowcontrol_combobox.setCurrentIndex(FLOWCONTROL_OFF)
        elif not conf.software_flowcontrol and conf.hardware_flowcontrol:
            self.flowcontrol_combobox.setCurrentIndex(FLOWCONTROL_HW)
        elif conf.software_flowcontrol and not conf.hardware_flowcontrol:
            self.flowcontrol_combobox.setCurrentIndex(FLOWCONTROL_SW)

        self.save_button.setEnabled(False)

    def text_type_changed(self):
        if self.text_type_combobox.currentIndex() == 0:
            self.hextext.hide()
            self.text.show()
        else:
            self.text.hide()
            self.hextext.show()

    def configuration_changed(self):
        self.save_button.setEnabled(True)

    def save_clicked(self):
        baudrate = self.baudrate_combobox.currentIndex()
        parity = self.parity_combobox.currentIndex()
        stopbits = self.stopbits_spinbox.value()
        wordlength = self.wordlength_spinbox.value()
        flowcontrol = self.flowcontrol_combobox.currentIndex()
        software_flowcontrol = 0
        hardware_flowcontrol = 0

        if flowcontrol == FLOWCONTROL_OFF:
            software_flowcontrol = 0
            hardware_flowcontrol = 0
        elif flowcontrol == FLOWCONTROL_SW:
            software_flowcontrol = 1
            hardware_flowcontrol = 0
        elif flowcontrol == FLOWCONTROL_HW:
            software_flowcontrol = 0
            hardware_flowcontrol = 1

        self.rs232.set_configuration(baudrate, parity, stopbits, wordlength, hardware_flowcontrol, software_flowcontrol)
        self.save_button.setEnabled(False)

    def is_read_callback_enabled_async(self, enabled):
        self.read_callback_was_enabled = enabled
        self.rs232.enable_read_callback()

    def start(self):
        self.read_callback_was_enabled = False

        async_call(self.rs232.is_read_callback_enabled, None, self.is_read_callback_enabled_async, self.increase_error_count)
        async_call(self.rs232.get_configuration, None, self.get_configuration_async, self.increase_error_count)

    def stop(self):
        if not self.read_callback_was_enabled:
            try:
                self.rs232.disable_read_callback()
            except ip_connection.Error:
                pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRS232.DEVICE_IDENTIFIER
