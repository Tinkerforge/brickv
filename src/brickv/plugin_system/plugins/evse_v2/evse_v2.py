# -*- coding: utf-8 -*-
"""
EVSE 2.0 Plugin
Copyright (C) 2021 Olaf Lüke <olaf@tinkerforge.com>

evse_v2.py: EVSE 2.0 Plugin implementation

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

from PyQt5.QtWidgets import QErrorMessage, QInputDialog, QAction
from PyQt5.QtCore import QTimer, Qt, pyqtSignal

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.evse_v2.ui_evse_v2 import Ui_EVSEV2
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_evse_v2 import BrickletEVSEV2
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.slider_spin_syncer import SliderSpinSyncer

IEC61851_STATE = ['A', 'B', 'C', 'D', 'EF']
VEHICLE_STATE = ['Not Connected', 'Connected', 'Charging', 'Error']
LED_STATE = ['Off', 'On', 'Blinking', 'Flicker', 'Breathing']
CONTACTOR_STATE = ['Not Live', 'Live']
LOCK_STATE = ['Init', 'Open', 'Closing', 'Close', 'Opening', 'Error']
JUMPER_CONFIGURATON = ['6A', '10A', '13A', '16A', '20A', '25A', '32A', 'Software', 'Unconfigured']
GPIO = ['Low', 'High']
CONTACTOR = ['Inactive', 'Active']
LOCK_SWITCH = ['Not Available', 'Available']

class EVSEV2(COMCUPluginBase, Ui_EVSEV2):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletEVSEV2, *args)

        self.setupUi(self)

        self.evse = self.device

        self.cbe_state = CallbackEmulator(self.evse.get_state, None, self.state_cb, self.increase_error_count)
        self.cbe_low_level_state = CallbackEmulator(self.evse.get_low_level_state, None, self.low_level_state_cb, self.increase_error_count)
        self.cbe_max_charging_current = CallbackEmulator(self.evse.get_max_charging_current, None, self.max_charging_current_cb, self.increase_error_count)
        self.cbe_energy_meter_values = CallbackEmulator(self.evse.get_energy_meter_values, None, self.energy_meter_values_cb, self.increase_error_count)
        self.cbe_energy_meter_state = CallbackEmulator(self.evse.get_energy_meter_state, None, self.energy_meter_state_cb, self.increase_error_count)
        self.cbe_dc_fault_current_state = CallbackEmulator(self.evse.get_dc_fault_current_state, None, self.dc_fault_current_state_cb, self.increase_error_count)

        self.combo_gpio_input.currentIndexChanged.connect(self.gpio_changed)
        self.combo_gpio_output.currentIndexChanged.connect(self.gpio_changed)
        self.checkbox_autostart.stateChanged.connect(self.autostart_changed)
        self.button_start_charging.clicked.connect(self.start_charging_clicked)
        self.button_stop_charging.clicked.connect(self.stop_charging_clicked)
        self.button_dc_fault_reset.clicked.connect(self.dc_fault_reset_clicked)
        self.button_energy_meter_reset.clicked.connect(self.energy_meter_reset_clicked)
        self.spinbox_max_charging_current.valueChanged.connect(self.max_charging_current_changed)

    def max_charging_current_changed(self, current):
        self.evse.set_max_charging_current(current)

    def start_charging_clicked(self):
        self.evse.start_charging()

    def stop_charging_clicked(self):
        self.evse.stop_charging()

    def dc_fault_reset_clicked(self):
        self.evse.reset_dc_fault_current(0xDC42FA23)

    def energy_meter_reset_clicked(self):
        self.evse.reset_energy_meter()

    def autostart_changed(self, state):
        self.evse.set_charging_autostart(state == Qt.Checked)

    def gpio_changed(self):
        print('gpio changed')

    def energy_meter_values_cb(self, emv):
        self.label_energy_meter_values.setText('Power: {0}W, Energy Relative: {1:.2f}kWh, Energy Absolute: {2:.2f}kWh'.format(emv.power, emv.energy_relative/1000, emv.energy_absolute/1000))

    def energy_meter_state_cb(self, ems):
        self.label_energy_meter_state.setText('Available: {0}, Error Counts: {1}'.format(ems.available, str(ems.error_count)))
    
    def dc_fault_current_state_cb(self, state):
        self.label_dc_fault_current_state.setText(str(state))
    
    def state_cb(self, state):
        self.label_iec61851_state.setText(IEC61851_STATE[state.iec61851_state])
        self.label_vehicle_state.setText(VEHICLE_STATE[state.vehicle_state])
        self.label_contactor_check.setText('Input: {0}, Output: {1}, Error: {2}'.format(CONTACTOR_STATE[state.contactor_state in (1, 3)], CONTACTOR_STATE[state.contactor_state in (2, 3)], state.contactor_error))
        self.label_lock_state.setText(LOCK_STATE[state.lock_state])
        m, s = divmod(int(state.uptime/1000), 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if d == 0:
            self.label_uptime.setText('{0:d}:{1:02d}:{2:02d}'.format(h, m, s))
        elif d == 1:
            self.label_uptime.setText('1 Day, {0:d}:{1:02d}:{2:02d}'.format(h, m, s))
        else:
            self.label_uptime.setText('{0} Days, {1:d}:{2:02d}:{3:02d}'.format(d, h, m, s))

        m, s = divmod(int(state.time_since_state_change/1000), 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if d == 0:
            self.label_time_since_state_change.setText('{0:d}:{1:02d}:{2:02d}'.format(h, m, s))
        elif d == 1:
            self.label_time_since_state_change.setText('1 Day, {0:d}:{1:02d}:{2:02d}'.format(h, m, s))
        else:
            self.label_time_since_state_change.setText('{0} Days, {1:d}:{2:02d}:{3:02d}'.format(d, h, m, s))

    def low_level_state_cb(self, state):
        gpio_str = ''
        for g in state.gpio:
            if g:
                gpio_str += '1'
            else:
                gpio_str += '0'

        self.label_led_state.setText(LED_STATE[state.led_state])
        self.label_adc_values.setText('CP/PE w/o resistor: {0}, CP/PE w/ resistor: {1}, PP/PE: {2}, +12V rail: {3}, -12V rail: {4}'.format(*state.adc_values))
        self.label_voltages.setText('CP/PE w/o resistor: {0:.2f}V, CP/PE w/ resistor: {1:.2f}V, PP/PE: {2:.2f}V, +12V rail: {3:.2f}V, -12V rail: {4:.2f}V'.format(state.voltages[0]/1000, state.voltages[1]/1000, state.voltages[2]/1000, state.voltages[3]/1000, state.voltages[4]/1000))
        self.label_resistances.setText('CP/PE: {0} Ohm, PP/PE: {1} Ohm'.format(*state.resistances))
        self.label_cp_pwm_duty_cycle.setText('{0} %'.format(state.cp_pwm_duty_cycle/10))
        self.label_gpios.setText(gpio_str)

    def max_charging_current_cb(self, mcc):
        self.label_max_current_configured.setText('{0:.1f} A'.format(mcc.max_current_configured/1000))
        self.label_max_current_incoming_cable.setText('{0:.1f} A'.format(mcc.max_current_incoming_cable/1000))
        self.label_max_current_outgoing_cable.setText('{0:.1f} A'.format(mcc.max_current_outgoing_cable/1000))

    def get_hardware_configuration_async(self, conf):
        self.label_jumper_configuration.setText(JUMPER_CONFIGURATON[conf.jumper_configuration])
        self.label_lock_switch.setText(LOCK_SWITCH[conf.has_lock_switch])

    def get_charging_autostart_async(self, autostart):
        self.checkbox_autostart.blockSignals(True)
        self.checkbox_autostart.setChecked(autostart)
        self.checkbox_autostart.blockSignals(False)

    def get_max_charging_current_async(self, mcc):
        self.spinbox_max_charging_current.blockSignals(True)
        self.spinbox_max_charging_current.setValue(mcc.max_current_configured)
        self.spinbox_max_charging_current.blockSignals(False)

    def start(self):
        async_call(self.evse.get_hardware_configuration, None, self.get_hardware_configuration_async, self.increase_error_count)
        async_call(self.evse.get_charging_autostart, None, self.get_charging_autostart_async, self.increase_error_count)
        async_call(self.evse.get_max_charging_current, None, self.get_max_charging_current_async, self.increase_error_count)
        self.cbe_state.set_period(100)
        self.cbe_low_level_state.set_period(100)
        self.cbe_max_charging_current.set_period(500)
        self.cbe_energy_meter_values.set_period(100)
        self.cbe_energy_meter_state.set_period(100)
        self.cbe_dc_fault_current_state.set_period(100)

    def stop(self):
        self.cbe_state.set_period(0)
        self.cbe_low_level_state.set_period(0)
        self.cbe_max_charging_current.set_period(0)
        self.cbe_energy_meter_values.set_period(100)
        self.cbe_energy_meter_state.set_period(100)
        self.cbe_dc_fault_current_state.set_period(100)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletEVSEV2.DEVICE_IDENTIFIER
