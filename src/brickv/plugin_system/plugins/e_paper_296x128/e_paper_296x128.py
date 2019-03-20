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

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.async_call import async_call
from brickv.plugin_system.plugins.e_paper_296x128.ui_e_paper_296x128 import Ui_EPaper296x128
from brickv.bindings.bricklet_e_paper_296x128 import BrickletEPaper296x128
from brickv.scribblewidget import ScribbleWidget

WIDTH = 296
HEIGHT = 128

class EPaper296x128(COMCUPluginBase, Ui_EPaper296x128):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletEPaper296x128, *args)

        self.setupUi(self)

        self.epaper = self.device

        self.scribble_widget = ScribbleWidget(WIDTH, HEIGHT, 2, QColor(Qt.white), QColor(Qt.black), enable_grid=False)
        self.image_button_layout.insertWidget(0, self.scribble_widget)

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
            self.scribble_widget.set_foreground_color(QColor(Qt.black))
        elif self.color_radio_white.isChecked():
            self.scribble_widget.set_foreground_color(QColor(Qt.white))
        elif self.color_radio_red.isChecked():
            if self.display == self.epaper.DISPLAY_BLACK_WHITE_RED:
                self.scribble_widget.set_foreground_color(QColor(Qt.red))
            else:
                self.scribble_widget.set_foreground_color(QColor(Qt.darkGray))

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
                if QColor(self.scribble_widget.image().pixel(j, i)) == Qt.white:
                    bw[i * WIDTH + j] = True

                if QColor(self.scribble_widget.image().pixel(j, i)) in (Qt.red, Qt.darkGray):
                    red[i * WIDTH + j] = True

        self.epaper.write_black_white(0, 0, WIDTH-1, HEIGHT-1, bw)
        self.epaper.write_color(0, 0, WIDTH-1, HEIGHT-1, red)
        self.epaper.draw()

    def cb_read_bw(self, pixels):
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if pixels[i*WIDTH + j]:
                    self.scribble_widget.image().setPixel(j, i, 0xFFFFFF)
                else:
                    self.scribble_widget.image().setPixel(j, i, 0)

        async_call(self.epaper.read_color, (0, 0, WIDTH - 1, HEIGHT - 1), self.cb_read_color, self.increase_error_count)

    def cb_read_color(self, pixels):
        if pixels:
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    if pixels[i * WIDTH + j]:
                        if self.display == self.epaper.DISPLAY_BLACK_WHITE_RED:
                            self.scribble_widget.image().setPixel(j, i, 0xFF0000)
                        else:
                            self.scribble_widget.image().setPixel(j, i, 0x808080)

        self.scribble_widget.update()

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
        async_call(self.epaper.read_black_white, (0, 0, WIDTH - 1, HEIGHT - 1), self.cb_read_bw, self.increase_error_count)

    def stop(self):
        pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletEPaper296x128.DEVICE_IDENTIFIER
