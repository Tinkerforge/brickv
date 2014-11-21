# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

red_tab_console.py: RED console tab implementation

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
from brickv.plugin_system.plugins.red.ui_red_tab_console import Ui_REDTabConsole
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.pyqterm import TerminalWidget
from brickv.samba import get_serial_ports

class REDTabConsole(QtGui.QWidget, Ui_REDTabConsole):
    append_text_signal = QtCore.pyqtSignal(str)
    
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session        = None # set from RED after construction
        self.script_manager = None # set from RED after construction

        self.console = TerminalWidget()
        self.console_layout.insertWidget(1, self.console)
        
        self.refresh_button.clicked.connect(self.refresh_ports)
        self.connect_button.clicked.connect(self.connect_clicked)
        self.copy_button.clicked.connect(self.console.copy_selection_to_clipboard)
        
        # make all elements on this tab non-focusable so the focus has
        # to stay on the console widget
        self.combo_serial_port.setFocusPolicy(QtCore.Qt.NoFocus)
        self.connect_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.refresh_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.copy_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        
        self.refresh_ports()

    def refresh_ports(self):
        current_text = self.combo_serial_port.currentText()
        self.combo_serial_port.clear()
        try:
            ports = get_serial_ports()
        except:
            ports = []

        preferred_index = None
        
        for port in ports:
            if preferred_index is None:
                if 'ttyACM' in port[0] or \
                   'ttyUSB' in port[0] or \
                   'RED Brick' in port[0] or \
                   'usbmodem' in port[0]:
                    preferred_index = self.combo_serial_port.count()

            if len(port[1]) > 0 and port[0] != port[1]:
                self.combo_serial_port.addItem(u'{0} - {1}'.format(port[0], port[1]), port[0])
            else:
                self.combo_serial_port.addItem(port[0], port[0])

        self.combo_serial_port.setEnabled(self.combo_serial_port.count() > 0)

        if self.combo_serial_port.count() == 0:
            self.combo_serial_port.addItem('No serial port found')
        elif preferred_index is not None:
            self.combo_serial_port.setCurrentIndex(preferred_index)
        else:
            index = self.combo_serial_port.findText(current_text)
            if index >= 0:
                self.combo_serial_port.setCurrentIndex(index)

    def connect_clicked(self):
        text = self.connect_button.text()
        if text == 'Connect':
            self.console.setDisabled(False)
            self.connect_button.setText("Disconnect")
            
            port = unicode(self.combo_serial_port.itemData(self.combo_serial_port.currentIndex()).toString())
            if self.console._session == None:
                try:
                    self.console.execute(command=port)
                    self.console.setFocus()
                except:
                    # TODO: Error popup?
                    self.console.setDisabled(True)
                    self.connect_button.setText("Connect")
                    self.destroy_session()
        else:
            self.console.setDisabled(True)
            self.connect_button.setText("Connect")
            self.destroy_session()

    def destroy_session(self):
        if self.console._session is not None:
            self.console.stop()
            self.console._session = None

    def tab_on_focus(self):
        self.console._reset()

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        self.destroy_session()
