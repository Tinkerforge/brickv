# -*- coding: utf-8 -*-
"""
Compass Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

compass.py: Compass Plugin Implementation

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

from PyQt5.QtCore import Qt, pyqtProperty, pyqtSignal, pyqtSlot, QPoint, QSize
from PyQt5.QtGui import QPainter, QFont, QFontMetricsF, QPalette, QPolygon, QPen
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QFrame, QPushButton, QDialog, QWidget

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_compass import BrickletCompass
from brickv.plot_widget import PlotWidget, CurveValueWrapper, FixedSizeLabel
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.plugin_system.plugins.compass.ui_calibration import Ui_Calibration
from brickv.utils import get_modeless_dialog_flags

class CompassWidget(QWidget):
    angle_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._angle = 0.0
        self._margins = 10
        self._point_text = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S", 225: "SW", 270: "W", 315: "NW"}

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self.draw_markings(painter)
        self.draw_needle(painter)

        painter.end()

    def draw_markings(self, painter):
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        scale = min((self.width() - self._margins)/120.0, (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)

        font = QFont(self.font())
        font.setPixelSize(12)
        metrics = QFontMetricsF(font)

        painter.setFont(font)
        painter.setPen(self.palette().color(QPalette.WindowText))

        i = 0
        while i < 360:
            if i % 45 == 0:
                painter.drawLine(0, -40, 0, -50)
                painter.drawText(int(-metrics.width(self._point_text[i])/2.0), -52, self._point_text[i])
            else:
                painter.drawLine(0, -45, 0, -50)

            painter.rotate(15)
            i += 15

        painter.restore()

    def draw_needle(self, painter):
        painter.save()
        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(self._angle)
        scale = min((self.width() - self._margins)/120.0, (self.height() - self._margins)/120.0)
        painter.scale(scale, scale)

        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(self.palette().brush(QPalette.WindowText))

        painter.drawPolygon(QPolygon([QPoint(-10, 0), QPoint(0, -45), QPoint(10, 0), QPoint(0, 45), QPoint(-10, 0)]))

        painter.setBrush(Qt.red)

        painter.drawPolygon(QPolygon([QPoint(-5, -25), QPoint(0, -45), QPoint(5, -25), QPoint(0, -30), QPoint(-5, -25)]))

        painter.restore()

    def sizeHint(self):
        return QSize(100, 100)

    def angle(self):
        return self._angle

    @pyqtSlot(float)
    def set_angle(self, angle):
        if angle != self._angle:
            self._angle = angle
            self.angle_changed.emit(angle)
            self.update()

    angle = pyqtProperty(float, angle, set_angle)

class Calibration(QDialog, Ui_Calibration):
    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())
        self.parent = parent

        self.setupUi(self)

        self.cbe_mfd = CallbackEmulator(self,
                                        self.parent.compass.get_magnetic_flux_density,
                                        None,
                                        self.cb_mfd,
                                        self.parent.increase_error_count)

        self.x = [0, 0, 0]
        self.y = [0, 0, 0]
        self.z = [0, 0, 0]

        self.button_calibration_remove.clicked.connect(self.calibration_remove_clicked)
        self.button_calibration_save.clicked.connect(self.calibration_save_clicked)

        self.button_calibration_save.setEnabled(False)

        self.button_close.clicked.connect(self.close)

    def show(self):
        QDialog.show(self)

        self.x = [0, 0, 0]
        self.y = [0, 0, 0]
        self.z = [0, 0, 0]

        self.cbe_mfd.set_period(20)

    def calibration_remove_clicked(self):
        self.button_calibration_remove.setEnabled(False)
        self.button_calibration_save.setEnabled(True)

        offset = [0]*3
        gain = [10000]*3
        self.parent.compass.set_calibration(offset, gain)

        self.x = [0, 0, 0]
        self.y = [0, 0, 0]
        self.z = [0, 0, 0]
        self.cbe_mfd.set_period(20)

    def calibration_save_clicked(self):
        self.button_calibration_save.setEnabled(False)
        self.button_calibration_remove.setEnabled(True)

        self.cbe_mfd.set_period(0)

        offset = [0]*3
        gain = [10000]*3

        offset[0] = int(round((self.x[1] + self.x[2])/2, 0))
        offset[1] = int(round((self.y[1] + self.y[2])/2, 0))
        offset[2] = int(round((self.z[1] + self.z[2])/2, 0))

        gain[0] = 10000
        gain[1] = int(round(10000*(abs(self.x[1]) + abs(self.x[2]))/(abs(self.y[1]) + abs(self.y[2])), 0))
        gain[2] = int(round(10000*(abs(self.x[1]) + abs(self.x[2]))/(abs(self.z[1]) + abs(self.z[2])), 0))

        self.parent.compass.set_calibration(offset, gain)
        self.close()

    def update_labels(self):
        self.x[1] = min(self.x[0], self.x[1])
        self.x[2] = max(self.x[0], self.x[2])
        self.y[1] = min(self.y[0], self.y[1])
        self.y[2] = max(self.y[0], self.y[2])
        self.z[1] = min(self.z[0], self.z[1])
        self.z[2] = max(self.z[0], self.z[2])

        self.label_x_cur.setText('{0}'.format(self.x[0]))
        self.label_y_cur.setText('{0}'.format(self.y[0]))
        self.label_z_cur.setText('{0}'.format(self.z[0]))

        self.label_x_min.setText('{0}'.format(self.x[1]))
        self.label_y_min.setText('{0}'.format(self.y[1]))
        self.label_z_min.setText('{0}'.format(self.z[1]))

        self.label_x_max.setText('{0}'.format(self.x[2]))
        self.label_y_max.setText('{0}'.format(self.y[2]))
        self.label_z_max.setText('{0}'.format(self.z[2]))

    def cb_mfd(self, data):
        x, y, z = data

        self.x[0] = x
        self.y[0] = y
        self.z[0] = z

        self.update_labels()

    def closeEvent(self, event):
        self.parent.button_calibration.setEnabled(True)
        self.cbe_mfd.set_period(0)

class HeadingLabel(FixedSizeLabel):
    def setText(self, heading):
        text = 'Heading: {}°'.format(heading)
        super().setText(text)

class InclinationLabel(FixedSizeLabel):
    def setText(self, inclination):
        text = 'Inclination: {}°'.format(inclination)
        super().setText(text)

class Compass(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletCompass, *args)

        self.compass = self.device

        self.cbe_mfd = CallbackEmulator(self,
                                        self.compass.get_magnetic_flux_density,
                                        None,
                                        self.cb_mfd,
                                        self.increase_error_count)

        self.calibration = None

        self.compass_widget = CompassWidget()

        self.current_mfd_x = CurveValueWrapper() # int, µT
        self.current_mfd_y = CurveValueWrapper() # int, µT
        self.current_mfd_z = CurveValueWrapper() # int, µT

        self.heading_label = HeadingLabel()
        self.inclination_label = InclinationLabel()

        self.label_widget = QWidget()
        self.label_layout = QVBoxLayout()
        self.label_layout.addWidget(self.heading_label)
        self.label_layout.addWidget(self.inclination_label)
        self.label_widget.setLayout(self.label_layout)

        plots = [('X', Qt.red, self.current_mfd_x, '{0} µT'.format),
                 ('Y', Qt.darkGreen, self.current_mfd_y, '{0} µT'.format),
                 ('Z', Qt.blue, self.current_mfd_z, '{0} µT'.format)]
        self.plot_widget = PlotWidget('Magnetic Flux Density [µT]', plots, extra_key_widgets=[self.compass_widget, self.label_widget],
                                      update_interval=0.1, y_resolution=1)

        self.dr_label = QLabel('Data Rate:')
        self.dr_combo = QComboBox()
        self.dr_combo.addItem("100 Hz")
        self.dr_combo.addItem("200 Hz")
        self.dr_combo.addItem("400 Hz")
        self.dr_combo.addItem("600 Hz")

        self.dr_combo.currentIndexChanged.connect(self.new_config)

        self.button_calibration = QPushButton('Calibrate')
        self.button_calibration.clicked.connect(self.calibration_clicked)

        hlayout = QHBoxLayout()
        hlayout.addStretch()
        hlayout.addWidget(self.dr_label)
        hlayout.addWidget(self.dr_combo)
        hlayout.addStretch()
        hlayout.addWidget(self.button_calibration)
        hlayout.addStretch()

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

    def calibration_clicked(self):
        if self.calibration == None:
            self.calibration = Calibration(self)

        self.button_calibration.setEnabled(False)
        self.calibration.show()

    def new_config(self):
        dr = self.dr_combo.currentIndex()
        self.compass.set_configuration(dr, True)

    def cb_mfd(self, data):
        x, y, z = data
        inclination = round(180/math.pi * math.atan2(z, math.hypot(y, x)))
        heading = math.atan2(y, x)*180/math.pi

        if heading < 0:
            heading += 360

        self.current_mfd_x.value = round(x / 100.0)
        self.current_mfd_y.value = round(y / 100.0)
        self.current_mfd_z.value = round(z / 100.0)
        self.heading_label.setText(round(heading))
        self.compass_widget.set_angle(heading)
        self.inclination_label.setText(inclination)

    def get_configuration_async(self, conf):
        self.dr_combo.setCurrentIndex(conf.data_rate)

    def start(self):
        async_call(self.compass.get_configuration, None, self.get_configuration_async, self.increase_error_count)
        self.cbe_mfd.set_period(50)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_mfd.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletCompass.DEVICE_IDENTIFIER
