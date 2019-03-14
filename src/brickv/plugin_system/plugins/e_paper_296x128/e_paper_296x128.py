# -*- coding: utf-8 -*-
"""
E-Paper 296x128 Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

e_paper_296x128.py: E-Paper 296x128 Plugin Implementation

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

from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage, QPainter, QPen, QColor

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.async_call import async_call
from brickv.slider_spin_syncer import SliderSpinSyncer
from brickv.plugin_system.plugins.e_paper_296x128.ui_e_paper_296x128 import Ui_EPaper296x128
from brickv.bindings.bricklet_e_paper_296x128 import BrickletEPaper296x128
from brickv.callback_emulator import CallbackEmulator

WIDTH = 296
HEIGHT = 128

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
        self.image_pen_width = 2
        self.pen_width = 1
        self.image = QImage(QSize(w, h), QImage.Format_RGB32)
        self.draw_color = Qt.white

        self.setMaximumSize(w*self.image_pen_width, w*self.image_pen_width)
        self.setMinimumSize(w*self.image_pen_width, h*self.image_pen_width)

        self.last_point = QPoint()
        self.clear_image()

        self.display = 0

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

    def draw_line_to(self, end_point):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.draw_color if self.scribbling == 1 else Qt.black,
                            self.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(self.last_point/self.image_pen_width, end_point/self.image_pen_width)

        self.update()
        self.last_point = QPoint(end_point)

class EPaper296x128(COMCUPluginBase, Ui_EPaper296x128):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletEPaper296x128, *args)

        self.setupUi(self)

        self.epaper = self.device

        self.scribble_area = ScribbleArea(WIDTH, HEIGHT)
        self.image_button_layout.insertWidget(0, self.scribble_area)

        self.draw_button.clicked.connect(self.draw_clicked)
        self.send_button.clicked.connect(self.send_clicked)

        self.fill_black_button.clicked.connect(lambda: self.fill_clicked(0))
        self.fill_white_button.clicked.connect(lambda: self.fill_clicked(1))
        self.fill_red_button.clicked.connect(lambda: self.fill_clicked(2))

        self.color_radio_black.toggled.connect(self.radio_toggled)
        self.color_radio_white.toggled.connect(self.radio_toggled)
        self.color_radio_red.toggled.connect(self.radio_toggled)
        
        self.display = self.epaper.DISPLAY_BLACK_WHITE_RED

    def radio_toggled(self):
        if self.color_radio_black.isChecked():
            self.scribble_area.draw_color = Qt.black
        elif self.color_radio_white.isChecked():
            self.scribble_area.draw_color = Qt.white
        elif self.color_radio_red.isChecked():
            if self.display == self.epaper.DISPLAY_BLACK_WHITE_RED:
                self.scribble_area.draw_color = Qt.red
            else:
                self.scribble_area.draw_color = Qt.darkGray

    def fill_clicked(self, color):
        self.epaper.fill_display(color)
        self.start()

    def send_clicked(self):
        pos_x = self.posx_spinbox.value()
        pos_y = self.posy_spinbox.value()
        font  = self.font_combo.currentIndex()
        color = self.color_combo.currentIndex()
        orien = self.orientation_combo.currentIndex()
        text  = self.text_edit.text()
        
        self.epaper.draw_text(pos_x, pos_y, font, color, orien, text)
        self.start()

    def draw_clicked(self):
        bw = [False]*WIDTH*HEIGHT
        red = [False]*WIDTH*HEIGHT
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if QColor(self.scribble_area.image.pixel(j, i)) == Qt.white:
                    bw[i*WIDTH +j] = True
                if QColor(self.scribble_area.image.pixel(j, i)) in (Qt.red, Qt.darkGray):
                    red[i*WIDTH +j] = True

        self.epaper.write_black_white(0, 0, WIDTH-1, HEIGHT-1, bw)
        self.epaper.write_color(0, 0, WIDTH-1, HEIGHT-1, red)
        self.epaper.draw()

    def cb_read_bw(self, pixels):
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if pixels[i*WIDTH + j]:
                    self.scribble_area.image.setPixel(j, i, 0xFFFFFF)
                else:
                    self.scribble_area.image.setPixel(j, i, 0)

        async_call(self.epaper.read_color, (0, 0, WIDTH-1, HEIGHT-1), self.cb_read_color, self.increase_error_count)

    def cb_read_color(self, pixels):
        if pixels:
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    if pixels[i*WIDTH + j]:
                        if self.display == self.epaper.DISPLAY_BLACK_WHITE_RED:
                            self.scribble_area.image.setPixel(j, i, 0xFF0000)
                        else:
                            self.scribble_area.image.setPixel(j, i, 0x808080)

        self.scribble_area.update()
    
    def cb_get_display(self, display):
        self.display = display

        if display == 0:
            color = 'Red'
        else:
            color = 'Grey'

        self.fill_red_button.setText('Fill ' + color)
        self.color_radio_red.setText(color)
        self.color_combo.removeItem(2)
        self.color_combo.insertItem(2, color)

    def start(self):
        async_call(self.epaper.get_display, None, self.cb_get_display, self.increase_error_count)
        async_call(self.epaper.read_black_white, (0, 0, WIDTH-1, HEIGHT-1), self.cb_read_bw, self.increase_error_count)

    def stop(self):
        pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletEPaper296x128.DEVICE_IDENTIFIER
