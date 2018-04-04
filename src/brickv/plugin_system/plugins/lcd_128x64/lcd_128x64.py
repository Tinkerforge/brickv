# -*- coding: utf-8 -*-
"""
LCD128x64 Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

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

from PyQt4.QtCore import Qt, QSize, QPoint
from PyQt4.QtGui import QWidget, QImage, QPainter, QPen, QColor

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.async_call import async_call
from brickv.slider_spin_syncer import SliderSpinSyncer
from brickv.plugin_system.plugins.lcd_128x64.ui_lcd_128x64 import Ui_LCD128x64
from brickv.bindings.bricklet_lcd_128x64 import BrickletLCD128x64
from brickv.callback_emulator import CallbackEmulator

class ScribbleArea(QWidget):
    """
      this scales the image but it's not good, too many refreshes really mess it up!!!
    """
    def __init__(self, w, h, parent=None):
        super(ScribbleArea, self).__init__(parent)

        self.setAttribute(Qt.WA_StaticContents)
        self.scribbling = 0

        self.width = w
        self.height = h
        self.image_pen_width = 5
        self.pen_width = 1
        self.circle_width = 30
        self.image = QImage(QSize(w, h), QImage.Format_RGB32)

        self.setMaximumSize(w*self.image_pen_width, w*self.image_pen_width)
        self.setMinimumSize(w*self.image_pen_width, h*self.image_pen_width)

        self.last_point = QPoint()
        self.clear_image()
        
        self.touch_x = 0
        self.touch_y = 0
        self.touch_pressure = 0
        self.touch_age = 100000
        self.touch_age_max = 250
        
        self.gesture = 0
        self.gesture_age = 10000
        self.gesture_age_max = 1000
        
    def touch_position(self, data):
        self.touch_x = data.x
        self.touch_y = 63-data.y
        self.touch_pressure = data.pressure
        self.touch_age = data.age
        
        self.repaint()
        
    def touch_gesture(self, data):
        self.gesture = data.gesture
        self.gesture_age = data.age

    def clear_image(self):
        self.image.fill(Qt.black)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_point = event.pos()
            self.scribbling = 1
        elif event.button() == Qt.RightButton:
            self.last_point = event.pos()
            self.scribbling = 2

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.scribbling == 1:
            self.draw_line_to(event.pos())
        elif (event.buttons() & Qt.RightButton) and self.scribbling == 2:
            self.draw_line_to(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.scribbling == 1:
            self.draw_line_to(event.pos())
            self.scribbling = 0
        elif event.button() == Qt.RightButton and self.scribbling == 2:
            self.draw_line_to(event.pos())
            self.scribbling = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(event.rect(), self.image.scaledToWidth(self.width*self.image_pen_width))

        if self.touch_age < self.touch_age_max: 
            painter.setPen(Qt.red)
            painter.drawEllipse(self.touch_x * self.image_pen_width - self.circle_width/2.0, self.touch_y * self.image_pen_width - self.circle_width/2.0, self.circle_width, self.circle_width)
            if self.touch_pressure > 100:
                painter.drawEllipse(self.touch_x * self.image_pen_width - self.circle_width/3.0, self.touch_y * self.image_pen_width - self.circle_width/3.0, self.circle_width/1.5, self.circle_width/1.5)
                if self.touch_pressure > 150:
                    painter.drawEllipse(self.touch_x * self.image_pen_width - self.circle_width/6.0, self.touch_y * self.image_pen_width - self.circle_width/6.0, self.circle_width/3.0, self.circle_width/3.0)
                    
        if self.gesture_age < self.gesture_age_max:
            painter.setPen(Qt.darkGreen)
            if self.gesture == BrickletLCD128x64.GESTURE_LEFT_TO_RIGHT:
                painter.drawChord(20-75/2.0, 20, 75, 10, 90*16, -180*16)
            elif self.gesture == BrickletLCD128x64.GESTURE_RIGHT_TO_LEFT:
                painter.drawChord(20, 20, 75, 10, 90*16, 180*16)
            if self.gesture == BrickletLCD128x64.GESTURE_BOTTOM_TO_TOP:
                painter.drawChord(20, 20, 10, 75, 0, 180*16)
            if self.gesture == BrickletLCD128x64.GESTURE_TOP_TO_BOTTOM:
                painter.drawChord(20, 20-75/2.0, 10, 75, 0, -180*16)
             
                

    def draw_line_to(self, end_point):
        painter = QPainter(self.image)
        painter.setPen(QPen(Qt.white if self.scribbling == 1 else Qt.black,
                            self.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(self.last_point/5, end_point/5)

        self.update()
        self.last_point = QPoint(end_point)

class LCD128x64(COMCUPluginBase, Ui_LCD128x64):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletLCD128x64, *args)

        self.setupUi(self)

        self.lcd = self.device

        self.scribble_area = ScribbleArea(128, 64)
        self.image_button_layout.insertWidget(0, self.scribble_area)

        self.contrast_syncer = SliderSpinSyncer(self.contrast_slider, self.contrast_spin, lambda value: self.new_configuration())
        self.backlight_syncer = SliderSpinSyncer(self.backlight_slider, self.backlight_spin, lambda value: self.new_configuration())
        self.char_syncer = SliderSpinSyncer(self.char_slider, self.char_spin, self.char_slider_changed)

        self.draw_button.clicked.connect(self.draw_clicked)
        self.clear_button.clicked.connect(self.clear_clicked)
        self.send_button.clicked.connect(self.send_clicked)
        self.clear_display_button.clicked.connect(self.clear_display_clicked)
        self.invert_checkbox.stateChanged.connect(self.new_configuration)

        self.current_char_value = -1
        
        self.cbe_touch_position = CallbackEmulator(self.lcd.get_touch_position,
                                                   self.scribble_area.touch_position,
                                                   self.increase_error_count)
        self.cbe_touch_gesture = CallbackEmulator(self.lcd.get_touch_gesture,
                                                  self.scribble_area.touch_gesture,
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
            self.lcd.write_line(j, 8, start + str(value+j) + ": " + chr(value+j) + '\0')

    def clear_display_clicked(self):
        self.lcd.clear_display()

    def clear_clicked(self):
        self.scribble_area.clear_image()

    def send_clicked(self):
        line = int(self.line_combobox.currentText())
        pos = int(self.pos_combobox.currentText())
        text = self.text_edit.text()
        self.lcd.write_line(line, pos, text)

    def draw_clicked(self):
        data = []
        for i in range(64):
            for j in range(128):
                if QColor(self.scribble_area.image.pixel(j, i)) == Qt.white:
                    data.append(True)
                else:
                    data.append(False)

        self.lcd.write_pixels(0, 0, 127, 63, data)

    def cb_display_configuration(self, conf):
        self.contrast_slider.setValue(conf.contrast)
        self.backlight_slider.setValue(conf.backlight)
        self.invert_checkbox.setChecked(conf.invert)

    def cb_read_pixels(self, pixels):
        for i in range(64):
            for j in range(128):
                if pixels[i*128 + j]:
                    self.scribble_area.image.setPixel(j, i, 0xFFFFFF)
                else:
                    self.scribble_area.image.setPixel(j, i, 0)

        self.scribble_area.update()

    def start(self):
        async_call(self.lcd.get_display_configuration, None, self.cb_display_configuration, self.increase_error_count)
        async_call(self.oled.read_pixels, (0, 0, 127, 63), self.cb_read_pixels, self.increase_error_count)
        self.cbe_touch_position.set_period(25)
        self.cbe_touch_gesture.set_period(25)

    def stop(self):
        self.cbe_touch_position.set_period(0)
        self.cbe_touch_gesture.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletLCD128x64.DEVICE_IDENTIFIER
