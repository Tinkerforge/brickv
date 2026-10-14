# -*- coding: utf-8 -*-
"""
CO2 2.0 Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

co2_v2.py: CO2 2.0 Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QMessageBox, QComboBox, QGroupBox, QWidget

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_co2_v2 import BrickletCO2V2
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import get_main_window

CALIBRATION_FIRMWARE_VERSION = (2, 0, 4)

CALIBRATION_MODE_AUTOMATIC = 0
CALIBRATION_MODE_FORCED = 1

HINT_AUTOMATIC = 'The sensor recalibrates itself. This requires fresh air for at least one hour every day.'
HINT_FORCED = 'For sensors that do not regularly see fresh air. Recalibrate with a known CO2 concentration.'
HINT_OLD_FIRMWARE = 'Firmware version 2.0.4 or newer is required to change the calibration mode.'

class CO2V2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletCO2V2, *args)

        self.co2 = self.device

        self.has_calibration = False

        self.cbe_all_values = CallbackEmulator(self,
                                               self.co2.get_all_values,
                                               None,
                                               self.cb_all_values,
                                               self.increase_error_count)

        self.cbe_forced_recalibration = CallbackEmulator(self,
                                                         self.co2.get_forced_recalibration,
                                                         None,
                                                         self.cb_forced_recalibration,
                                                         self.increase_error_count)

        self.current_co2 = CurveValueWrapper() # int, ppm
        self.current_temperature = CurveValueWrapper() # float, °C
        self.current_humidity = CurveValueWrapper() # float, %RH

        plots_co2 = [('CO2', Qt.red, self.current_co2, '{} PPM'.format)]
        self.plot_widget_co2 = PlotWidget('CO2 [PPM]', plots_co2, y_resolution=1.0)

        plots_temperature = [('Temperature', Qt.red, self.current_temperature, '{} °C'.format)]
        self.plot_widget_temperature = PlotWidget('Temperature [°C]', plots_temperature, y_resolution=0.01)

        plots_humidity = [('Relative Humidity', Qt.red, self.current_humidity, '{} %RH'.format)]
        self.plot_widget_humidity = PlotWidget('Relative Humidity [%RH]', plots_humidity, y_resolution=0.01)

        layout_plot1 = QHBoxLayout()
        layout_plot1.addWidget(self.plot_widget_co2)

        layout_plot2 = QHBoxLayout()
        layout_plot2.addWidget(self.plot_widget_temperature)
        layout_plot2.addWidget(self.plot_widget_humidity)

        # Calibration mode
        self.combo_calibration_mode = QComboBox()
        self.combo_calibration_mode.addItem('Automatic Self-Calibration')
        self.combo_calibration_mode.addItem('Forced Recalibration')
        self.combo_calibration_mode.currentIndexChanged.connect(self.calibration_mode_changed)

        self.label_calibration_hint = QLabel()
        self.label_calibration_hint.setWordWrap(True)

        layout_mode = QHBoxLayout()
        layout_mode.addWidget(QLabel('Mode:'))
        layout_mode.addWidget(self.combo_calibration_mode)
        layout_mode.addWidget(self.label_calibration_hint, 1)

        # Forced recalibration, only shown if automatic self-calibration is disabled
        self.spinbox_frc = QSpinBox()
        self.spinbox_frc.setRange(400, 2000)
        self.spinbox_frc.setValue(400)
        self.spinbox_frc.setSuffix(' ppm')

        self.button_frc = QPushButton('Recalibrate')
        self.button_frc.clicked.connect(self.frc_clicked)

        label_frc_title = QLabel('Last Reference:')
        label_frc_title.setToolTip('Reference CO2 concentration of the most recent forced recalibration as reported by the sensor.\n'
                                   'The sensor reports 400 ppm after a power loss, but the recalibration itself stays in use.')
        self.label_frc = QLabel('-')

        self.widget_frc = QWidget()
        layout_frc = QHBoxLayout(self.widget_frc)
        layout_frc.setContentsMargins(0, 0, 0, 0)
        layout_frc.addWidget(QLabel('Reference CO2 Concentration:'))
        layout_frc.addWidget(self.spinbox_frc)
        layout_frc.addWidget(self.button_frc)
        layout_frc.addSpacing(20)
        layout_frc.addWidget(label_frc_title)
        layout_frc.addWidget(self.label_frc)
        layout_frc.addStretch()

        group_calibration = QGroupBox('Calibration')
        layout_calibration = QVBoxLayout(group_calibration)
        layout_calibration.addLayout(layout_mode)
        layout_calibration.addWidget(self.widget_frc)

        layout_main = QVBoxLayout(self)
        layout_main.addLayout(layout_plot1)
        layout_main.addLayout(layout_plot2)
        layout_main.addWidget(group_calibration)

        self.update_calibration_ui()

    def cb_all_values(self, values):
        self.current_co2.value = values.co2_concentration
        self.current_temperature.value = values.temperature / 100.0
        self.current_humidity.value = values.humidity / 100.0

    def cb_forced_recalibration(self, co2_concentration):
        self.label_frc.setText('{} ppm'.format(co2_concentration))

    def update_calibration_ui(self):
        forced = self.combo_calibration_mode.currentIndex() == CALIBRATION_MODE_FORCED

        self.combo_calibration_mode.setEnabled(self.has_calibration)
        self.widget_frc.setVisible(self.has_calibration and forced)

        if not self.has_calibration:
            self.label_calibration_hint.setText(HINT_OLD_FIRMWARE)
        elif forced:
            self.label_calibration_hint.setText(HINT_FORCED)
        else:
            self.label_calibration_hint.setText(HINT_AUTOMATIC)

    def set_calibration_mode(self, mode):
        self.combo_calibration_mode.blockSignals(True)
        self.combo_calibration_mode.setCurrentIndex(mode)
        self.combo_calibration_mode.blockSignals(False)

        self.update_calibration_ui()

    def get_automatic_self_calibration_async(self, enabled):
        self.set_calibration_mode(CALIBRATION_MODE_AUTOMATIC if enabled else CALIBRATION_MODE_FORCED)

    def calibration_mode_changed(self, mode):
        self.update_calibration_ui()

        async_call(self.co2.set_automatic_self_calibration, mode == CALIBRATION_MODE_AUTOMATIC, None, self.increase_error_count)

    def frc_clicked(self):
        co2_concentration = self.spinbox_frc.value()

        text = 'The CO2 sensor will be permanently recalibrated to a reference CO2 concentration of {0} ppm.\n\n' \
               'Make sure that the Bricklet is operated in a stable environment with a known CO2 concentration of {0} ppm ' \
               'close to the sensor. The recalibration is applied once the Bricklet has been running for at least two minutes.'.format(co2_concentration)

        button = QMessageBox.question(get_main_window(), 'Forced Recalibration', text, QMessageBox.Ok, QMessageBox.Cancel)

        if button != QMessageBox.Ok:
            return

        async_call(self.co2.set_forced_recalibration, co2_concentration, None, self.increase_error_count)

    def start(self):
        self.has_calibration = self.firmware_version >= CALIBRATION_FIRMWARE_VERSION

        self.update_calibration_ui()

        if self.has_calibration:
            async_call(self.co2.get_automatic_self_calibration, None, self.get_automatic_self_calibration_async, self.increase_error_count)
            self.cbe_forced_recalibration.set_period(1000)
        else:
            # Before firmware version 2.0.4 ASC is always enabled
            self.set_calibration_mode(CALIBRATION_MODE_AUTOMATIC)

        self.cbe_all_values.set_period(250)

        self.plot_widget_co2.stop = False
        self.plot_widget_temperature.stop = False
        self.plot_widget_humidity.stop = False

    def stop(self):
        self.cbe_all_values.set_period(0)
        self.cbe_forced_recalibration.set_period(0)

        self.plot_widget_co2.stop = True
        self.plot_widget_temperature.stop = True
        self.plot_widget_humidity.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletCO2V2.DEVICE_IDENTIFIER
