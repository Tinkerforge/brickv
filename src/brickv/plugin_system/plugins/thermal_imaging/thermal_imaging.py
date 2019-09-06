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

import math

from PyQt5.QtCore import pyqtSignal, Qt, QSize, QPoint, QLineF
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QImage, QPainter, QPen, QColor

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.thermal_imaging.ui_thermal_imaging import Ui_ThermalImaging
from brickv.bindings.bricklet_thermal_imaging import BrickletThermalImaging
from brickv.async_call import async_call
from brickv.utils import draw_rect

from brickv.config import BRICKV_VERSION

class ThermalImageBar(QWidget):
    def __init__(self, w, h, thermal_image, main_ui, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_StaticContents)
        self.main_ui = main_ui
        self.width = w
        self.height = h
        self.thermal_image = thermal_image

        self.thermal_image.image_pixel_size_changed.connect(self.image_pixel_size_changed)

        self.image_pixel_size_changed()

    def image_pixel_size_changed(self):
        self.setFixedSize(self.width * self.thermal_image.image_pixel_size, self.height)

        self.image = QImage(QSize(self.width * self.thermal_image.image_pixel_size, self.height), QImage.Format_RGB32)

        self.update_image()

    def update_image(self):
        rgb_table = self.thermal_image.rgb_lookup[self.main_ui.color_palette_box.currentIndex()]
        painter = QPainter(self.image)

        for i in range(self.width*self.thermal_image.image_pixel_size):
            index = (256*i)//(self.width*self.thermal_image.image_pixel_size)
            color = QColor(*rgb_table[index])
            painter.fillRect(i, 0, 1, self.height, color)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(event.rect(), self.image)

class ThermalImage(QWidget):
    image_pixel_size_changed = pyqtSignal()
    agc_roi_changed = pyqtSignal(QPoint, QPoint)
    spotmeter_roi_changed = pyqtSignal(QPoint, QPoint)

    def __init__(self, w, h, main_ui, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_StaticContents)

        self.parent = parent
        self.main_ui = main_ui
        self.width = w
        self.height = h
        self.image_pixel_size = 5
        self.crosshair_width = 5
        self.image_is_16bit = False
        self.image = QImage(QSize(w, h), QImage.Format_RGB32)

        self.scale_factor_changed(5)

        self.create_rgb_lookup()
        self.clear_image()
        self.agc_roi_from = None
        self.agc_roi_to = None

        self.spotmeter_roi_from = None
        self.spotmeter_roi_to = None
        self.wait_for_minmax = 2

    def scale_factor_changed(self, factor):
        self.image_pixel_size = factor
        self.crosshair_width = factor

        self.setFixedSize(self.width * self.image_pixel_size, self.height * self.image_pixel_size)

        self.image_pixel_size_changed.emit()

    def create_rgb_lookup(self):
        self.rgb_lookup = []

        # Standard
        standard = []

        for x in range(256):
            x /= 255.0
            r = int(round(255 * math.sqrt(x)))
            g = int(round(255 * pow(x, 3)))

            if math.sin(2 * math.pi * x) >= 0:
                b = int(round(255 * math.sin(2 * math.pi * x)))
            else:
                b = 0

            standard.append((r, g, b))

        self.rgb_lookup.append(standard)

        # Greyscale
        self.rgb_lookup.append([(x, x, x) for x in range(256)])

        # Hot Cold
        self.rgb_lookup.append([(0, 0, 255)] * 32 + [(0, 0, 0)] * (256 - 2 * 32) + [(255, 0, 0)] * 32)

    def new_image(self, image, is_16bit=False):
        self.image_is_16bit = is_16bit

        table_index = self.main_ui.color_palette_box.currentIndex()

        if is_16bit:
            minimum = min(image)
            maximum = max(image)

            if self.wait_for_minmax == 0:
                self.parent.temperature_min.setText('min: ' + self.main_ui.kelvin_to_degstr(minimum) + ' °C')
                self.parent.temperature_max.setText('max: ' + self.main_ui.kelvin_to_degstr(maximum) + ' °C')
            else:
                self.wait_for_minmax -= 1

        else:
            self.parent.temperature_min.setText('')
            self.parent.temperature_max.setText('')
            self.wait_for_minmax = 2

        for i, value in enumerate(image):
            if is_16bit:
                value = ((value - minimum) * 255) // (maximum - minimum)

            r, g, b = self.rgb_lookup[table_index][value]

            self.image.setPixel(QPoint(i % 80, i // 80), (r << 16) | (g << 8) | b)

        self.update()

    def clear_image(self):
        self.image.fill(Qt.black)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.main_ui.combo_interpolation.currentIndex() == 0:
            scale_mode = Qt.SmoothTransformation
        else:
            scale_mode = Qt.FastTransformation

        painter.drawImage(event.rect(), self.image.scaledToWidth(self.width * self.image_pixel_size, scale_mode))

        if self.agc_roi_from != None and self.agc_roi_to != None and not self.image_is_16bit:
            from_x, from_y, to_x, to_y = self.agc_roi_from.x(), self.agc_roi_from.y(), self.agc_roi_to.x(), self.agc_roi_to.y()
            draw_rect(painter,
                      from_x * self.image_pixel_size + self.image_pixel_size // 2,
                      from_y * self.image_pixel_size + self.image_pixel_size // 2,
                      (to_x - from_x) * self.image_pixel_size + 1,
                      (to_y - from_y) * self.image_pixel_size + 1,
                      1,
                      Qt.green)

            self.main_ui.update_agc_roi_label()

        if self.spotmeter_roi_from != None and self.spotmeter_roi_to != None:
            pen = QPen()
            pen.setColor(Qt.white)
            pen.setWidth(1)
            painter.setPen(pen)

            from_x, from_y, to_x, to_y = self.spotmeter_roi_from.x(), self.spotmeter_roi_from.y(), self.spotmeter_roi_to.x(), self.spotmeter_roi_to.y()

            from_x = from_x * self.image_pixel_size + self.image_pixel_size // 2 + 1
            from_y = from_y * self.image_pixel_size + self.image_pixel_size // 2 + 1
            to_x = to_x * self.image_pixel_size + self.image_pixel_size // 2 - 1
            to_y = to_y * self.image_pixel_size + self.image_pixel_size // 2 - 1

            cross_x = from_x + (to_x - from_x) / 2.0
            cross_y = from_y + (to_y - from_y) / 2.0

            if to_x - from_x > self.image_pixel_size or to_y - from_y > self.image_pixel_size:
                lines = [QLineF(from_x, from_y, from_x + self.crosshair_width, from_y),
                         QLineF(from_x, from_y, from_x, from_y + self.crosshair_width),
                         QLineF(to_x, to_y, to_x, to_y - self.crosshair_width),
                         QLineF(to_x, to_y, to_x - self.crosshair_width, to_y),
                         QLineF(from_x, to_y, from_x, to_y-self.crosshair_width),
                         QLineF(from_x, to_y, from_x + self.crosshair_width, to_y),
                         QLineF(to_x, from_y, to_x, from_y+self.crosshair_width),
                         QLineF(to_x, from_y, to_x - self.crosshair_width, from_y)]
                painter.drawLines(lines)

            lines = [QLineF(cross_x - self.crosshair_width, cross_y, cross_x + self.crosshair_width, cross_y),
                     QLineF(cross_x, cross_y - self.crosshair_width, cross_x, cross_y+self.crosshair_width)]
            painter.drawLines(lines)

            self.main_ui.update_spotmeter_roi_label()

    def clip_pos(self, pos, start=None):
        pos = QPoint(pos) # make copy before modifying
        max_width = self.width - 1
        max_height = self.height - 1

        if pos.x() < 0:
            pos.setX(0)
        elif pos.x() > max_width:
            pos.setX(max_width)

        if pos.y() < 0:
            pos.setY(0)
        elif pos.y() > max_height:
            pos.setY(max_height)

        if start != None:
            if pos.x() == start.x():
                pos.setX(pos.x() + 1)
            if pos.y() == start.y():
                pos.setY(pos.y() + 1)

        return pos

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = QPoint(event.pos().x() // self.image_pixel_size, event.pos().y() // self.image_pixel_size)

            if self.main_ui.agc_roi_button.isChecked():
                self.agc_roi_from = self.clip_pos(pos)
                self.agc_roi_to = self.clip_pos(pos, self.agc_roi_from)
            elif self.main_ui.spotmeter_roi_button.isChecked():
                self.spotmeter_roi_from = self.clip_pos(pos)
                self.spotmeter_roi_to = self.clip_pos(pos, self.spotmeter_roi_from)

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton):
            pos = QPoint(event.pos().x() // self.image_pixel_size, event.pos().y() // self.image_pixel_size)

            if self.main_ui.agc_roi_button.isChecked():
                self.agc_roi_to = self.clip_pos(pos, self.agc_roi_from)
            elif self.main_ui.spotmeter_roi_button.isChecked():
                self.spotmeter_roi_to = self.clip_pos(pos, self.spotmeter_roi_from)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = QPoint(event.pos().x() // self.image_pixel_size, event.pos().y() // self.image_pixel_size)

            if self.main_ui.agc_roi_button.isChecked():
                self.agc_roi_to = self.clip_pos(pos, self.agc_roi_from)
                self.main_ui.agc_roi_button.setChecked(False)
                QApplication.restoreOverrideCursor()
                self.agc_roi_changed.emit(self.agc_roi_from, self.agc_roi_to)
            elif self.main_ui.spotmeter_roi_button.isChecked():
                self.spotmeter_roi_to = self.clip_pos(pos, self.spotmeter_roi_from)
                self.main_ui.spotmeter_roi_button.setChecked(False)
                QApplication.restoreOverrideCursor()
                self.spotmeter_roi_changed.emit(self.spotmeter_roi_from, self.spotmeter_roi_to)

    def update_agc_roi(self, p_from, p_to):
        self.agc_roi_from = p_from
        self.agc_roi_to = p_to

    def update_spotmeter_roi(self, p_from, p_to):
        self.spotmeter_roi_from = p_from
        self.spotmeter_roi_to = p_to

class WrapperWidget(QWidget):
    def __init__(self, plugin):
        super().__init__()

        self.plugin = plugin

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setMinimumSize(200, 200)
        self.layout().addStretch()

        inner_layout = QVBoxLayout()
        inner_widget = QWidget()

        label_layout = QHBoxLayout()
        label_widget = QWidget()
        self.temperature_min = QLabel("", parent=label_widget)
        self.temperature_max = QLabel("", parent=label_widget)

        self.thermal_image = ThermalImage(80, 60, self.plugin, self)
        inner_layout.addWidget(self.thermal_image)

        inner_layout.addStretch()

        label_layout.addWidget(self.temperature_min)
        label_layout.addStretch()
        label_layout.addWidget(self.temperature_max)
        label_widget.setLayout(label_layout)
        inner_layout.addWidget(label_widget)

        self.thermal_image_bar = ThermalImageBar(80, 20, self.thermal_image, self.plugin, inner_widget)
        inner_layout.addWidget(self.thermal_image_bar)

        inner_widget.setLayout(inner_layout)

        self.layout().addWidget(inner_widget)

        self.layout().addStretch()

        self.setWindowTitle('Thermal Imaging Bricklet - Thermal Image - Brick Viewer ' + BRICKV_VERSION)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        pixel_size = min(self.width() // 80, (self.height() - int(self.thermal_image_bar.height * 1.8) - int(self.temperature_min.height() * 1.8)) // 60)

        self.thermal_image.scale_factor_changed(pixel_size)

    def closeEvent(self, _event):
        self.plugin.thermal_image_wrapper = None
        self.plugin.button_detach_image.setEnabled(True)

    def minimumSizeHint(self):
        return QSize(500, 500)

    def sizeHint(self):
        return QSize(500, 500)

class ThermalImaging(COMCUPluginBase, Ui_ThermalImaging):
    qtcb_high_contrast_image = pyqtSignal(object)
    qtcb_temperature_image = pyqtSignal(object)

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletThermalImaging, *args)

        self.setupUi(self)
        self.thermal_imaging = self.device

        self.previous_image_transfer_config = None

        self.agc_roi_from = QPoint(0, 0)
        self.agc_roi_to = QPoint(79, 59)
        self.spotmeter_roi_from = QPoint(0, 0)
        self.spotmeter_roi_to = QPoint(79, 59)

        self.thermal_image = ThermalImage(80, 60, self, self)
        self.thermal_image.agc_roi_changed.connect(self.update_agc_roi)
        self.thermal_image.spotmeter_roi_changed.connect(self.update_spotmeter_roi)


        self.thermal_image_layout.insertWidget(0, self.thermal_image)
        self.thermal_image_bar = ThermalImageBar(80, 20, self.thermal_image, self, self)
        self.thermal_image_layout.insertWidget(2, self.thermal_image_bar)

        self.combo_scale_factor.currentIndexChanged.connect(
            lambda: self.thermal_image.scale_factor_changed(int(1 + 4 * float(self.combo_scale_factor.currentText()[:-1]))))

        self.agc_roi_button.clicked.connect(self.cb_roi_button)
        self.spotmeter_roi_button.clicked.connect(self.cb_roi_button)

        self.image_combo.setItemData(0, BrickletThermalImaging.IMAGE_TRANSFER_CALLBACK_HIGH_CONTRAST_IMAGE)
        self.image_combo.setItemData(1, BrickletThermalImaging.IMAGE_TRANSFER_CALLBACK_TEMPERATURE_IMAGE)

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

        self.thermal_image_wrapper = None
        self.button_detach_image.clicked.connect(self.detach_image_clicked)

        self.update_agc_roi_label()

    def detach_image_clicked(self):
        if self.thermal_image_wrapper != None:
            self.thermal_image_wrapper.close()

        self.button_detach_image.setEnabled(False)

        self.thermal_image_wrapper = WrapperWidget(self)
        # Give detached window the current ROIs
        self.thermal_image_wrapper.thermal_image.update_agc_roi(self.agc_roi_from, self.agc_roi_to)
        self.thermal_image_wrapper.thermal_image.update_spotmeter_roi(self.spotmeter_roi_from, self.spotmeter_roi_to)

        # Let wrapper update our ROIs
        self.thermal_image_wrapper.thermal_image.agc_roi_changed.connect(self.update_agc_roi)
        self.thermal_image_wrapper.thermal_image.spotmeter_roi_changed.connect(self.update_spotmeter_roi)

        # Let wrapper update the normal image ROIs
        self.thermal_image_wrapper.thermal_image.agc_roi_changed.connect(self.thermal_image.update_agc_roi)
        self.thermal_image_wrapper.thermal_image.spotmeter_roi_changed.connect(self.thermal_image.update_spotmeter_roi)

        # Let the normal image update the wrapper ROIs
        self.thermal_image.agc_roi_changed.connect(self.thermal_image_wrapper.thermal_image.update_agc_roi)
        self.thermal_image.spotmeter_roi_changed.connect(self.thermal_image_wrapper.thermal_image.update_spotmeter_roi)

        self.thermal_image_wrapper.show()

    def color_palette_changed(self):
        if self.thermal_image_wrapper is None:
            self.thermal_image_bar.update_image()
        else:
            self.thermal_image_wrapper.thermal_image_bar.update_image()

    def update_agc_roi(self, p_from, p_to):
        self.agc_roi_from = p_from
        self.agc_roi_to = p_to
        self.update_agc_data()

    def update_spotmeter_roi(self, p_from, p_to):
        self.spotmeter_roi_from = p_from
        self.spotmeter_roi_to = p_to
        self.update_spotmeter_roi_data()

    def get_agc_roi(self):
        return self.agc_roi_from.x(), self.agc_roi_from.y(), self.agc_roi_to.x(), self.agc_roi_to.y()

    def get_spotmeter_roi(self):
        return self.spotmeter_roi_from.x(), self.spotmeter_roi_from.y(), self.spotmeter_roi_to.x(), self.spotmeter_roi_to.y()

    def update_image_combo(self):
        config = self.image_combo.itemData(self.image_combo.currentIndex())

        async_call(self.thermal_imaging.set_image_transfer_config, config, None, self.increase_error_count)

        self.high_contrast_groupbox.setVisible(config == BrickletThermalImaging.IMAGE_TRANSFER_CALLBACK_HIGH_CONTRAST_IMAGE)

    def update_resolution(self):
        self.thermal_image.wait_for_minmax = 2
        if self.thermal_image_wrapper is not None:
            self.thermal_image_wrapper.thermal_image.wait_for_minmax = 2

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
            if self.thermal_image_wrapper is not None:
                self.thermal_image_wrapper.thermal_image.new_image(image)
            async_call(self.thermal_imaging.get_statistics, None, self.get_statistics_async, self.increase_error_count)

    def cb_temperature_image(self, image):
        if image != None:
            self.thermal_image.new_image(image, is_16bit=True)
            if self.thermal_image_wrapper is not None:
                self.thermal_image_wrapper.thermal_image.new_image(image, is_16bit=True)
            async_call(self.thermal_imaging.get_statistics, None, self.get_statistics_async, self.increase_error_count)

    def kelvin_to_degstr(self, value, res=None):
        if res == None:
            res = self.valid_resolution

        if res == 0:
            return "{0:.2f}".format(value / 10.0 - 273.15)
        else:
            return "{0:.2f}".format(value / 100.0 - 273.15)

    def get_statistics_async(self, statistics):
        self.valid_resolution = statistics.resolution

        spot_mean = self.kelvin_to_degstr(statistics.spotmeter_statistics[0])
        spot_max = self.kelvin_to_degstr(statistics.spotmeter_statistics[1])
        spot_min = self.kelvin_to_degstr(statistics.spotmeter_statistics[2])
        spot_pix = str(statistics.spotmeter_statistics[3])

        self.spotmeter_mean_label.setText(spot_mean)
        self.spotmeter_minimum_label.setText(spot_min)
        self.spotmeter_maximum_label.setText(spot_max)
        self.spotmeter_pixel_count_label.setText(spot_pix)

        temp_fpa = self.kelvin_to_degstr(statistics.temperatures[0], 1)
        temp_fpa_ffc = self.kelvin_to_degstr(statistics.temperatures[1], 1)
        temp_housing = self.kelvin_to_degstr(statistics.temperatures[2], 1)
        temp_housing_ffc = self.kelvin_to_degstr(statistics.temperatures[3], 1)

        self.temp_fpa_label.setText(temp_fpa)
        self.temp_fpa_ffc_label.setText(temp_fpa_ffc)
        self.temp_housing_label.setText(temp_housing)
        self.temp_housing_ffc_label.setText(temp_housing_ffc)

        sheet_green  = "QLabel { color: green; }"
        sheet_orange = "QLabel { color: orange; }"
        sheet_red    = "QLabel { color: red; }"

        if statistics.ffc_status == 0b00:
            self.ffc_state_label.setStyleSheet(sheet_orange)
            self.ffc_state_label.setText('Never Commanded')
        elif statistics.ffc_status == 0b01:
            self.ffc_state_label.setStyleSheet(sheet_orange)
            self.ffc_state_label.setText('Imminent')
        elif statistics.ffc_status == 0b10:
            self.ffc_state_label.setStyleSheet(sheet_orange)
            self.ffc_state_label.setText('In Progress')
        elif statistics.ffc_status == 0b11:
            self.ffc_state_label.setStyleSheet(sheet_green)
            self.ffc_state_label.setText('Complete')

        if statistics.temperature_warning[0]:
            self.shutter_lockout_label.setStyleSheet(sheet_red)
            self.shutter_lockout_label.setText('Yes')
        else:
            self.shutter_lockout_label.setStyleSheet(sheet_green)
            self.shutter_lockout_label.setText('No')

        if statistics.temperature_warning[1]:
            self.overtemp_label.setStyleSheet(sheet_red)
            self.overtemp_label.setText('Yes')
        else:
            self.overtemp_label.setStyleSheet(sheet_green)
            self.overtemp_label.setText('No')

    def get_image_transfer_config_async(self, config):
        self.previous_image_transfer_config = config

        self.update_image_combo()

    def get_high_contrast_config_async(self, config):
        self.agc_roi_from = QPoint(config.region_of_interest[0], config.region_of_interest[1])
        self.agc_roi_to   = QPoint(config.region_of_interest[2], config.region_of_interest[3])

        self.thermal_image.agc_roi_from = self.agc_roi_from
        self.thermal_image.agc_roi_to   = self.agc_roi_to

        if self.thermal_image_wrapper is not None:
            self.thermal_image_wrapper.thermal_image.agc_roi_from = self.agc_roi_from
            self.thermal_image_wrapper.thermal_image.agc_roi_to   = self.agc_roi_to

        self.agc_clip_limit_high_spin.setValue(config.clip_limit[0])
        self.agc_clip_limit_low_spin.setValue(config.clip_limit[1])
        self.agc_dampening_factor_spin.setValue(config.dampening_factor)
        self.agc_empty_counts_spin.setValue(config.empty_counts)

    def get_spotmeter_config_async(self, config):
        self.spotmeter_roi_from = QPoint(config[0], config[1])
        self.spotmeter_roi_to   = QPoint(config[2], config[3])

        self.thermal_image.spotmeter_roi_from = self.spotmeter_roi_from
        self.thermal_image.spotmeter_roi_to   = self.spotmeter_roi_to

        if self.thermal_image_wrapper is not None:
            self.thermal_image_wrapper.thermal_image.spotmeter_roi_from = self.spotmeter_roi_from
            self.thermal_image_wrapper.thermal_image.spotmeter_roi_to   = self.spotmeter_roi_to

    def get_resolution_async(self, resolution):
        self.resolution_box.setCurrentIndex(resolution)

    def start(self):
        self.previous_image_transfer_config = None

        async_call(self.thermal_imaging.get_image_transfer_config, None, self.get_image_transfer_config_async, self.increase_error_count)
        async_call(self.thermal_imaging.get_high_contrast_config, None, self.get_high_contrast_config_async, self.increase_error_count)
        async_call(self.thermal_imaging.get_spotmeter_config, None, self.get_spotmeter_config_async, self.increase_error_count)
        async_call(self.thermal_imaging.get_resolution, None, self.get_resolution_async, self.increase_error_count)

        self.thermal_imaging.register_callback(self.thermal_imaging.CALLBACK_HIGH_CONTRAST_IMAGE, self.qtcb_high_contrast_image.emit)
        self.thermal_imaging.register_callback(self.thermal_imaging.CALLBACK_TEMPERATURE_IMAGE, self.qtcb_temperature_image.emit)

    def stop(self):
        if self.thermal_image_wrapper is not None:
            return

        if self.previous_image_transfer_config != None:
            async_call(self.thermal_imaging.set_image_transfer_config, self.previous_image_transfer_config, None, self.increase_error_count)

        self.thermal_imaging.register_callback(self.thermal_imaging.CALLBACK_HIGH_CONTRAST_IMAGE, None)
        self.thermal_imaging.register_callback(self.thermal_imaging.CALLBACK_TEMPERATURE_IMAGE, None)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletThermalImaging.DEVICE_IDENTIFIER
