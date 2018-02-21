# -*- coding: utf-8 -*-
"""
Segment Display 4x7 Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

segment_display_4x7.py: Segment Display 4x7 Plugin Implementation

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

from PyQt4.QtCore import QTimer, pyqtSignal

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.segment_display_4x7.ui_segment_display_4x7 import Ui_SegmentDisplay4x7
from brickv.bindings.bricklet_segment_display_4x7 import BrickletSegmentDisplay4x7
from brickv.async_call import async_call

class SegmentDisplay4x7(PluginBase, Ui_SegmentDisplay4x7):
    qtcb_finished = pyqtSignal()
    STYLE_OFF = "QPushButton { background-color: grey; color: grey; }"
    STYLE_ON = ["QPushButton { background-color: #880000; color: #880000; }",
                "QPushButton { background-color: #990000; color: #990000; }",
                "QPushButton { background-color: #AA0000; color: #AA0000; }",
                "QPushButton { background-color: #BB0000; color: #BB0000; }",
                "QPushButton { background-color: #CC0000; color: #CC0000; }",
                "QPushButton { background-color: #DD0000; color: #DD0000; }",
                "QPushButton { background-color: #EE0000; color: #EE0000; }",
                "QPushButton { background-color: #FF0000; color: #FF0000; }"]

    def __init__(self, *args):
        PluginBase.__init__(self, BrickletSegmentDisplay4x7, *args)

        self.setupUi(self)

        self.sd4x7 = self.device

        self.qtcb_finished.connect(self.cb_counter_finished)
        self.sd4x7.register_callback(self.sd4x7.CALLBACK_COUNTER_FINISHED,
                                     self.qtcb_finished.emit)

        self.digit0 = [self.digit0_segment0, self.digit0_segment1, self.digit0_segment2, self.digit0_segment3, self.digit0_segment4, self.digit0_segment5, self.digit0_segment6]
        self.digit1 = [self.digit1_segment0, self.digit1_segment1, self.digit1_segment2, self.digit1_segment3, self.digit1_segment4, self.digit1_segment5, self.digit1_segment6]
        self.digit2 = [self.digit2_segment0, self.digit2_segment1, self.digit2_segment2, self.digit2_segment3, self.digit2_segment4, self.digit2_segment5, self.digit2_segment6]
        self.digit3 = [self.digit3_segment0, self.digit3_segment1, self.digit3_segment2, self.digit3_segment3, self.digit3_segment4, self.digit3_segment5, self.digit3_segment6]
        self.points = [self.point0, self.point1]

        self.digits = [self.digit0, self.digit1, self.digit2, self.digit3, self.points]
        self.digit_state = [[False]*7, [False]*7, [False]*7, [False]*7, [False]*2]

        self.all_buttons = []
        self.all_buttons.extend(self.points)
        self.all_buttons.extend(self.digit0)
        self.all_buttons.extend(self.digit1)
        self.all_buttons.extend(self.digit2)
        self.all_buttons.extend(self.digit3)

        self.brightness = 7
        self.box_brightness.currentIndexChanged.connect(self.brightness_changed)
        self.button_all_segments_on.clicked.connect(self.all_segments_on_clicked)
        self.button_all_segments_off.clicked.connect(self.all_segments_off_clicked)
        self.button_start.clicked.connect(self.start_clicked)

        def get_clicked_func(digit, segment):
            return lambda: self.button_clicked(digit, segment)

        for d in range(4):
            for i in range(7):
                button = self.digits[d][i]
                button.setStyleSheet(self.STYLE_OFF)
                button.clicked.connect(get_clicked_func(d, i))

        for i in range(2):
            button = self.points[i]
            button.setStyleSheet(self.STYLE_OFF)
            button.clicked.connect(get_clicked_func(4, i))

        self.counter_timer = QTimer()
        self.counter_timer.timeout.connect(self.update_counter)
        self.counter_timer.setInterval(100)

    def all_segments_on_clicked(self):
        self.counter_timer.stop()
        value = ([0xFF, 0xFF, 0xFF, 0xFF], self.brightness, True)
        self.sd4x7.set_segments(*value)
        self.cb_get_segments(value)

    def all_segments_off_clicked(self):
        self.counter_timer.stop()
        value = ([0, 0, 0, 0], self.brightness, False)
        self.sd4x7.set_segments(*value)
        self.cb_get_segments(value)

    def cb_counter_finished(self):
        self.counter_timer.stop()
        async_call(self.sd4x7.get_segments, None, self.cb_get_segments, self.increase_error_count)

    def update_counter(self):
        async_call(self.sd4x7.get_segments, None, self.cb_get_segments, self.increase_error_count)

    def start_clicked(self):
        fr = self.box_from.value()
        to = self.box_to.value()
        increment = self.box_increment.value()
        length = self.box_length.value()

        self.counter_timer.start()

        if (length == 0) or (increment == 0) or (increment > 0 and fr > to) or (increment < 0 and fr < to):
            return

        self.sd4x7.start_counter(fr, to, increment, length)

    def brightness_changed(self, brightness):
        if self.brightness != brightness:
            self.brightness = brightness

            self.update_colors()
            self.update_segments()

    def update_colors(self):
        if self.digit_state[4][0]:
            self.digits[4][0].setStyleSheet(self.STYLE_ON[self.brightness])
            self.digits[4][1].setStyleSheet(self.STYLE_ON[self.brightness])

        for d in range(4):
            for s in range(7):
                if self.digit_state[d][s]:
                    self.digits[d][s].setStyleSheet(self.STYLE_ON[self.brightness])

    def button_clicked(self, digit, segment):
        self.counter_timer.stop()
        if digit == 4:
            if self.digit_state[4][0]:
                self.digits[4][0].setStyleSheet(self.STYLE_OFF)
                self.digits[4][1].setStyleSheet(self.STYLE_OFF)
                self.digit_state[4][0] = False
                self.digit_state[4][1] = False
            else:
                self.digits[4][0].setStyleSheet(self.STYLE_ON[self.brightness])
                self.digits[4][1].setStyleSheet(self.STYLE_ON[self.brightness])
                self.digit_state[4][0] = True
                self.digit_state[4][1] = True
        else:
            if self.digit_state[digit][segment]:
                self.digits[digit][segment].setStyleSheet(self.STYLE_OFF)
                self.digit_state[digit][segment] = False
            else:
                self.digits[digit][segment].setStyleSheet(self.STYLE_ON[self.brightness])
                self.digit_state[digit][segment] = True

        self.update_segments()

    def update_segments(self):
        segments = [0, 0, 0, 0]
        for d in range(4):
            for s in range(7):
                if self.digit_state[d][s]:
                    segments[d] |= (1 << s)

        self.sd4x7.set_segments(segments, self.brightness, self.digit_state[4][0])

    def cb_get_segments(self, value):
        segments, brightness, colon = value

        self.brightness = brightness
        self.box_brightness.setCurrentIndex(self.brightness)

        if colon:
            self.digit_state[4][0] = True
            self.digits[4][0].setStyleSheet(self.STYLE_ON[self.brightness])
            self.digit_state[4][0] = True
            self.digits[4][1].setStyleSheet(self.STYLE_ON[self.brightness])
        else:
            self.digit_state[4][0] = False
            self.digits[4][0].setStyleSheet(self.STYLE_OFF)
            self.digit_state[4][0] = False
            self.digits[4][1].setStyleSheet(self.STYLE_OFF)

        for d in range(4):
            for s in range(7):
                if segments[d] & (1 << s):
                    self.digit_state[d][s] = True
                    self.digits[d][s].setStyleSheet(self.STYLE_ON[self.brightness])
                else:
                    self.digit_state[d][s] = False
                    self.digits[d][s].setStyleSheet(self.STYLE_OFF)

    def start(self):
        async_call(self.sd4x7.get_segments, None, self.cb_get_segments, self.increase_error_count)

    def stop(self):
        self.counter_timer.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletSegmentDisplay4x7.DEVICE_IDENTIFIER
