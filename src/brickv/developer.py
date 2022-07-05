# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2021 Matthias Bolte <matthias@tinkerforge.com>

developer.py: GUI for developer features

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
import gc
import serial
import threading
import time
from datetime import datetime

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QMessageBox

from brickv.ui_developer import Ui_Developer
from brickv.utils import get_modeless_dialog_flags, get_home_path, get_save_file_name
from brickv.samba import get_serial_ports

class DeveloperWindow(QDialog, Ui_Developer):
    gc_stats_changed = pyqtSignal(int, int)
    new_serial_text = pyqtSignal(str)

    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())

        self.setupUi(self)

        self.ipcon_available = False

        # GC
        self.gc_runs = 0
        self.gc_collected = 0
        self.gc_uncollectable = 0

        self.gc_stats_changed.connect(self.update_gc_stats)

        self.button_force_gc.clicked.connect(self.force_gc)

        # ESP32 (Ethernet) Brick
        gc.callbacks.append(self.gc_callback)

        self.serial_text = ''
        self.serial_running_ref = None
        self.serial_thread = None

        self.button_serial_port_refresh.clicked.connect(self.refresh_serial_ports)
        self.button_serial_port_open.clicked.connect(self.open_serial_port)
        self.button_serial_text_clear.clicked.connect(self.clear_serial_text)
        self.button_serial_text_save.clicked.connect(self.save_serial_text)
        self.new_serial_text.connect(self.append_serial_text)

        self.button_close.clicked.connect(self.hide)

        self.combo_serial_port.addItem('Click refresh button to update')
        self.combo_serial_port.setEnabled(False)
        self.button_serial_port_open.setEnabled(False)

    def reject(self):
        pass # avoid closing using ESC key

    def closeEvent(self, event):
        pass # dont touch event to avoid closing using ESC key

    def force_gc(self):
        gc.collect()

    def gc_callback(self, phase, info):
        try:
            if phase == 'stop':
                self.gc_stats_changed.emit(info['collected'], info['uncollectable'])
        except RuntimeError as e:
            if str(e) != 'wrapped C/C++ object of type DeveloperWindow has been deleted':
                raise

    def update_gc_stats(self, collected, uncollectable):
        self.gc_runs += 1
        objects = len(gc.get_objects())
        self.gc_collected += collected
        self.gc_uncollectable += uncollectable

        self.label_gc_runs.setText(str(self.gc_runs))
        self.label_gc_objects.setText(str(objects))
        self.label_gc_collected.setText(str(self.gc_collected))
        self.label_gc_uncollectable.setText(str(self.gc_uncollectable))

    def refresh_serial_ports(self):
        self.combo_serial_port.clear()
        self.combo_serial_port.setEnabled(False)
        self.button_serial_port_open.setEnabled(False)

        for info in get_serial_ports(vid=0x10c4, pid=0xea60, opaque='esp32'): # CP2102N USB to UART chip used on ESP32 (Ethernet) Bricks
            self.combo_serial_port.addItem(info.description, info)

        if self.combo_serial_port.count() == 0:
            self.combo_serial_port.addItem('No ESP32 (Ethernet) Brick found')
        else:
            self.combo_serial_port.setEnabled(True)
            self.button_serial_port_open.setEnabled(True)

    def open_serial_port(self):
        i = self.combo_serial_port.currentIndex()

        if i < 0:
            return

        info = self.combo_serial_port.itemData(i)

        if info == None:
            return

        if self.serial_running_ref == None:
            self.combo_serial_port.setEnabled(False)
            self.button_serial_port_refresh.setEnabled(False)
            self.button_serial_port_open.setText('Close')

            self.serial_running_ref = [True]
            self.serial_thread = threading.Thread(target=self.serial_port_loop, args=(info.path, self.serial_running_ref), daemon=True)
            self.serial_thread.start()
        else:
            self.serial_running_ref[0] = False
            self.serial_running_ref = None

            self.combo_serial_port.setEnabled(True)
            self.button_serial_port_refresh.setEnabled(True)
            self.button_serial_port_open.setText('Open')

    def serial_port_loop(self, path, running_ref):
        serial_port = None
        pending_data = b''

        while running_ref[0]:
            self.new_serial_text.emit('===== Opening {0} ...\n'.format(path))

            while running_ref[0]:
                try:
                    serial_port = serial.Serial(path, 115200, timeout=1)
                except:
                    time.sleep(0.1)
                    continue

                break

            if serial_port != None:
                self.new_serial_text.emit('===== {0} is open\n'.format(path))

                while running_ref[0]:
                    try:
                        data = serial_port.read(1000)
                    except Exception as e:
                        self.new_serial_text.emit('===== Error for {0}: {1}\n'.format(path, e))

                        break

                    pending_data += data

                    while len(pending_data) > 0:
                        i = pending_data.find(b'\n')

                        if i < 0:
                            break

                        line = pending_data[:i + 1]
                        pending_data = pending_data[i + 1:]
                        line = line.decode('utf-8', errors='replace')

                        self.new_serial_text.emit(line)

                self.new_serial_text.emit('===== Closing {0}\n'.format(path))
                serial_port.close()

    def append_serial_text(self, text):
        self.serial_text += text
        self.edit_serial_text.setPlainText(self.serial_text)

        scrollbar = self.edit_serial_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_serial_text(self):
        self.serial_text = ''
        self.edit_serial_text.clear()

    def save_serial_text(self):
        date = datetime.now().replace(microsecond=0).isoformat().replace('T', '_').replace(':', '-')
        filename = get_save_file_name(self, 'Save...', os.path.join(get_home_path(), 'esp32_serial_{0}.log'.format(date)))

        if len(filename) == 0:
            return

        try:
            with open(filename, 'w') as f:
                f.write(self.serial_text)
        except Exception as e:
            QMessageBox.critical(self, 'Save...',
                                 'Could not save to file:\n\n' + str(e),
                                 QMessageBox.Ok)

    def update_ui_state(self):
        pass

    def set_ipcon_available(self, ipcon_available):
        self.ipcon_available = ipcon_available

        self.update_ui_state()
