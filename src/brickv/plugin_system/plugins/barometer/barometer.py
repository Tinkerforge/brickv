# -*- coding: utf-8 -*-
"""
Barometer Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012, 2014 Matthias Bolte <matthias@tinkerforge.com>

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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plot_widget import PlotWidget
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_barometer import BrickletBarometer
from brickv.async_call import async_call

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QLineEdit, QSpinBox, QFrame
from PyQt4.QtCore import pyqtSignal, Qt, QTimer

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

    def __init__(self, *args):
        PluginBase.__init__(self, 'Barometer Bricklet', BrickletBarometer, *args)

        self.barometer = self.device

        has_calibrate = self.firmware_version == (1, 0, 0)
        has_averaging = self.firmware_version >= (2, 0, 1)
        
        self.moving_average_pressure = 25
        self.average_pressure = 10
        self.average_temperature = 10

        self.qtcb_air_pressure.connect(self.cb_air_pressure)
        self.barometer.register_callback(self.barometer.CALLBACK_AIR_PRESSURE,
                                         self.qtcb_air_pressure.emit)
        self.qtcb_altitude.connect(self.cb_altitude)
        self.barometer.register_callback(self.barometer.CALLBACK_ALTITUDE,
                                         self.qtcb_altitude.emit)

        self.air_pressure_label = AirPressureLabel()

        self.altitude_label = AltitudeLabel()

        self.chip_temperature_label = ChipTemperatureLabel()
        if has_calibrate:
            self.chip_temperature_label.setAlignment(Qt.AlignCenter)

        self.current_air_pressure = None
        self.current_altitude = None

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
            
        if has_averaging:
            self.avg_pressure_box = QSpinBox()
            self.avg_pressure_box.setMinimum(0)
            self.avg_pressure_box.setMaximum(10)
            self.avg_pressure_box.setSingleStep(1)
            self.avg_pressure_box.setValue(10)
            self.avg_temperature_box = QSpinBox()
            self.avg_temperature_box.setMinimum(0)
            self.avg_temperature_box.setMaximum(255)
            self.avg_temperature_box.setSingleStep(1)
            self.avg_temperature_box.setValue(10)
            self.avg_moving_pressure_box = QSpinBox()
            self.avg_moving_pressure_box.setMinimum(0)
            self.avg_moving_pressure_box.setMaximum(25)
            self.avg_moving_pressure_box.setSingleStep(1)
            self.avg_moving_pressure_box.setValue(25)
            
            self.avg_pressure_box.editingFinished.connect(self.avg_pressure_box_finished)
            self.avg_temperature_box.editingFinished.connect(self.avg_temperature_box_finished)
            self.avg_moving_pressure_box.editingFinished.connect(self.avg_moving_pressure_box_finished)

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
            
        if has_averaging:
            line1 = QFrame()
            line1.setFrameShape(QFrame.VLine)
            line1.setFrameShadow(QFrame.Sunken)
            line2 = QFrame()
            line2.setFrameShape(QFrame.VLine)
            line2.setFrameShadow(QFrame.Sunken)
            
            layout_h4 = QHBoxLayout()
            layout_h4.addWidget(QLabel('Air Pressure Moving Average Length:'))
            layout_h4.addWidget(self.avg_moving_pressure_box)
            layout_h4.addWidget(line1)
            layout_h4.addWidget(QLabel('Air Pressure Average Length:'))
            layout_h4.addWidget(self.avg_pressure_box)
            layout_h4.addWidget(line2)
            layout_h4.addWidget(QLabel('Temperate Average Length:'))
            layout_h4.addWidget(self.avg_temperature_box)

        layout_h1 = QHBoxLayout()
        layout_h1.addLayout(layout_v1)
        layout_h1.addLayout(layout_v2)

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h1)

        if has_calibrate:
            layout.addLayout(layout_h3)
        else:
            layout.addLayout(layout_v3)
            
        if has_averaging:
            lineh = QFrame()
            lineh.setFrameShape(QFrame.HLine)
            lineh.setFrameShadow(QFrame.Sunken)
            layout.addWidget(lineh)
            layout.addLayout(layout_h4)

        self.chip_temp_timer = QTimer()
        self.chip_temp_timer.timeout.connect(self.update_chip_temp)
        self.chip_temp_timer.setInterval(100)

    def start(self):
        async_call(self.barometer.get_air_pressure, None, self.cb_air_pressure, self.increase_error_count)
        async_call(self.barometer.get_altitude, None, self.cb_altitude, self.increase_error_count)

        async_call(self.barometer.set_air_pressure_callback_period, 100, None, self.increase_error_count)
        async_call(self.barometer.set_altitude_callback_period, 100, None, self.increase_error_count)
        
        async_call(self.barometer.get_averaging, None, self.cb_averaging, self.increase_error_count)

        self.air_pressure_plot_widget.stop = False
        self.altitude_plot_widget.stop = False

        self.update_chip_temp()
        self.chip_temp_timer.start()

    def stop(self):
        async_call(self.barometer.set_air_pressure_callback_period, 0, None, self.increase_error_count)
        async_call(self.barometer.set_altitude_callback_period, 0, None, self.increase_error_count)

        self.air_pressure_plot_widget.stop = True
        self.altitude_plot_widget.stop = True

        self.chip_temp_timer.stop()

    def destroy(self):
        self.destroy_ui()

    def get_url_part(self):
        return 'barometer'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletBarometer.DEVICE_IDENTIFIER

    def cb_averaging(self, avg):
        moving_average_pressure, average_pressure, average_temperature = avg
        self.moving_average_pressure = moving_average_pressure
        self.average_pressure = average_pressure
        self.average_temperature = average_temperature
        
        self.avg_moving_pressure_box.setValue(moving_average_pressure)
        self.avg_pressure_box.setValue(average_pressure)
        self.avg_temperature_box.setValue(average_temperature)
    
    def avg_pressure_box_finished(self):
        self.average_pressure = self.avg_pressure_box.value()
        self.save_new_averaging()
    
    def avg_temperature_box_finished(self):
        self.average_temperature = self.avg_temperature_box.value()
        self.save_new_averaging()
    
    def avg_moving_pressure_box_finished(self):
        self.moving_average_pressure = self.avg_moving_pressure_box.value()
        self.save_new_averaging()
    
    def save_new_averaging(self):
        self.barometer.set_averaging(self.moving_average_pressure, self.average_pressure, self.average_temperature)

    def calibrate_pressed(self):
        try:
            # Call set_reference_air_pressure that has the same function ID as
            # calibrate_altitude the extra parameter will just be ignored
            self.barometer.set_reference_air_pressure(0)
        except ip_connection.Error:
            pass

    def get_reference_pressed_async(self, reference):
        r = str(reference/1000.0)
        self.reference_edit.setText(r)
        
    def get_reference_pressed(self):
        async_call(self.barometer.get_reference_air_pressure, None, self.get_reference_pressed_async, self.increase_error_count)

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

    def update_chip_temp_async(self, temp):
        t = temp/100.0
        self.chip_temperature_label.setText('%.2f' % t)

    def update_chip_temp(self):
        async_call(self.barometer.get_chip_temperature, None, self.update_chip_temp_async, self.increase_error_count)

    def cb_air_pressure(self, air_pressure):
        self.current_air_pressure = air_pressure/1000.0
        self.air_pressure_label.setText('%.3f' % self.current_air_pressure)

    def cb_altitude(self, altitude):
        self.current_altitude = altitude/100.0
        self.altitude_label.setText('%.2f' % self.current_altitude,
                                    '%.2f' % (self.current_altitude/0.3048))
