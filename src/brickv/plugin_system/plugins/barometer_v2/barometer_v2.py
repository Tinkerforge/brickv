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

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QGridLayout, \
                        QPushButton, QSpinBox, QFrame, QDoubleSpinBox, QDialog

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_barometer_v2 import BrickletBarometerV2
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import get_modeless_dialog_flags
from brickv.plugin_system.plugins.barometer_v2.ui_calibration import Ui_Calibration

class Calibration(QDialog, Ui_Calibration):
    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())
        self.parent = parent

        self.setupUi(self)

        # Synced air pressure, altitude and temperature. Updated with callbacks.
        self.p = 0
        self.a = 0
        self.t = 0

        self.btn_cal_remove.clicked.connect(self.btn_cal_remove_clicked)
        self.btn_cal_calibrate.clicked.connect(self.btn_cal_calibrate_clicked)
 
        self.cbe_p = CallbackEmulator(self.parent.barometer.get_air_pressure,
                                      self.cb_get_p,
                                      self.parent.increase_error_count)

        self.cbe_a = CallbackEmulator(self.parent.barometer.get_altitude,
                                      self.cb_get_a,
                                      self.parent.increase_error_count)

        self.cbe_t = CallbackEmulator(self.parent.barometer.get_temperature,
                                      self.cb_get_t,
                                      self.parent.increase_error_count)

    def show(self):
        QDialog.show(self)

        self.cbe_p.set_period(100)
        self.cbe_a.set_period(100)
        self.cbe_t.set_period(100)

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
        self.parent.barometer.set_calibration(int(self.p * 1000), int(self.sbox_cal_actual_air_pressure.value()*1000))

        async_call(self.parent.barometer.get_calibration,
                   None,
                   self.get_calibration_async,
                   self.parent.increase_error_count)

    def get_calibration_async(self, cal):
        if cal.measured_air_pressure == 0 and cal.actual_air_pressure == 0:
            self.sbox_cal_actual_air_pressure.setValue(1013.250)
        else:
            self.sbox_cal_actual_air_pressure.setValue(cal.actual_air_pressure/1000.0)

    def cb_get_p(self, air_pressure):
        self.p = air_pressure / 1000.0
        self.lbl_p.setText('{:.3f} mbar (QFE)'.format(self.p))

    def cb_get_a(self, altitude):
        self.a = altitude / 1000.0
        self.lbl_a.setText('{:.3f} m ({:.3f} ft)'.format(self.a, self.a/0.3048))

    def cb_get_t(self, temperature):
        self.t = temperature/100.0
        self.lbl_t.setText(u'{:.3f} °C'.format(self.t))

    def closeEvent(self, event):
        self.cbe_p.set_period(0)
        self.cbe_a.set_period(0)
        self.cbe_t.set_period(0)
        self.parent.btn_calibration.setEnabled(True)

class BarometerV2(COMCUPluginBase):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletBarometerV2, *args)

        self.barometer = self.device

        self.cbe_air_pressure = CallbackEmulator(self.barometer.get_air_pressure,
                                                 self.cb_get_air_pressure,
                                                 self.increase_error_count)

        self.cbe_altitude = CallbackEmulator(self.barometer.get_altitude,
                                             self.cb_get_altitude,
                                             self.increase_error_count)

        self.cbe_temperature = CallbackEmulator(self.barometer.get_temperature,
                                                self.cb_get_temperature,
                                                self.increase_error_count)

        self.current_altitude = None
        self.current_temperature = None
        self.current_air_pressure = None

        self.calibration = None
        self.btn_clear_graphs = QPushButton('Clear Graphs')
        self.btn_calibration = QPushButton('Calibration...')
        self.btn_calibration.clicked.connect(self.btn_calibration_clicked)

        self.lbl_temperature = QLabel(u'Temperature:')
        self.lbl_temperature_value = QLabel('-')

        self.lbl_reference = QLabel('Reference Air Pressure:')
        self.sbox_reference_air_pressure = QDoubleSpinBox()
        self.sbox_reference_air_pressure.setSuffix(' mbar')
        self.sbox_reference_air_pressure.setMinimum(260)
        self.sbox_reference_air_pressure.setMaximum(1260)
        self.sbox_reference_air_pressure.setDecimals(3)
        self.sbox_reference_air_pressure.setValue(1013.250)
        self.sbox_reference_air_pressure.setSingleStep(1)
        self.btn_use_current = QPushButton('Use Current')
        self.btn_use_current.clicked.connect(self.btn_use_current_clicked)
        self.sbox_reference_air_pressure.valueChanged.connect(self.sbox_reference_air_pressure_value_changed)

        self.sbox_moving_avg_len_altitude = QSpinBox()
        self.sbox_moving_avg_len_temperature = QSpinBox()
        self.sbox_moving_avg_len_air_pressure = QSpinBox()
        self.sbox_moving_avg_len_altitude.setMinimum(1)
        self.sbox_moving_avg_len_altitude.setMaximum(1000)
        self.sbox_moving_avg_len_altitude.setSingleStep(1)
        self.sbox_moving_avg_len_altitude.setValue(100)
        self.sbox_moving_avg_len_temperature.setMinimum(1)
        self.sbox_moving_avg_len_temperature.setMaximum(1000)
        self.sbox_moving_avg_len_temperature.setSingleStep(1)
        self.sbox_moving_avg_len_temperature.setValue(100)
        self.sbox_moving_avg_len_air_pressure.setMinimum(1)
        self.sbox_moving_avg_len_air_pressure.setMaximum(1000)
        self.sbox_moving_avg_len_air_pressure.setSingleStep(1)
        self.sbox_moving_avg_len_air_pressure.setValue(100)
        self.sbox_moving_avg_len_altitude.editingFinished.connect(self.sbox_moving_avg_len_editing_finished)
        self.sbox_moving_avg_len_temperature.editingFinished.connect(self.sbox_moving_avg_len_editing_finished)
        self.sbox_moving_avg_len_air_pressure.editingFinished.connect(self.sbox_moving_avg_len_editing_finished)

        plot_config_air_pressure = [('Air Pressure',
                                    Qt.red,
                                    lambda: self.current_air_pressure,
                                    '{:.3f} mbar (QFE)'.format)]

        plot_config_altitude = [('Altitude',
                                Qt.darkGreen,
                                lambda: self.current_altitude,
                                lambda value: '{:.3f} m ({:.3f} ft)'.format(value, value / 0.3048))]

        self.plot_widget_air_pressure = PlotWidget('Air Pressure [mbar]',
                                                   plot_config_air_pressure,
                                                   self.btn_clear_graphs)

        self.plot_widget_altitude= PlotWidget('Altitude [m]',
                                              plot_config_altitude,
                                              self.btn_clear_graphs)

        # Layout
        line = QFrame()
        layout_h1 = QHBoxLayout()
        layout_h2 = QHBoxLayout()
        layout_h3 = QHBoxLayout()
        layout_g1 = QGridLayout()
        layout = QVBoxLayout(self)

        layout_h1.addWidget(self.plot_widget_air_pressure)
        layout_h1.addWidget(self.plot_widget_altitude)
        layout_h2.addWidget(self.btn_clear_graphs)

        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout_g1.addWidget(self.lbl_temperature, 0, 0)
        layout_g1.addWidget(self.lbl_temperature_value, 0, 1, 1, 3)
        layout_g1.addWidget(self.lbl_reference, 1, 0)
        layout_g1.addWidget(self.sbox_reference_air_pressure, 1, 1)
        layout_g1.addWidget(self.btn_use_current, 1, 2, 1, 2)
        layout_g1.addWidget(QLabel('Moving Average Length (Air Pressure, Altitude, Temperature):'), 2, 0)
        layout_g1.addWidget(self.sbox_moving_avg_len_air_pressure, 2, 1)
        layout_g1.addWidget(self.sbox_moving_avg_len_altitude, 2, 2)
        layout_g1.addWidget(self.sbox_moving_avg_len_temperature, 2, 3)

        layout_h3.addWidget(self.btn_calibration)

        layout.addLayout(layout_h1)
        layout.addLayout(layout_h2)
        layout.addWidget(line)
        layout.addLayout(layout_g1)
        layout.addLayout(layout_h3)

    def start(self):
        async_call(self.barometer.get_altitude,
                   None,
                   self.cb_get_altitude,
                   self.increase_error_count)

        async_call(self.barometer.get_temperature,
                   None,
                   self.cb_get_temperature,
                   self.increase_error_count)

        async_call(self.barometer.get_air_pressure,
                   None,
                   self.cb_get_air_pressure,
                   self.increase_error_count)

        async_call(self.barometer.get_reference_air_pressure,
                   None,
                   self.get_reference_air_pressure_async,
                   self.increase_error_count)

        async_call(self.barometer.get_moving_average_configuration,
                   None,
                   self.get_moving_average_configuration_async,
                   self.increase_error_count)

        self.cbe_altitude.set_period(100)
        self.cbe_temperature.set_period(100)
        self.cbe_air_pressure.set_period(100)

        self.plot_widget_altitude.stop = False
        self.plot_widget_air_pressure.stop = False

    def stop(self):
        self.cbe_altitude.set_period(0)
        self.cbe_temperature.set_period(0)
        self.cbe_air_pressure.set_period(0)

        self.plot_widget_altitude.stop = True
        self.plot_widget_air_pressure.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletBarometerV2.DEVICE_IDENTIFIER

    def cb_get_altitude(self, altitude):
        self.current_altitude = altitude / 1000.0

    def cb_get_temperature(self, temperature):
        self.current_temperature = temperature / 100.0
        self.lbl_temperature_value.setText(u'{:.3f} °C'.format(self.current_temperature))

    def cb_get_air_pressure(self, air_pressure):
        self.current_air_pressure = air_pressure / 1000.0

    def get_reference_air_pressure_async(self, air_pressure):
        self.sbox_reference_air_pressure.setValue(air_pressure / 1000.0)

    def btn_use_current_clicked(self):
        self.barometer.set_reference_air_pressure(0)

        async_call(self.barometer.get_reference_air_pressure,
                   None,
                   self.get_reference_air_pressure_async,
                   self.increase_error_count)

    def sbox_reference_air_pressure_value_changed(self, value):
        self.barometer.set_reference_air_pressure(value * 1000.0)

    def get_moving_average_configuration_async(self, avg):
        m_avg_air_pressure, m_avg_altitude, m_avg_temperature = avg

        self.sbox_moving_avg_len_altitude.setValue(m_avg_altitude)
        self.sbox_moving_avg_len_temperature.setValue(m_avg_temperature)
        self.sbox_moving_avg_len_air_pressure.setValue(m_avg_air_pressure)

    def sbox_moving_avg_len_editing_finished(self):
        self.barometer.set_moving_average_configuration(self.sbox_moving_avg_len_air_pressure.value(),
                                                        self.sbox_moving_avg_len_altitude.value(),
                                                        self.sbox_moving_avg_len_temperature.value())

    def btn_calibration_clicked(self):
        if self.calibration == None:
            self.calibration = Calibration(self)

        self.btn_calibration.setEnabled(False)
        self.calibration.show()
