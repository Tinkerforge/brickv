# -*- coding: utf-8 -*-
"""
Thermal Imaging Plugin
Copyright (C) 2017 Olaf Lüke <olaf@tinkerforge.com>

thermal_imaging.py: Thermal Imaging Plugin Implementation

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
import math

from PyQt5.QtCore import pyqtSignal, Qt, QSize, QPoint, QLineF
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QImage, QPainter, QPen, QColor

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.thermal_imaging.ui_thermal_imaging import Ui_ThermalImaging
from brickv.bindings.bricklet_thermal_imaging import BrickletThermalImaging
from brickv.callback_emulator import CallbackEmulator
from brickv.async_call import async_call

class ThermalImageBar(QWidget):
    def __init__(self, w, h, thermal_image, parent=None):
        super(ThermalImageBar, self).__init__(parent)

        self.setAttribute(Qt.WA_StaticContents)
        self.parent = parent
        self.width = w
        self.height = h
        self.thermal_image = thermal_image

        self.setMaximumSize(w*thermal_image.image_pixel_width, h)
        self.setMinimumSize(w*thermal_image.image_pixel_width, h)

        self.image = QImage(QSize(w*thermal_image.image_pixel_width, h), QImage.Format_RGB32)
        self.update_image()

    def update_image(self):
        rgb_table = self.thermal_image.rgb_lookup[self.parent.color_palette_box.currentIndex()]
        painter = QPainter(self.image)
        for i in range(self.width*self.thermal_image.image_pixel_width):
            index = (256*i)//(self.width*self.thermal_image.image_pixel_width)
            color = QColor(*rgb_table[index])
            painter.fillRect(i, 0, 1, self.height, color)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(event.rect(), self.image)

class ThermalImage(QWidget):
    def __init__(self, w, h, parent=None):
        super(ThermalImage, self).__init__(parent)

        self.setAttribute(Qt.WA_StaticContents)

        self.parent = parent
        self.width = w
        self.height = h
        self.image_pixel_width = 5
        self.image_is_16bit = False
        self.crosshair_width = 5
        self.image = QImage(QSize(w, h), QImage.Format_RGB32)

        self.setMaximumSize(w*self.image_pixel_width, h*self.image_pixel_width)
        self.setMinimumSize(w*self.image_pixel_width, h*self.image_pixel_width)

        self.create_rgb_lookup()
        self.clear_image()
        self.agc_roi_from = None
        self.agc_roi_to = None

        self.spotmeter_roi_from = None
        self.spotmeter_roi_to = None
        self.wait_for_minmax = 2

    def create_rgb_lookup(self):
        self.rgb_lookup = []

        # Standard
        standard = []
        for x in range(256):
            x /= 255.0
            r = int(round(255*math.sqrt(x)))
            g = int(round(255*pow(x,3)))
            if math.sin(2 * math.pi * x) >= 0:
                b = int(round(255*math.sin(2 * math.pi * x)))
            else:
                b = 0
            standard.append((r, g, b))

        self.rgb_lookup.append(standard)

        # Greyscale
        self.rgb_lookup.append([(x, x, x) for x in range(256)])

        # Hot Cold
        self.rgb_lookup.append([(0, 0, 255)]*32 + [(0,0,0)]*(256-2*32) + [(255,0,0)]*32)


    def new_image(self, image, is_16bit=False):
        self.image_is_16bit = is_16bit

        table_index = self.parent.color_palette_box.currentIndex()

        if is_16bit:
            minimum = min(image)
            maximum = max(image)

            if self.wait_for_minmax == 0:
                self.parent.temperature_min.setText('min: ' + self.parent.kelvin_to_degstr(minimum) + ' °C')
                self.parent.temperature_max.setText('max: ' + self.parent.kelvin_to_degstr(maximum) + ' °C')
            else:
                self.wait_for_minmax -= 1

        else:
            self.parent.temperature_min.setText('')
            self.parent.temperature_max.setText('')
            self.wait_for_minmax = 2

        for i, value in enumerate(image):
            if is_16bit:
                value = ((value-minimum)*255)//(maximum-minimum)
            r, g, b = self.rgb_lookup[table_index][value]

            self.image.setPixel(QPoint(i%80, i//80), (r << 16) | (g << 8) | b)

        self.update()

    def clear_image(self):
        self.image.fill(Qt.black)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(event.rect(), self.image.scaledToWidth(self.width*self.image_pixel_width, Qt.SmoothTransformation))

        if self.agc_roi_from != None and self.agc_roi_to != None and not self.image_is_16bit:
            pen = QPen()
            pen.setColor(Qt.green)
            pen.setWidth(1)
            painter.setPen(pen)

            roi = self.parent.get_agc_roi()
            painter.drawRect(roi[0]*self.image_pixel_width + 1,
                             roi[1]*self.image_pixel_width + 1,
                             (roi[2] - roi[0])*self.image_pixel_width + 1,
                             (roi[3] - roi[1])*self.image_pixel_width + 1)

            self.parent.update_agc_roi_label()

        if self.spotmeter_roi_from != None and self.spotmeter_roi_to != None:
            pen = QPen()
            pen.setColor(Qt.white)
            pen.setWidth(1)
            painter.setPen(pen)

            from_x, from_y, to_x, to_y = self.parent.get_spotmeter_roi()

            from_x = from_x*self.image_pixel_width+1
            from_y = from_y*self.image_pixel_width+1
            to_x = to_x*self.image_pixel_width+1
            to_y = to_y*self.image_pixel_width+1

            cross_x = from_x + (to_x-from_x)/2.0
            cross_y = from_y + (to_y-from_y)/2.0

            if to_x-from_x > 5 or to_y - from_y > 5:
                lines = [QLineF(from_x, from_y, from_x+self.crosshair_width, from_y),
                         QLineF(from_x, from_y, from_x, from_y+self.crosshair_width),
                         QLineF(to_x, to_y, to_x, to_y-self.crosshair_width),
                         QLineF(to_x, to_y, to_x-self.crosshair_width, to_y),
                         QLineF(from_x, to_y, from_x, to_y-self.crosshair_width),
                         QLineF(from_x, to_y, from_x+self.crosshair_width, to_y),
                         QLineF(to_x, from_y, to_x, from_y+self.crosshair_width),
                         QLineF(to_x, from_y, to_x-self.crosshair_width, from_y)]
                painter.drawLines(lines)

            lines = [QLineF(cross_x-self.crosshair_width, cross_y, cross_x+self.crosshair_width, cross_y),
                     QLineF(cross_x, cross_y-self.crosshair_width, cross_x, cross_y+self.crosshair_width)]
            painter.drawLines(lines)

            self.parent.update_spotmeter_roi_label()

    def clip_pos(self, pos, start = None):
        max_width  = self.width *self.image_pixel_width-1
        max_height = self.height*self.image_pixel_width-1
        if pos.x() < 0:
            pos.setX(0)
        if pos.x() > max_width:
            pos.setX(max_width)

        if pos.y() < 0:
            pos.setY(0)
        if pos.y() > max_height:
            pos.setY(max_height)

        if start != None:
            if pos.x()//5 == start.x()//5:
                pos.setX(pos.x()+self.image_pixel_width)
            if pos.y()//5 == start.y()//5:
                pos.setY(pos.y()+self.image_pixel_width)

        return pos

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.parent.agc_roi_button.isChecked():
                self.agc_roi_from = self.clip_pos(event.pos())
                self.agc_roi_to = self.clip_pos(event.pos(), self.agc_roi_from)
            elif self.parent.spotmeter_roi_button.isChecked():
                self.spotmeter_roi_from = self.clip_pos(event.pos())
                self.spotmeter_roi_to = self.clip_pos(event.pos(), self.spotmeter_roi_from)

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton):
            if self.parent.agc_roi_button.isChecked():
                self.agc_roi_to = self.clip_pos(event.pos(), self.agc_roi_from)
            elif self.parent.spotmeter_roi_button.isChecked():
                self.spotmeter_roi_to = self.clip_pos(event.pos(), self.spotmeter_roi_from)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.parent.agc_roi_button.isChecked():
                self.agc_roi_to = self.clip_pos(event.pos(), self.agc_roi_from)
                self.parent.agc_roi_button.setChecked(False)
                QApplication.restoreOverrideCursor()
                self.parent.update_agc_data()
            elif self.parent.spotmeter_roi_button.isChecked():
                self.spotmeter_roi_to = self.clip_pos(event.pos(), self.spotmeter_roi_from)
                self.parent.spotmeter_roi_button.setChecked(False)
                QApplication.restoreOverrideCursor()
                self.parent.update_spotmeter_roi_data()

class ThermalImaging(COMCUPluginBase, Ui_ThermalImaging):
    qtcb_high_contrast_image = pyqtSignal(object)
    qtcb_temperature_image = pyqtSignal(object)

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletThermalImaging, *args)

        self.setupUi(self)
        self.thermal_imaging = self.device

        self.thermal_image = ThermalImage(80, 60, self)
        self.thermal_image_layout.insertWidget(0, self.thermal_image)
        self.thermal_image_bar = ThermalImageBar(80, 20, self.thermal_image, self)
        self.thermal_image_layout.insertWidget(2, self.thermal_image_bar)

        self.agc_roi_button.clicked.connect(self.cb_roi_button)
        self.spotmeter_roi_button.clicked.connect(self.cb_roi_button)

        self.agc_clip_limit_high_spin.editingFinished.connect(self.update_agc_data)
        self.agc_clip_limit_low_spin.editingFinished.connect(self.update_agc_data)
        self.agc_dampening_factor_spin.editingFinished.connect(self.update_agc_data)
        self.agc_empty_counts_spin.editingFinished.connect(self.update_agc_data)
        self.color_palette_box.currentIndexChanged.connect(self.color_palette_changed)
        self.resolution_box.currentIndexChanged.connect(self.update_resolution)
        self.image_combo.currentIndexChanged.connect(self.update_image_combo)

        self.qtcb_high_contrast_image.connect(self.cb_high_contrast_image)
        self.qtcb_temperature_image.connect(self.cb_temperature_image)
        self.valid_resolution = self.resolution_box.currentIndex()

        self.update_agc_roi_label()

    def color_palette_changed(self):
        self.thermal_image_bar.update_image()

    def get_agc_roi(self):
        if self.thermal_image.agc_roi_from != None and self.thermal_image.agc_roi_to != None:
            from_x = self.thermal_image.agc_roi_from.x()//self.thermal_image.image_pixel_width
            from_y = self.thermal_image.agc_roi_from.y()//self.thermal_image.image_pixel_width
            to_x   = self.thermal_image.agc_roi_to.x()//self.thermal_image.image_pixel_width
            to_y   = self.thermal_image.agc_roi_to.y()//self.thermal_image.image_pixel_width
        else:
            from_x = 0
            from_y = 0
            to_x   = 79
            to_y   = 59

        if from_x > to_x:
            from_x, to_x = to_x, from_x

        if from_y > to_y:
            from_y, to_y = to_y, from_y

        return from_x, from_y, to_x, to_y

    def get_spotmeter_roi(self):
        if self.thermal_image.spotmeter_roi_from != None and self.thermal_image.spotmeter_roi_to != None:
            from_x = self.thermal_image.spotmeter_roi_from.x()//self.thermal_image.image_pixel_width
            from_y = self.thermal_image.spotmeter_roi_from.y()//self.thermal_image.image_pixel_width
            to_x   = self.thermal_image.spotmeter_roi_to.x()//self.thermal_image.image_pixel_width
            to_y   = self.thermal_image.spotmeter_roi_to.y()//self.thermal_image.image_pixel_width
        else:
            from_x = 0
            from_y = 0
            to_x   = 79
            to_y   = 59

        if from_x > to_x:
            from_x, to_x = to_x, from_x

        if from_y > to_y:
            from_y, to_y = to_y, from_y

        return from_x, from_y, to_x, to_y

    def update_image_combo(self):
        if self.image_combo.currentIndex() == 0:
            async_call(self.thermal_imaging.set_image_transfer_config, BrickletThermalImaging.IMAGE_TRANSFER_CALLBACK_HIGH_CONTRAST_IMAGE, None, self.increase_error_count)
            self.high_contrast_groupbox.show()
        else:
            self.high_contrast_groupbox.hide()
            async_call(self.thermal_imaging.set_image_transfer_config, BrickletThermalImaging.IMAGE_TRANSFER_CALLBACK_TEMPERATURE_IMAGE, None, self.increase_error_count)

    def update_resolution(self):
        self.thermal_image.wait_for_minmax = 2
        self.thermal_imaging.set_resolution(self.resolution_box.currentIndex())

    def update_agc_data(self):
        roi = self.get_agc_roi()
        dampening_factor = self.agc_dampening_factor_spin.value()
        clip_limit = (self.agc_clip_limit_high_spin.value(), self.agc_clip_limit_low_spin.value())
        empty_counts = self.agc_empty_counts_spin.value()
        async_call(self.thermal_imaging.set_high_contrast_config, (roi, dampening_factor, clip_limit, empty_counts), None, self.increase_error_count)

    def update_spotmeter_roi_data(self):
        roi = self.get_spotmeter_roi()
        async_call(self.thermal_imaging.set_spotmeter_config, (roi,), None, self.increase_error_count)

    def update_agc_roi_label(self):
        from_x, from_y, to_x, to_y = self.get_agc_roi()
        self.agc_roi_label.setText('from <b>[{0}, {1}]</b> to <b>[{2}, {3}]</b>'.format(from_x, from_y, to_x, to_y))

    def update_spotmeter_roi_label(self):
        from_x, from_y, to_x, to_y = self.get_spotmeter_roi()
        self.spotmeter_roi_label.setText('from <b>[{0}, {1}]</b> to <b>[{2}, {3}]</b>'.format(from_x, from_y, to_x, to_y))

    def cb_roi_button(self):
        if self.agc_roi_button.isChecked() or self.spotmeter_roi_button.isChecked():
            QApplication.setOverrideCursor(Qt.CrossCursor)
        else:
            QApplication.restoreOverrideCursor()

    def cb_high_contrast_image(self, image):
        if image != None:
            self.thermal_image.new_image(image)
            async_call(self.thermal_imaging.get_statistics, None, self.cb_statistics, self.increase_error_count)

    def cb_temperature_image(self, image):
        if image != None:
            self.thermal_image.new_image(image, is_16bit=True)
            async_call(self.thermal_imaging.get_statistics, None, self.cb_statistics, self.increase_error_count)

    def kelvin_to_degstr(self, value, res = None):
        if res == None:
            res = self.valid_resolution
        if res == 0:
            return "{0:.2f}".format(value/10.0 - 273.15)
        else:
            return "{0:.2f}".format(value/100.0 - 273.15)

    def cb_statistics(self, data):
        self.valid_resolution = data.resolution
        spot_mean = self.kelvin_to_degstr(data.spotmeter_statistics[0])
        spot_max = self.kelvin_to_degstr(data.spotmeter_statistics[1])
        spot_min = self.kelvin_to_degstr(data.spotmeter_statistics[2])
        spot_pix = str(data.spotmeter_statistics[3])
        self.spotmeter_mean_label.setText(spot_mean)
        self.spotmeter_minimum_label.setText(spot_min)
        self.spotmeter_maximum_label.setText(spot_max)
        self.spotmeter_pixel_count_label.setText(spot_pix)

        temp_fpa = self.kelvin_to_degstr(data.temperatures[0], 1)
        temp_fpa_ffc = self.kelvin_to_degstr(data.temperatures[1], 1)
        temp_housing = self.kelvin_to_degstr(data.temperatures[2], 1)
        temp_housing_ffc = self.kelvin_to_degstr(data.temperatures[3], 1)
        self.temp_fpa_label.setText(temp_fpa)
        self.temp_fpa_ffc_label.setText(temp_fpa_ffc)
        self.temp_housing_label.setText(temp_housing)
        self.temp_housing_ffc_label.setText(temp_housing_ffc)

        sheet_green  = "QLabel { color: green; }"
        sheet_orange = "QLabel { color: orange; }"
        sheet_red    = "QLabel { color: red; }"

        if data.ffc_status == 0b00:
            self.ffc_state_label.setStyleSheet(sheet_orange)
            self.ffc_state_label.setText('Never Commanded')
        elif data.ffc_status == 0b01:
            self.ffc_state_label.setStyleSheet(sheet_orange)
            self.ffc_state_label.setText('Imminent')
        elif data.ffc_status == 0b10:
            self.ffc_state_label.setStyleSheet(sheet_orange)
            self.ffc_state_label.setText('In Progress')
        elif data.ffc_status == 0b11:
            self.ffc_state_label.setStyleSheet(sheet_green)
            self.ffc_state_label.setText('Complete')

        if data.temperature_warning[0]:
            self.shutter_lockout_label.setStyleSheet(sheet_red)
            self.shutter_lockout_label.setText('Yes')
        else:
            self.shutter_lockout_label.setStyleSheet(sheet_green)
            self.shutter_lockout_label.setText('No')

        if data.temperature_warning[1]:
            self.overtemp_label.setStyleSheet(sheet_red)
            self.overtemp_label.setText('Yes')
        else:
            self.overtemp_label.setStyleSheet(sheet_green)
            self.overtemp_label.setText('No')

    def cb_get_high_contrast_config(self, data):
        self.thermal_image.agc_roi_from = QPoint(data.region_of_interest[0]*self.thermal_image.image_pixel_width,data.region_of_interest[1]*self.thermal_image.image_pixel_width)
        self.thermal_image.agc_roi_to   = QPoint(data.region_of_interest[2]*self.thermal_image.image_pixel_width,data.region_of_interest[3]*self.thermal_image.image_pixel_width)
        self.agc_clip_limit_high_spin.setValue(data.clip_limit[0])
        self.agc_clip_limit_low_spin.setValue(data.clip_limit[1])
        self.agc_dampening_factor_spin.setValue(data.dampening_factor)
        self.agc_empty_counts_spin.setValue(data.empty_counts)

    def cb_get_spotmeter_config(self, data):
        self.thermal_image.spotmeter_roi_from = QPoint(data[0]*self.thermal_image.image_pixel_width,data[1]*self.thermal_image.image_pixel_width)
        self.thermal_image.spotmeter_roi_to   = QPoint(data[2]*self.thermal_image.image_pixel_width,data[3]*self.thermal_image.image_pixel_width)

    def cb_get_resolution(self, data):
        self.resolution_box.setCurrentIndex(data)

    def start(self):
        async_call(self.thermal_imaging.get_high_contrast_config, None, self.cb_get_high_contrast_config, self.increase_error_count)
        async_call(self.thermal_imaging.get_spotmeter_config, None, self.cb_get_spotmeter_config, self.increase_error_count)
        async_call(self.thermal_imaging.get_resolution, None, self.cb_get_resolution, self.increase_error_count)
        self.thermal_imaging.set_image_transfer_config(BrickletThermalImaging.IMAGE_TRANSFER_CALLBACK_HIGH_CONTRAST_IMAGE)
        self.thermal_imaging.register_callback(self.thermal_imaging.CALLBACK_HIGH_CONTRAST_IMAGE, self.qtcb_high_contrast_image.emit)
        self.thermal_imaging.register_callback(self.thermal_imaging.CALLBACK_TEMPERATURE_IMAGE, self.qtcb_temperature_image.emit)

    def stop(self):
        self.thermal_imaging.register_callback(self.thermal_imaging.CALLBACK_HIGH_CONTRAST_IMAGE, None)
        self.thermal_imaging.register_callback(self.thermal_imaging.CALLBACK_TEMPERATURE_IMAGE, None)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletThermalImaging.DEVICE_IDENTIFIER
