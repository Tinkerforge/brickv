# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QMessageBox

from brickv.plugin_system.plugins.red.red_tab import REDTab
from brickv.plugin_system.plugins.red.ui_red_tab_console import Ui_REDTabConsole
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.pyqterm import TerminalWidget
from brickv.samba import get_serial_ports
from brickv.utils import get_main_window

class REDTabConsole(REDTab, Ui_REDTabConsole):
    append_text_signal = pyqtSignal(str)

    def __init__(self):
        REDTab.__init__(self)

        self.setupUi(self)

        self.console = TerminalWidget()
        self.console_layout.insertWidget(1, self.console)

        self.refresh_button.clicked.connect(self.refresh_ports)
        self.connect_button.clicked.connect(self.connect_clicked)
        self.copy_button.clicked.connect(self.console.copy_selection_to_clipboard)

        # make all elements on this tab non-focusable so the focus has
        # to stay on the console widget
        self.combo_serial_port.setFocusPolicy(Qt.NoFocus)
        self.connect_button.setFocusPolicy(Qt.NoFocus)
        self.refresh_button.setFocusPolicy(Qt.NoFocus)
        self.copy_button.setFocusPolicy(Qt.NoFocus)
        self.setFocusPolicy(Qt.NoFocus)

        self.combo_serial_port.currentIndexChanged.connect(self.selected_serial_port_changed)

        self.refresh_ports()

    def selected_serial_port_changed(self, index):
        if index > 0:
            self.connect_button.setEnabled(True)
        else:
            self.connect_button.setEnabled(False)

    def refresh_ports(self):
        current_text = self.combo_serial_port.currentText()
        self.combo_serial_port.clear()
        try:
            ports = get_serial_ports()
        except:
            ports = []

        for port in ports:
            if len(port[1]) > 0 and port[0] != port[1]:
                self.combo_serial_port.addItem('{0} - {1}'.format(port[0], port[1]), port[0])
            else:
                self.combo_serial_port.addItem(port[0], port[0])

        self.combo_serial_port.setEnabled(self.combo_serial_port.count() > 0)

        self.connect_button.setEnabled(False)
        if self.combo_serial_port.count() == 0:
            self.combo_serial_port.addItem('No serial port found')
        else:
            self.combo_serial_port.insertItem(0, 'Select...')
            self.combo_serial_port.insertSeparator(1)
            self.combo_serial_port.setCurrentIndex(0)
            if current_text != '':
                index = self.combo_serial_port.findText(current_text)
                if index >= 0:
                    self.combo_serial_port.setCurrentIndex(index)

    def connect_clicked(self):
        text = self.connect_button.text().replace('&', '')

        if text == 'Connect':
            def open_console():
                self.combo_serial_port.setEnabled(False)
                self.refresh_button.setEnabled(False)
                self.console.setEnabled(True)
                self.connect_button.setText("Disconnect")

                port = self.combo_serial_port.itemData(self.combo_serial_port.currentIndex())

                if self.console._session == None:
                    try:
                        self.console.execute(command=port)
                        self.console.setFocus()
                    except Exception as e:
                        self.destroy_session()
                        if isinstance(e, OSError) and e.errno == 16:
                            QMessageBox.critical(get_main_window(), 'Serial Connect Error',
                                                 'Could not connect to serial console:\n\n{0}\n\nMaybe some other process is currently probing the serial port. Please try again later.'.format(e))
                        else:
                            QMessageBox.critical(get_main_window(), 'Serial Connect Error',
                                                 'Could not connect to serial console:\n\n{0}'.format(e))

            def cb_pkill_ttyGS0(result):
                if result == None or result.exit_code not in [0, 1]: # 0 == no error, 1 == nothing killed
                    # FIXME: report error
                    return

                open_console()

            # FIXME: disable this for now as it doesn't work reliable. init
            #        seems to stop spawning getty for a while after some kills
            # kill everything running on ttyGS0 with force, this ensures that no hanging
            # process blocks ttyGS0 and that we get a clean shell instance
            #self.script_manager.execute_script('pkill_ttyGS0', cb_pkill_ttyGS0, ['SIGKILL'])
            open_console()
        else:
            self.destroy_session()

    def destroy_session(self):
        if self.console._session != None:
            self.console.stop()
            self.console._session = None

            def cb_pkill_ttyGS0(result):
                pass

            # FIXME: disable this for now as it doesn't work reliable. init
            #        seems to stop spawning getty for a while after some kills
            # ask everything running on ttyGS0 to exit
            #self.script_manager.execute_script('pkill_ttyGS0', cb_pkill_ttyGS0, ['SIGTERM'])

        self.combo_serial_port.setEnabled(True)
        self.refresh_button.setEnabled(True)
        self.console.setEnabled(False)
        self.connect_button.setText("Connect")

    def tab_on_focus(self):
        self.console._reset()

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        self.destroy_session()
