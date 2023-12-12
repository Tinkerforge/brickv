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
from PyQt5.QtWidgets import QErrorMessage, QInputDialog, QAction, QTableWidget, QTableWidgetItem, QSpinBox
from PyQt5.QtCore import QTimer, Qt, pyqtSignal


class CurrentSpinBox(QSpinBox):
    def stepBy(self, steps):
        newValue = int(self.checkValue(self.value() + (steps * self.singleStep())))
        self.setValue(newValue);

    def checkValue(self, value):
        if (value < 4) or (value < 0):
            return 6

        if (value >= 4) and (value < 6):
            return 0

        if value > 32:
            return 32

        return value

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.evse_v2.ui_evse_v2 import Ui_EVSEV2
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_evse_v2 import BrickletEVSEV2
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.slider_spin_syncer import SliderSpinSyncer

IEC61851_STATE = ['A', 'B', 'C', 'D', 'EF']
CHARGER_STATE = ['Not Connected', 'Waiting For Charge Release', 'Ready To Charge', 'Charging', 'Error']
LED_STATE = ['Off', 'On', 'Blinking', 'Flicker', 'Breathing', 'API']
CONTACTOR_STATE = ['Not Live', 'Live']
LOCK_STATE = ['Init', 'Open', 'Closing', 'Close', 'Opening', 'Error']
JUMPER_CONFIGURATON = ['6A', '10A', '13A', '16A', '20A', '25A', '32A', 'Software', 'Unconfigured']
GPIO = ['Low', 'High']
CONTACTOR = ['Inactive', 'Active']
LOCK_SWITCH = ['Not Available', 'Available']
CONTROL_PILOT = ['Disconnected', 'Connected', 'Automatic']
DC_FAULT_STATE = ['Normal Condition', '6mA Fault', 'System Fault', 'Unkown Fault', 'Calibration Fault']
DC_FAULT_TYPE = ['X904 (old)', 'X804 (new)']

class DataStorageTable(QTableWidget):
    def __init__(self, page, data, *args):
        QTableWidget.__init__(self, *args)
        self.page = page
        self.data = data
        self.update_data()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def update_data(self):
        self.setWindowTitle('Page {0}'.format(self.page))
        header = ['Byte', 'Value']
        self.setHorizontalHeaderLabels(header)
        for i, item in enumerate(self.data):
            item_property = QTableWidgetItem(str(i))
            item_value = QTableWidgetItem(str(item))
            self.setItem(i, 0, item_property)
            self.setItem(i, 1, item_value)

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
        self.cbe_energy_meter_values = CallbackEmulator(self,
                                                        self.evse.get_energy_meter_values,
                                                        None,
                                                        self.energy_meter_values_cb,
                                                        self.increase_error_count)
        self.cbe_energy_meter_errors = CallbackEmulator(self,
                                                       self.evse.get_energy_meter_errors,
                                                       None,
                                                       self.energy_meter_errors_cb,
                                                       self.increase_error_count)
        self.cbe_all_charging_slots = CallbackEmulator(self,
                                                       self.evse.get_all_charging_slots,
                                                       None,
                                                       self.all_charging_slots_cb,
                                                       self.increase_error_count)

        self.cbe_control_pilot_config = CallbackEmulator(self,
                                                         self.evse.get_control_pilot_disconnect,
                                                         None,
                                                         self.control_pilot_config_cb,
                                                         self.increase_error_count)

        self.combo_gpio_input.currentIndexChanged.connect(self.gpio_changed)
        self.combo_gpio_output.currentIndexChanged.connect(self.gpio_changed)
        self.combo_shutdown_input.currentIndexChanged.connect(self.gpio_changed)
        self.button_dc_fault_reset.clicked.connect(self.dc_fault_reset_clicked)
        self.button_energy_meter_reset.clicked.connect(self.energy_meter_reset_clicked)
        self.button_energy_meter_all.clicked.connect(self.energy_meter_all_clicked)
        self.button_read_page.clicked.connect(self.read_page_clicked)
        self.combo_button_config.currentIndexChanged.connect(self.button_config_changed)
        self.button_set_indicator.clicked.connect(self.set_indicator_clicked)
        self.button_control_pilot_disconnect.clicked.connect(lambda: self.evse.set_control_pilot_configuration(0))
        self.button_control_pilot_connect.clicked.connect(lambda: self.evse.set_control_pilot_configuration(1))
        self.button_control_pilot_automatic.clicked.connect(lambda: self.evse.set_control_pilot_configuration(2))

        self.spin_slot_current = [self.spin_slot_current_0, self.spin_slot_current_1, self.spin_slot_current_2, self.spin_slot_current_3, self.spin_slot_current_4, self.spin_slot_current_5, self.spin_slot_current_6, self.spin_slot_current_7, self.spin_slot_current_8, self.spin_slot_current_9, self.spin_slot_current_10, self.spin_slot_current_11, self.spin_slot_current_12, self.spin_slot_current_13, self.spin_slot_current_14, self.spin_slot_current_15, self.spin_slot_current_16, self.spin_slot_current_17, self.spin_slot_current_18, self.spin_slot_current_19]
        self.check_slot_active = [self.check_slot_active_0, self.check_slot_active_1, self.check_slot_active_2, self.check_slot_active_3, self.check_slot_active_4, self.check_slot_active_5, self.check_slot_active_6, self.check_slot_active_7, self.check_slot_active_8, self.check_slot_active_9, self.check_slot_active_10, self.check_slot_active_11, self.check_slot_active_12, self.check_slot_active_13, self.check_slot_active_14, self.check_slot_active_15, self.check_slot_active_16, self.check_slot_active_17, self.check_slot_active_18, self.check_slot_active_19]
        self.check_slot_clear  = [self.check_slot_clear_0,  self.check_slot_clear_1,  self.check_slot_clear_2,  self.check_slot_clear_3,  self.check_slot_clear_4,  self.check_slot_clear_5,  self.check_slot_clear_6,  self.check_slot_clear_7,  self.check_slot_clear_8,  self.check_slot_clear_9,  self.check_slot_clear_10,  self.check_slot_clear_11,  self.check_slot_clear_12,  self.check_slot_clear_13,  self.check_slot_clear_14,  self.check_slot_clear_15,  self.check_slot_clear_16,  self.check_slot_clear_17,  self.check_slot_clear_18,  self.check_slot_clear_19]

        def get_slot_changed_lambda(i):
            return lambda: self.slot_changed(i)

        for i in range(len(self.spin_slot_current)):
            self.spin_slot_current[i].valueChanged.connect(get_slot_changed_lambda(i))
            self.check_slot_active[i].stateChanged.connect(get_slot_changed_lambda(i))
            self.check_slot_clear[i].stateChanged.connect(get_slot_changed_lambda(i))

    def slot_changed(self, slot):
        current = self.spin_slot_current[slot].value()*1000
        active  = self.check_slot_active[slot].isChecked()
        clear   = self.check_slot_clear[slot].isChecked()
        self.evse.set_charging_slot(slot, current, active, clear)

    def set_indicator_clicked(self):
        index = self.combobox_indication.currentIndex()

        indication = -1
        if index == 0:
            indication = -1
        elif index == 1:
            indication = 0
        elif index == 2:
            indication = 64
        elif index == 3:
            indication = 128
        elif index == 4:
            indication = 192
        elif index == 5:
            indication = 255
        elif index == 6:
            indication = 1001
        elif index == 7:
            indication = 1002
        elif index == 8:
            indication = 1003

        self.evse.set_indicator_led(indication, self.spin_duration.value())

    def button_config_changed(self, config):
        self.evse.set_button_configuration(config)
    
    def read_page_clicked(self):
        page = self.spinbox_page.value()
        data = self.evse.get_data_storage(page)

        table = DataStorageTable(page, data, len(data), 2, self)
        # add Qt.Window to table's flags 
        table.setWindowFlags(table.windowFlags() | Qt.Window)
        table.resize(500, 700)
        table.show()

    def energy_meter_all_clicked(self):
        values = self.evse.get_all_energy_meter_values()
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
        data['average_line_to_current_thd']              = values[54]
        data['current_demand[SDM630_PHASE_NUM]']         = values[55], values[56], values[57]
        data['maximum_current_demand[SDM630_PHASE_NUM]'] = values[58], values[59], values[60]
        data['line1_to_line2_volts_thd']                 = values[61]
        data['line2_to_line3_volts_thd']                 = values[62]
        data['line3_to_line1_volts_thd']                 = values[63]
        data['average_line_to_line_volts_thd']           = values[64]
        data['total_kwh_sum']                            = values[65]
        data['total_kvarh_sum']                          = values[66]
        data['import_kwh[SDM630_PHASE_NUM]']             = values[67], values[68], values[69]
        data['export_kwh[SDM630_PHASE_NUM]']             = values[70], values[71], values[72]
        data['total_kwh[SDM630_PHASE_NUM]']              = values[73], values[74], values[75]
        data['import_kvarh[SDM630_PHASE_NUM]']           = values[76], values[77], values[78]
        data['export_kvarh[SDM630_PHASE_NUM]']           = values[79], values[80], values[81]
        data['total_kvarh[SDM630_PHASE_NUM]']            = values[82], values[83], values[84]

        table = EnergyMeterTable(data, 50, 2, self)
        # add Qt.Window to table's flags 
        table.setWindowFlags(table.windowFlags() | Qt.Window)
        table.resize(500, 700)
        table.show()

    def dc_fault_reset_clicked(self):
        self.evse.reset_dc_fault_current_state(0xDC42FA23)

    def energy_meter_reset_clicked(self):
        self.evse.reset_energy_meter_relative_energy()

    def gpio_changed(self):
        shutdown_input = self.combo_shutdown_input.currentIndex()
        gpio_input     = 0 # self.combo_gpio_input.currentIndex()
        gpio_output    = self.combo_gpio_output.currentIndex()
        self.evse.set_gpio_configuration(shutdown_input, gpio_input, gpio_output)

    def control_pilot_config_cb(self, disconnected):
        self.label_control_pilot.setText('Disconnected: {0}'.format(disconnected))

    def energy_meter_values_cb(self, emv):
        self.label_energy_meter_values.setText('Power: {0:.2f}W, Current: {1:.2f}A, {2:.2f}A, {3:.2f}A\nActive Phases: {4}, Connected Phases: {5}'.format(emv.power, *emv.current, str(emv.phases_active), str(emv.phases_connected)))

    def energy_meter_errors_cb(self, eme):
        self.label_energy_meter_errors.setText('Error Counts: {0}'.format(str(eme)))

    def all_charging_slots_cb(self, acs):
        for i in range(len(self.spin_slot_current)):
            self.spin_slot_current[i].blockSignals(True)
            self.spin_slot_current[i].setValue(int(acs.max_current[i]/1000))
            self.spin_slot_current[i].blockSignals(False)
            self.check_slot_active[i].blockSignals(True)
            self.check_slot_active[i].setChecked(bool(acs.active_and_clear_on_disconnect[i] & 1))
            self.check_slot_active[i].blockSignals(False)
            self.check_slot_clear[i].blockSignals(True)
            self.check_slot_clear[i].setChecked(bool(acs.active_and_clear_on_disconnect[i] & 2))
            self.check_slot_clear[i].blockSignals(False)

    def state_cb(self, state):
        self.label_dc_fault_current_state.setText('State: {0}, Pin x6: {1}, Pin x30: {2}, Pin err: {3}, Sensor Type {4}'.format(DC_FAULT_STATE[state.dc_fault_current_state & 0b111], (state.dc_fault_current_state >> 3) & 1, (state.dc_fault_current_state >> 4) & 1, (state.dc_fault_current_state >> 5) & 1, (state.dc_fault_current_state >> 6) & 1))
        self.label_iec61851_state.setText(IEC61851_STATE[state.iec61851_state])
        self.label_charger_state.setText(CHARGER_STATE[state.charger_state])
        self.label_contactor_check.setText('State: {0}, PE Error: {1}, Error: {2}'.format(str(bin(state.contactor_state)), state.contactor_error & 1, state.contactor_error >> 1))
        self.label_lock_state.setText(LOCK_STATE[state.lock_state])

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

    def get_hardware_configuration_async(self, conf):
        self.label_jumper_configuration.setText(JUMPER_CONFIGURATON[conf.jumper_configuration])
        self.label_lock_switch.setText(LOCK_SWITCH[conf.has_lock_switch])

    def get_indicator_led_async(self, led):
        self.spin_duration.blockSignals(True)
        self.spin_duration.setValue(led.duration)
        self.spin_duration.blockSignals(False)

        self.combobox_indication.blockSignals(True)
        if led.indication == -1:
           self.combobox_indication.setCurrentIndex(0)
        elif led.indication == 0:
           self.combobox_indication.setCurrentIndex(1)
        elif led.indication == 64:
           self.combobox_indication.setCurrentIndex(2)
        elif led.indication == 128:
           self.combobox_indication.setCurrentIndex(3)
        elif led.indication == 192:
           self.combobox_indication.setCurrentIndex(4)
        elif led.indication == 255:
           self.combobox_indication.setCurrentIndex(5)
        elif led.indication == 1001:
           self.combobox_indication.setCurrentIndex(6)
        elif led.indication == 1002:
           self.combobox_indication.setCurrentIndex(7)
        elif led.indication == 1003:
           self.combobox_indication.setCurrentIndex(8)
        else:
           self.combobox_indication.setCurrentIndex(-1)
        self.combobox_indication.blockSignals(False)

    def get_button_configuration_async(self, config):
        self.combo_button_config.blockSignals(True)
        self.combo_button_config.setCurrentIndex(config)
        self.combo_button_config.blockSignals(False)

    def get_gpio_configuration_async(self, config):
        self.combo_shutdown_input.blockSignals(True)
        self.combo_gpio_input.blockSignals(True)
        self.combo_gpio_output.blockSignals(True)
        self.combo_shutdown_input.setCurrentIndex(config.shutdown_input_configuration)
#        self.combo_gpio_input.setCurrentIndex(config.input_configuration)
        self.combo_gpio_output.setCurrentIndex(config.output_configuration)
        self.combo_shutdown_input.blockSignals(False)
        self.combo_gpio_input.blockSignals(False)
        self.combo_gpio_output.blockSignals(False)

    def start(self):
        async_call(self.evse.get_hardware_configuration, None, self.get_hardware_configuration_async, self.increase_error_count)
        async_call(self.evse.get_indicator_led, None, self.get_indicator_led_async, self.increase_error_count)
        async_call(self.evse.get_button_configuration, None, self.get_button_configuration_async, self.increase_error_count)
        async_call(self.evse.get_gpio_configuration, None, self.get_gpio_configuration_async, self.increase_error_count)
        self.cbe_state.set_period(100)
        self.cbe_low_level_state.set_period(100)
        self.cbe_energy_meter_values.set_period(100)
        self.cbe_energy_meter_errors.set_period(100)
        self.cbe_control_pilot_config.set_period(100)
        self.cbe_all_charging_slots.set_period(500)

    def stop(self):
        self.cbe_state.set_period(0)
        self.cbe_low_level_state.set_period(0)
        self.cbe_energy_meter_values.set_period(0)
        self.cbe_energy_meter_errors.set_period(0)
        self.cbe_control_pilot_config.set_period(0)
        self.cbe_all_charging_slots.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletEVSEV2.DEVICE_IDENTIFIER
