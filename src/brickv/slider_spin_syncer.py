# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2020 Olaf Lüke <olaf@tinkerforge.com>

slider_spin_syncer.py: Sync QSlider and QSpinBox

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

class SliderSpinSyncer:
    def __init__(self, slider, spin, changed_callback, spin_signal='editingFinished'):
        self.slider = slider
        self.spin = spin
        self.changed_callback = changed_callback

        self.slider.valueChanged.connect(self.set_spinbox_from_slider_value)
        self.slider.sliderMoved.connect(self.set_spinbox_from_slider_position)
        getattr(self.spin, spin_signal).connect(self.set_slider_from_spinbox)

    def set_value(self, value):
        old_state = self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(old_state)

        old_state = self.spin.blockSignals(True)
        self.spin.setValue(value)
        self.spin.blockSignals(old_state)

    def set_spinbox_from_slider_value(self):
        value = self.slider.value()
        self.spin.setValue(value)
        self.report_change(value)

    def set_spinbox_from_slider_position(self):
        self.spin.setValue(self.slider.sliderPosition())

    def set_slider_from_spinbox(self):
        value = self.spin.value()
        self.slider.setValue(value)
        self.report_change(value)

    def report_change(self, value):
        changed_callback = self.changed_callback

        if changed_callback != None:
            changed_callback(value)
