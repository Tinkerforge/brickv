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

from PyQt4.QtCore import QTimer
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
        
        self.cbe_identifiers = CallbackEmulator(self.outdoor_weather.get_weather_station_identifiers,
                                                self.cb_weather_station_identifiers,
                                                self.increase_error_count)
        
        self.identifiers = []
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.data_timeout)
        
    def data_timeout(self):
        if len(self.identifiers) > 0:
            identifier = int(str(self.combo_identifier.itemText(self.combo_identifier.currentIndex())))
            async_call(lambda: self.outdoor_weather.get_weather_station_data(identifier), None, self.cb_weather_station_data, self.increase_error_count)
        else:
            pass # TODO


    def cb_weather_station_identifiers(self, identifiers):
        if len(identifiers) == 0:
            return
        
        old_index = self.combo_identifier.currentIndex()
        old_text = str(self.combo_identifier.itemText(old_index))
        self.combo_identifier.clear()
        
        self.identifiers = identifiers
        for index, identifier in enumerate(identifiers):
            new_text = str(identifier)
            self.combo_identifier.addItem(new_text)
            if new_text == old_text:
                self.combo_identifier.setCurrentIndex(index)
        
        self.data_timeout()
        
    def cb_weather_station_data(self, data):
        self.label_temperature.setText("{:.1f}".format(data.temperature/10.0))
        self.label_humidity.setText("{}".format(data.humidity))
        self.label_wind_speed.setText("{:.1f}".format(data.wind_speed/10.0))
        self.label_gust_speed.setText("{:.1f}".format(data.gust_speed/10.0))
        self.label_rain_level.setText("{:.1f}".format(data.rain/10.0))
        self.label_last_change.setText("{}".format(data.last_change))

        if data.battery_low:
            self.label_battery_level.setText("<font color='red'>LOW</font>")
        else:
            self.label_battery_level.setText("OK")
           
        try: 
            wind_direction = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'][data.wind_direction]
        except:
            wind_direction = 'Unkown (error occurred)'
            
        self.label_wind_direction.setText(wind_direction)
            
    def start(self):
        async_call(self.outdoor_weather.get_weather_station_identifiers, None, self.cb_weather_station_identifiers, self.increase_error_count)
         
        self.cbe_identifiers.set_period(10000)
        self.data_timer.start(1000)

    def stop(self):
        self.cbe_identifiers.set_period(0)
        self.data_timer.stop()

    def destroy(self):
        pass

    def get_url_part(self):
        return 'outdoor_weather'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletOutdoorWeather.DEVICE_IDENTIFIER
