# -*- coding: utf-8 -*-
"""
RGB LED Matrix Plugin
Copyright (C) 2015-2017 Olaf Lüke <olaf@tinkerforge.com>

rgb_led_matrix.py: RGB LED Matrix Plugin Implementation

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

import colorsys

from PyQt4.QtCore import pyqtSignal, Qt, QSize, QPoint
from PyQt4.QtGui import QWidget, QImage, QPainter, QPen, QColor, QPushButton, QColorDialog

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.rgb_led_matrix.ui_rgb_led_matrix import Ui_RGBLEDMatrix
from brickv.bindings.bricklet_rgb_led_matrix import BrickletRGBLEDMatrix
from brickv.callback_emulator import CallbackEmulator
from brickv.async_call import async_call

NUM_LEDS = 64

class QColorButton(QPushButton):
    colorChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(QColorButton, self).__init__(*args, **kwargs)

        self._color = QColor(255, 0, 0)
        self.setStyleSheet("background-color: %s;" % self._color.name())
        self.setMaximumWidth(32)
        self.pressed.connect(self.onColorPicker)
        
    def set_color(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit()
            self.setStyleSheet("background-color: %s;" % self._color.name())

    def color(self):
        return self._color

    def onColorPicker(self):
        dialog = QColorDialog()
        dialog.setCurrentColor(self._color)
        if dialog.exec_():
            self.set_color(dialog.currentColor())

    def mousePressEvent(self, e):
        return super(QColorButton, self).mousePressEvent(e)

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
        self.image_pen_width = 50
        self.pen_width = 1
        self.draw_color = Qt.red
        self.image = QImage(QSize(w, h), QImage.Format_RGB32)

        self.setMaximumSize(w*self.image_pen_width, w*self.image_pen_width)
        self.setMinimumSize(w*self.image_pen_width, h*self.image_pen_width)

        self.last_point = QPoint()
        self.clear_image()
        
    def set_draw_color(self, color):
        self.draw_color = color
        
    def array_draw(self, r, g, b, scale=1):
        for i in range(len(r)):
            self.image.setPixel(QPoint(i%8, i//8), (r[i]*scale << 16) | (g[i]*scale << 8) | b[i]*scale)

        self.update()
        
    def fill_image(self, color):
        self.image.fill(color)
        self.update()

    def clear_image(self):
        self.image.fill(Qt.black)
        self.update()

    def mousePressEvent(self, event):
        self.parent().state = self.parent().STATE_COLOR_SCRIBBLE
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

    def draw_line_to(self, end_point):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.draw_color if self.scribbling == 1 else Qt.black,
                            self.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(QPoint(self.last_point.x()//self.image_pen_width, self.last_point.y()//self.image_pen_width), 
                         QPoint(end_point.x()//self.image_pen_width,       end_point.y()//self.image_pen_width))

        self.update()
        self.last_point = QPoint(end_point)

class RGBLEDMatrix(COMCUPluginBase, Ui_RGBLEDMatrix):
    qtcb_frame_started = pyqtSignal(int)

    STATE_IDLE = 0
    STATE_COLOR_GRADIENT = 3
    STATE_COLOR_DOT = 4
    STATE_COLOR_SCRIBBLE = 5

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletRGBLEDMatrix, *args)

        self.setupUi(self)

        self.rgb_led_matrix = self.device
        
        self.scribble_area = ScribbleArea(8, 8, self)
        self.scribble_layout.insertWidget(1, self.scribble_area)
        
        self.color_button = QColorButton()
        self.below_scribble_layout.insertWidget(2, self.color_button)

        self.qtcb_frame_started.connect(self.cb_frame_started)

        self.color_button.colorChanged.connect(self.color_changed)
        self.button_clear_drawing.clicked.connect(self.scribble_area.clear_image)
        self.button_drawing.clicked.connect(self.drawing_clicked)
        self.button_color.clicked.connect(self.color_clicked)
        self.button_gradient.clicked.connect(self.gradient_clicked)
        self.button_dot.clicked.connect(self.dot_clicked)
        self.box_frame_duration.valueChanged.connect(self.frame_duration_changed)

        self.state = self.STATE_IDLE

        self.gradient_counter = 0
        self.dot_counter = 0
        self.dot_direction = 1

        self.voltage = 0
        
        self.cbe_supply_voltage = CallbackEmulator(self.rgb_led_matrix.get_supply_voltage,
                                                   self.cb_supply_voltage,
                                                   self.increase_error_count)

    def set_rgb(self, r, g, b):
        async_call(self.rgb_led_matrix.set_red, r, None, self.increase_error_count)
        async_call(self.rgb_led_matrix.set_green, g, None, self.increase_error_count)
        async_call(self.rgb_led_matrix.set_blue, b, None, self.increase_error_count)

    def cb_supply_voltage(self, voltage):
        self.label_voltage.setText(str(voltage/1000.0) + 'V')

    def cb_frame_started(self):
        if self.state == self.STATE_COLOR_GRADIENT:
            self.render_color_gradient()
        elif self.state == self.STATE_COLOR_DOT:
            self.render_color_dot()
        elif self.state == self.STATE_COLOR_SCRIBBLE:
            self.render_color_scribble()

    def color_changed(self):
        self.scribble_area.set_draw_color(self.color_button.color())

    def frame_duration_changed(self, duration):
        async_call(self.rgb_led_matrix.set_frame_duration, duration, None, self.increase_error_count)
        
    def drawing_clicked(self):
        old_state = self.state
        self.state = self.STATE_COLOR_SCRIBBLE
        if old_state == self.STATE_IDLE:
            self.render_color_scribble()
    
    def color_clicked(self):
        old_state = self.state
        self.state = self.STATE_COLOR_SCRIBBLE
        self.scribble_area.fill_image(self.color_button.color())
        if old_state == self.STATE_IDLE:
            self.render_color_scribble()

    def gradient_clicked(self):
        old_state = self.state
        self.state = self.STATE_COLOR_GRADIENT
        if old_state == self.STATE_IDLE:
            self.render_color_gradient()

    def dot_clicked(self):
        self.dot_counter = 0
        self.dot_direction = 1
        old_state = self.state
        self.state = self.STATE_COLOR_DOT
        if old_state == self.STATE_IDLE:
            self.render_color_dot()

    def render_color_scribble(self):
        r = []
        g = []
        b = []
        for i in range(8):
            for j in range(8):
                color = QColor(self.scribble_area.image.pixel(j, i))
                r.append(color.red())
                g.append(color.green())
                b.append(color.blue())
        
        self.set_rgb(r, g, b)

    def render_color_gradient(self):
        self.gradient_counter += NUM_LEDS * self.box_speed.value() / 100.0 / 4.0
        ra = []
        ga = []
        ba = []

        range_leds = range(NUM_LEDS)
        range_leds = range_leds[int(self.gradient_counter) % NUM_LEDS:] + range_leds[:int(self.gradient_counter) % NUM_LEDS]
        range_leds = reversed(range_leds)

        for i in range_leds:
            r, g, b = colorsys.hsv_to_rgb(1.0*i/NUM_LEDS, 1, 0.2)
            ra.append(int(r*255))
            ga.append(int(g*255))
            ba.append(int(b*255))

        self.scribble_area.array_draw(ra, ga, ba, 4)
        self.set_rgb(ra, ga, ba)

    def render_color_dot(self):
        color = self.color_button.color()
        r = color.red()
        g = color.green()
        b = color.blue()

        self.dot_counter = self.dot_counter % NUM_LEDS

        index = self.dot_counter
        line = self.dot_counter // 8
        if line % 2:
            index = line*8 + (7 - (self.dot_counter % 8))

        r_val = [0]*NUM_LEDS
        g_val = [0]*NUM_LEDS
        b_val = [0]*NUM_LEDS

        r_val[index] = r
        g_val[index] = g
        b_val[index] = b

        self.scribble_area.array_draw(r_val, g_val, b_val)
        self.set_rgb(r_val, g_val, b_val)

        self.dot_counter += self.dot_direction * self.box_speed.value()

        if self.dot_counter >= NUM_LEDS:
            self.dot_direction = -1
            self.dot_counter = NUM_LEDS - 1
        elif self.dot_counter < 0:
            self.dot_direction = 1
            self.dot_counter = 0

    def start(self):
        self.rgb_led_matrix.register_callback(self.rgb_led_matrix.CALLBACK_FRAME_STARTED, self.qtcb_frame_started.emit)
        self.cbe_supply_voltage.set_period(250)
        async_call(self.rgb_led_matrix.set_frame_duration, self.box_frame_duration.value(), None, self.increase_error_count)

    def stop(self):
        self.rgb_led_matrix.register_callback(self.rgb_led_matrix.CALLBACK_FRAME_STARTED, None)
        self.cbe_supply_voltage.set_period(0)
        async_call(self.rgb_led_matrix.set_frame_duration, 0, None, self.increase_error_count)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRGBLEDMatrix.DEVICE_IDENTIFIER
