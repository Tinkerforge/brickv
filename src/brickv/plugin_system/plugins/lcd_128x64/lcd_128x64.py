# -*- coding: utf-8 -*-
"""
LCD128x64 Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2020 Erik Fleckstein <erik@tinkerforge.com>

lcd_128x64.py: LCD 128x64 Plugin Implementation

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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QBrush

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.async_call import async_call
from brickv.slider_spin_syncer import SliderSpinSyncer
from brickv.plugin_system.plugins.lcd_128x64.ui_lcd_128x64 import Ui_LCD128x64
from brickv.bindings.bricklet_lcd_128x64 import BrickletLCD128x64
from brickv.callback_emulator import CallbackEmulator
from brickv.scribblewidget import ScribbleWidget

class TouchScribbleWidget(ScribbleWidget):
    def __init__(self, width, height, scaling_factor, foreground_color, background_color, outline_color=None, enable_grid=True, grid_color=None, parent=None):
        super().__init__(width, height, scaling_factor, foreground_color, background_color, outline_color, enable_grid, grid_color, parent)

        self.circle_width = 30

        self.touch_x = 0
        self.touch_y = 0
        self.touch_pressure = 0
        self.touch_age = 100000
        self.touch_age_max = 250

        self.gesture = 0
        self.gesture_age = 10000
        self.gesture_age_max = 1000
        self.gesture_pressure_max = 0

    def touch_position(self, data):
        self.touch_x = data.x
        self.touch_y = data.y
        self.touch_pressure = data.pressure
        self.touch_age = data.age

        self.repaint()

    def touch_gesture(self, data):
        self.gesture = data.gesture
        self.gesture_pressure_max = data.pressure_max
        self.gesture_age = data.age

    def paint_overlay(self, event, painter):
        if self.touch_age < self.touch_age_max:
            painter.setPen(Qt.red)
            painter.drawEllipse(int(self.touch_x * self.scaling_factor - self.circle_width/2.0), int(self.touch_y * self.scaling_factor - self.circle_width/2.0), self.circle_width, self.circle_width)
            if self.touch_pressure > 100:
                painter.drawEllipse(int(self.touch_x * self.scaling_factor - self.circle_width/3.0), int(self.touch_y * self.scaling_factor - self.circle_width/3.0), int(self.circle_width/1.5), int(self.circle_width/1.5))
                if self.touch_pressure > 175:
                    painter.drawEllipse(int(self.touch_x * self.scaling_factor - self.circle_width/6.0), int(self.touch_y * self.scaling_factor - self.circle_width/6.0), int(self.circle_width/3.0), int(self.circle_width/3.0))

        if self.gesture_age < self.gesture_age_max:
            pen_width = 1
            if self.gesture_pressure_max > 100:
                pen_width = 2
                if self.gesture_pressure_max > 175:
                    pen_width = 3

            painter.setPen(QPen(Qt.darkGreen, pen_width))
            painter.setBrush(QBrush(Qt.green))

            scaling_factor = 2
            if self.gesture == BrickletLCD128x64.GESTURE_LEFT_TO_RIGHT:
                painter.drawChord(int(20-75/2.0*scaling_factor), 20, 75 * scaling_factor, 10 * scaling_factor, 90*16, -180*16)
            elif self.gesture == BrickletLCD128x64.GESTURE_RIGHT_TO_LEFT:
                painter.drawChord(20, 20, 75 * scaling_factor, 10 * scaling_factor, 90*16, 180*16)
            elif self.gesture == BrickletLCD128x64.GESTURE_BOTTOM_TO_TOP:
                painter.drawChord(20, 20, 10 * scaling_factor, 75 * scaling_factor, 0, 180*16)
            elif self.gesture == BrickletLCD128x64.GESTURE_TOP_TO_BOTTOM:
                painter.drawChord(20, int(20-75/2.0*scaling_factor), 10 * scaling_factor, 75 * scaling_factor, 0, -180*16)


class LCD128x64(COMCUPluginBase, Ui_LCD128x64):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletLCD128x64, *args)

        self.setupUi(self)

        self.lcd = self.device

        self.scribble_widget = TouchScribbleWidget(128, 64, 5, QColor(Qt.black), QColor(Qt.white), enable_grid=False)
        self.image_button_layout.insertWidget(0, self.scribble_widget)

        self.contrast_syncer = SliderSpinSyncer(self.contrast_slider, self.contrast_spin, lambda value: self.new_configuration(), spin_signal='valueChanged')
        self.backlight_syncer = SliderSpinSyncer(self.backlight_slider, self.backlight_spin, lambda value: self.new_configuration(), spin_signal='valueChanged')
        self.char_syncer = SliderSpinSyncer(self.char_slider, self.char_spin, self.char_slider_changed, spin_signal='valueChanged')

        self.draw_button.clicked.connect(self.draw_clicked)
        self.clear_button.clicked.connect(self.clear_clicked)
        self.send_button.clicked.connect(self.send_clicked)
        self.clear_display_button.clicked.connect(self.clear_display_clicked)
        self.invert_checkbox.stateChanged.connect(self.new_configuration)

        self.current_char_value = -1
        self.write_line_response_expected = None

        self.cbe_touch_position = CallbackEmulator(self,
                                                   self.lcd.get_touch_position,
                                                   None,
                                                   self.scribble_widget.touch_position,
                                                   self.increase_error_count)
        self.cbe_touch_gesture = CallbackEmulator(self,
                                                  self.lcd.get_touch_gesture,
                                                  None,
                                                  self.scribble_widget.touch_gesture,
                                                  self.increase_error_count)

    def char_slider_changed(self, value):
        if value != self.current_char_value:
            self.current_char_value = value
            self.write_chars(value)
            self.char_slider.setValue(value)

    def new_configuration(self):
        contrast = self.contrast_slider.value()
        backlight = self.backlight_slider.value()
        invert = self.invert_checkbox.isChecked()
        self.lcd.set_display_configuration(contrast, backlight, invert, True)

    def write_chars(self, value):
        if value > 248:
            value = 248

        for j in range(8):
            start = ""

            if value + j < 10:
                start = "  "
            elif value + j < 100:
                start = " "

            self.lcd.write_line(j, 8, start + str(value + j) + ": " + chr(value + j) + '\0')

    def clear_display_clicked(self):
        self.lcd.clear_display()

    def clear_clicked(self):
        self.scribble_widget.clear_image()

    def send_clicked(self):
        line = int(self.line_combobox.currentText())
        pos = int(self.pos_combobox.currentText())
        text = self.text_edit.text()
        self.lcd.write_line(line, pos, text)

    def draw_clicked(self):
        data = []

        for i in range(64):
            for j in range(128):
                if QColor(self.scribble_widget.image().pixel(j, i)) == self.scribble_widget.foreground_color():
                    data.append(True)
                else:
                    data.append(False)

        async_call(self.lcd.write_pixels, (0, 0, 127, 63, data), None, self.increase_error_count)

    def get_display_configuration_async(self, conf):
        self.contrast_slider.setValue(conf.contrast)
        self.backlight_slider.setValue(conf.backlight)
        self.invert_checkbox.setChecked(conf.invert)

    def read_pixels_async(self, pixels):
        for i in range(64):
            for j in range(128):
                if pixels[i * 128 + j]:
                    self.scribble_widget.image().setPixel(j, i, self.scribble_widget.foreground_color().rgb())
                else:
                    self.scribble_widget.image().setPixel(j, i, self.scribble_widget.background_color().rgb())

        self.scribble_widget.update()

    def start(self):
        # Use response expected for write_line function, to make sure that the
        # data queue can't fill up while you move the slider around.
        self.write_line_response_expected = self.lcd.get_response_expected(self.lcd.FUNCTION_WRITE_LINE)
        self.lcd.set_response_expected(self.lcd.FUNCTION_WRITE_LINE, True)

        async_call(self.lcd.get_display_configuration, None, self.get_display_configuration_async, self.increase_error_count)
        async_call(self.lcd.read_pixels, (0, 0, 127, 63), self.read_pixels_async, self.increase_error_count)

        self.cbe_touch_position.set_period(25)
        self.cbe_touch_gesture.set_period(25)

    def stop(self):
        if self.write_line_response_expected != None:
            self.lcd.set_response_expected(self.lcd.FUNCTION_WRITE_LINE, self.write_line_response_expected)

        self.cbe_touch_position.set_period(0)
        self.cbe_touch_gesture.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletLCD128x64.DEVICE_IDENTIFIER
