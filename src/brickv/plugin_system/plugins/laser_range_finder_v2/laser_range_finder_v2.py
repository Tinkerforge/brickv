# -*- coding: utf-8 -*-
"""
Laser Range Finder 2.0 Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

laser_range_finder_v2.py: Laser Range Finder 2.0 Plugin Implementation

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
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QSpinBox, QCheckBox, \
                            QFrame, QComboBox

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_laser_range_finder_v2 import BrickletLaserRangeFinderV2
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

def format_distance(distance): # cm
    if distance < 100:
        return str(distance) + ' cm'
    else:
        return '{:.2f} m'.format(round(distance / 100.0, 2))

class LaserRangeFinderV2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletLaserRangeFinderV2, *args)

        self.lrf = self.device

        self.cbe_distance = CallbackEmulator(self.lrf.get_distance,
                                             None,
                                             self.cb_distance,
                                             self.increase_error_count)
        self.cbe_velocity = CallbackEmulator(self.lrf.get_velocity,
                                             None,
                                             self.cb_velocity,
                                             self.increase_error_count)

        self.current_distance = CurveValueWrapper() # int, cm
        self.current_velocity = CurveValueWrapper() # float, m/s

        plots_distance = [('Distance', Qt.red, self.current_distance, format_distance)]
        plots_velocity = [('Velocity', Qt.red, self.current_velocity, '{:.2f} m/s'.format)]
        self.plot_widget_distance = PlotWidget('Distance [cm]', plots_distance, y_resolution=1.0)
        self.plot_widget_velocity = PlotWidget('Velocity [m/s]', plots_velocity, y_resolution=0.01)

        self.label_average_distance = QLabel('Moving Average for Distance:')

        self.spin_average_distance = QSpinBox()
        self.spin_average_distance.setMinimum(0)
        self.spin_average_distance.setMaximum(255)
        self.spin_average_distance.setSingleStep(1)
        self.spin_average_distance.setValue(10)
        self.spin_average_distance.editingFinished.connect(self.spin_average_finished)

        self.label_average_velocity = QLabel('Moving Average for Velocity:')

        self.spin_average_velocity = QSpinBox()
        self.spin_average_velocity.setMinimum(0)
        self.spin_average_velocity.setMaximum(255)
        self.spin_average_velocity.setSingleStep(1)
        self.spin_average_velocity.setValue(10)
        self.spin_average_velocity.editingFinished.connect(self.spin_average_finished)

        self.enable_laser = QCheckBox("Enable Laser")
        self.enable_laser.stateChanged.connect(self.enable_laser_changed)

        self.label_acquisition_count = QLabel('Acquisition Count:')
        self.spin_acquisition_count = QSpinBox()
        self.spin_acquisition_count.setMinimum(1)
        self.spin_acquisition_count.setMaximum(255)
        self.spin_acquisition_count.setSingleStep(1)
        self.spin_acquisition_count.setValue(128)

        self.enable_qick_termination = QCheckBox("Quick Termination")

        self.label_threshold = QLabel('Threshold:')
        self.threshold = QCheckBox("Automatic Threshold")

        self.spin_threshold = QSpinBox()
        self.spin_threshold.setMinimum(1)
        self.spin_threshold.setMaximum(255)
        self.spin_threshold.setSingleStep(1)
        self.spin_threshold.setValue(1)

        self.label_frequency = QLabel('Frequency [Hz]:')
        self.frequency = QCheckBox("Automatic Frequency (Disable for Velocity)")

        self.spin_frequency = QSpinBox()
        self.spin_frequency.setMinimum(10)
        self.spin_frequency.setMaximum(500)
        self.spin_frequency.setSingleStep(1)
        self.spin_frequency.setValue(10)

        self.spin_acquisition_count.editingFinished.connect(self.configuration_changed)
        self.enable_qick_termination.stateChanged.connect(self.configuration_changed)
        self.spin_threshold.editingFinished.connect(self.configuration_changed)
        self.threshold.stateChanged.connect(self.configuration_changed)
        self.spin_frequency.editingFinished.connect(self.configuration_changed)
        self.frequency.stateChanged.connect(self.configuration_changed)

        layout_h1 = QHBoxLayout()
        layout_h1.addWidget(self.plot_widget_distance)
        layout_h1.addWidget(self.plot_widget_velocity)

        layout_h2 = QHBoxLayout()
        layout_h2.addWidget(self.label_average_distance)
        layout_h2.addWidget(self.spin_average_distance)
        layout_h2.addWidget(self.label_average_velocity)
        layout_h2.addWidget(self.spin_average_velocity)
        layout_h2.addStretch()
        layout_h2.addWidget(self.enable_laser)

        layout_h3 = QHBoxLayout()
        layout_h3.addWidget(self.label_frequency)
        layout_h3.addWidget(self.spin_frequency)
        layout_h3.addWidget(self.frequency)
        layout_h3.addStretch()
        layout_h3.addWidget(self.enable_qick_termination)

        layout_h4 = QHBoxLayout()
        layout_h4.addWidget(self.label_threshold)
        layout_h4.addWidget(self.spin_threshold)
        layout_h4.addWidget(self.threshold)
        layout_h4.addStretch()
        layout_h4.addWidget(self.label_acquisition_count)
        layout_h4.addWidget(self.spin_acquisition_count)

        self.widgets_distance = [self.plot_widget_distance, self.spin_average_distance, self.label_average_distance]
        self.widgets_velocity = [self.plot_widget_velocity, self.spin_average_velocity, self.label_average_velocity]

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h1)
        layout.addWidget(line)
        layout.addLayout(layout_h2)
        layout.addLayout(layout_h3)
        layout.addLayout(layout_h4)

    def start(self):
        async_call(self.lrf.get_configuration, None, self.get_configuration_async, self.increase_error_count)

        async_call(self.lrf.get_enable, None, self.enable_laser.setChecked, self.increase_error_count)
        async_call(self.lrf.get_moving_average, None, self.get_moving_average_async, self.increase_error_count)

        self.cbe_distance.set_period(25)
        self.cbe_velocity.set_period(25)

        self.plot_widget_distance.stop = False
        self.plot_widget_velocity.stop = False

    def stop(self):
        self.cbe_distance.set_period(0)
        self.cbe_velocity.set_period(0)

        self.plot_widget_distance.stop = True
        self.plot_widget_velocity.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletLaserRangeFinderV2.DEVICE_IDENTIFIER

    def enable_laser_changed(self, state):
        self.lrf.set_enable(state == Qt.Checked)

    def cb_distance(self, distance):
        self.current_distance.value = distance

    def cb_velocity(self, velocity):
        self.current_velocity.value = velocity / 100.0

    def configuration_changed(self):
        acquisition_count = self.spin_acquisition_count.value()
        enable_quick_termination = self.enable_qick_termination.isChecked()

        if self.threshold.isChecked():
            threshold = 0
        else:
            threshold = self.spin_threshold.value()

        if self.frequency.isChecked():
            frequency = 0
            for w in self.widgets_velocity:
                w.hide()
        else:
            frequency = self.spin_frequency.value()
            for w in self.widgets_velocity:
                w.show()

        self.spin_threshold.setDisabled(threshold == 0)
        self.spin_frequency.setDisabled(frequency == 0)

        self.lrf.set_configuration(acquisition_count, enable_quick_termination, threshold, frequency)

    def get_configuration_async(self, conf):
        self.spin_acquisition_count.blockSignals(True)
        self.spin_acquisition_count.setValue(conf.acquisition_count)
        self.spin_acquisition_count.blockSignals(False)

        self.enable_qick_termination.blockSignals(True)
        self.enable_qick_termination.setChecked(conf.enable_quick_termination)
        self.enable_qick_termination.blockSignals(False)

        self.spin_threshold.blockSignals(True)
        self.spin_threshold.setValue(conf.threshold_value)
        self.spin_threshold.setDisabled(conf.threshold_value == 0)
        self.spin_threshold.blockSignals(False)

        self.spin_frequency.blockSignals(True)
        self.spin_frequency.setValue(conf.measurement_frequency)
        self.spin_frequency.setDisabled(conf.measurement_frequency == 0)
        self.spin_frequency.blockSignals(False)

        self.threshold.blockSignals(True)
        self.threshold.setChecked(conf.threshold_value == 0)
        self.threshold.blockSignals(False)

        self.frequency.blockSignals(True)
        self.frequency.setChecked(conf.measurement_frequency == 0)
        self.frequency.blockSignals(False)

        self.configuration_changed()

    def get_moving_average_async(self, avg):
        self.spin_average_distance.setValue(avg.distance_average_length)
        self.spin_average_velocity.setValue(avg.velocity_average_length)

    def spin_average_finished(self):
        self.lrf.set_moving_average(self.spin_average_distance.value(), self.spin_average_velocity.value())
