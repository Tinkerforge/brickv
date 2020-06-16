# -*- coding: utf-8 -*-
"""
Barometer Plugin 2.0
Copyright (C) 2018 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

barometer_v2.py: Barometer 2.0 Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, \
                            QPushButton, QSpinBox, QFrame, QDoubleSpinBox, QDialog

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_barometer_v2 import BrickletBarometerV2
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import get_modeless_dialog_flags
from brickv.plugin_system.plugins.barometer_v2.ui_calibration import Ui_Calibration

METER_TO_FEET_DIVISOR = 0.3048

class Calibration(QDialog, Ui_Calibration):
    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())
        self.parent = parent

        self.setupUi(self)

        # Synced air pressure, altitude and temperature. Updated with callbacks.
        self.air_pressure = 0
        self.altitude = 0
        self.temperature = 0

        self.btn_cal_remove.clicked.connect(self.btn_cal_remove_clicked)
        self.btn_cal_calibrate.clicked.connect(self.btn_cal_calibrate_clicked)
        self.btn_close.clicked.connect(self.close)

        self.cbe_air_pressure = CallbackEmulator(self.parent.barometer.get_air_pressure,
                                                 None,
                                                 self.cb_air_pressure,
                                                 self.parent.increase_error_count)

        self.cbe_altitude = CallbackEmulator(self.parent.barometer.get_altitude,
                                             None,
                                             self.cb_altitude,
                                             self.parent.increase_error_count)

        self.cbe_temperature = CallbackEmulator(self.parent.barometer.get_temperature,
                                                None,
                                                self.cb_temperature,
                                                self.parent.increase_error_count)

    def show(self):
        QDialog.show(self)

        self.cbe_air_pressure.set_period(100)
        self.cbe_altitude.set_period(100)
        self.cbe_temperature.set_period(100)

        self.sbox_cal_actual_air_pressure.setValue(1013.250)

        async_call(self.parent.barometer.get_calibration,
                   None,
                   self.get_calibration_async,
                   self.parent.increase_error_count)

    def btn_cal_remove_clicked(self):
        self.parent.barometer.set_calibration(0, 0)

        async_call(self.parent.barometer.get_calibration,
                   None,
                   self.get_calibration_async,
                   self.parent.increase_error_count)

    def btn_cal_calibrate_clicked(self):
        self.parent.barometer.set_calibration(int(self.air_pressure * 1000), int(self.sbox_cal_actual_air_pressure.value() * 1000))

        async_call(self.parent.barometer.get_calibration,
                   None,
                   self.get_calibration_async,
                   self.parent.increase_error_count)

    def get_calibration_async(self, cal):
        if cal.measured_air_pressure == 0 and cal.actual_air_pressure == 0:
            self.sbox_cal_actual_air_pressure.setValue(1013.25)
        else:
            self.sbox_cal_actual_air_pressure.setValue(cal.actual_air_pressure / 1000.0)

    def cb_air_pressure(self, air_pressure):
        self.air_pressure = air_pressure / 1000.0
        self.lbl_air_pressure.setText('{:.3f} hPa (QFE)'.format(self.air_pressure))

    def cb_altitude(self, altitude):
        self.altitude = altitude / 1000.0
        self.lbl_altitude.setText('{:.3f} m ({:.3f} ft)'.format(self.altitude, self.altitude / METER_TO_FEET_DIVISOR))

    def cb_temperature(self, temperature):
        self.temperature = temperature / 100.0
        self.lbl_temperature.setText('{:.2f} °C'.format(self.temperature))

    def closeEvent(self, _event):
        self.cbe_air_pressure.set_period(0)
        self.cbe_altitude.set_period(0)
        self.cbe_temperature.set_period(0)
        self.parent.btn_calibration.setEnabled(True)


class BarometerV2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletBarometerV2, *args)

        self.barometer = self.device

        self.cbe_air_pressure = CallbackEmulator(self.barometer.get_air_pressure,
                                                 None,
                                                 self.cb_air_pressure,
                                                 self.increase_error_count)

        self.cbe_altitude = CallbackEmulator(self.barometer.get_altitude,
                                             None,
                                             self.cb_altitude,
                                             self.increase_error_count)

        self.cbe_temperature = CallbackEmulator(self.barometer.get_temperature,
                                                None,
                                                self.cb_temperature,
                                                self.increase_error_count)

        self.current_altitude = CurveValueWrapper()
        self.current_air_pressure = CurveValueWrapper()

        self.calibration = None
        self.btn_clear_graphs = QPushButton('Clear Graphs')
        self.btn_calibration = QPushButton('Calibration...')
        self.btn_calibration.clicked.connect(self.btn_calibration_clicked)

        self.lbl_temperature_value = QLabel('-')

        self.sbox_reference_air_pressure = QDoubleSpinBox()
        self.sbox_reference_air_pressure.setMinimum(260)
        self.sbox_reference_air_pressure.setMaximum(1260)
        self.sbox_reference_air_pressure.setDecimals(3)
        self.sbox_reference_air_pressure.setValue(1013.25)
        self.sbox_reference_air_pressure.setSingleStep(1)
        self.btn_use_current = QPushButton('Use Current')
        self.btn_use_current.clicked.connect(self.btn_use_current_clicked)
        self.sbox_reference_air_pressure.editingFinished.connect(self.sbox_reference_air_pressure_editing_finished)

        self.sbox_moving_avg_len_air_pressure = QSpinBox()
        self.sbox_moving_avg_len_air_pressure.setMinimum(1)
        self.sbox_moving_avg_len_air_pressure.setMaximum(1000)
        self.sbox_moving_avg_len_air_pressure.setSingleStep(1)
        self.sbox_moving_avg_len_air_pressure.setValue(100)
        self.sbox_moving_avg_len_air_pressure.editingFinished.connect(self.sbox_moving_avg_len_editing_finished)

        self.sbox_moving_avg_len_temperature = QSpinBox()
        self.sbox_moving_avg_len_temperature.setMinimum(1)
        self.sbox_moving_avg_len_temperature.setMaximum(1000)
        self.sbox_moving_avg_len_temperature.setSingleStep(1)
        self.sbox_moving_avg_len_temperature.setValue(100)
        self.sbox_moving_avg_len_temperature.editingFinished.connect(self.sbox_moving_avg_len_editing_finished)

        plot_config_air_pressure = [('Air Pressure',
                                     Qt.red,
                                     self.current_air_pressure,
                                     '{:.3f} hPa (QFE)'.format)]

        plot_config_altitude = [('Altitude',
                                 Qt.darkGreen,
                                 self.current_altitude,
                                 lambda value: '{:.3f} m ({:.3f} ft)'.format(value, value / METER_TO_FEET_DIVISOR))]

        self.plot_widget_air_pressure = PlotWidget('Air Pressure [hPa]',
                                                   plot_config_air_pressure,
                                                   self.btn_clear_graphs,
                                                   y_resolution=0.001)

        self.plot_widget_altitude = PlotWidget('Altitude [m]',
                                               plot_config_altitude,
                                               self.btn_clear_graphs,
                                               y_resolution=0.001)

        self.combo_data_rate = QComboBox()
        self.combo_data_rate.addItem('Off', BrickletBarometerV2.DATA_RATE_OFF)
        self.combo_data_rate.addItem('1 Hz', BrickletBarometerV2.DATA_RATE_1HZ)
        self.combo_data_rate.addItem('10 Hz', BrickletBarometerV2.DATA_RATE_10HZ)
        self.combo_data_rate.addItem('25 Hz', BrickletBarometerV2.DATA_RATE_25HZ)
        self.combo_data_rate.addItem('50 Hz', BrickletBarometerV2.DATA_RATE_50HZ)
        self.combo_data_rate.addItem('75 Hz', BrickletBarometerV2.DATA_RATE_75HZ)
        self.combo_data_rate.currentIndexChanged.connect(self.new_sensor_config)

        self.combo_air_pressure_low_pass_filter = QComboBox()
        self.combo_air_pressure_low_pass_filter.addItem('Off', BrickletBarometerV2.LOW_PASS_FILTER_OFF)
        self.combo_air_pressure_low_pass_filter.addItem('1/9th', BrickletBarometerV2.LOW_PASS_FILTER_1_9TH)
        self.combo_air_pressure_low_pass_filter.addItem('1/20th', BrickletBarometerV2.LOW_PASS_FILTER_1_20TH)
        self.combo_air_pressure_low_pass_filter.currentIndexChanged.connect(self.new_sensor_config)

        # Layout
        layout_h1 = QHBoxLayout()
        layout_h1.addWidget(self.plot_widget_air_pressure)
        layout_h1.addWidget(self.plot_widget_altitude)

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h1)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout.addWidget(line)

        layout_h2 = QHBoxLayout()
        layout_h2.addWidget(QLabel('Reference Air Pressure [hPa]:'))
        layout_h2.addWidget(self.sbox_reference_air_pressure)
        layout_h2.addWidget(self.btn_use_current)
        layout_h2.addStretch()
        layout_h2.addWidget(QLabel('Temperature:'))
        layout_h2.addWidget(self.lbl_temperature_value)
        layout_h2.addStretch()
        layout_h2.addWidget(self.btn_clear_graphs)

        layout.addLayout(layout_h2)

        layout_h3 = QHBoxLayout()
        layout_h3.addWidget(QLabel('Air Pressure Moving Average Length:'))
        layout_h3.addWidget(self.sbox_moving_avg_len_air_pressure)
        layout_h3.addStretch()
        layout_h3.addWidget(QLabel('Temperature Moving Average Length:'))
        layout_h3.addWidget(self.sbox_moving_avg_len_temperature)

        layout.addLayout(layout_h3)

        layout_h4 = QHBoxLayout()
        layout_h4.addWidget(QLabel('Data Rate:'))
        layout_h4.addWidget(self.combo_data_rate)
        layout_h4.addStretch()
        layout_h4.addWidget(QLabel('Air Pressure Low Pass Filter:'))
        layout_h4.addWidget(self.combo_air_pressure_low_pass_filter)
        layout_h4.addStretch()
        layout_h4.addWidget(self.btn_calibration)

        layout.addLayout(layout_h4)

    def start(self):
        async_call(self.barometer.get_reference_air_pressure, None, self.get_reference_air_pressure_async, self.increase_error_count)
        async_call(self.barometer.get_moving_average_configuration, None, self.get_moving_average_configuration_async, self.increase_error_count)
        async_call(self.barometer.get_sensor_configuration, None, self.get_sensor_configuration_async, self.increase_error_count)

        self.cbe_air_pressure.set_period(50)
        self.cbe_altitude.set_period(50)
        self.cbe_temperature.set_period(100)

        self.plot_widget_air_pressure.stop = False
        self.plot_widget_altitude.stop = False

    def stop(self):
        self.cbe_air_pressure.set_period(0)
        self.cbe_altitude.set_period(0)
        self.cbe_temperature.set_period(0)

        self.plot_widget_air_pressure.stop = True
        self.plot_widget_altitude.stop = True

    def destroy(self):
        if self.calibration != None:
            self.calibration.close()

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletBarometerV2.DEVICE_IDENTIFIER

    def cb_air_pressure(self, air_pressure):
        self.current_air_pressure.value = air_pressure / 1000.0

    def cb_altitude(self, altitude):
        self.current_altitude.value = altitude / 1000.0

    def cb_temperature(self, temperature):
        self.lbl_temperature_value.setText('{:.2f} °C'.format(temperature / 100.0))

    def get_reference_air_pressure_async(self, air_pressure):
        self.sbox_reference_air_pressure.setValue(air_pressure / 1000.0)

    def btn_use_current_clicked(self):
        self.barometer.set_reference_air_pressure(0)
        async_call(self.barometer.get_reference_air_pressure, None, self.get_reference_air_pressure_async, self.increase_error_count)

    def sbox_reference_air_pressure_editing_finished(self):
        self.barometer.set_reference_air_pressure(self.sbox_reference_air_pressure.value() * 1000.0)

    def get_moving_average_configuration_async(self, avg):
        m_avg_air_pressure, m_avg_temperature = avg

        self.sbox_moving_avg_len_air_pressure.setValue(m_avg_air_pressure)
        self.sbox_moving_avg_len_temperature.setValue(m_avg_temperature)

    def sbox_moving_avg_len_editing_finished(self):
        self.barometer.set_moving_average_configuration(self.sbox_moving_avg_len_air_pressure.value(),
                                                        self.sbox_moving_avg_len_temperature.value())

    def get_sensor_configuration_async(self, config):
        data_rate, air_pressure_low_pass_filter = config

        self.combo_data_rate.setCurrentIndex(self.combo_data_rate.findData(data_rate))
        self.combo_air_pressure_low_pass_filter.setCurrentIndex(self.combo_air_pressure_low_pass_filter.findData(air_pressure_low_pass_filter))

    def new_sensor_config(self):
        data_rate = self.combo_data_rate.itemData(self.combo_data_rate.currentIndex())
        air_pressure_low_pass_filter = self.combo_air_pressure_low_pass_filter.itemData(self.combo_air_pressure_low_pass_filter.currentIndex())

        self.barometer.set_sensor_configuration(data_rate, air_pressure_low_pass_filter)

    def btn_calibration_clicked(self):
        if self.calibration == None:
            self.calibration = Calibration(self)

        self.btn_calibration.setEnabled(False)
        self.calibration.show()
