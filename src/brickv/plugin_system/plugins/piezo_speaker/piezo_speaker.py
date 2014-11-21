# -*- coding: utf-8 -*-  
"""
Piezo Speaker Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

humidity.py: Piezo Speaker Plugin Implementation

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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_piezo_speaker import BrickletPiezoSpeaker

from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QSpinBox, QApplication, QSizePolicy
from PyQt4.QtCore import pyqtSignal, QTimer

class PiezoSpeaker(PluginBase):
    qtcb_beep_finished = pyqtSignal()
    qtcb_morse_finished = pyqtSignal()
    
    def __init__(self, *args):
        PluginBase.__init__(self, 'Piezo Speaker Bricklet', BrickletPiezoSpeaker, *args)
        
        self.ps = self.device
        
        self.qtcb_beep_finished.connect(self.cb_beep)
        self.ps.register_callback(self.ps.CALLBACK_BEEP_FINISHED,
                                  self.qtcb_beep_finished.emit)
        self.qtcb_morse_finished.connect(self.cb_morse)
        self.ps.register_callback(self.ps.CALLBACK_MORSE_CODE_FINISHED,
                                  self.qtcb_morse_finished.emit)
        
        self.has_stoppable_beep = self.firmware_version >= (2, 0, 2)
        
        self.frequency_label = QLabel('Frequency (585Hz-7100Hz): ')
        self.frequency_box = QSpinBox()
        self.frequency_box.setMinimum(585)
        self.frequency_box.setMaximum(7100)
        self.frequency_box.setValue(1000)
        self.frequency_layout = QHBoxLayout()
        self.frequency_layout.addWidget(self.frequency_label)
        self.frequency_layout.addWidget(self.frequency_box)
        self.frequency_layout.addStretch()
        
        self.beep_box = QSpinBox()
        self.beep_box.setMinimum(0)
        self.beep_box.setMaximum(2147483647)
        self.beep_box.setValue(1000)
        self.beep_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.beep_label = QLabel('Duration (ms): ')
        self.beep_button = QPushButton('Send Beep')
        self.beep_layout = QHBoxLayout()
        self.beep_layout.addWidget(self.beep_label)
        self.beep_layout.addWidget(self.beep_box)
        self.beep_layout.addWidget(self.beep_button)
        
        self.morse_edit = QLineEdit()
        self.morse_edit.setText('- .. -. -.- . .-. ..-. --- .-. --. .')
        self.morse_edit.setMaxLength(60)
        self.morse_label = QLabel('Morse Code: ')
        self.morse_button = QPushButton('Send Morse Code')
        self.morse_layout = QHBoxLayout()
        self.morse_layout.addWidget(self.morse_label)
        self.morse_layout.addWidget(self.morse_edit)
        self.morse_layout.addWidget(self.morse_button)
        
        self.calibrate_button = QPushButton('Calibrate')
        self.scale_button = QPushButton('Play Scale')
        self.scale_layout = QHBoxLayout()
        self.scale_layout.addWidget(self.scale_button)
        self.scale_layout.addWidget(self.calibrate_button)
        self.scale_layout.addStretch()
        
        self.calibrate_layout = QHBoxLayout()
        self.calibrate_layout.addStretch()
        
        self.scale_timer = QTimer()
        self.scale_timer.setInterval(25)
        self.scale_time = 585
        
        self.status_label = QLabel('')
        
        self.beep_button.clicked.connect(self.beep_clicked)
        self.morse_button.clicked.connect(self.morse_clicked)
        self.scale_button.clicked.connect(self.scale_clicked)
        self.scale_timer.timeout.connect(self.scale_timeout)
        self.calibrate_button.clicked.connect(self.calibrate_clicked)
        
        layout = QVBoxLayout(self)
        layout.addLayout(self.frequency_layout)
        layout.addLayout(self.beep_layout)
        layout.addLayout(self.morse_layout)
        layout.addLayout(self.scale_layout)
        layout.addWidget(self.status_label)
#        layout.addLayout(self.calibrate_layout)
        layout.addStretch()

    def start(self):
        pass
        
    def stop(self):
        pass

    def destroy(self):
        pass

    def get_url_part(self):
        return 'piezo_speaker'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletPiezoSpeaker.DEVICE_IDENTIFIER
    
    def cb_beep(self):
        self.beep_button.setDisabled(False)
        self.morse_button.setDisabled(False)
        self.scale_button.setDisabled(False)
        self.status_label.setText('')
        
    def cb_morse(self):
        self.beep_button.setDisabled(False)
        self.morse_button.setDisabled(False)
        self.scale_button.setDisabled(False)
        self.status_label.setText('')
        
    def calibrate_clicked(self):
        self.status_label.setText('Calibrating')
        self.status_label.repaint()
        QApplication.processEvents()
        self.ps.calibrate()
        self.status_label.setText('New calibration stored in EEPROM')
        
    def scale_timeout(self):
        try:
            self.status_label.setText(str(self.scale_time) + 'Hz')
            self.ps.beep(40, self.scale_time)
        except ip_connection.Error:
            return
        
        self.scale_time += 50
        if self.scale_time > 7100:
            self.scale_time = 585
            self.scale_timer.stop()
        
    def scale_clicked(self):
        self.scale_time = 585
        self.scale_timeout()
        self.scale_timer.start()
        self.beep_button.setDisabled(True)
        self.morse_button.setDisabled(True)
        self.scale_button.setDisabled(True)

    def beep_clicked(self):
        freq = self.frequency_box.value()
        duration = self.beep_box.value()

        try:
            self.ps.beep(duration, freq)
        except ip_connection.Error:
            return

        if duration > 0 or not self.has_stoppable_beep:
            self.beep_button.setDisabled(True)
            self.morse_button.setDisabled(True)
            self.scale_button.setDisabled(True)
            self.status_label.setText('Beeping...')

    def morse_clicked(self):
        freq = self.frequency_box.value()
        morse = str(self.morse_edit.text())
        try:
            self.ps.morse_code(morse, freq)
        except ip_connection.Error:
            return
        
        self.beep_button.setDisabled(True)
        self.morse_button.setDisabled(True)
        self.scale_button.setDisabled(True)
        self.status_label.setText('Beeping...')
