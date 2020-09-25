# -*- coding: utf-8 -*-
"""
EVSE Plugin
Copyright (C) 2020 Olaf Lüke <olaf@tinkerforge.com>

evse.py: EVSE Plugin implementation

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
from brickv.plugin_system.plugins.evse.ui_evse import Ui_EVSE
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_evse import BrickletEVSE
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.slider_spin_syncer import SliderSpinSyncer

IEC61851_STATE = ['A', 'B', 'C', 'D', 'EF']
LED_STATE = ['Off', 'On', 'Blinking', 'Breathing']
CONTACTOR_STATE = ['Not Live', 'Live']
LOCK_STATE = ['Init', 'Open', 'Closing', 'Close', 'Opening', 'Error']
JUMPER_CONFIGURATON = ['6A', '10A', '13A', '16A', '20A', '25A', '32A', 'Software', 'Unconfigured']
GPIO = ['Low', 'High']
CONTACTOR = ['Inactive', 'Active']
LOCK_SWITCH = ['Not Available', 'Available']

class EVSE(COMCUPluginBase, Ui_EVSE):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletEVSE, *args)

        self.setupUi(self)

        self.evse = self.device

        self.cbe_state = CallbackEmulator(self.evse.get_state, None, self.state_cb, self.increase_error_count)
        self.cbe_low_level_state = CallbackEmulator(self.evse.get_low_level_state, None, self.low_level_state_cb, self.increase_error_count)

    
    def state_cb(self, state):
        self.label_iec61851_state.setText(IEC61851_STATE[state.iec61851_state])
        self.label_contactor_input.setText(CONTACTOR_STATE[state.contactor_state in (1, 3)])
        self.label_contactor_output.setText(CONTACTOR_STATE[state.contactor_state in (2, 3)])
        self.label_contactor_error.setText(str(state.contactor_error))
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
        if state.resistances[0] > 100000:
            res_cp = 'Open'
        else:
            res_cp = '{0} Ohm'.format(state.resistances[0])

        if state.resistances[1] > 100000:
            res_pp = 'Open'
        else:
            res_pp = '{0} Ohm'.format(state.resistances[1])

        self.label_led_state.setText(LED_STATE[state.led_state])
        self.label_adc_value_cp_pe.setText(str(state.adc_values[0]))
        self.label_voltage_cp_pe.setText('{0:.2f} V'.format(state.voltages[0]))
        self.label_voltage_peak_cp_pe.setText('{0:.2f} V'.format(state.voltages[2]))
        self.label_resistance_cp_pe.setText(res_cp)
        self.label_adc_value_pp_pe.setText(str(state.adc_values[1]))
        self.label_voltage_pp_pe.setText('{0:.2f} V'.format(state.voltages[1]))
        self.label_resistance_pp_pe.setText(res_pp)
        self.label_cp_pwm_duty_cycle.setText('{0} %'.format(state.cp_pwm_duty_cycle/10))
        self.label_contactor.setText(CONTACTOR[state.gpio[3]])
        self.label_gpio_enable.setText(GPIO[state.gpio[0]])
        self.label_gpio_led.setText(GPIO[state.gpio[1]])
        self.label_gpio_motor_switch.setText(GPIO[state.gpio[2]])
        self.label_gpio_motor_fault.setText(GPIO[state.gpio[4]])

    def get_hardware_configuration_async(self, conf):
        self.label_jumper_configuration.setText(JUMPER_CONFIGURATON[conf.jumper_configuration])
        self.label_lock_switch.setText(LOCK_SWITCH[conf.has_lock_switch])

    def start(self):
        async_call(self.evse.get_hardware_configuration, None, self.get_hardware_configuration_async, self.increase_error_count)
        self.cbe_state.set_period(100)
        self.cbe_low_level_state.set_period(100)

    def stop(self):
        self.cbe_state.set_period(0)
        self.cbe_low_level_state.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletEVSE.DEVICE_IDENTIFIER
