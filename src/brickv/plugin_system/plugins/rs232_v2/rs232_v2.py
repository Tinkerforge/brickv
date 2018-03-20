# -*- coding: utf-8 -*-
"""
RS232 V2 Plugin
Copyright (C) 2018 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

rs232_v2.py: RS232 V2 Plugin Implementation

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

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_rs232_v2 import BrickletRS232V2
from brickv.plugin_system.plugins.rs232_v2.ui_rs232_v2 import Ui_RS232_V2
from brickv.async_call import async_call
from brickv.hex_validator import HexValidator

from brickv.plugin_system.plugins.rs232.qhexedit import QHexeditWidget

CBOX_IDX_FC_HW = 2
BAUDRATE_MAX_RS232  = 250000

class RS232V2(COMCUPluginBase, Ui_RS232_V2):
    qtcb_read = pyqtSignal(object)
    qtcb_error_count = pyqtSignal(int, int)

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletRS232V2, *args)

        self.setupUi(self)

        self.text.setReadOnly(True)

        self.rs232 = self.device

        self.read_callback_was_enabled = False

        self.qtcb_read.connect(self.cb_read)
        self.rs232.register_callback(self.rs232.CALLBACK_READ,
                                     self.qtcb_read.emit)


        self.qtcb_error_count.connect(self.cb_error_count)
        self.rs232.register_callback(self.rs232.CALLBACK_ERROR_COUNT,
                                     self.qtcb_error_count.emit)

        self.input_combobox.addItem("")
        self.input_combobox.lineEdit().setMaxLength(65533)
        self.input_combobox.lineEdit().returnPressed.connect(self.input_changed)

        self.line_ending_lineedit.setValidator(HexValidator())
        self.line_ending_combobox.currentIndexChanged.connect(self.line_ending_changed)
        self.line_ending_lineedit.editingFinished.connect(self.line_ending_changed)

        self.baudrate_spinbox.valueChanged.connect(self.configuration_changed)
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

        self.error_stream_oos = 0

        self.last_char = ''

        if self.baudrate_spinbox.value() > BAUDRATE_MAX_RS232:
            self.label_note_baud.show()
        else:
            self.label_note_baud.hide()

        if self.flowcontrol_combobox.currentIndex() == CBOX_IDX_FC_HW:
            self.label_note_fc_hw.show()
        else:
            self.label_note_fc_hw.hide()

    def cb_error_count(self, error_count_overrun, error_count_parity):
        self.label_error_overrun.setText(str(error_count_overrun))
        self.label_error_parity.setText(str(error_count_parity))

    def cb_read(self, message):
        if message == None:
            # Increase stream error counter
            self.error_stream_oos = self.error_stream_oos + 1
            self.label_error_streaming.setText(str(self.error_stream_oos))

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

    def append_text(self, text):
        self.text.moveCursor(QTextCursor.End)
        self.text.insertPlainText(text)
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
        pos = 0
        written = 0
        text = self.input_combobox.currentText().encode('utf-8') + self.get_line_ending()
        c = ['\0']*len(text)
        for i, t in enumerate(text):
            c[i] = t

        while pos < len(c):
            written = self.rs232.write(c[pos:])
            pos = pos + written

        self.input_combobox.setCurrentIndex(0)

    def get_configuration_async(self, conf):
        self.stopbits_spinbox.setValue(conf.stopbits)
        self.baudrate_spinbox.setValue(conf.baudrate)
        self.wordlength_spinbox.setValue(conf.wordlength)
        self.parity_combobox.setCurrentIndex(conf.parity)
        self.flowcontrol_combobox.setCurrentIndex(conf.flowcontrol)
        self.save_button.setEnabled(False)

    def text_type_changed(self):
        if self.text_type_combobox.currentIndex() == 0:
            self.hextext.hide()
            self.text.show()
        else:
            self.text.hide()
            self.hextext.show()

    def configuration_changed(self):
        if self.baudrate_spinbox.value() > BAUDRATE_MAX_RS232:
            self.label_note_baud.show()
        else:
            self.label_note_baud.hide()

        self.save_button.setEnabled(True)

        if self.flowcontrol_combobox.currentIndex() == CBOX_IDX_FC_HW:
            self.label_note_fc_hw.show()
        else:
            self.label_note_fc_hw.hide()

    def save_clicked(self):
        baudrate = self.baudrate_spinbox.value()
        stopbits = self.stopbits_spinbox.value()
        wordlength = self.wordlength_spinbox.value()
        parity = self.parity_combobox.currentIndex()
        flowcontrol = self.flowcontrol_combobox.currentIndex()

        self.rs232.set_configuration(baudrate, parity, stopbits, wordlength, flowcontrol)
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
            except:
                pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRS232V2.DEVICE_IDENTIFIER
