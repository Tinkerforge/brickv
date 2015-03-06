# -*- coding: utf-8 -*-  
"""
Heart Rate Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

heart_rate.py: Heart Rate Plugin Implementation

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
from brickv.bindings.bricklet_heart_rate import BrickletHeartRate
from brickv.async_call import async_call
from brickv.bmp_to_pixmap import bmp_to_pixmap

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout
from PyQt4.QtCore import pyqtSignal, Qt

class HeartRateLabel(QLabel):
    def setText(self, text):
        text = "Heart Rate: " + text + " BPM"
        super(HeartRateLabel, self).setText(text)
    
class HeartRate(PluginBase):
    qtcb_heart_rate = pyqtSignal(int)
    qtcb_beat_state_changed = pyqtSignal(int)
    
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletHeartRate, *args)
        
        self.hr = self.device
        
        self.qtcb_heart_rate.connect(self.cb_heart_rate)
        self.hr.register_callback(self.hr.CALLBACK_HEART_RATE,
                                  self.qtcb_heart_rate.emit) 
        self.qtcb_beat_state_changed.connect(self.cb_beat_state_changed)
        self.hr.register_callback(self.hr.CALLBACK_BEAT_STATE_CHANGED,
                                  self.qtcb_beat_state_changed.emit) 
        
        self.heart_rate_label = HeartRateLabel()
        self.heart_white_bitmap = bmp_to_pixmap('plugin_system/plugins/heart_rate/heart_white_small.bmp')
        self.heart_red_bitmap = bmp_to_pixmap('plugin_system/plugins/heart_rate/heart_red_small.bmp')
        self.heart_icon = QLabel()
        self.heart_icon.setPixmap(self.heart_white_bitmap)
        
        self.current_value = None
        
        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Heart Rate [BPM]', plot_list)
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.heart_rate_label)
        layout_h.addWidget(self.heart_icon)
        layout_h.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addWidget(self.plot_widget)

    def start(self):
        async_call(self.hr.get_heart_rate, None, self.cb_heart_rate, self.increase_error_count)
        async_call(self.hr.set_heart_rate_callback_period, 100, None, self.increase_error_count)
        async_call(self.hr.enable_beat_state_changed_callback, None, None, self.increase_error_count)
        
        self.plot_widget.stop = False
        
    def stop(self):
        async_call(self.hr.set_heart_rate_callback_period, 0, None, self.increase_error_count)
        async_call(self.hr.disable_beat_state_changed_callback, None, None, self.increase_error_count)
        
        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'heart_rate'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletHeartRate.DEVICE_IDENTIFIER

    def get_current_value(self):
        return self.current_value

    def cb_heart_rate(self, heart_rate):
        self.current_value = heart_rate
        self.heart_rate_label.setText(str(heart_rate))
        
    def cb_beat_state_changed(self, state):
        if state == self.hr.BEAT_STATE_RISING:
            self.heart_icon.setPixmap(self.heart_red_bitmap)
        else:
            self.heart_icon.setPixmap(self.heart_white_bitmap)
