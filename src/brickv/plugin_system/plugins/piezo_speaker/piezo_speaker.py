# -*- coding: utf-8 -*-  
"""
Piezo Speaker Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>

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

from plugin_system.plugin_base import PluginBase
from bindings import ip_connection
from bindings.bricklet_piezo_speaker import BrickletPiezoSpeaker

from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QSpinBox
from PyQt4.QtCore import pyqtSignal, QTimer

class PiezoSpeaker(PluginBase):
    qtcb_beep_finished = pyqtSignal()
    qtcb_morse_finished = pyqtSignal()
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Piezo Speaker Bricklet', version)
        
        self.ps = BrickletPiezoSpeaker(uid, ipcon)
        
        self.qtcb_beep_finished.connect(self.cb_beep)
        self.ps.register_callback(self.ps.CALLBACK_BEEP_FINISHED,
                                  self.qtcb_beep_finished.emit)
        self.qtcb_morse_finished.connect(self.cb_morse)
        self.ps.register_callback(self.ps.CALLBACK_MORSE_CODE_FINISHED,
                                  self.qtcb_morse_finished.emit)
        
        self.frequency_label = QLabel('Frequency (460-7000Hz): ')
        self.frequency_box = QSpinBox()
        self.frequency_box.setMinimum(450)
        self.frequency_box.setMaximum(7000)
        self.frequency_box.setValue(1000)
        self.frequency_layout = QHBoxLayout()
        self.frequency_layout.addWidget(self.frequency_label)
        self.frequency_layout.addWidget(self.frequency_box)
        self.frequency_layout.addStretch()
        
        self.beep_edit = QLineEdit()
        self.beep_edit.setText(str(1000))
        self.beep_label = QLabel('Duration (ms): ')
        self.beep_button = QPushButton('Send Beep')
        self.beep_layout = QHBoxLayout()
        self.beep_layout.addWidget(self.beep_label)
        self.beep_layout.addWidget(self.beep_edit)
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
        
        self.scale_button = QPushButton('Play Scale')
        self.scale_layout = QHBoxLayout()
        self.scale_layout.addWidget(self.scale_button)
        self.scale_layout.addStretch()
        
        self.scale_timer = QTimer()
        self.scale_timer.setInterval(25)
        self.scale_time = 460
        
        self.status_label = QLabel('')
        
        self.beep_button.pressed.connect(self.beep_pressed)
        self.morse_button.pressed.connect(self.morse_pressed)
        self.scale_button.pressed.connect(self.scale_pressed)
        self.scale_timer.timeout.connect(self.scale_timeout)
        
        layout = QVBoxLayout(self)
        layout.addLayout(self.frequency_layout)
        layout.addLayout(self.beep_layout)
        layout.addLayout(self.morse_layout)
        layout.addLayout(self.scale_layout)
        layout.addWidget(self.status_label)
        layout.addStretch()

    def start(self):
        pass
        
    def stop(self):
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
        
    def scale_timeout(self):
        try:
            self.status_label.setText(str(self.scale_time) + 'Hz')
            self.ps.beep(40, self.scale_time)
        except ip_connection.Error:
            return
        self.scale_time += 25
        if self.scale_time > 7000:
            self.scale_time = 460
            self.scale_timer.stop()
        
    def scale_pressed(self):
        self.scale_time = 460
        self.scale_timeout()
        self.scale_timer.start()
        self.beep_button.setDisabled(True)
        self.morse_button.setDisabled(True)
        self.scale_button.setDisabled(True)

    
    def beep_pressed(self):
        freq = self.frequency_box.value()
        duration = int(self.beep_edit.text())
        try:
            self.ps.beep(duration, freq)
        except ip_connection.Error:
            return
        
        self.beep_button.setDisabled(True)
        self.morse_button.setDisabled(True)
        self.scale_button.setDisabled(True)
        self.status_label.setText('Beeping...')        
        
    def morse_pressed(self):
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
