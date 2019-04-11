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

        self.changing = False

        self.setupUi(self)

        self.cbe_identifiers_station = CallbackEmulator(self.outdoor_weather.get_station_identifiers,
                                                        self.cb_station_identifiers,
                                                        self.increase_error_count)

        self.cbe_identifiers_sensor = CallbackEmulator(self.outdoor_weather.get_sensor_identifiers,
                                                       self.cb_sensor_identifiers,
                                                       self.increase_error_count)

        self.combo_identifier_station.currentIndexChanged.connect(self.data_timeout_station)

        self.identifiers_station = []
        self.identifiers_sensor = []

        self.data_timer_station = QTimer()
        self.data_timer_station.timeout.connect(self.data_timeout_station)

        self.data_timer_sensor = QTimer()
        self.data_timer_sensor.timeout.connect(self.data_timeout_sensor)

    def data_timeout_station(self):
        if len(self.identifiers_station) > 0:
            try:
                identifier = int(str(self.combo_identifier_station.itemText(self.combo_identifier_station.currentIndex())))
            except:
                return

            async_call(lambda: self.outdoor_weather.get_station_data(identifier), None, self.cb_station_data, self.increase_error_count)
        else:
            pass # TODO

    def data_timeout_sensor(self):
        if len(self.identifiers_sensor) > 0:
            try:
                identifier = int(str(self.combo_identifier_sensor.itemText(self.combo_identifier_sensor.currentIndex())))
            except:
                return

            async_call(lambda: self.outdoor_weather.get_sensor_data(identifier), None, self.cb_sensor_data, self.increase_error_count)
        else:
            pass # TODO

    def cb_station_identifiers(self, identifiers):
        if len(identifiers) == 0:
            return

        old_index = self.combo_identifier_station.currentIndex()
        old_text = str(self.combo_identifier_station.itemText(old_index))
        self.combo_identifier_station.clear()

        self.identifiers_station = identifiers
        for index, identifier in enumerate(identifiers):
            new_text = str(identifier)
            self.combo_identifier_station.addItem(new_text)
            if new_text == old_text:
                self.combo_identifier_station.setCurrentIndex(index)

        self.data_timeout_station()

    def cb_sensor_identifiers(self, identifiers):
        if len(identifiers) == 0:
            return

        old_index = self.combo_identifier_sensor.currentIndex()
        old_text = str(self.combo_identifier_sensor.itemText(old_index))
        self.combo_identifier_sensor.clear()

        self.identifiers_sensor = identifiers
        for index, identifier in enumerate(identifiers):
            new_text = str(identifier)
            self.combo_identifier_sensor.addItem(new_text)
            if new_text == old_text:
                self.combo_identifier_sensor.setCurrentIndex(index)

        self.data_timeout_sensor()

    def cb_station_data(self, data):
        self.label_temperature_station.setText("{:.1f}".format(data.temperature/10.0))
        self.label_humidity_station.setText("{}".format(data.humidity))
        self.label_wind_speed_station.setText("{:.1f}".format(data.wind_speed/10.0))
        self.label_gust_speed_station.setText("{:.1f}".format(data.gust_speed/10.0))
        self.label_rain_level_station.setText("{:.1f}".format(data.rain/10.0))
        self.label_last_change_station.setText("{}".format(data.last_change))

        if data.battery_low:
            self.label_battery_level_station.setText("<font color='red'>LOW</font>")
        else:
            self.label_battery_level_station.setText("OK")

        try:
            wind_direction = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'][data.wind_direction]
        except:
            wind_direction = "<font color='red'>Unknown (Station Error)</font>"

        self.label_wind_direction_station.setText(wind_direction)

    def cb_sensor_data(self, data):
        self.label_temperature_sensor.setText("{:.1f}".format(data.temperature/10.0))
        self.label_humidity_sensor.setText("{}".format(data.humidity))
        self.label_last_change_sensor.setText("{}".format(data.last_change))

    def start(self):
        async_call(self.outdoor_weather.get_station_identifiers, None, self.cb_station_identifiers, self.increase_error_count)
        async_call(self.outdoor_weather.get_sensor_identifiers, None, self.cb_sensor_identifiers, self.increase_error_count)

        self.cbe_identifiers_station.set_period(10000)
        self.cbe_identifiers_sensor.set_period(10000)

        self.data_timer_station.start(1000)
        self.data_timer_sensor.start(1000)

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
