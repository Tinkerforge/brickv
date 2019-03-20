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

from PyQt5.QtCore import pyqtSignal, QTimer
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

        self.left_syncer = SliderSpinSyncer(self.slider_left, self.spin_left, self.indicator_changed, spin_signal='valueChanged')
        self.right_syncer = SliderSpinSyncer(self.slider_right, self.spin_right, self.indicator_changed, spin_signal='valueChanged')
        self.bottom_syncer = SliderSpinSyncer(self.slider_bottom, self.spin_bottom, self.indicator_changed, spin_signal='valueChanged')

        self.all_syncer = SliderSpinSyncer(self.slider_all, self.spin_all, self.all_changed, spin_signal='valueChanged')

        self.sensitivity_syncer = SliderSpinSyncer(self.slider_sensitivity, self.spin_sensitivity, self.sensitivity_changed, spin_signal='valueChanged')

        def set_indicator(l, r, b):
            self.changing = True
            self.spin_left.setValue(l)
            self.spin_right.setValue(r)
            self.spin_bottom.setValue(b)
            self.changing = False
            self.indicator_changed()

        self.button_off.clicked.connect(lambda: set_indicator(0, 0, 0))
        self.button_on.clicked.connect(lambda: set_indicator(255, 255, 255))
        self.button_left.clicked.connect(lambda: set_indicator(255, 0, 0))
        self.button_right.clicked.connect(lambda: set_indicator(0, 255, 0))
        self.button_bottom.clicked.connect(lambda: set_indicator(0, 0, 255))

        self.indicator_update = False
        self.indicator_value = [0, 0, 0]
        self.sensitivity_update = False
        self.sensitivity_value = 50

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(50)
        self.update_timer.start()

    def start(self):
        async_call(self.motion_detector_v2.get_indicator, None, self.get_indicator_async, self.increase_error_count)
        async_call(self.motion_detector_v2.get_motion_detected, None, self.get_motion_detected_async, self.increase_error_count)
        async_call(self.motion_detector_v2.get_sensitivity, None, self.get_sensitivity_async, self.increase_error_count)

    def stop(self):
        pass

    # Make sure that we update values with at most a 50ms interval
    def update(self):
        if self.indicator_update:
            self.indicator_update = False
            self.motion_detector_v2.set_indicator(*self.indicator_value)
        if self.sensitivity_update:
            self.sensitivity_update = False
            self.motion_detector_v2.set_sensitivity(self.sensitivity_value)

    def sensitivity_changed(self, value):
        self.sensitivity_value = value
        self.sensitivity_update = True

    def get_sensitivity_async(self, sensitivity):
        self.spin_sensitivity.setValue(sensitivity)

    def get_motion_detected_async(self, motion):
        if motion == self.motion_detector_v2.MOTION_DETECTED:
            self.cb_motion_detected()
        elif motion == self.motion_detector_v2.MOTION_NOT_DETECTED:
            self.cb_detection_cycle_ended()

    def cb_motion_detected(self):
        self.label_motion.setText("<font color='red'>Motion Detected</font>")

    def cb_detection_cycle_ended(self):
        self.label_motion.setText("No Motion Detected")

    def indicator_changed(self, *_args):
        if self.changing:
            return

        left, right, bottom = self.spin_left.value(), self.spin_right.value(), self.spin_bottom.value()

        self.changing = True
        self.spin_all.setValue((left+right+bottom)/3)
        self.changing = False

        self.indicator_value = [left, right, bottom]
        self.indicator_update = True
        self.label_color_left.setStyleSheet('QLabel {{ background: #{:02x}{:02x}{:02x} }}'.format(0, 0, left))
        self.label_color_right.setStyleSheet('QLabel {{ background: #{:02x}{:02x}{:02x} }}'.format(0, 0, right))
        self.label_color_bottom.setStyleSheet('QLabel {{ background: #{:02x}{:02x}{:02x} }}'.format(0, 0, bottom))

    def all_changed(self, *_args):
        if self.changing:
            return

        x =  self.spin_all.value()

        self.changing = True
        self.spin_left.setValue(x)
        self.spin_right.setValue(x)
        self.spin_bottom.setValue(x)
        self.changing = False

        self.indicator_value = [x, x, x]
        self.indicator_update = True
        self.label_color_left.setStyleSheet('QLabel {{ background: #{:02x}{:02x}{:02x} }}'.format(0, 0, x))
        self.label_color_right.setStyleSheet('QLabel {{ background: #{:02x}{:02x}{:02x} }}'.format(0, 0, x))
        self.label_color_bottom.setStyleSheet('QLabel {{ background: #{:02x}{:02x}{:02x} }}'.format(0, 0, x))

    def get_indicator_async(self, indicator):
        self.changing = True
        self.spin_left.setValue(indicator.top_left)
        self.spin_right.setValue(indicator.top_right)
        self.spin_bottom.setValue(indicator.bottom)
        self.changing = False
        self.indicator_changed()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletMotionDetectorV2.DEVICE_IDENTIFIER
