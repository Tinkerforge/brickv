# -*- coding: utf-8 -*-
"""
Color 2.0 Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

color_v2.py: Color 2.0 Plugin Implementation

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
from PyQt5.QtWidgets import QPushButton, QLabel, QHBoxLayout, QComboBox, QFrame, QCheckBox, QVBoxLayout
from PyQt5.QtGui import QPainter, QBrush, QColor

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_color_v2 import BrickletColorV2
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.color_frame import ColorFrame

class ColorV2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletColorV2, *args)

        self.color = self.device

        self.cbe_color = CallbackEmulator(self.color.get_color,
                                          None,
                                          self.cb_color,
                                          self.increase_error_count,
                                          expand_result_tuple_for_callback=True)
        self.cbe_illuminance = CallbackEmulator(self.color.get_illuminance,
                                                None,
                                                self.cb_illuminance,
                                                self.increase_error_count)
        self.cbe_color_temperature = CallbackEmulator(self.color.get_color_temperature,
                                                      None,
                                                      self.cb_color_temperature,
                                                      self.increase_error_count)

        self.color_frame = ColorFrame(25, 25, QColor(128, 128, 128))
        self.illuminance_frame = ColorFrame(25, 25, QColor(128, 128, 128))
        self.color_temperature_frame = ColorFrame(25, 25, QColor(128, 128, 128))

        self.current_color_r = CurveValueWrapper() # int
        self.current_color_g = CurveValueWrapper() # int
        self.current_color_b = CurveValueWrapper() # int
        self.current_color_c = CurveValueWrapper() # int
        self.current_illuminance = CurveValueWrapper() # float, lx
        self.current_color_temperature = CurveValueWrapper() # int, K

        self.clear_graphs_button = QPushButton("Clear Graphs")

        plots = [('R', Qt.red, self.current_color_r, lambda value: self.format_color(0, value)),
                 ('G', Qt.darkGreen, self.current_color_g, lambda value: self.format_color(1, value)),
                 ('B', Qt.blue, self.current_color_b, lambda value: self.format_color(2, value)),
                 ('C', Qt.black, self.current_color_c, str)]
        self.plot_widget = PlotWidget('Color', plots, clear_button=self.clear_graphs_button,
                                      extra_key_widgets=[self.color_frame], y_resolution=1.0)
        self.plot_widget.setMinimumSize(250, 200)

        plots_illuminance = [('Illuminance', Qt.red, self.current_illuminance, '{} lx (Lux)'.format)]
        self.plot_widget_illuminance = PlotWidget('Illuminance [lx]', plots_illuminance,
                                                  clear_button=self.clear_graphs_button,
                                                  extra_key_widgets=[self.illuminance_frame],
                                                  y_resolution=0.1)
        self.plot_widget_illuminance.setMinimumSize(250, 200)

        plots_color_temperature = [('Color Temperature', Qt.red, self.current_color_temperature, '{} K'.format)]
        self.plot_widget_color_temperature = PlotWidget('Color Temperature [K]', plots_color_temperature,
                                                        clear_button=self.clear_graphs_button,
                                                        extra_key_widgets=[self.color_temperature_frame],
                                                        y_resolution=1.0)
        self.plot_widget_color_temperature.setMinimumSize(250, 200)

        self.gain_label = QLabel('Gain:')
        self.gain_combo = QComboBox()
        self.gain_combo.addItem("1x")
        self.gain_combo.addItem("4x")
        self.gain_combo.addItem("16x")
        self.gain_combo.addItem("60x")

        self.gain_combo.currentIndexChanged.connect(self.gain_changed)

        self.current_gain_factor = 60

        self.conversion_label = QLabel('Integration Time:')
        self.conversion_combo = QComboBox()
        self.conversion_combo.addItem("2.4 ms")
        self.conversion_combo.addItem("24 ms")
        self.conversion_combo.addItem("101 ms")
        self.conversion_combo.addItem("154 ms")
        self.conversion_combo.addItem("700 ms")

        self.current_conversion_time = 154

        self.conversion_combo.currentIndexChanged.connect(self.conversion_changed)

        self.light_checkbox = QCheckBox("Enable Light")

        self.light_checkbox.stateChanged.connect(self.light_state_changed)

        layout_h1 = QHBoxLayout()
        layout_h1.addWidget(self.plot_widget_illuminance)
        layout_h1.addWidget(self.plot_widget_color_temperature)

        layout_h2 = QHBoxLayout()
        layout_h2.addWidget(self.gain_label)
        layout_h2.addWidget(self.gain_combo)
        layout_h2.addWidget(self.conversion_label)
        layout_h2.addWidget(self.conversion_combo)
        layout_h2.addWidget(self.light_checkbox)
        layout_h2.addStretch()
        layout_h2.addWidget(self.clear_graphs_button)

        line1 = QFrame()
        line1.setObjectName("line1")
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)

        line2 = QFrame()
        line2.setObjectName("line2")
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line1)
        layout.addLayout(layout_h1)
        layout.addWidget(line2)
        layout.addLayout(layout_h2)

        self.k_to_rgb = {1000:(255, 56, 0), 1100:(255, 71, 0), 1200:(255, 83, 0), 1300:(255, 93, 0), 1400:(255, 101, 0), 1500:(255, 109, 0), 1600:(255, 115, 0), 1700:(255, 121, 0), 1800:(255, 126, 0), 1900:(255, 131, 0), 2000:(255, 137, 18), 2100:(255, 142, 33), 2200:(255, 147, 44), 2300:(255, 152, 54), 2400:(255, 157, 63), 2500:(255, 161, 72), 2600:(255, 165, 79), 2700:(255, 169, 87), 2800:(255, 173, 94), 2900:(255, 177, 101), 3000:(255, 180, 107), 3100:(255, 184, 114), 3200:(255, 187, 120), 3300:(255, 190, 126), 3400:(255, 193, 132), 3500:(255, 196, 137), 3600:(255, 199, 143), 3700:(255, 201, 148), 3800:(255, 204, 153), 3900:(255, 206, 159), 4000:(255, 209, 163), 4100:(255, 211, 168), 4200:(255, 213, 173), 4300:(255, 215, 177), 4400:(255, 217, 182), 4500:(255, 219, 186), 4600:(255, 221, 190), 4700:(255, 223, 194), 4800:(255, 225, 198), 4900:(255, 227, 202), 5000:(255, 228, 206), 5100:(255, 230, 210), 5200:(255, 232, 213), 5300:(255, 233, 217), 5400:(255, 235, 220), 5500:(255, 236, 224), 5600:(255, 238, 227), 5700:(255, 239, 230), 5800:(255, 240, 233), 5900:(255, 242, 236), 6000:(255, 243, 239), 6100:(255, 244, 242), 6200:(255, 245, 245), 6300:(255, 246, 248), 6400:(255, 248, 251), 6500:(255, 249, 253), 6600:(254, 249, 255), 6700:(252, 247, 255), 6800:(249, 246, 255), 6900:(247, 245, 255), 7000:(245, 243, 255), 7100:(243, 242, 255), 7200:(240, 241, 255), 7300:(239, 240, 255), 7400:(237, 239, 255), 7500:(235, 238, 255), 7600:(233, 237, 255), 7700:(231, 236, 255), 7800:(230, 235, 255), 7900:(228, 234, 255), 8000:(227, 233, 255), 8100:(225, 232, 255), 8200:(224, 231, 255), 8300:(222, 230, 255), 8400:(221, 230, 255), 8500:(220, 229, 255), 8600:(218, 228, 255), 8700:(217, 227, 255), 8800:(216, 227, 255), 8900:(215, 226, 255), 9000:(214, 225, 255), 9100:(212, 225, 255), 9200:(211, 224, 255), 9300:(210, 223, 255), 9400:(209, 223, 255), 9500:(208, 222, 255), 9600:(207, 221, 255), 9700:(207, 221, 255), 9800:(206, 220, 255), 9900:(205, 220, 255), 10000:(204, 219, 255), 10100:(203, 219, 255), 10200:(202, 218, 255), 10300:(201, 218, 255), 10400:(201, 217, 255), 10500:(200, 217, 255), 10600:(199, 216, 255), 10700:(199, 216, 255), 10800:(198, 216, 255), 10900:(197, 215, 255), 11000:(196, 215, 255), 11100:(196, 214, 255), 11200:(195, 214, 255), 11300:(195, 214, 255), 11400:(194, 213, 255), 11500:(193, 213, 255), 11600:(193, 212, 255), 11700:(192, 212, 255), 11800:(192, 212, 255), 11900:(191, 211, 255), 12000:(191, 211, 255), 12100:(190, 211, 255), 12200:(190, 210, 255), 12300:(189, 210, 255), 12400:(189, 210, 255), 12500:(188, 210, 255), 12600:(188, 209, 255), 12700:(187, 209, 255), 12800:(187, 209, 255), 12900:(186, 208, 255), 13000:(186, 208, 255), 13100:(185, 208, 255), 13200:(185, 208, 255), 13300:(185, 207, 255), 13400:(184, 207, 255), 13500:(184, 207, 255), 13600:(183, 207, 255), 13700:(183, 206, 255), 13800:(183, 206, 255), 13900:(182, 206, 255), 14000:(182, 206, 255), 14100:(182, 205, 255), 14200:(181, 205, 255), 14300:(181, 205, 255), 14400:(181, 205, 255), 14500:(180, 205, 255), 14600:(180, 204, 255), 14700:(180, 204, 255), 14800:(179, 204, 255), 14900:(179, 204, 255), 15000:(179, 204, 255), 15100:(178, 203, 255), 15200:(178, 203, 255), 15300:(178, 203, 255), 15400:(178, 203, 255), 15500:(177, 203, 255), 15600:(177, 202, 255), 15700:(177, 202, 255), 15800:(177, 202, 255), 15900:(176, 202, 255), 16000:(176, 202, 255), 16100:(176, 202, 255), 16200:(175, 201, 255), 16300:(175, 201, 255), 16400:(175, 201, 255), 16500:(175, 201, 255), 16600:(175, 201, 255), 16700:(174, 201, 255), 16800:(174, 201, 255), 16900:(174, 200, 255), 17000:(174, 200, 255), 17100:(173, 200, 255), 17200:(173, 200, 255), 17300:(173, 200, 255), 17400:(173, 200, 255), 17500:(173, 200, 255), 17600:(172, 199, 255), 17700:(172, 199, 255), 17800:(172, 199, 255), 17900:(172, 199, 255), 18000:(172, 199, 255), 18100:(171, 199, 255), 18200:(171, 199, 255), 18300:(171, 199, 255), 18400:(171, 198, 255), 18500:(171, 198, 255), 18600:(170, 198, 255), 18700:(170, 198, 255), 18800:(170, 198, 255), 18900:(170, 198, 255), 19000:(170, 198, 255), 19100:(170, 198, 255), 19200:(169, 198, 255), 19300:(169, 197, 255), 19400:(169, 197, 255), 19500:(169, 197, 255), 19600:(169, 197, 255), 19700:(169, 197, 255), 19800:(169, 197, 255), 19900:(168, 197, 255), 20000:(168, 197, 255), 20100:(168, 197, 255), 20200:(168, 197, 255), 20300:(168, 196, 255), 20400:(168, 196, 255), 20500:(168, 196, 255), 20600:(167, 196, 255), 20700:(167, 196, 255), 20800:(167, 196, 255), 20900:(167, 196, 255), 21000:(167, 196, 255), 21100:(167, 196, 255), 21200:(167, 196, 255), 21300:(166, 196, 255), 21400:(166, 195, 255), 21500:(166, 195, 255), 21600:(166, 195, 255), 21700:(166, 195, 255), 21800:(166, 195, 255), 21900:(166, 195, 255), 22000:(166, 195, 255), 22100:(165, 195, 255), 22200:(165, 195, 255), 22300:(165, 195, 255), 22400:(165, 195, 255), 22500:(165, 195, 255), 22600:(165, 195, 255), 22700:(165, 194, 255), 22800:(165, 194, 255), 22900:(165, 194, 255), 23000:(164, 194, 255), 23100:(164, 194, 255), 23200:(164, 194, 255), 23300:(164, 194, 255), 23400:(164, 194, 255), 23500:(164, 194, 255), 23600:(164, 194, 255), 23700:(164, 194, 255), 23800:(164, 194, 255), 23900:(164, 194, 255), 24000:(163, 194, 255), 24100:(163, 194, 255), 24200:(163, 193, 255), 24300:(163, 193, 255), 24400:(163, 193, 255), 24500:(163, 193, 255), 24600:(163, 193, 255), 24700:(163, 193, 255), 24800:(163, 193, 255), 24900:(163, 193, 255), 25000:(163, 193, 255), 25100:(162, 193, 255), 25200:(162, 193, 255), 25300:(162, 193, 255), 25400:(162, 193, 255), 25500:(162, 193, 255), 25600:(162, 193, 255), 25700:(162, 193, 255), 25800:(162, 193, 255), 25900:(162, 192, 255), 26000:(162, 192, 255), 26100:(162, 192, 255), 26200:(162, 192, 255), 26300:(162, 192, 255), 26400:(161, 192, 255), 26500:(161, 192, 255), 26600:(161, 192, 255), 26700:(161, 192, 255), 26800:(161, 192, 255), 26900:(161, 192, 255), 27000:(161, 192, 255), 27100:(161, 192, 255), 27200:(161, 192, 255), 27300:(161, 192, 255), 27400:(161, 192, 255), 27500:(161, 192, 255), 27600:(161, 192, 255), 27700:(161, 192, 255), 27800:(160, 192, 255), 27900:(160, 192, 255), 28000:(160, 191, 255), 28100:(160, 191, 255), 28200:(160, 191, 255), 28300:(160, 191, 255), 28400:(160, 191, 255), 28500:(160, 191, 255), 28600:(160, 191, 255), 28700:(160, 191, 255), 28800:(160, 191, 255), 28900:(160, 191, 255), 29000:(160, 191, 255), 29100:(160, 191, 255), 29200:(160, 191, 255), 29300:(159, 191, 255), 29400:(159, 191, 255), 29500:(159, 191, 255), 29600:(159, 191, 255), 29700:(159, 191, 255), 29800:(159, 191, 255), 29900:(159, 191, 255), 30000:(159, 191, 255), 30100:(159, 191, 255), 30200:(159, 191, 255), 30300:(159, 191, 255), 30400:(159, 190, 255), 30500:(159, 190, 255), 30600:(159, 190, 255), 30700:(159, 190, 255), 30800:(159, 190, 255), 30900:(159, 190, 255), 31000:(159, 190, 255), 31100:(158, 190, 255), 31200:(158, 190, 255), 31300:(158, 190, 255), 31400:(158, 190, 255), 31500:(158, 190, 255), 31600:(158, 190, 255), 31700:(158, 190, 255), 31800:(158, 190, 255), 31900:(158, 190, 255), 32000:(158, 190, 255), 32100:(158, 190, 255), 32200:(158, 190, 255), 32300:(158, 190, 255), 32400:(158, 190, 255), 32500:(158, 190, 255), 32600:(158, 190, 255), 32700:(158, 190, 255), 32800:(158, 190, 255), 32900:(158, 190, 255), 33000:(158, 190, 255), 33100:(158, 190, 255), 33200:(157, 190, 255), 33300:(157, 190, 255), 33400:(157, 189, 255), 33500:(157, 189, 255), 33600:(157, 189, 255), 33700:(157, 189, 255), 33800:(157, 189, 255), 33900:(157, 189, 255), 34000:(157, 189, 255), 34100:(157, 189, 255), 34200:(157, 189, 255), 34300:(157, 189, 255), 34400:(157, 189, 255), 34500:(157, 189, 255), 34600:(157, 189, 255), 34700:(157, 189, 255), 34800:(157, 189, 255), 34900:(157, 189, 255), 35000:(157, 189, 255), 35100:(157, 189, 255), 35200:(157, 189, 255), 35300:(157, 189, 255), 35400:(157, 189, 255), 35500:(157, 189, 255), 35600:(156, 189, 255), 35700:(156, 189, 255), 35800:(156, 189, 255), 35900:(156, 189, 255), 36000:(156, 189, 255), 36100:(156, 189, 255), 36200:(156, 189, 255), 36300:(156, 189, 255), 36400:(156, 189, 255), 36500:(156, 189, 255), 36600:(156, 189, 255), 36700:(156, 189, 255), 36800:(156, 189, 255), 36900:(156, 189, 255), 37000:(156, 189, 255), 37100:(156, 189, 255), 37200:(156, 188, 255), 37300:(156, 188, 255), 37400:(156, 188, 255), 37500:(156, 188, 255), 37600:(156, 188, 255), 37700:(156, 188, 255), 37800:(156, 188, 255), 37900:(156, 188, 255), 38000:(156, 188, 255), 38100:(156, 188, 255), 38200:(156, 188, 255), 38300:(156, 188, 255), 38400:(155, 188, 255), 38500:(155, 188, 255), 38600:(155, 188, 255), 38700:(155, 188, 255), 38800:(155, 188, 255), 38900:(155, 188, 255), 39000:(155, 188, 255), 39100:(155, 188, 255), 39200:(155, 188, 255), 39300:(155, 188, 255), 39400:(155, 188, 255), 39500:(155, 188, 255), 39600:(155, 188, 255), 39700:(155, 188, 255), 39800:(155, 188, 255), 39900:(155, 188, 255), 40000:(155, 188, 255)}

    def start(self):
        async_call(self.color.get_configuration, None, self.get_configuration_async, self.increase_error_count)
        async_call(self.color.get_light, None, self.get_light_async, self.increase_error_count)

        self.cbe_color.set_period(50)
        self.cbe_illuminance.set_period(100)
        self.cbe_color_temperature.set_period(100)

        self.plot_widget.stop = False
        self.plot_widget_illuminance.stop = False
        self.plot_widget_color_temperature.stop = False

    def stop(self):
        self.cbe_color.set_period(0)
        self.cbe_illuminance.set_period(0)
        self.cbe_color_temperature.set_period(0)

        self.plot_widget.stop = True
        self.plot_widget_illuminance.stop = True
        self.plot_widget_color_temperature.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletColorV2.DEVICE_IDENTIFIER

    def format_color(self, i, value):
        if value >= 65535:
            self.plot_widget.get_key_item(i).setStyleSheet('QToolButton { color: red }')
        else:
            self.plot_widget.get_key_item(i).setStyleSheet('')

        return str(value)

    def cb_color(self, r, g, b, c):
        self.current_color_r.value = r
        self.current_color_g.value = g
        self.current_color_b.value = b
        self.current_color_c.value = c

        if r >= 65535 or g >= 65535 or b >= 65535:
            self.plot_widget_illuminance.get_key_item(0).setStyleSheet('QLabel { color: red }')
            self.plot_widget_color_temperature.get_key_item(0).setStyleSheet('QLabel { color: red }')
        else:
            self.plot_widget_illuminance.get_key_item(0).setStyleSheet('')
            self.plot_widget_color_temperature.get_key_item(0).setStyleSheet('')

        normalize = 0xFFFF
        self.color_frame.set_color(QColor(r * 255 // normalize, g * 255 // normalize, b * 255 // normalize))

    def cb_illuminance(self, illuminance):
        self.current_illuminance.value = round(illuminance * 700.0 / self.current_gain_factor / self.current_conversion_time, 1)

        i = int(self.current_illuminance.value) * 255 // 20000

        if i > 255:
            i = 255

        self.illuminance_frame.set_color(QColor(i, i, i))

    def cb_color_temperature(self, color_temperature):
        self.current_color_temperature.value = color_temperature

        m = color_temperature % 100
        color_temperature -= m

        if m > 50:
            color_temperature += 100

        if color_temperature < 1000:
            color_temperature = 1000

        if color_temperature > 40000:
            color_temperature = 40000

        r, g, b = self.k_to_rgb[color_temperature]

        self.color_temperature_frame.set_color(QColor(r, g, b))

    def get_light_async(self, enable):
        self.light_checkbox.setChecked(enable)

    def light_state_changed(self, state):
        self.color.set_light(state == Qt.Checked)

    def get_configuration_async(self, config):
        gain, gain_factor, conv, conv_time = self.gain_conv_to_combo(config.gain, config.integration_time)

        self.gain_combo.setCurrentIndex(gain)
        self.conversion_combo.setCurrentIndex(conv)

        self.current_gain_factor = gain_factor
        self.current_conversion_time = conv_time

    def gain_conv_to_combo(self, gain, conv):
        if gain == BrickletColorV2.GAIN_1X:
            gain = 0
            gain_factor = 1
        elif gain == BrickletColorV2.GAIN_4X:
            gain = 1
            gain_factor = 4
        elif gain == BrickletColorV2.GAIN_16X:
            gain = 2
            gain_factor = 16
        elif gain == BrickletColorV2.GAIN_60X:
            gain = 3
            gain_factor = 60

        if conv == BrickletColorV2.INTEGRATION_TIME_2MS:
            conv = 0
            conv_time = 2.4
        elif conv == BrickletColorV2.INTEGRATION_TIME_24MS:
            conv = 1
            conv_time = 24
        elif conv == BrickletColorV2.INTEGRATION_TIME_101MS:
            conv = 2
            conv_time = 101
        elif conv == BrickletColorV2.INTEGRATION_TIME_154MS:
            conv = 3
            conv_time = 154
        elif conv == BrickletColorV2.INTEGRATION_TIME_700MS:
            conv = 4
            conv_time = 700

        return gain, gain_factor, conv, conv_time

    def combo_to_gain_conv(self, gain, conv):
        if gain == 0:
            gain = BrickletColorV2.GAIN_1X
            gain_factor = 1
        elif gain == 1:
            gain = BrickletColorV2.GAIN_4X
            gain_factor = 4
        elif gain == 2:
            gain = BrickletColorV2.GAIN_16X
            gain_factor = 16
        elif gain == 3:
            gain = BrickletColorV2.GAIN_60X
            gain_factor = 60

        if conv == 0:
            conv = BrickletColorV2.INTEGRATION_TIME_2MS
            conv_time = 2.4
        elif conv == 1:
            conv = BrickletColorV2.INTEGRATION_TIME_24MS
            conv_time = 24
        elif conv == 2:
            conv = BrickletColorV2.INTEGRATION_TIME_101MS
            conv_time = 101
        elif conv == 3:
            conv = BrickletColorV2.INTEGRATION_TIME_154MS
            conv_time = 154
        elif conv == 4:
            conv = BrickletColorV2.INTEGRATION_TIME_700MS
            conv_time = 700

        return gain, gain_factor, conv, conv_time

    def gain_changed(self, gain):
        conversion = self.conversion_combo.currentIndex()

        g, gf, c, ct = self.combo_to_gain_conv(gain, conversion)

        self.current_gain_factor = gf
        self.current_conversion_time = ct

        self.color.set_configuration(g, c)

    def conversion_changed(self, conversion):
        gain = self.gain_combo.currentIndex()

        g, gf, c, ct = self.combo_to_gain_conv(gain, conversion)

        self.current_gain_factor = gf
        self.current_conversion_time = ct

        self.color.set_configuration(g, c)
