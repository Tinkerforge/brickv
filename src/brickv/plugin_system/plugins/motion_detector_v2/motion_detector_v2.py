# -*- coding: utf-8 -*-
"""
Motion Detector V2 Plugin
Copyright (C) 2017 Olaf Lüke <olaf@tinkerforge.com>

motion_detector_v2.py: Motion Detector V2 Plugin Implementation

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

from PyQt4.QtGui import QColor

from PyQt4.QtCore import pyqtSignal
from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_motion_detector_v2 import BrickletMotionDetectorV2
from brickv.plugin_system.plugins.motion_detector_v2.ui_motion_detector_v2 import Ui_MotionDetectorV2
from brickv.slider_spin_syncer import SliderSpinSyncer
from brickv.async_call import async_call

class MotionDetectorV2(COMCUPluginBase, Ui_MotionDetectorV2):
    qtcb_motion_detected = pyqtSignal()
    qtcb_detection_cylce_ended = pyqtSignal()
    
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletMotionDetectorV2, *args)

        self.motion_detector_v2 = self.device

        self.changing = False

        self.setupUi(self)
        
        self.qtcb_motion_detected.connect(self.cb_motion_detected)
        self.motion_detector_v2.register_callback(self.motion_detector_v2.CALLBACK_MOTION_DETECTED,
                                                  self.qtcb_motion_detected.emit)

        self.qtcb_detection_cylce_ended.connect(self.cb_detection_cycle_ended)
        self.motion_detector_v2.register_callback(self.motion_detector_v2.CALLBACK_DETECTION_CYCLE_ENDED,
                                                  self.qtcb_detection_cylce_ended.emit)

        self.r_syncer = SliderSpinSyncer(self.slider_r, self.spin_r, self.rgb_changed, spin_signal='valueChanged')
        self.g_syncer = SliderSpinSyncer(self.slider_g, self.spin_g, self.rgb_changed, spin_signal='valueChanged')
        self.b_syncer = SliderSpinSyncer(self.slider_b, self.spin_b, self.rgb_changed, spin_signal='valueChanged')

        self.h_syncer = SliderSpinSyncer(self.slider_h, self.spin_h, self.hsl_changed, spin_signal='valueChanged')
        self.s_syncer = SliderSpinSyncer(self.slider_s, self.spin_s, self.hsl_changed, spin_signal='valueChanged')
        self.l_syncer = SliderSpinSyncer(self.slider_l, self.spin_l, self.hsl_changed, spin_signal='valueChanged')

        def set_color(r, g, b):
            self.changing = True
            self.spin_r.setValue(r)
            self.spin_g.setValue(g)
            self.spin_b.setValue(b)
            self.changing = False
            self.rgb_changed()

        self.button_black.clicked.connect(lambda: set_color(0, 0, 0))
        self.button_white.clicked.connect(lambda: set_color(255, 255, 255))
        self.button_red.clicked.connect(lambda: set_color(255, 0, 0))
        self.button_yellow.clicked.connect(lambda: set_color(255, 255, 0))
        self.button_green.clicked.connect(lambda: set_color(0, 255, 0))
        self.button_cyan.clicked.connect(lambda: set_color(0, 255, 255))
        self.button_blue.clicked.connect(lambda: set_color(0, 0, 255))
        self.button_magenta.clicked.connect(lambda: set_color(255, 0, 255))
        
        self.spinbox_sensitivity.valueChanged.connect(self.sensitivity_changed)

    def start(self):
        async_call(self.motion_detector_v2.get_color, None, self.get_color_async, self.increase_error_count)
        async_call(self.motion_detector_v2.get_motion_detected, None, self.get_motion_detected_async, self.increase_error_count)
        async_call(self.motion_detector_v2.get_sensitivity, None, self.get_sensitivity_async, self.increase_error_count)

    def stop(self):
        pass
    
    def sensitivity_changed(self, value):
        self.motion_detector_v2.set_sensitivity(value)
    
    def get_sensitivity_async(self, sensitivity):
        self.spinbox_sensitivity.setValue(sensitivity)
    
    def get_motion_detected_async(self, motion):
        if motion == self.motion_detector_v2.MOTION_DETECTED:
            self.cb_motion_detected()
        elif motion == self.motion_detector_v2.MOTION_NOT_DETECTED:
            self.cb_detection_cycle_ended()
            
    def cb_motion_detected(self):
        self.label_motion.setText("<font color='red'>Motion Detected</font>")

    def cb_detection_cycle_ended(self):
        self.label_motion.setText("No Motion Detected")

    def rgb_changed(self, *args):
        if self.changing:
            return

        r, g, b = self.spin_r.value(), self.spin_g.value(), self.spin_b.value()
        rgb = QColor(r, g, b)
        h, s, l = rgb.hue(), rgb.saturation(), rgb.lightness()

        self.changing = True
        self.spin_h.setValue(h)
        self.spin_s.setValue(s)
        self.spin_l.setValue(l)
        self.changing = False

        self.motion_detector_v2.set_color(r, g, b)
        self.label_color.setStyleSheet('QLabel {{ background: #{:02x}{:02x}{:02x} }}'.format(r, g, b))

    def hsl_changed(self, *args):
        if self.changing:
            return

        h, s, l = self.spin_h.value(), self.spin_s.value(), self.spin_l.value()
        hsl = QColor()
        hsl.setHsl(h, s, l)
        r, g, b = hsl.red(), hsl.green(), hsl.blue()

        self.changing = True
        self.spin_r.setValue(r)
        self.spin_g.setValue(g)
        self.spin_b.setValue(b)
        self.changing = False

        self.motion_detector_v2.set_color(r, g, b)
        self.label_color.setStyleSheet('QLabel {{ background: #{:02x}{:02x}{:02x} }}'.format(r, g, b))

    def get_color_async(self, rgb):
        self.changing = True
        self.spin_r.setValue(rgb.red)
        self.spin_g.setValue(rgb.green)
        self.spin_b.setValue(rgb.blue)
        self.changing = False
        self.rgb_changed()

    def destroy(self):
        pass

    def get_url_part(self):
        return 'motion_detector_v2'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletMotionDetectorV2.DEVICE_IDENTIFIER
