# -*- coding: utf-8 -*-  
"""
brickv (Brick Viewer) 
Copyright (C) 2009-2011 Olaf Lüke <olaf@tinkerforge.com>

dc.py: DC Plugin implementation

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

from PyQt4.QtGui import QErrorMessage, QInputDialog
from PyQt4.QtCore import QTimer, Qt, pyqtSignal

from speedometer import SpeedoMeter
from plugin_system.plugin_base import PluginBase
from bindings import ip_connection
from bindings import brick_dc

from ui_dc import Ui_DC

class DC(PluginBase, Ui_DC):
    qtcb_position_reached = pyqtSignal(int)
    qtcb_under_voltage = pyqtSignal(int)
    qtcb_emergency_shutdown = pyqtSignal()
    
    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)
     
        self.setupUi(self)
        
        self.dc = brick_dc.DC(self.uid)
        self.device = self.dc
        self.ipcon.add_device(self.dc)
        self.version = '.'.join(map(str, self.dc.get_version()[1]))
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        

        self.speedometer = SpeedoMeter()
        self.vertical_layout_right.insertWidget(4, self.speedometer)
        
        self.new_value = 0
        self.update_counter = 0
        
        self.full_brake_time = 0
        
        self.velocity_slider.sliderReleased.connect(self.velocity_slider_released)
        self.velocity_slider.valueChanged.connect(self.velocity_spin.setValue)
        self.velocity_spin.editingFinished.connect(self.velocity_spin_finished)
        
        self.acceleration_slider.sliderReleased.connect(self.acceleration_slider_released)
        self.acceleration_slider.valueChanged.connect(self.acceleration_spin.setValue)
        self.acceleration_spin.editingFinished.connect(self.acceleration_spin_finished)
        
        self.frequency_slider.sliderReleased.connect(self.frequency_slider_released)
        self.frequency_slider.valueChanged.connect(self.frequency_spin.setValue)
        self.frequency_spin.editingFinished.connect(self.frequency_spin_finished)
        
        self.radio_mode_brake.toggled.connect(self.brake_value_changed)
        self.radio_mode_coast.toggled.connect(self.coast_value_changed)
        
        self.minimum_voltage_button.pressed.connect(self.minimum_voltage_button_pressed)
        self.full_brake_button.pressed.connect(self.full_brake_pressed)
        self.enable_checkbox.stateChanged.connect(self.enable_state_changed)
        
        self.emergency_signal = None
        self.under_signal = None
        self.current_velocity_signal = None
        self.velocity_reached_signal = None
        
        self.qem = QErrorMessage(self)
        
        self.qtcb_under_voltage.connect(self.cb_under_voltage)
        self.dc.register_callback(self.dc.CALLBACK_UNDER_VOLTAGE,
                                  self.qtcb_under_voltage.emit) 
        
        self.qtcb_emergency_shutdown.connect(self.cb_emergency_shutdown)
        self.dc.register_callback(self.dc.CALLBACK_EMERGENCY_SHUTDOWN,
                                  self.qtcb_emergency_shutdown.emit) 
        
        self.qtcb_position_reached.connect(self.update_velocity)
        self.dc.register_callback(self.dc.CALLBACK_VELOCITY_REACHED,
                                  self.qtcb_position_reached.emit) 
        self.dc.register_callback(self.dc.CALLBACK_CURRENT_VELOCITY,
                                  self.qtcb_position_reached.emit) 
    
    def start(self):
        self.update_timer.start(1000)
        try:
            self.dc.set_current_velocity_period(100)
            self.update_start()
            self.update_data()
        except ip_connection.Error:
            return
        
    def stop(self):
        self.update_timer.stop()
        try:
            self.dc.set_current_velocity_period(0)
        except ip_connection.Error:
            return
        
    @staticmethod
    def has_name(name):
        return 'DC Brick' in name 
        
    def cb_emergency_shutdown(self):
        if not self.qem.isVisible():
            self.qem.setWindowTitle("Emergency Shutdown")
            self.qem.showMessage("Emergency Shutdown: Short-Circuit or Over-Temperature")
        
    def cb_under_voltage(self, ov):
        mv_str = self.minimum_voltage_label.text()
        ov_str = "%gV"  % round(ov/1000.0, 1)
        if not self.qem.isVisible():
            self.qem.setWindowTitle("Under Voltage")
            self.qem.showMessage("Under Voltage: Output Voltage of " + ov_str +
                                 " is below minimum voltage of " + mv_str)
        
    def enable_state_changed(self, state):
        try:
            if state == Qt.Checked:
                self.dc.enable()
            elif state == Qt.Unchecked:
                self.dc.disable()
        except ip_connection.Error:
            return
            
    def brake_value_changed(self, checked):
        if checked:
            try:
                self.dc.set_drive_mode(0)
            except ip_connection.Error:
                return
        
    def coast_value_changed(self, checked):
        if checked:
            try:
                self.dc.set_drive_mode(1)
            except ip_connection.Error:
                return
        
    def full_brake_pressed(self):
        try:
            self.dc.full_brake()
        except ip_connection.Error:
            return
        
    def minimum_voltage_selected(self, value):
        try:
            self.dc.set_minimum_voltage(value)
        except ip_connection.Error:
            return
        
    def minimum_voltage_button_pressed(self):
        qid = QInputDialog(self)
        qid.setInputMode(QInputDialog.IntInput)
        qid.setIntMinimum(5000)
        qid.setIntMaximum(0xFFFF)
        qid.setIntStep(100)
        try:
            qid.setIntValue(self.dc.get_minimum_voltage())
        except ip_connection.Error:
            return
        qid.intValueSelected.connect(self.minimum_voltage_selected)
        qid.setLabelText("Choose minimum motor voltage in mV.")
        qid.open()
        
    def stack_input_voltage_update(self, sv):
        sv_str = "%gV"  % round(sv/1000.0, 1)
        self.stack_voltage_label.setText(sv_str)
        
    def external_input_voltage_update(self, ev):
        ev_str = "%gV"  % round(ev/1000.0, 1)
        self.external_voltage_label.setText(ev_str)
        
    def minimum_voltage_update(self, mv):
        mv_str = "%gV"  % round(mv/1000.0, 1)
        self.minimum_voltage_label.setText(mv_str)
        
    def drive_mode_update(self, dm):
        if dm == 0:
            self.radio_mode_brake.setChecked(True)
            self.radio_mode_coast.setChecked(False)
        else:
            self.radio_mode_brake.setChecked(False)
            self.radio_mode_coast.setChecked(True)
            
    def current_consumption_update(self, cc):
        if cc >= 1000:
            cc_str = "%gA"  % round(cc/1000.0, 1)
        else:
            cc_str = "%gmA" % cc
            
        self.current_label.setText(cc_str)

    
    def update_velocity(self, value):
        if value != self.speedometer.value():
            self.speedometer.set_velocity(value)
        
    def update_start(self):
        try:
            dm = self.dc.get_drive_mode()
            self.drive_mode_update(dm)
            
            if not self.velocity_slider.isSliderDown():
                velocity = self.dc.get_velocity()
                if velocity != self.velocity_slider.sliderPosition():
                    self.velocity_slider.setSliderPosition(velocity)
                    self.velocity_spin.setValue(velocity)
                 
            if not self.acceleration_slider.isSliderDown():
                acceleration = self.dc.get_acceleration()
                if acceleration != self.acceleration_slider.sliderPosition():
                    self.acceleration_slider.setSliderPosition(acceleration)
                    self.acceleration_spin.setValue(acceleration)
                    
            if not self.frequency_slider.isSliderDown():
                frequency = self.dc.get_pwm_frequency()
                if frequency != self.frequency_slider.sliderPosition():
                    self.frequency_slider.setSliderPosition(frequency)
                    self.frequency_spin.setValue(frequency)
    
            enabled = self.dc.is_enabled()
            if enabled:
                self.enable_checkbox.setCheckState(Qt.Checked)
            else:
                self.enable_checkbox.setCheckState(Qt.Unchecked)
        except ip_connection.Error:
            return
        
    def update_data(self):
        try:
            sv = self.dc.get_stack_input_voltage()
            ev = self.dc.get_external_input_voltage()
            mv = self.dc.get_minimum_voltage()
            cc = self.dc.get_current_consumption()
        except ip_connection.Error:
            return
        
        self.stack_input_voltage_update(sv)
        self.external_input_voltage_update(ev)
        self.minimum_voltage_update(mv)
        self.current_consumption_update(cc)
        
    def acceleration_slider_released(self):
        value = self.acceleration_slider.value()
        self.acceleration_spin.setValue(value)
        try:
            self.dc.set_acceleration(value)
        except ip_connection.Error:
            return
        
    def acceleration_spin_finished(self):
        value = self.acceleration_spin.value()
        self.acceleration_slider.setValue(value)
        try:
            self.dc.set_acceleration(value)
        except ip_connection.Error:
            return
        
    def velocity_slider_released(self):
        value = self.velocity_slider.value()
        self.velocity_spin.setValue(value)
        try:
            self.dc.set_velocity(value)
        except ip_connection.Error:
            return
        
    def velocity_spin_finished(self):
        value = self.velocity_spin.value()
        self.velocity_slider.setValue(value)
        try:
            self.dc.set_velocity(value)
        except ip_connection.Error:
            return
        
    def frequency_slider_released(self):
        value = self.frequency_slider.value()
        self.frequency_spin.setValue(value)
        try:
            self.dc.set_pwm_frequency(value)
        except ip_connection.Error:
            return
        
    def frequency_spin_finished(self):
        value = self.frequency_spin.value()
        self.frequency_slider.setValue(value)
        try:
            self.dc.set_pwm_frequency(value)
        except ip_connection.Error:
            return