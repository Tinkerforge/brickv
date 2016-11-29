# -*- coding: utf-8 -*-
"""
RS485 Plugin
Copyright (C) 2016 Olaf Lüke <olaf@tinkerforge.com>

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

from PyQt4.QtGui import QTextCursor
from PyQt4.QtCore import pyqtSignal

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_rs485 import BrickletRS485
from brickv.plugin_system.plugins.rs485.ui_rs485 import Ui_RS485
from brickv.async_call import async_call
from brickv.hex_validator import HexValidator
from brickv.callback_emulator import CallbackEmulator

from brickv.plugin_system.plugins.rs485.qhexedit import QHexeditWidget

class RS485(PluginBase, Ui_RS485):
    qtcb_read = pyqtSignal(object, int)
    qtcb_error = pyqtSignal(int)

    def __init__(self, *args):
        PluginBase.__init__(self, BrickletRS485, *args)

        self.setupUi(self)
        
        self.text.setReadOnly(True)

        self.rs485 = self.device
        
        self.cbe_error_count = CallbackEmulator(self.rs485.get_error_count,
                                                self.cb_error_count,
                                                self.increase_error_count)

        self.read_callback_was_enabled = False

        self.qtcb_read.connect(self.cb_read)
        self.rs485.register_callback(self.rs485.CALLBACK_READ_CALLBACK,
                                     self.qtcb_read.emit)

        self.input_combobox.addItem("")
        self.input_combobox.lineEdit().setMaxLength(58)
        self.input_combobox.lineEdit().returnPressed.connect(self.input_changed)

        self.line_ending_lineedit.setValidator(HexValidator())
        self.line_ending_combobox.currentIndexChanged.connect(self.line_ending_changed)
        self.line_ending_lineedit.editingFinished.connect(self.line_ending_changed)

        self.baudrate_spinbox.valueChanged.connect(self.configuration_changed)
        self.parity_combobox.currentIndexChanged.connect(self.configuration_changed)
        self.stopbits_spinbox.valueChanged.connect(self.configuration_changed)
        self.wordlength_spinbox.valueChanged.connect(self.configuration_changed)
        self.duplex_combobox.currentIndexChanged.connect(self.configuration_changed)
        self.text_type_combobox.currentIndexChanged.connect(self.text_type_changed)

        self.hextext = QHexeditWidget(self.text.font())
        self.hextext.hide()
        self.layout().insertWidget(2, self.hextext)

        self.button_clear_text.clicked.connect(lambda: self.text.setPlainText(""))
        self.button_clear_text.clicked.connect(self.hextext.clear)

        self.save_button.clicked.connect(self.save_clicked)
        
        self.error_overrun = 0
        self.error_parity = 0

        self.last_char = ''

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

        ascii = ''
        for c in s:
            if (ord(c) < 32 or ord(c) > 126) and not (ord(c) in (10, 13)):
                ascii += '.'
            else:
                ascii += c

        self.text.moveCursor(QTextCursor.End)
        self.text.insertPlainText(ascii)
        self.text.moveCursor(QTextCursor.End)

    def line_ending_changed(self):
        selected_line_ending = self.line_ending_combobox.currentText()
        self.line_ending_lineedit.setEnabled( (selected_line_ending == 'Hex:' ))

    def get_line_ending(self):
        selected_line_ending = self.line_ending_combobox.currentText()

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
            hex_le = self.line_ending_lineedit.text()
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
        text = self.input_combobox.currentText().encode('utf-8') + self.get_line_ending()
        c = ['\0']*60
        for i, t in enumerate(text):
            c[i] = t

        length = len(text)
        written = 0
        while length != 0:
            written = self.rs485.write(c, length)
            c = c[written:]
            c = c + ['\0']*written
            length = length - written

        self.input_combobox.setCurrentIndex(0)

    def get_configuration_async(self, conf):
        self.baudrate_spinbox.setValue(conf.baudrate)
        self.parity_combobox.setCurrentIndex(conf.parity)
        self.stopbits_spinbox.setValue(conf.stopbits)
        self.wordlength_spinbox.setValue(conf.wordlength)
        self.duplex_combobox.setCurrentIndex(conf.duplex)
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
        baudrate = self.baudrate_spinbox.value()
        parity = self.parity_combobox.currentIndex()
        stopbits = self.stopbits_spinbox.value()
        wordlength = self.wordlength_spinbox.value()
        duplex = self.duplex_combobox.currentIndex()

        self.rs485.set_configuration(baudrate, parity, stopbits, wordlength, duplex)
        self.save_button.setEnabled(False)

    def is_read_callback_enabled_async(self, enabled):
        self.read_callback_was_enabled = enabled
        self.rs485.enable_read_callback()
        
    def cb_error_count(self, error):
        self.label_error_overrun.setText(str(error.overrun_error_count))
        self.label_error_parity.setText(str(error.parity_error_count))

    def start(self):
        self.read_callback_was_enabled = False

        async_call(self.rs485.is_read_callback_enabled, None, self.is_read_callback_enabled_async, self.increase_error_count)
        async_call(self.rs485.get_configuration, None, self.get_configuration_async, self.increase_error_count)
        self.cbe_error_count.set_period(250)

    def stop(self):
        self.cbe_error_count.set_period(0)
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
