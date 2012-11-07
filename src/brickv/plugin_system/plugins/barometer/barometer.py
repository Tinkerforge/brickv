# -*- coding: utf-8 -*-
"""
Barometer Plugin
Copyright (C) 2012 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>

barometer.py: Barometer Plugin Implementation

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

from plugin_system.plugin_base import PluginBase
from bindings import ip_connection
from plot_widget import PlotWidget

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QLineEdit
from PyQt4.QtCore import pyqtSignal, Qt, QTimer

from bindings import bricklet_barometer

class AirPressureLabel(QLabel):
    def setText(self, text):
        text = "Air Pressure: " + text + " mbar"
        super(AirPressureLabel, self).setText(text)

class AltitudeLabel(QLabel):
    def setText(self, text1, text2):
        text = "Altitude: " + text1 + " m (" + text2 + " ft)"
        super(AltitudeLabel, self).setText(text)

class ChipTemperatureLabel(QLabel):
    def setText(self, text):
        text = "Chip Temperature: " + text + " %cC" % 0xB0
        super(ChipTemperatureLabel, self).setText(text)

class Barometer(PluginBase):
    qtcb_air_pressure = pyqtSignal(int)
    qtcb_altitude = pyqtSignal(int)

    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)

        self.barometer = bricklet_barometer.Barometer(self.uid)
        self.ipcon.add_device(self.barometer)
        version = self.barometer.get_version()
        self.version = '.'.join(map(str, version[1]))
        self.version_minor = version[1][1]
        self.version_release = version[1][2]

        if self.version_minor == 0 and self.version_release == 0:
            has_calibrate = True
        else:
            has_calibrate = False

        self.qtcb_air_pressure.connect(self.cb_air_pressure)
        self.barometer.register_callback(self.barometer.CALLBACK_AIR_PRESSURE,
                                         self.qtcb_air_pressure.emit)
        self.qtcb_altitude.connect(self.cb_altitude)
        self.barometer.register_callback(self.barometer.CALLBACK_ALTITUDE,
                                         self.qtcb_altitude.emit)

        self.air_pressure_label = AirPressureLabel()
        self.cb_air_pressure(self.barometer.get_air_pressure())

        self.altitude_label = AltitudeLabel()
        self.cb_altitude(self.barometer.get_altitude())

        self.chip_temperature_label = ChipTemperatureLabel()
        if has_calibrate:
            self.chip_temperature_label.setAlignment(Qt.AlignCenter)

        self.current_air_pressure = 0
        self.current_altitude = 0

        plot_list = [['', Qt.red, self.get_current_air_pressure]]
        self.air_pressure_plot_widget = PlotWidget('Air Pressure [mbar]', plot_list)

        plot_list = [['', Qt.darkGreen, self.get_current_altitude]]
        self.altitude_plot_widget = PlotWidget('Altitude [m]', plot_list)

        if has_calibrate:
            self.calibrate_button = QPushButton('Calibrate Altitude')
            self.calibrate_button.pressed.connect(self.calibrate_pressed)
        else:
            self.get_reference_button = QPushButton('Get')
            self.get_reference_button.pressed.connect(self.get_reference_pressed)
            self.set_reference_button = QPushButton('Set')
            self.set_reference_button.pressed.connect(self.set_reference_pressed)
            self.reference_label = QLabel('Reference Air Pressure [mbar]:')
            self.reference_edit = QLineEdit()
            self.get_reference_pressed()

        layout_h1 = QHBoxLayout()
        layout_h1.addStretch()
        layout_h1.addWidget(self.air_pressure_label)
        layout_h1.addStretch()

        layout_v1 = QVBoxLayout()
        layout_v1.addLayout(layout_h1)
        layout_v1.addWidget(self.air_pressure_plot_widget)

        layout_h2 = QHBoxLayout()
        layout_h2.addStretch()
        layout_h2.addWidget(self.altitude_label)
        layout_h2.addStretch()

        layout_v2 = QVBoxLayout()
        layout_v2.addLayout(layout_h2)
        layout_v2.addWidget(self.altitude_plot_widget)

        if has_calibrate:
            layout_h3 = QHBoxLayout()
            layout_h3.addWidget(self.chip_temperature_label)
            layout_h3.addWidget(self.calibrate_button)
        else:
            layout_h3 = QHBoxLayout()
            layout_h3.addWidget(self.reference_label)
            layout_h3.addWidget(self.reference_edit)
            layout_h3.addWidget(self.get_reference_button)
            layout_h3.addWidget(self.set_reference_button)

            layout_v3 = QVBoxLayout()
            layout_v3.addWidget(self.chip_temperature_label)
            layout_v3.addLayout(layout_h3)

        layout_h1 = QHBoxLayout()
        layout_h1.addLayout(layout_v1)
        layout_h1.addLayout(layout_v2)

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h1)

        if has_calibrate:
            layout.addLayout(layout_h3)
        else:
            layout.addLayout(layout_v3)

        self.chip_temp_timer = QTimer()
        self.chip_temp_timer.timeout.connect(self.update_chip_temp)
        self.chip_temp_timer.setInterval(100)
        self.chip_temp_timer.start()

    def start(self):
        try:
            self.cb_air_pressure(self.barometer.get_air_pressure())
            self.barometer.set_air_pressure_callback_period(100)

            self.cb_altitude(self.barometer.get_altitude())
            self.barometer.set_altitude_callback_period(100)
        except ip_connection.Error:
            return

        self.air_pressure_plot_widget.stop = False
        self.altitude_plot_widget.stop = False

        self.update_chip_temp()
        self.chip_temp_timer.start()

    def stop(self):
        try:
            self.barometer.set_air_pressure_callback_period(0)
            self.barometer.set_altitude_callback_period(0)
        except ip_connection.Error:
            pass

        self.air_pressure_plot_widget.stop = True
        self.altitude_plot_widget.stop = True

        self.chip_temp_timer.stop()

    @staticmethod
    def has_name(name):
        return 'Barometer Bricklet' in name

    def calibrate_pressed(self):
        try:
            # Call set_reference_air_pressure that has the same function ID as
            # calibrate_altitude the extra parameter will just be ignored
            self.barometer.set_reference_air_pressure(0)
        except ip_connection.Error:
            pass

    def get_reference_pressed(self):
        try:
            r = str(self.barometer.get_reference_air_pressure()/1000.0)
        except ip_connection.Error:
            r = 'Error while getting reference air pressure'

        self.reference_edit.setText(r)

    def set_reference_pressed(self):
        try:
            r = round(float(self.reference_edit.text())*1000)
        except:
            self.reference_edit.setText('Invalid input')
            return

        try:
            self.barometer.set_reference_air_pressure(r)
        except ip_connection.Error:
            self.reference_edit.setText('Error while setting reference air pressure')
            return

    def get_current_air_pressure(self):
        return self.current_air_pressure

    def get_current_altitude(self):
        return self.current_altitude

    def update_chip_temp(self):
        try:
            t = self.barometer.get_chip_temperature()/100.0
            self.chip_temperature_label.setText('%.2f' % t)
        except ip_connection.Error:
            pass

    def cb_air_pressure(self, air_pressure):
        self.current_air_pressure = air_pressure/1000.0
        self.air_pressure_label.setText('%.3f' % self.current_air_pressure)

    def cb_altitude(self, altitude):
        self.current_altitude = altitude/100.0
        self.altitude_label.setText('%.2f' % self.current_altitude,
                                    '%.2f' % (self.current_altitude/0.3048))
