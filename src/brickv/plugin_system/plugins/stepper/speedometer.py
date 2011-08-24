# -*- coding: utf-8 -*-  
"""
brickv (Brick Viewer) 
Copyright (C) 2010 Olaf Lüke <olaf@tinkerforge.com>

speedometer.py: TODO

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

from PyQt4.QtGui import QColor, QPalette, QSizePolicy
from PyQt4.QtCore import Qt, QRect

import PyQt4.Qwt5 as Qwt

class SpeedoMeter(Qwt.QwtDial):
    def __init__(self, *args):
        Qwt.QwtDial.__init__(self, *args)
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.direction = 'Standstill'
        self.setWrapping(False)
        self.setReadOnly(True)

        self.setOrigin(135.0)
        self.setScaleArc(0.0, 270.0)
        self.setScale(0, 5000, 500)
        self.setRange(0, 5000)
        self.scale = 5000

        self.setNeedle(Qwt.QwtDialSimpleNeedle(Qwt.QwtDialSimpleNeedle.Arrow,
                                               True,
                                               QColor(Qt.red),
                                               QColor(Qt.gray).light(130)))

        self.setScaleOptions(Qwt.QwtDial.ScaleTicks | Qwt.QwtDial.ScaleLabel)
        self.setScaleTicks(0, 4, 8)
        
    def set_velocity(self, value):
        if value > 0:
            self.direction = 'Forward'
        elif value < 0: 
            self.direction = 'Backward'
        else:
            self.direction = 'Standstill'
            
        if value < 0:
            value = -value
            
        if value <= 5000:
            if self.scale != 5000:
                self.setScale(0, 5000, 500)
                self.setRange(0, 5000)
                self.scale = 5000
        else:
            if self.scale != 65000:
                self.setScale(0, 65000, 10000)
                self.setRange(0, 65000)
                self.scale = 65000
            
        self.setValue(value)
    
    def drawScaleContents(self, painter, center, radius):
        rect = QRect(0, 0, 2 * radius, 2 * radius + 30)
        rect.moveCenter(center)
        painter.setPen(self.palette().color(QPalette.Text))
        painter.drawText(rect, Qt.AlignBottom | Qt.AlignHCenter, self.direction)