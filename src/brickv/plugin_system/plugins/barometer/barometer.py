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

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt4.QtCore import pyqtSignal, Qt

from bindings import bricklet_barometer

class AirPressureLabel(QLabel):
    def setText(self, text):
        text = "Air Pressure: " + text + " mbar"
        super(AirPressureLabel, self).setText(text)

class AltitudeLabel(QLabel):
    def setText(self, text):
        text = "Altitude: " + text + " m"
        super(AltitudeLabel, self).setText(text)

class TemperatureLabel(QLabel):
    def setText(self, text):
        text = "Temperature: " + text + " %cC" % 0xB0
        super(TemperatureLabel, self).setText(text)

class Barometer(PluginBase):
    qtcb_air_pressure = pyqtSignal(int)
    qtcb_altitude = pyqtSignal(int)

    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)

        self.barometer = bricklet_barometer.Barometer(self.uid)
        self.ipcon.add_device(self.barometer)
        self.version = '.'.join(map(str, self.barometer.get_version()[1]))

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

        self.temperature_label = TemperatureLabel()

        self.current_air_pressure = 0
        self.current_altitude = 0

        plot_list = [['', Qt.red, self.get_current_air_pressure]]
        self.air_pressure_plot_widget = PlotWidget('Air Pressure [mbar]', plot_list)

        plot_list = [['', Qt.green, self.get_current_altitude]]
        self.altitude_plot_widget = PlotWidget('Altitude [m]', plot_list)

        plot_list = [['', Qt.blue, self.get_current_temperature]]
        self.temperature_plot_widget = PlotWidget('Temperature [%cC]' % 0xB0, plot_list)

        self.calibrate_button = QPushButton('Calibrate')
        self.calibrate_button.pressed.connect(self.calibrate_pressed)

        layout_v1 = QVBoxLayout()
        layout_v1.addWidget(self.air_pressure_label)
        layout_v1.addWidget(self.air_pressure_plot_widget)

        layout_v2 = QVBoxLayout()
        layout_v2.addWidget(self.altitude_label)
        layout_v2.addWidget(self.altitude_plot_widget)

        layout_v3 = QVBoxLayout()
        layout_v3.addWidget(self.temperature_label)
        layout_v3.addWidget(self.temperature_plot_widget)

        layout_h1 = QHBoxLayout()
        layout_h1.addLayout(layout_v1)
        layout_h1.addLayout(layout_v2)
        layout_h1.addLayout(layout_v3)


        layout = QVBoxLayout(self)
        layout.addLayout(layout_h1)
        layout.addWidget(self.calibrate_button)

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
        self.temperature_plot_widget.stop = False

    def stop(self):
        try:
            self.barometer.set_air_pressure_callback_period(0)
            self.barometer.set_altitude_callback_period(0)
        except ip_connection.Error:
            pass

        self.air_pressure_plot_widget.stop = True
        self.altitude_plot_widget.stop = True
        self.temperature_plot_widget.stop = True

    @staticmethod
    def has_name(name):
        return 'Barometer Bricklet' in name

    def calibrate_pressed(self):
        try:
            self.barometer.calibrate_altitude()
        except ip_connection.Error:
            return

    def get_current_air_pressure(self):
        #return self.current_air_pressure
        t = self.barometer.get_air_pressure()/100.0
        self.air_pressure_label.setText(str(t))
        return t

    def get_current_altitude(self):
        #return self.current_altitude
        t = self.barometer.get_altitude()/100.0
        self.altitude_label.setText(str(t))
        return t

    def get_current_temperature(self):
        t = self.barometer.get_temperature()/100.0
        self.temperature_label.setText(str(t))
        return t

    def cb_air_pressure(self, air_pressure):
        self.current_air_pressure = air_pressure/100.0
        self.air_pressure_label.setText(str(air_pressure/100.0))

    def cb_altitude(self, altitude):
        self.current_altitude = altitude/100.0
        self.altitude_label.setText(str(altitude/100.0))
