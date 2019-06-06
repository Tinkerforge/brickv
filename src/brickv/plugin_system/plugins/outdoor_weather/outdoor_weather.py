# -*- coding: utf-8 -*-
"""
Outdoor Weather Plugin
Copyright (C) 2017 Olaf Lüke <olaf@tinkerforge.com>

outdoor_weather.py: Outdoor Weather Plugin Implementation

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

from PyQt5.QtCore import QTimer
from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_outdoor_weather import BrickletOutdoorWeather
from brickv.plugin_system.plugins.outdoor_weather.ui_outdoor_weather import Ui_OutdoorWeather
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class OutdoorWeather(COMCUPluginBase, Ui_OutdoorWeather):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletOutdoorWeather, *args)

        self.outdoor_weather = self.device

        self.setupUi(self)

        self.cbe_identifiers_station = CallbackEmulator(self.outdoor_weather.get_station_identifiers,
                                                        None,
                                                        self.cb_station_identifiers,
                                                        self.increase_error_count)

        self.cbe_identifiers_sensor = CallbackEmulator(self.outdoor_weather.get_sensor_identifiers,
                                                       None,
                                                       self.cb_sensor_identifiers,
                                                       self.increase_error_count)

        self.combo_identifier_station.currentIndexChanged.connect(self.update_station)
        self.combo_identifier_sensor.currentIndexChanged.connect(self.update_sensor)

        self.combo_identifier_station.setEnabled(False)
        self.combo_identifier_sensor.setEnabled(False)

        self.data_timer_station = QTimer(self)
        self.data_timer_station.timeout.connect(self.update_station)

        self.data_timer_sensor = QTimer(self)
        self.data_timer_sensor.timeout.connect(self.update_sensor)

    def update_station(self):
        if self.combo_identifier_station.isEnabled():
            try:
                identifier = int(self.combo_identifier_station.currentText())
            except:
                return

            async_call(self.outdoor_weather.get_station_data, identifier, self.get_station_data_async, self.increase_error_count)
        else:
            self.label_temperature_station.setText('---')
            self.label_humidity_station.setText('---')
            self.label_wind_speed_station.setText('---')
            self.label_gust_speed_station.setText('---')
            self.label_rain_level_station.setText('---')
            self.label_battery_level_station.setText('---')
            self.label_wind_direction_station.setText('---')
            self.label_last_change_station.setText('---')

    def update_sensor(self):
        if self.combo_identifier_sensor.isEnabled():
            try:
                identifier = int(self.combo_identifier_sensor.currentText())
            except:
                return

            async_call(self.outdoor_weather.get_sensor_data, identifier, self.get_sensor_data_async, self.increase_error_count)
        else:
            self.label_temperature_sensor.setText('---')
            self.label_humidity_sensor.setText('---')
            self.label_last_change_sensor.setText('---')

    def cb_station_identifiers(self, identifiers):
        old_text = self.combo_identifier_station.currentText()

        self.combo_identifier_station.setEnabled(False)
        self.combo_identifier_station.clear()

        for index, identifier in enumerate(identifiers):
            new_text = str(identifier)
            self.combo_identifier_station.addItem(new_text)

            if new_text == old_text:
                self.combo_identifier_station.setCurrentIndex(index)

        if self.combo_identifier_station.count() > 0:
            self.combo_identifier_station.setEnabled(True)
        else:
            self.combo_identifier_station.addItem('No Stations found')

        self.update_station()

    def cb_sensor_identifiers(self, identifiers):
        old_text = self.combo_identifier_sensor.currentText()

        self.combo_identifier_sensor.setEnabled(False)
        self.combo_identifier_sensor.clear()

        for index, identifier in enumerate(identifiers):
            new_text = str(identifier)
            self.combo_identifier_sensor.addItem(new_text)

            if new_text == old_text:
                self.combo_identifier_sensor.setCurrentIndex(index)

        if self.combo_identifier_sensor.count() > 0:
            self.combo_identifier_sensor.setEnabled(True)
        else:
            self.combo_identifier_sensor.addItem('No Sensors found')

        self.update_sensor()

    def get_station_data_async(self, data):
        self.label_temperature_station.setText("{:.1f}".format(data.temperature/10.0))
        self.label_humidity_station.setText("{}".format(data.humidity))
        self.label_wind_speed_station.setText("{:.1f}".format(data.wind_speed/10.0))
        self.label_gust_speed_station.setText("{:.1f}".format(data.gust_speed/10.0))
        self.label_rain_level_station.setText("{:.1f}".format(data.rain/10.0))
        self.label_last_change_station.setText("{}".format(data.last_change))

        if data.battery_low:
            self.label_battery_level_station.setText("<font color='red'>Low</font>")
        else:
            self.label_battery_level_station.setText("OK")

        try:
            wind_direction = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'][data.wind_direction]
        except:
            wind_direction = "<font color='red'>Unknown (Station Error)</font>"

        self.label_wind_direction_station.setText(wind_direction)

    def get_sensor_data_async(self, data):
        self.label_temperature_sensor.setText("{:.1f}".format(data.temperature/10.0))
        self.label_humidity_sensor.setText("{}".format(data.humidity))
        self.label_last_change_sensor.setText("{}".format(data.last_change))

    def start(self):
        self.cbe_identifiers_station.set_period(10000)
        self.cbe_identifiers_sensor.set_period(10000)

        self.data_timer_station.start(250)
        self.data_timer_sensor.start(250)

    def stop(self):
        self.cbe_identifiers_station.set_period(0)
        self.cbe_identifiers_sensor.set_period(0)

        self.data_timer_station.stop()
        self.data_timer_sensor.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletOutdoorWeather.DEVICE_IDENTIFIER
