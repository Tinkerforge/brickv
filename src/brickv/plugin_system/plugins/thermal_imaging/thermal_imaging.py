# -*- coding: utf-8 -*-
"""
Thermal Imaging Plugin
Copyright (C) 2017 Olaf Lüke <olaf@tinkerforge.com>

thermal_imaging.py: Thermal Imaging Plugin Implementation

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

import colorsys
import math

from PyQt4.QtCore import pyqtSignal, Qt, QSize, QPoint
from PyQt4.QtGui import QWidget, QImage, QPainter, QPen, QApplication

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.thermal_imaging.ui_thermal_imaging import Ui_ThermalImaging
from brickv.bindings.bricklet_thermal_imaging import BrickletThermalImaging
from brickv.callback_emulator import CallbackEmulator
from brickv.async_call import async_call

class ThermalImage(QWidget):
    def __init__(self, w, h, parent=None):
        super(ThermalImage, self).__init__(parent)

        self.setAttribute(Qt.WA_StaticContents)
    
        self.parent = parent
        self.width = w
        self.height = h
        self.image_pixel_width = 5
        self.image = QImage(QSize(w, h), QImage.Format_RGB32)

        self.setMaximumSize(w*self.image_pixel_width, w*self.image_pixel_width)
        self.setMinimumSize(w*self.image_pixel_width, h*self.image_pixel_width)

        self.create_rgb_lookup()
        self.clear_image()
        self.agc_roi_from = None
        self.agc_roi_to = None
        
    def create_rgb_lookup(self):
        self.rgb_lookup = []
        
        # Standard
        standard = []
        for x in range(256):
            x /= 255.0
            r = int(round(255*math.sqrt(x)))
            g = int(round(255*pow(x,3)))
            if math.sin(2 * math.pi * x) >= 0:
                b = int(round(255*math.sin(2 * math.pi * x)))
            else:
                b = 0
            standard.append((r, g, b))
            
        self.rgb_lookup.append(standard)
            
        # Greyscale
        self.rgb_lookup.append([(x, x, x) for x in range(256)]) 

#        rainbow = []
#        for i in range(256):
#            r, g, b = colorsys.hsv_to_rgb(1.0*i/256, 1, 1)
#            r = int(round(r*255))
#            g = int(round(g*255))
#            b = int(round(b*255))
#            
#            rainbow.append((r, g, b))

        # Hot Cold
        self.rgb_lookup.append([(0, 0, 255)]*32 + [(0,0,0)]*(256-2*32) + [(255,0,0)]*32)
        
        
    def new_image_data(self, data, is_14bit = False):
        table_index = self.parent.color_palette_box.currentIndex() 
        for i in range(len(data)):
            value = data[i]
            if is_14bit:
                value = data[i] >> 6
            r, g, b = self.rgb_lookup[table_index][value]
            
            self.image.setPixel(QPoint(i%80, i//80), (r << 16) | (g << 8) | b)

        self.update()

    def clear_image(self):
        self.image.fill(Qt.black)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(event.rect(), self.image.scaledToWidth(self.width*self.image_pixel_width, Qt.SmoothTransformation))
        if self.agc_roi_from and self.agc_roi_to:
            pen = QPen()
            pen.setColor(Qt.green)
            pen.setWidth(1)
            painter.setPen(pen)
            
            from_x = (self.agc_roi_from.x())//self.image_pixel_width
            from_y = (self.agc_roi_from.y())//self.image_pixel_width
            to_x   = (self.agc_roi_to.x() - self.agc_roi_from.x())//self.image_pixel_width
            to_y   = (self.agc_roi_to.y() - self.agc_roi_from.y())//self.image_pixel_width
            painter.drawRect(from_x*self.image_pixel_width + 1, 
                             from_y*self.image_pixel_width + 1, 
                             to_x*self.image_pixel_width + 1, 
                             to_y*self.image_pixel_width + 1)
            
            self.parent.update_agc_roi_label()
            
    def clip_pos(self, pos):
        max_width  = self.width *self.image_pixel_width-1
        max_height = self.height*self.image_pixel_width-1
        if pos.x() < 0:
            pos.setX(0)
        if pos.x() > max_width:
            pos.setX(max_width)  
            
        if pos.y() < 0:
            pos.setY(0)
        if pos.y() > max_height:
            pos.setY(max_height)
            
        return pos

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.parent.agc_roi_button.isChecked():
                self.agc_roi_from = self.clip_pos(event.pos())

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton):
            if self.parent.agc_roi_button.isChecked():
                self.agc_roi_to = self.clip_pos(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.parent.agc_roi_button.isChecked():
                self.agc_roi_to = self.clip_pos(event.pos())
                self.parent.agc_roi_button.setChecked(False)
                QApplication.restoreOverrideCursor()
                self.parent.update_agc_data()

class ThermalImaging(COMCUPluginBase, Ui_ThermalImaging):
    qtcb_image = pyqtSignal(int, tuple)
    qtcb_raw_image = pyqtSignal(int, tuple)
    
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletThermalImaging, *args)

        self.setupUi(self)
        self.thermal_imaging = self.device
        
        self.thermal_image = ThermalImage(80, 60, self)
        self.thermal_image_layout.insertWidget(0, self.thermal_image)
        
        self.agc_roi_button.clicked.connect(self.cb_agc_roi_button)
        
        self.agc_clip_limit_high_spin.editingFinished.connect(self.update_agc_data)
        self.agc_clip_limit_low_spin.editingFinished.connect(self.update_agc_data)
        self.agc_dampening_factor_spin.editingFinished.connect(self.update_agc_data)
        self.agc_empty_counts_spin.editingFinished.connect(self.update_agc_data)
        
        self.qtcb_image.connect(self.cb_qtcb_image)
        self.qtcb_raw_image.connect(self.cb_qtcb_raw_image)
        
        self.update_agc_roi_label()
                
    def get_agc_roi(self):
        if self.thermal_image.agc_roi_from != None and self.thermal_image.agc_roi_to != None:
            from_x = self.thermal_image.agc_roi_from.x()//self.thermal_image.image_pixel_width
            from_y = self.thermal_image.agc_roi_from.y()//self.thermal_image.image_pixel_width
            to_x   = self.thermal_image.agc_roi_to.x()//self.thermal_image.image_pixel_width
            to_y   = self.thermal_image.agc_roi_to.y()//self.thermal_image.image_pixel_width
        else:
            from_x = 0
            from_y = 0
            to_x   = 79
            to_y   = 59
            
        if from_x > to_x:
            from_x, to_x = from_x, to_x
            
        if from_y > to_y:
            from_y, to_y = from_y, to_y
            
        return from_x, from_y, to_x, to_y 

    def update_agc_data(self):
        roi = self.get_agc_roi()
        dampening_factor = self.agc_dampening_factor_spin.value()
        clip_limit = (self.agc_clip_limit_high_spin.value(), self.agc_clip_limit_low_spin.value())
        empty_counts = self.agc_empty_counts_spin.value()
        self.thermal_imaging.set_automatic_gain_control_config(roi, dampening_factor, clip_limit, empty_counts)
            
    def update_agc_roi_label(self):
        from_x, from_y, to_x, to_y =  self.get_agc_roi()
        self.agc_roi_label.setText('from <b>[{0}, {1}]</b> to <b>[{2}, {3}]</b>'.format(from_x, from_y, to_x, to_y))
        
    def cb_agc_roi_button(self):
        if self.agc_roi_button.isChecked():
            QApplication.setOverrideCursor(Qt.CrossCursor)
        else:
            QApplication.restoreOverrideCursor()
        
    def cb_qtcb_image(self, error, data):
        if error == 0:
            self.thermal_image.new_image_data(data)
            
    def cb_qtcb_raw_image(self, error, data):
        if error == 0:
            self.thermal_image.new_image_data(data, is_14bit=True)
    
    def cb_get_automatic_gain_control_config(self, data):
        self.thermal_image.agc_roi_from = QPoint(data.region_of_interest[0]*self.thermal_image.image_pixel_width,data.region_of_interest[1]*self.thermal_image.image_pixel_width)
        self.thermal_image.agc_roi_to   = QPoint(data.region_of_interest[2]*self.thermal_image.image_pixel_width,data.region_of_interest[3]*self.thermal_image.image_pixel_width)
        self.agc_clip_limit_high_spin.setValue(data.clip_limit[0])
        self.agc_clip_limit_low_spin.setValue(data.clip_limit[1])
        self.agc_dampening_factor_spin.setValue(data.dampening_factor)
        self.agc_empty_counts_spin.setValue(data.empty_counts)

    def start(self):
        async_call(self.thermal_imaging.get_automatic_gain_control_config, None, self.cb_get_automatic_gain_control_config, self.increase_error_count)
        self.thermal_imaging.set_callback_config(BrickletThermalImaging.CALLBACK_CONFIG_CALLBACK_IMAGE)
        self.thermal_imaging.register_callback(self.thermal_imaging.CALLBACK_IMAGE, self.qtcb_image.emit)
        self.thermal_imaging.register_callback(self.thermal_imaging.CALLBACK_RAW_IMAGE, self.qtcb_raw_image.emit)

    def stop(self):
        self.thermal_imaging.register_callback(self.thermal_imaging.CALLBACK_IMAGE, None)
        self.thermal_imaging.register_callback(self.thermal_imaging.CALLBACK_RAW_IMAGE, None)

    def destroy(self):
        pass

    def get_url_part(self):
        return 'thermal_imaging'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletThermalImaging.DEVICE_IDENTIFIER
