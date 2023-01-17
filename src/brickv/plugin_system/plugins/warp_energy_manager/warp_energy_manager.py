# -*- coding: utf-8 -*-
"""
WARP Energy Manager Plugin
Copyright (C) 2021 Olaf Lüke <olaf@tinkerforge.com>

warp_energy_manager.py: WARP Energy Manager Plugin Implementation

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

from typing import ValuesView
from PyQt5.QtCore import  QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPixmap, QIcon, QPainter
from PyQt5.QtWidgets import QErrorMessage, QInputDialog, QAction, QTableWidget, QTableWidgetItem

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_warp_energy_manager import BrickletWARPEnergyManager
from brickv.plugin_system.plugins.warp_energy_manager.ui_warp_energy_manager import Ui_WARPEnergyManager
from brickv.slider_spin_syncer import SliderSpinSyncer
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

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

class WARPEnergyManager(COMCUPluginBase, Ui_WARPEnergyManager):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletWARPEnergyManager, *args)

        self.warp = self.device

        self.changing = False
        self.set_rgb_value_response_expected = None

        self.setupUi(self)

        self.r_syncer = SliderSpinSyncer(self.slider_r, self.spin_r, self.rgb_changed, spin_signal='valueChanged')
        self.g_syncer = SliderSpinSyncer(self.slider_g, self.spin_g, self.rgb_changed, spin_signal='valueChanged')
        self.b_syncer = SliderSpinSyncer(self.slider_b, self.spin_b, self.rgb_changed, spin_signal='valueChanged')

        self.h_syncer = SliderSpinSyncer(self.slider_h, self.spin_h, self.hsl_changed, spin_signal='valueChanged')
        self.s_syncer = SliderSpinSyncer(self.slider_s, self.spin_s, self.hsl_changed, spin_signal='valueChanged')
        self.l_syncer = SliderSpinSyncer(self.slider_l, self.spin_l, self.hsl_changed, spin_signal='valueChanged')

        self.checkbox_enable_contactor.stateChanged.connect(self.enable_contactor_changed)
        self.checkbox_enable_output.stateChanged.connect(self.enable_output_changed)
        self.button_energy_meter_reset.clicked.connect(self.energy_meter_reset_clicked)
        self.button_energy_meter_detailed.clicked.connect(self.energy_meter_detailed_clicked)
        self.cbe_input_voltage = CallbackEmulator(self, self.warp.get_input_voltage, None, self.cb_input_voltage, self.increase_error_count)
        self.cbe_input = CallbackEmulator(self, self.warp.get_input, None, self.cb_input, self.increase_error_count)
        self.cbe_state = CallbackEmulator(self, self.warp.get_state, None, self.cb_state, self.increase_error_count)
        self.cbe_energy_meter_values = CallbackEmulator(self, self.warp.get_energy_meter_values, None, self.energy_meter_values_cb, self.increase_error_count)
        self.cbe_energy_meter_state = CallbackEmulator(self, self.warp.get_energy_meter_state, None, self.energy_meter_state_cb, self.increase_error_count)

        def set_color(r, g, b):
            self.changing = True
            self.spin_r.setValue(r)
            self.spin_g.setValue(g)
            self.spin_b.setValue(b)
            self.changing = False
            self.rgb_changed()

        for color, button in zip([(0, 0, 0), (255, 255, 255), (255, 0, 0), (255, 255, 0),
                                  (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)],
                                 [self.button_black, self.button_white, self.button_red, self.button_yellow,
                                  self.button_green, self.button_cyan, self.button_blue, self.button_magenta]):
            button.clicked.connect(lambda clicked, c=color: set_color(*c))
            pixmap = QPixmap(16, 16)
            QPainter(pixmap).fillRect(0, 0, 16, 16, QColor(*color))
            button.setIcon(QIcon(pixmap))
            button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

    def cb_input_voltage(self, voltage):
        self.label_input_voltage.setText('{:.2f}V'.format(voltage / 1000.0))

    def cb_input(self, input):
        t = {True: 'High', False: 'Low'}
        self.label_input0.setText(t[input[0]])
        self.label_input1.setText(t[input[1]])

    def cb_state(self, state):
        self.label_contactor_check_state.setText(str(state))

    def energy_meter_values_cb(self, emv):
        self.label_energy_meter_values.setText('Power: {0:.2f}W, Energy Import: {1:.2f}Wh, Energy Export: {2:.2f}Wh'.format(emv.power, emv.energy_import, emv.energy_export))

    def energy_meter_state_cb(self, ems):
        self.label_energy_meter_state.setText('Type: {0}, Error Counts: {1}'.format(ems.energy_meter_type, str(ems.error_count)))

    def energy_meter_detailed_clicked(self):
        values = self.warp.get_energy_meter_detailed_values()
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

    def start(self):
        # Use response expected for set_rgb_value function, to make sure that the
        # data queue can't fill up while you move the slider around.
        self.set_rgb_value_response_expected = self.warp.get_response_expected(self.warp.FUNCTION_SET_RGB_VALUE)
        self.warp.set_response_expected(self.warp.FUNCTION_SET_RGB_VALUE, True)

        async_call(self.warp.get_rgb_value, None, self.get_rgb_value_async, self.increase_error_count, expand_result_tuple_for_callback=True)
        async_call(self.warp.get_contactor, None, self.get_contactor_async, self.increase_error_count)
        async_call(self.warp.get_output, None, self.get_output_async, self.increase_error_count)
        self.cbe_input_voltage.set_period(100)
        self.cbe_input.set_period(100)
        self.cbe_state.set_period(100)
        self.cbe_energy_meter_values.set_period(100)
        self.cbe_energy_meter_state.set_period(100)

    def stop(self):
        self.cbe_input_voltage.set_period(0)
        self.cbe_input.set_period(0)
        self.cbe_state.set_period(0)
        self.cbe_energy_meter_values.set_period(0)
        self.cbe_energy_meter_state.set_period(0)

        if self.set_rgb_value_response_expected != None:
            self.warp.set_response_expected(self.warp.FUNCTION_SET_RGB_VALUE, self.set_rgb_value_response_expected)

    def enable_contactor_changed(self, state):
        self.warp.set_contactor(state == Qt.Checked)

    def enable_output_changed(self, state):
        self.warp.set_output(state == Qt.Checked)

    def energy_meter_reset_clicked(self):
        self.warp.reset_energy_meter_relative_energy()

    def rgb_changed(self, *_args):
        if self.changing:
            return

        r, g, b = self.spin_r.value(), self.spin_g.value(), self.spin_b.value()
        rgb = QColor(r, g, b)
        h, s, l = rgb.hslHue(), rgb.hslSaturation(), rgb.lightness()

        self.changing = True

        if h != -1: # Qt returns -1 if the color is achromatic (i.e. grey).
            self.spin_h.setValue(h)
        self.spin_s.setValue(s)
        self.spin_l.setValue(l)
        self.changing = False

        self.warp.set_rgb_value(r, g, b)
        self.label_color.setStyleSheet('QLabel {{ background: #{:02x}{:02x}{:02x} }}'.format(r, g, b))

    def hsl_changed(self, *_args):
        if self.changing:
            return

        h, s, l = self.spin_h.value(), self.spin_s.value(), self.spin_l.value()
        hsl = QColor()
        hsl.setHsl(h, s, l)
        r, g, b = hsl.red(), hsl.green(), hsl.blue()

        self.changing = True
        self.spin_r.setValue(r)
        self.spin_g.setValue(g)
        self.spin_b.setValue(b)
        self.changing = False

        self.warp.set_rgb_value(r, g, b)
        self.label_color.setStyleSheet('QLabel {{ background: #{:02x}{:02x}{:02x} }}'.format(r, g, b))

    def get_rgb_value_async(self, r, g, b):
        self.changing = True
        self.spin_r.setValue(r)
        self.spin_g.setValue(g)
        self.spin_b.setValue(b)
        self.changing = False
        self.rgb_changed()

    def get_contactor_async(self, value):
        self.checkbox_enable_contactor.blockSignals(True)
        self.checkbox_enable_contactor.setChecked(value)
        self.checkbox_enable_contactor.blockSignals(False)

    def get_output_async(self, value):
        self.checkbox_enable_output.blockSignals(True)
        self.checkbox_enable_output.setChecked(value)
        self.checkbox_enable_output.blockSignals(False)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletWARPEnergyManager.DEVICE_IDENTIFIER
