# -*- coding: utf-8 -*-
"""
Piezo Speaker Plugin
Copyright (C) 2018-2019 Olaf Lüke <olaf@tinkerforge.com>

piezo_speaker_v2.py: Piezo Speaker 2.0 Plugin Implementation

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

from PyQt5.QtCore import pyqtSignal, QTimer

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_piezo_speaker_v2 import BrickletPiezoSpeakerV2
from brickv.plugin_system.plugins.piezo_speaker_v2.ui_piezo_speaker_v2 import Ui_PiezoSpeakerV2
from brickv.slider_spin_syncer import SliderSpinSyncer

class PiezoSpeakerV2(COMCUPluginBase, Ui_PiezoSpeakerV2):
    qtcb_beep_finished = pyqtSignal()
    qtcb_alarm_finished = pyqtSignal()

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletPiezoSpeakerV2, *args)

        self.setupUi(self)

        self.ps = self.device

        self.qtcb_beep_finished.connect(self.cb_beep)
        self.ps.register_callback(self.ps.CALLBACK_BEEP_FINISHED, self.qtcb_beep_finished.emit)
        self.qtcb_alarm_finished.connect(self.cb_alarm)
        self.ps.register_callback(self.ps.CALLBACK_ALARM_FINISHED, self.qtcb_alarm_finished.emit)

        self.frequency_syncer = SliderSpinSyncer(self.frequency_slider, self.frequency_spinbox, self.frequency_changed, spin_signal='valueChanged')
        self.volume_syncer = SliderSpinSyncer(self.volume_slider, self.volume_spinbox, self.volume_changed, spin_signal='valueChanged')
        self.beep_duration_syncer = SliderSpinSyncer(self.beep_duration_slider, self.beep_duration_spinbox, self.beep_duration_changed, spin_signal='valueChanged')
        self.alarm_duration_syncer = SliderSpinSyncer(self.alarm_duration_slider, self.alarm_duration_spinbox, self.alarm_duration_changed, spin_signal='valueChanged')
        self.alarm_start_frequency_syncer = SliderSpinSyncer(self.alarm_start_frequency_slider, self.alarm_start_frequency_spinbox, self.alarm_start_frequency_changed, spin_signal='valueChanged')
        self.alarm_end_frequency_syncer = SliderSpinSyncer(self.alarm_end_frequency_slider, self.alarm_end_frequency_spinbox, self.alarm_end_frequency_changed, spin_signal='valueChanged')
        self.alarm_step_size_syncer = SliderSpinSyncer(self.alarm_step_size_slider, self.alarm_step_size_spinbox, self.alarm_step_size_changed, spin_signal='valueChanged')
        self.alarm_step_delay_syncer = SliderSpinSyncer(self.alarm_step_delay_slider, self.alarm_step_delay_spinbox, self.alarm_step_delay_changed, spin_signal='valueChanged')

        self.beep_button.clicked.connect(self.beep_clicked)
        self.alarm_button.clicked.connect(self.alarm_clicked)

        self.new_value_timer = QTimer(self)
        self.new_value_timer.timeout.connect(self.new_value_update)
        self.last_frequency = self.frequency_spinbox.value()
        self.last_volume    = self.volume_spinbox.value()

    def new_value_update(self):
        frequency = self.frequency_spinbox.value()
        if frequency != self.last_frequency:
            self.ps.update_frequency(frequency)
            self.last_frequency = frequency

        volume = self.volume_spinbox.value()
        if volume != self.last_volume:
            self.ps.update_volume(volume)
            self.last_volume = volume

    def frequency_changed(self, frequency):
        pass

    def volume_changed(self, volume):
        pass

    def beep_duration_changed(self, duration):
        pass

    def alarm_duration_changed(self, duration):
        pass

    def alarm_start_frequency_changed(self, start_frequency):
        end_frequency = self.alarm_end_frequency_spinbox.value()
        if start_frequency >= end_frequency:
            self.alarm_end_frequency_spinbox.setValue(start_frequency+1)

    def alarm_end_frequency_changed(self, end_frequency):
        start_frequency = self.alarm_start_frequency_spinbox.value()
        if end_frequency <= start_frequency:
            self.alarm_start_frequency_spinbox.setValue(end_frequency-1)

    def alarm_step_size_changed(self, step_size):
        pass

    def alarm_step_delay_changed(self, step_delay):
        pass

    def start(self):
        # Use timer to update frequency and volume at most 10x per second
        self.new_value_timer.start(100)

    def stop(self):
        self.new_value_timer.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletPiezoSpeakerV2.DEVICE_IDENTIFIER

    def cb_beep(self):
        pass

    def cb_alarm(self):
        pass

    def beep_clicked(self):
        freq     = self.frequency_spinbox.value()
        volume   = self.volume_spinbox.value()
        duration = self.beep_duration_spinbox.value()

        self.ps.set_beep(freq, volume, duration)

    def alarm_clicked(self):
        start_freq = self.alarm_start_frequency_spinbox.value()
        end_freq   = self.alarm_end_frequency_spinbox.value()
        step_size  = self.alarm_step_size_spinbox.value()
        step_delay = self.alarm_step_delay_spinbox.value()
        volume     = self.volume_spinbox.value()
        duration   = self.alarm_duration_spinbox.value()

        self.ps.set_alarm(start_freq, end_freq, step_size, step_delay, volume, duration)
