# -*- coding: utf-8 -*-  
"""
Motion Detector Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>

motion_detector.py: Motion Detector Plugin Implementation

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
from bindings.bricklet_motion_detector import BrickletMotionDetector
from async_call import async_call

from PyQt4.QtGui import QLabel, QVBoxLayout, QHBoxLayout
from PyQt4.QtCore import pyqtSignal
    
class MotionDetector(PluginBase):
    qtcb_motion_detected = pyqtSignal()
    qtcb_detection_cylce_ended = pyqtSignal()
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Motion Detector Bricklet', version)

        self.md = BrickletMotionDetector(uid, ipcon)
        
        self.qtcb_motion_detected.connect(self.cb_motion_detected)
        self.md.register_callback(self.md.CALLBACK_MOTION_DETECTED,
                                  self.qtcb_motion_detected.emit)
        
        self.qtcb_detection_cylce_ended.connect(self.cb_detection_cycle_ended)
        self.md.register_callback(self.md.CALLBACK_DETECTION_CYCLE_ENDED,
                                  self.qtcb_detection_cylce_ended.emit)
        
        self.label = QLabel("No Motion Detected")
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.label)
        layout_h.addStretch()
        
        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addLayout(layout_h)
        layout.addStretch()
        
    def cb_motion_detected(self):
        self.label.setText("Motion Detected")
        
    def cb_detection_cycle_ended(self):
        self.label.setText("No Motion Detected")
        
    def get_motion_detected_async(self, motion):
        print "get_motion_detected_async", motion
        if motion == 0:
            self.cb_motion_detected()
        elif motion == 1:
            self.cb_detection_cycle_ended()

    def start(self):
        async_call(self.md.get_motion_detected, None, self.get_motion_detected_async, self.increase_error_count)
        pass
        
    def stop(self):
        pass

    def get_url_part(self):
        return 'motion_detector'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletMotionDetector.DEVICE_IDENTIFIER