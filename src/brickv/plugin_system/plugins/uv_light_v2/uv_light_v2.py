# -*- coding: utf-8 -*-
"""
UV Light 2.0 Plugin
Copyright (C) 2018 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

uv_light_v2.py: UV Light 2.0 Bricklet Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QFrame

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_uv_light_v2 import BrickletUVLightV2
from brickv.plot_widget import PlotWidget, CurveValueWrapper, FixedSizeLabel
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class IndexLabel(FixedSizeLabel):
    def setText(self, text):
        super().setText(' UVI: ' + text + ' ')

class UVLightV2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletUVLightV2, *args)

        self.uv_light = self.device

        self.cbe_uva = CallbackEmulator(self,
                                        self.uv_light.get_uva,
                                        None,
                                        self.cb_uva,
                                        self.increase_error_count)

        self.cbe_uvb = CallbackEmulator(self,
                                        self.uv_light.get_uvb,
                                        None,
                                        self.cb_uvb,
                                        self.increase_error_count)

        self.cbe_uvi = CallbackEmulator(self,
                                        self.uv_light.get_uvi,
                                        None,
                                        self.cb_uvi,
                                        self.increase_error_count)

        self.index_label = IndexLabel(' UVI: ? ')
        self.index_label.setText('0.0')

        self.current_uva = CurveValueWrapper()
        self.current_uvb = CurveValueWrapper()

        plots = [('UVA', Qt.red, self.current_uva, '{} mW/m²'.format),
                 ('UVB', Qt.darkGreen, self.current_uvb, '{} mW/m²'.format)]

        self.plot_widget = PlotWidget('UV [mW/m²]', plots, extra_key_widgets=[self.index_label], y_resolution=0.1)

        self.time_label = QLabel('Integration Time:')
        self.time_combo = QComboBox()
        self.time_combo.addItem("50 ms", BrickletUVLightV2.INTEGRATION_TIME_50MS)
        self.time_combo.addItem("100 ms", BrickletUVLightV2.INTEGRATION_TIME_100MS)
        self.time_combo.addItem("200 ms", BrickletUVLightV2.INTEGRATION_TIME_200MS)
        self.time_combo.addItem("400 ms", BrickletUVLightV2.INTEGRATION_TIME_400MS)
        self.time_combo.addItem("800 ms", BrickletUVLightV2.INTEGRATION_TIME_800MS)
        self.time_combo.currentIndexChanged.connect(self.new_config)

        self.saturation_label = QLabel('Sensor is saturated, choose a shorter integration time!')
        self.saturation_label.setStyleSheet('QLabel { color : red }')
        self.saturation_label.hide()

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.time_label)
        hlayout.addWidget(self.time_combo)
        hlayout.addStretch()
        hlayout.addWidget(self.saturation_label)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

    def start(self):
        async_call(self.uv_light.get_configuration, None, self.get_configucation_async, self.increase_error_count)

        self.cbe_uva.set_period(100)
        self.cbe_uvb.set_period(100)
        self.cbe_uvi.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_uva.set_period(0)
        self.cbe_uvb.set_period(0)
        self.cbe_uvi.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletUVLightV2.DEVICE_IDENTIFIER

    def get_configucation_async(self, integration_time):
        self.time_combo.setCurrentIndex(self.time_combo.findData(integration_time))

    def new_config(self, value):
        try:
            self.uv_light.set_configuration(self.time_combo.itemData(self.time_combo.currentIndex()))
        except:
            pass

    def cb_uva(self, uva):
        self.saturation_label.setVisible(uva < 0)

        if uva < 0: # saturated
            return

        self.current_uva.value = uva / 10.0

    def cb_uvb(self, uvb):
        self.saturation_label.setVisible(uvb < 0)

        if uvb < 0: # saturated
            return

        self.current_uvb.value = uvb / 10.0

    def cb_uvi(self, uvi):
        self.saturation_label.setVisible(uvi < 0)

        if uvi < 0: # saturated
            return

        uvi = round(uvi / 10.0, 1)

        self.index_label.setText(str(uvi))

        if uvi < 2.5:
            background = 'green'
            color = 'white'
        elif uvi < 5.5:
            background = 'yellow'
            color = 'black'
        elif uvi < 7.5:
            background = 'orange'
            color = 'black'
        elif uvi < 10.5:
            background = 'red'
            color = 'white'
        else:
            background = 'magenta'
            color = 'white'

        self.index_label.setStyleSheet('QLabel {{ background : {0}; color : {1} }}'.format(background, color))
