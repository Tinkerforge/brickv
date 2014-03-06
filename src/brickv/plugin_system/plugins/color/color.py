# -*- coding: utf-8 -*-
"""
Color Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

color.py: Color Plugin Implementation

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
from brickv.plot_widget import PlotWidget
from brickv.bindings.bricklet_color import BrickletColor
from brickv.async_call import async_call

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QPainter, QFrame, QBrush, QColor, QCheckBox
from PyQt4.QtCore import pyqtSignal, Qt

class ColorFrame(QFrame):
    def __init__(self, parent = None):
        QFrame.__init__(self, parent)
        self.color = QColor(128, 128, 128)
        self.setMinimumSize(25, 25)
        self.setMaximumSize(25, 25)
        
    def set_color(self, r, g, b):
        self.color = QColor(r, g, b)
        self.repaint()
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QBrush(self.color))
        qp.setPen(self.color)
        qp.drawRect(0, 0, 25, 25)
        qp.setBrush(Qt.NoBrush)
        qp.setPen(Qt.black)
        qp.drawRect(1, 1, 24, 24)
        qp.end()

class ColorLabel(QLabel):
    def setText(self, r, g, b, c):
        text = 'Color Value -> r: ' + str(r) + ', g: ' + str(g) + ', b: ' + str(b) + ', c: ' + str(c)
        super(ColorLabel, self).setText(text)

class Color(PluginBase):
    qtcb_color = pyqtSignal(int, int, int, int)

    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Color Bricklet', version)

        self.color = BrickletColor(uid, ipcon)

        self.qtcb_color.connect(self.cb_color)
        self.color.register_callback(self.color.CALLBACK_COLOR,
                                     self.qtcb_color.emit)

        self.color_label = ColorLabel()
        self.color_frame = ColorFrame()

        self.current_color = (0, 0, 0, 0)

        plot_list = [['', Qt.red, self.get_current_r],
                     ['', Qt.green, self.get_current_g],
                     ['', Qt.blue, self.get_current_b],
                     ['', Qt.white, self.get_current_c]]
        self.plot_widget = PlotWidget('Color Value', plot_list)
        
        self.gain_label = QLabel('Gain: ')
        self.gain_combo = QComboBox()
        self.gain_combo.addItem("1x")
        self.gain_combo.addItem("4x")
        self.gain_combo.addItem("16x")
        self.gain_combo.addItem("60x")
        
        self.gain_combo.activated.connect(self.gain_changed)
        
        self.conversion_label = QLabel('Integration Time: ')
        self.conversion_combo = QComboBox()
        self.conversion_combo.addItem("2.4ms")
        self.conversion_combo.addItem("24ms")
        self.conversion_combo.addItem("101ms")
        self.conversion_combo.addItem("154ms")
        self.conversion_combo.addItem("700ms")
        
        self.conversion_combo.activated.connect(self.conversion_changed)
        
        self.light_label = QLabel("Enable Light")
        self.light_checkbox = QCheckBox()
        
        self.light_checkbox.stateChanged.connect(self.light_state_changed)
        
        layout_config = QHBoxLayout()
        layout_config.addWidget(self.gain_label)
        layout_config.addWidget(self.gain_combo)
        layout_config.addWidget(self.conversion_label)
        layout_config.addWidget(self.conversion_combo)
        layout_config.addWidget(self.light_label)
        layout_config.addWidget(self.light_checkbox)
        layout_config.addStretch()
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.color_label)
        layout_h.addWidget(self.color_frame)
        layout_h.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addWidget(self.plot_widget)
        layout.addLayout(layout_config)
    

    def start(self):
        async_call(self.color.get_color, None, self.cb_color_get, self.increase_error_count)
        async_call(self.color.set_color_callback_period, 50, None, self.increase_error_count)
        async_call(self.color.get_config, None, self.cb_config, self.increase_error_count)
        async_call(self.color.is_light_on, None, self.cb_light_on, self.increase_error_count)
        
        self.plot_widget.stop = False

    def stop(self):
        async_call(self.color.set_color_callback_period, 0, None, self.increase_error_count)
        
        self.plot_widget.stop = True

    def get_url_part(self):
        return 'color'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletColor.DEVICE_IDENTIFIER
    
    def cb_light_on(self, light):
        if light == BrickletColor.LIGHT_ON:
            self.light_checkbox.setCheckState(2)
        else:
            self.light_checkbox.setCheckState(0)
            
    
    def light_state_changed(self, state):
        if state == 2:
            self.color.light_on()
        else:
            self.color.light_off()
    
    def cb_config(self, config):
        print config
        gain, conv = self.gain_conv_to_combo(config.gain, config.integration_time)
        self.gain_combo.setCurrentIndex(gain)
        self.conversion_combo.setCurrentIndex(conv)
    
    def gain_conv_to_combo(self, gain, conv):
        if gain == BrickletColor.GAIN_1X:
            gain = 0
        elif gain == BrickletColor.GAIN_4X:
            gain = 1
        elif gain == BrickletColor.GAIN_16X:
            gain = 2
        elif gain == BrickletColor.GAIN_60X:
            gain = 3
            
        if conv == BrickletColor.INTEGRATION_TIME_2MS:
            conv = 0
        elif conv == BrickletColor.INTEGRATION_TIME_24MS:
            conv = 1
        elif conv == BrickletColor.INTEGRATION_TIME_101MS:
            conv = 2
        elif conv == BrickletColor.INTEGRATION_TIME_154MS:
            conv = 3
        elif conv == BrickletColor.INTEGRATION_TIME_700MS:
            conv = 4
            
        return gain, conv
            
 
    def combo_to_gain_conv(self, gain, conv):
        if gain == 0:
            gain = BrickletColor.GAIN_1X
        elif gain == 1:
            gain = BrickletColor.GAIN_4X
        elif gain == 2:
            gain = BrickletColor.GAIN_16X
        elif gain == 3:
            gain = BrickletColor.GAIN_60X
            
        if conv == 0:
            conv = BrickletColor.INTEGRATION_TIME_2MS
        elif conv == 1:
            conv = BrickletColor.INTEGRATION_TIME_24MS
        elif conv == 2:
            conv = BrickletColor.INTEGRATION_TIME_101MS
        elif conv == 3:
            conv = BrickletColor.INTEGRATION_TIME_154MS
        elif conv == 4:
            conv = BrickletColor.INTEGRATION_TIME_700MS
            
        return gain, conv
    
    def gain_changed(self, gain):
        conversion = self.conversion_combo.currentIndex()
        
        g, c = self.combo_to_gain_conv(gain, conversion)
        self.color.set_config(g, c)
        
    def conversion_changed(self, conversion):
        gain = self.gain_combo.currentIndex()
        
        g, c = self.combo_to_gain_conv(gain, conversion)
        self.color.set_config(g, c)
        
    def cb_color_get(self, color):
        self.cb_color(color.r, color.g, color.b, color.c)

    def cb_color(self, r, g, b, c):
        self.current_color = (r, g, b, c)
        self.color_label.setText(r, g, b, c)
        
#        normalize = r+g+b
        normalize = 0xFFFF
        self.color_frame.set_color(r*255.0/normalize, g*255.0/normalize, b*255.0/normalize)
    
    def get_current_r(self):
        return self.current_color[0]
    
    def get_current_g(self):
        return self.current_color[1]
    
    def get_current_b(self):
        return self.current_color[2]
    
    def get_current_c(self):
        return self.current_color[3]