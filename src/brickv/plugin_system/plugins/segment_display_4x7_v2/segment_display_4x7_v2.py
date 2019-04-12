# -*- coding: utf-8 -*-
"""
Segment Display 4x7 2.0 Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

segment_display_4x7_v2.py: Segment Display 4x7 2.0 Plugin implementation

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

from PyQt5.QtCore import QTimer, pyqtSignal

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.segment_display_4x7_v2.ui_segment_display_4x7_v2 import Ui_SegmentDisplay4x7V2
from brickv.bindings.bricklet_segment_display_4x7_v2 import BrickletSegmentDisplay4x7V2
from brickv.async_call import async_call

class SegmentDisplay4x7V2(COMCUPluginBase, Ui_SegmentDisplay4x7V2):
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
        COMCUPluginBase.__init__(self, BrickletSegmentDisplay4x7V2, *args)

        self.setupUi(self)

        self.sd4x7 = self.device

        self.qtcb_finished.connect(self.cb_counter_finished)
        self.sd4x7.register_callback(self.sd4x7.CALLBACK_COUNTER_FINISHED, self.qtcb_finished.emit)

        self.segments = [
            self.digit0_segment0, self.digit0_segment1, self.digit0_segment2, self.digit0_segment3, self.digit0_segment4, self.digit0_segment5, self.digit0_segment6, self.digit0_segment7,
            self.digit1_segment0, self.digit1_segment1, self.digit1_segment2, self.digit1_segment3, self.digit1_segment4, self.digit1_segment5, self.digit1_segment6, self.digit1_segment7,
            self.digit2_segment0, self.digit2_segment1, self.digit2_segment2, self.digit2_segment3, self.digit2_segment4, self.digit2_segment5, self.digit2_segment6, self.digit2_segment7,
            self.digit3_segment0, self.digit3_segment1, self.digit3_segment2, self.digit3_segment3, self.digit3_segment4, self.digit3_segment5, self.digit3_segment6, self.digit3_segment7,
            self.colon0, self.colon1,
            self.tick
        ]

        self.brightness = 7
        self.box_brightness.currentIndexChanged.connect(self.brightness_changed)
        self.button_all_segments_on.clicked.connect(self.all_segments_on_clicked)
        self.button_all_segments_off.clicked.connect(self.all_segments_off_clicked)
        self.button_start.clicked.connect(self.start_clicked)

        def get_clicked_func(segment):
            return lambda: self.button_clicked(segment)

        for i, segment in enumerate(self.segments):
            segment.setStyleSheet(self.STYLE_OFF)
            segment.clicked.connect(get_clicked_func(i))

        self.counter_timer = QTimer(self)
        self.counter_timer.timeout.connect(self.update_counter)
        self.counter_timer.setInterval(100)

    def all_segments_on_clicked(self):
        self.counter_timer.stop()
        value = ([True]*8, [True]*8, [True]*8, [True]*8, [True]*2, True)
        self.sd4x7.set_segments(*value)
        self.get_segments_async(value)

    def all_segments_off_clicked(self):
        self.counter_timer.stop()
        value = ([False]*8, [False]*8, [False]*8, [False]*8, [False]*2, False)
        self.sd4x7.set_segments(*value)
        self.get_segments_async(value)

    def cb_counter_finished(self):
        self.counter_timer.stop()
        async_call(self.sd4x7.get_segments, None, self.get_segments_async, self.increase_error_count)

    def update_counter(self):
        async_call(self.sd4x7.get_segments, None, self.get_segments_async, self.increase_error_count)

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
            self.sd4x7.set_brightness(self.brightness)

    def update_colors(self):
        for segment in self.segments:
            if segment.styleSheet() != self.STYLE_OFF:
                segment.setStyleSheet(self.STYLE_ON[self.brightness])

    def button_clicked(self, segment):
        self.counter_timer.stop()

        if self.segments[segment].styleSheet() == self.STYLE_OFF:
            self.segments[segment].setStyleSheet(self.STYLE_ON[self.brightness])
        else:
            self.segments[segment].setStyleSheet(self.STYLE_OFF)

        self.update_segments()

    def update_segments(self):
        values = []
        for segment in self.segments:
            values.append(segment.styleSheet() != self.STYLE_OFF)

        self.sd4x7.set_segments(values[0:8], values[8:16], values[16:24], values[24:32], values[32:34], values[34])

    def get_brightness_async(self, brightness):
        self.brightness = brightness
        self.box_brightness.setCurrentIndex(brightness)

    def get_segments_async(self, value):
        digit0, digit1, digit2, digit3, colon, tick = value

        values = []
        values.extend(digit0)
        values.extend(digit1)
        values.extend(digit2)
        values.extend(digit3)
        values.extend(colon)
        values.append(tick)

        for i in range(len(self.segments)):
            if values[i]:
                self.segments[i].setStyleSheet(self.STYLE_ON[self.brightness])
            else:
                self.segments[i].setStyleSheet(self.STYLE_OFF)

    def start(self):
        async_call(self.sd4x7.get_segments, None, self.get_segments_async, self.increase_error_count)
        async_call(self.sd4x7.get_brightness, None, self.get_brightness_async, self.increase_error_count)

    def stop(self):
        self.counter_timer.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletSegmentDisplay4x7V2.DEVICE_IDENTIFIER
