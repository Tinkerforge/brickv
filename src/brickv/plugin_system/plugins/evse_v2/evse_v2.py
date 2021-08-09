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

from typing import Tuple
from PyQt5.QtWidgets import QErrorMessage, QInputDialog, QAction, QTableWidget, QTableWidgetItem
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

class EnergyMeterTable(QTableWidget):
    def __init__(self, data, *args):
        QTableWidget.__init__(self, *args)
        self.data = data
        self.update_data()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def update_data(self):
        header = ['Property', 'Value']
        self.setHorizontalHeaderLabels(header)
        for i, item in enumerate(self.data.items()):
            property, value = item
            try:
                value = ', '.join(map(str, value))
            except:
                value = str(value)

            item_property = QTableWidgetItem(property)
            item_value = QTableWidgetItem(value)
            self.setItem(i, 0, item_property)
            self.setItem(i, 1, item_value)

class EVSEV2(COMCUPluginBase, Ui_EVSEV2):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletEVSEV2, *args)

        self.setupUi(self)

        self.evse = self.device

        self.cbe_state = CallbackEmulator(self,
                                          self.evse.get_state,
                                          None,
                                          self.state_cb,
                                          self.increase_error_count)
        self.cbe_low_level_state = CallbackEmulator(self,
                                                    self.evse.get_low_level_state,
                                                    None,
                                                    self.low_level_state_cb,
                                                    self.increase_error_count)
        self.cbe_max_charging_current = CallbackEmulator(self,
                                                         self.evse.get_max_charging_current,
                                                         None,
                                                         self.max_charging_current_cb,
                                                         self.increase_error_count)
        self.cbe_energy_meter_values = CallbackEmulator(self,
                                                        self.evse.get_energy_meter_values,
                                                        None,
                                                        self.energy_meter_values_cb,
                                                        self.increase_error_count)
        self.cbe_energy_meter_state = CallbackEmulator(self,
                                                       self.evse.get_energy_meter_state,
                                                       None,
                                                       self.energy_meter_state_cb,
                                                       self.increase_error_count)
        self.cbe_dc_fault_current_state = CallbackEmulator(self,
                                                           self.evse.get_dc_fault_current_state,
                                                           None,
                                                           self.dc_fault_current_state_cb,
                                                           self.increase_error_count)

        self.combo_gpio_input.currentIndexChanged.connect(self.gpio_changed)
        self.combo_gpio_output.currentIndexChanged.connect(self.gpio_changed)
        self.checkbox_autostart.stateChanged.connect(self.autostart_changed)
        self.button_start_charging.clicked.connect(self.start_charging_clicked)
        self.button_stop_charging.clicked.connect(self.stop_charging_clicked)
        self.button_dc_fault_reset.clicked.connect(self.dc_fault_reset_clicked)
        self.button_energy_meter_reset.clicked.connect(self.energy_meter_reset_clicked)
        self.spinbox_max_charging_current.valueChanged.connect(self.max_charging_current_changed)
        self.button_energy_meter_detailed.clicked.connect(self.energy_meter_detailed_clicked)

    def energy_meter_detailed_clicked(self):
        values = self.evse.get_energy_meter_detailed_values()
        data = {}
        data['line_to_neutral_volts[SDM630_PHASE_NUM]']  = values[0], values[1], values[2]
        data['current[SDM630_PHASE_NUM]']                = values[3], values[4], values[5]
        data['power[SDM630_PHASE_NUM]']                  = values[6], values[7], values[8]
        data['volt_amps[SDM630_PHASE_NUM]']              = values[9], values[10], values[11]
        data['volt_amps_reactive[SDM630_PHASE_NUM]']     = values[12], values[13], values[14]
        data['power_factor[SDM630_PHASE_NUM]']           = values[15], values[16], values[17]
        data['phase_angle[SDM630_PHASE_NUM]']            = values[18], values[19], values[20]
        data['average_line_to_neutral_volts']            = values[21]
        data['average_line_current']                     = values[22]
        data['sum_of_line_currents']                     = values[23]
        data['total_system_power']                       = values[24]
        data['total_system_volt_amps']                   = values[25]
        data['total_system_var']                         = values[26]
        data['total_system_power_factor']                = values[27]
        data['total_system_phase_angle']                 = values[28]
        data['frequency_of_supply_voltages']             = values[29]
        data['total_import_kwh']                         = values[30]
        data['total_export_kwh']                         = values[31]
        data['total_import_kvarh']                       = values[32]
        data['total_export_kvarh']                       = values[33]
        data['total_vah']                                = values[34]
        data['ah']                                       = values[35]
        data['total_system_power_demand']                = values[36]
        data['maximum_total_system_power_demand']        = values[37]
        data['total_system_va_demand']                   = values[38]
        data['maximum_total_system_va_demand']           = values[39]
        data['neutral_current_demand']                   = values[40]
        data['maximum_neutral_current_demand']           = values[41]
        data['line1_to_line2_volts']                     = values[42]
        data['line2_to_line3_volts']                     = values[43]
        data['line3_to_line1_volts']                     = values[44]
        data['average_line_to_line_volts']               = values[45]
        data['neutral_current']                          = values[46]
        data['ln_volts_thd[SDM630_PHASE_NUM]']           = values[47], values[48], values[49]
        data['current_thd[SDM630_PHASE_NUM]']            = values[50], values[51], values[52]
        data['average_line_to_neutral_volts_thd']        = values[53]
        data['current_demand[SDM630_PHASE_NUM]']         = values[54], values[55], values[56]
        data['maximum_current_demand[SDM630_PHASE_NUM]'] = values[57], values[58], values[59]
        data['line1_to_line2_volts_thd']                 = values[60]
        data['line2_to_line3_volts_thd']                 = values[61]
        data['line3_to_line1_volts_thd']                 = values[62]
        data['average_line_to_line_volts_thd']           = values[63]
        data['total_kwh_sum']                            = values[64]
        data['total_kvarh_sum']                          = values[65]
        data['import_kwh[SDM630_PHASE_NUM]']             = values[66], values[67], values[68]
        data['export_kwh[SDM630_PHASE_NUM]']             = values[69], values[70], values[71]
        data['total_kwh[SDM630_PHASE_NUM]']              = values[72], values[73], values[74]
        data['import_kvarh[SDM630_PHASE_NUM]']           = values[75], values[76], values[77]
        data['export_kvarh[SDM630_PHASE_NUM]']           = values[78], values[79], values[80]
        data['total_kvarh[SDM630_PHASE_NUM]']            = values[81], values[82], values[83]

        table = EnergyMeterTable(data, 50, 2, self)
        # add Qt.Window to table's flags 
        table.setWindowFlags(table.windowFlags() | Qt.Window)
        table.resize(500, 700)
        table.show()

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
        self.label_energy_meter_values.setText('Power: {0:.2f}W, Energy Relative: {1:.2f}kWh, Energy Absolute: {2:.2f}kWh, Active Phases: {3}'.format(emv.power, emv.energy_relative, emv.energy_absolute, str(emv.phases_active)))

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
        self.label_adc_values.setText('CP/PE w/o resistor (PWM high): {0}, CP/PE w/ resistor (PWM high): {1}\nCP/PE w/o resistor (PWM low): {2}, CP/PE w/ resistor (PWM low): {3}\nPP/PE: {4}, +12V rail: {5}, -12V rail: {6}'.format(*state.adc_values))
        self.label_voltages.setText('CP/PE w/o resistor (PWM high): {0:.2f}V, CP/PE w/ resistor (PWM high): {1:.2f}V\nCP/PE w/o resistor (PWM low): {2:.2f}V, CP/PE w/ resistor (PWM low): {3:.2f}V\nPP/PE: {4:.2f}V, +12V rail: {5:.2f}V, -12V rail: {6:.2f}V'.format(state.voltages[0]/1000, state.voltages[1]/1000, state.voltages[2]/1000, state.voltages[3]/1000, state.voltages[4]/1000, state.voltages[5]/1000, state.voltages[6]/1000))
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
