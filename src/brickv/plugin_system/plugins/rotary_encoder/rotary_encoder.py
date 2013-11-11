# -*- coding: utf-8 -*-  
"""
Rotary Encoder Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>

rotary_encoder.py: Rotary Encoder Plugin Implementation

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
from brickv.bindings.bricklet_rotary_encoder import BrickletRotaryEncoder
from brickv.async_call import async_call

from PyQt4.QtGui import QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QPainter, QBrush
from PyQt4.QtCore import pyqtSignal, Qt
    
class CountLabel(QLabel):
    def setText(self, text):
        text = "Count: " + text
        super(CountLabel, self).setText(text)
    
class EncoderFrame(QFrame):
    def __init__(self, parent = None):
        QFrame.__init__(self, parent)
        self.count = 0
        self.pressed = False
        
    def set_pressed(self, pressed):
        self.pressed = pressed
        self.repaint()
        
    def set_count(self, count):
        self.count = count
        self.repaint()
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.translate(self.width()/2, self.height()/2);
        for i in range(24):
            qp.drawLine(88, 0, 96, 0);
            qp.rotate(15.0);
            
        qp.rotate(((self.count % 24)*15+270)%360)
        qp.drawLine(50, 0, 80, 0)
        
        if self.pressed:
            qp.setBrush(QBrush(Qt.red))
            
        qp.drawEllipse(-50, -50, 100, 100)
        
        qp.end()
    
class RotaryEncoder(PluginBase):
    qtcb_count = pyqtSignal(int)
    qtcb_pressed = pyqtSignal()
    qtcb_released = pyqtSignal()
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Rotary Encoder Bricklet', version)

        self.re = BrickletRotaryEncoder(uid, ipcon)
        
        self.qtcb_count.connect(self.cb_count)
        self.re.register_callback(self.re.CALLBACK_COUNT,
                                  self.qtcb_count.emit)

        self.qtcb_pressed.connect(self.cb_pressed)
        self.re.register_callback(self.re.CALLBACK_PRESSED,
                                  self.qtcb_pressed.emit)
        
        self.qtcb_released.connect(self.cb_released)
        self.re.register_callback(self.re.CALLBACK_RELEASED,
                                  self.qtcb_released.emit)
        
        self.count_label = CountLabel('Count: 0')
        self.reset_button = QPushButton('Reset Count')
        self.reset_button.pressed.connect(self.reset_pressed)
        
        self.encoder_frame = EncoderFrame(self)
        self.encoder_frame.setMinimumSize(220, 220)
        self.encoder_frame.setMaximumSize(220, 220)
        self.encoder_frame.set_count(0)
        
        layout_h1 = QHBoxLayout()
        layout_h1.addStretch()
        layout_h1.addWidget(self.count_label)
        layout_h1.addStretch()
        
        layout_h2 = QHBoxLayout()
        layout_h2.addStretch()
        layout_h2.addWidget(self.encoder_frame)
        layout_h2.addStretch()
        
        layout_h3 = QHBoxLayout()
        layout_h3.addStretch()
        layout_h3.addWidget(self.reset_button)
        layout_h3.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h1)
        layout.addLayout(layout_h2)
        layout.addLayout(layout_h3)
        layout.addStretch()
        
    def cb_released(self):
        self.encoder_frame.set_pressed(False)

    def cb_pressed(self):
        self.encoder_frame.set_pressed(True)
        
    def cb_count(self, count):
        self.count_label.setText(str(count))
        self.encoder_frame.set_count(count)
        
    def reset_pressed(self):
        async_call(self.re.get_count, True, None, self.increase_error_count)
        self.cb_count(0)

    def start(self):
        async_call(self.re.set_count_callback_period, 100, None, self.increase_error_count)
        async_call(self.re.get_count, False, self.cb_count, self.increase_error_count)
        
    def stop(self):
        async_call(self.re.set_count_callback_period, 0, None, self.increase_error_count)

    def get_url_part(self):
        return 'rotary_encoder'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRotaryEncoder.DEVICE_IDENTIFIER