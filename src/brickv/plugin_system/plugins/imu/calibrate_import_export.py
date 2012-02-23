# -*- coding: utf-8 -*-  
"""
IMU Plugin
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>

calibrate_import_export.py: IMU Calibration Import/Export implementation

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

from PyQt4.QtGui import QWidget, QMessageBox

from ui_calibrate_import_export import Ui_calibrate_import_export

class CalibrateImportExport(QWidget, Ui_calibrate_import_export):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.setupUi(self)
        
        self.parent = parent
        self.imu = self.parent.imu
        
        self.export_button.pressed.connect(self.export_pressed)
        self.import_button.pressed.connect(self.import_pressed)
        
    def start(self):
        pass
        
    def stop(self):
        pass
    
    def popup_fail(self):
        text = """Could not parse data, please check the syntax:
Each line starts with "calibration type:"
followed by the x, y and z calibration, separated by a comma.
Multiplier and Divider are written as "mul/div" """

        QMessageBox.critical(self, "Failure", text, QMessageBox.Ok)
    
    def import_pressed(self):
        text = str(self.text_edit.toPlainText())
        
        values = []
        try:
            for line in text.split('\n'):
                if not line.startswith('#'):
                    x = line.split(':')
                    if len(x) != 2:
                        continue
                    
                    y = x[1].split(',')
                    
                    if x[0] in ('0', '2', '4'):
                        a = y[0].split('/')
                        b = y[1].split('/')
                        c = y[2].split('/')
                        values.append([int(x[0]), [int(a[0]), int(b[0]), int(c[0]), int(a[1]), int(b[1]), int(c[1]), 0, 0, 0, 0]])
                    elif x[0] in ('1', '3'):
                        values.append([int(x[0]), [int(y[0]), int(y[1]), int(y[2]), 0, 0, 0, 0, 0, 0, 0]])
                    elif x[0] in ('5',):
                        values.append([int(x[0]), [int(y[0]), int(y[1]), int(y[2]), int(y[3]), int(y[4]), int(y[5]), int(y[6]), int(y[7]), 0, 0]])
                        
            for value in values:
                self.imu.set_calibration(value[0], value[1])
        except:
            self.popup_fail()
            return
                
        self.parent.refresh_values()
        
    def export_pressed(self):
        text = """# Each line starts with "calibration type:"
# followed by the x, y and z calibration, separated by a comma.
# Multiplier and Divider are written as "mul/div"

"""
        c = []
        for i in range(6):
            c.append(self.imu.get_calibration(i))
            
            
        text += '0: ' + str(c[0][0]) + '/' + str(c[0][3]) + ', ' + str(c[0][1]) + '/' + str(c[0][4]) + ', ' + str(c[0][2]) + '/' + str(c[0][5])
        text += '\n'
        text += '1: ' + str(c[1][0]) + ', ' + str(c[1][1]) + ', ' + str(c[1][2])
        text += '\n'
        text += '2: ' + str(c[2][0]) + '/' + str(c[2][3]) + ', ' + str(c[2][1]) + '/' + str(c[2][4]) + ', ' + str(c[2][2]) + '/' + str(c[2][5])
        text += '\n'
        text += '3: ' + str(c[3][0]) + ', ' + str(c[3][1]) + ', ' + str(c[3][2])
        text += '\n'
        text += '4: ' + str(c[4][0]) + '/' + str(c[4][3]) + ', ' + str(c[4][1]) + '/' + str(c[4][4]) + ', ' + str(c[4][2]) + '/' + str(c[4][5])
        text += '\n'
        text += '5: ' + str(c[5][0]) + ', ' + str(c[5][1]) + ', ' + str(c[5][2]) + ', ' + str(c[5][3]) + ', ' + str(c[5][4]) + ', ' + str(c[5][5]) + ', ' + str(c[5][6]) + ', ' + str(c[5][7])
        
        self.text_edit.setPlainText(text)
