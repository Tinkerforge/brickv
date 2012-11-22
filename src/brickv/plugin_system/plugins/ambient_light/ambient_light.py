# -*- coding: utf-8 -*-  
"""
Ambient Light Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>

ambientlight.py: Ambient Light Bricklet Plugin Implementation

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

from plugin_system.plugin_base import PluginBase
from plot_widget import PlotWidget
from bindings import ip_connection
from bindings.bricklet_ambient_light import BrickletAmbientLight
from async_call import async_call

from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPainter, QColor, QBrush, QFrame
from PyQt4.QtCore import Qt, pyqtSignal

class AmbientLightFrame(QFrame):
    def __init__(self, parent = None):
        QFrame.__init__(self, parent)
        self.color = QColor(128, 128, 128)
        self.setMinimumSize(25, 25)
        self.setMaximumSize(25, 25)
        
    def set_color(self, r, g, b):
        self.color = QColor(r, g, b)
        self.repaint()
        
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QBrush(self.color))
        qp.setPen(self.color)
        qp.drawRect(0, 0, 25, 25)
        qp.setBrush(Qt.NoBrush)
        qp.setPen(Qt.black)
        qp.drawRect(1, 1, 24, 24)
        qp.end()
        
class IlluminanceLabel(QLabel):
    def setText(self, text):
        text = "Illuminance: " + text + " lx (Lux)"
        super(IlluminanceLabel, self).setText(text)
    
class AmbientLight(PluginBase):
    qtcb_illuminance = pyqtSignal(int)
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Ambient Light Bricklet', version)
        
        self.al = BrickletAmbientLight(uid, ipcon)
        
        self.qtcb_illuminance.connect(self.cb_illuminance)
        self.al.register_callback(self.al.CALLBACK_ILLUMINANCE,
                                  self.qtcb_illuminance.emit) 
        
        self.illuminance_label = IlluminanceLabel('Illuminance: ')
        self.alf = AmbientLightFrame()
        
        self.current_value = 0
        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Illuminance [lx]', plot_list)
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.illuminance_label)
        layout_h.addWidget(self.alf)
        layout_h.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addWidget(self.plot_widget)
        
    def start(self):
        async_call(self.al.get_illuminance, None, self.cb_illuminance, self.increase_error_count)
        
        try:
            self.al.set_illuminance_callback_period(100)
        except ip_connection.Error:
            return
        
        self.plot_widget.stop = False
        
    def stop(self):
        try:
            self.al.set_illuminance_callback_period(0)
        except ip_connection.Error:
            pass
        
        self.plot_widget.stop = True

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAmbientLight.DEVICE_IDENTIFIER
    
    def get_current_value(self):
        return self.current_value

    def cb_illuminance(self, illuminance):
        self.current_value = illuminance/10.0
        self.illuminance_label.setText(str(self.current_value))        
        
        value = illuminance*255/9000
        self.alf.set_color(value, value, value)
