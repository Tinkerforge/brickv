# -*- coding: utf-8 -*-
"""
IMU Plugin
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012-2015 Matthias Bolte <matthias@tinkerforge.com>

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

import urllib.request
import urllib.error
import html

from PyQt5.QtWidgets import QWidget, QMessageBox, QProgressDialog
from PyQt5.QtCore import Qt

from brickv.plugin_system.plugins.imu.ui_calibrate_import_export import Ui_calibrate_import_export
from brickv.imu_calibration import parse_imu_calibration, IMU_CALIBRATION_URL
from brickv.bindings import ip_connection
from brickv.utils import get_main_window
from brickv.urlopen import urlopen

class CalibrateImportExport(QWidget, Ui_calibrate_import_export):
    def __init__(self, parent):
        QWidget.__init__(self)

        self.setupUi(self)

        self.parent = parent
        self.imu = self.parent.imu

        self.restore_button.clicked.connect(self.restore_clicked)
        self.export_button.clicked.connect(self.export_clicked)
        self.import_button.clicked.connect(self.import_clicked)

    def start(self):
        pass

    def stop(self):
        pass

    def popup_ok(self, title, message):
        QMessageBox.information(get_main_window(), title, message, QMessageBox.Ok)

    def popup_fail(self, title, message):
        QMessageBox.critical(get_main_window(), title, message, QMessageBox.Ok)

    def create_progress_bar(self, title):
        progress = QProgressDialog(self)
        progress.setAutoClose(False)
        progress.setWindowTitle(title)
        progress.setCancelButton(None)
        progress.setWindowModality(Qt.WindowModal)
        return progress

    def restore_clicked(self):
        progress = self.create_progress_bar('Factory Calibration')
        uid = self.parent.parent.uid

        progress.setLabelText('Downloading factory calibration')
        progress.setMaximum(0)
        progress.setValue(0)
        progress.show()

        try:
            imu_calibration_text = b'# This is the factory calibration\n\n'
            response = urlopen(IMU_CALIBRATION_URL + '{0}.txt'.format(uid))
            chunk = response.read(1024)

            while len(chunk) > 0:
                imu_calibration_text += chunk
                chunk = response.read(1024)

            response.close()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                progress.cancel()
                self.popup_ok('Factory Calibration', 'No factory calibration available')
                return
            else:
                progress.cancel()
                self.popup_fail('Factory Calibration', 'Could not download factory calibration')
                return
        except urllib.error.URLError:
            progress.cancel()
            self.popup_fail('Factory Calibration', 'Could not download factory calibration')
            return

        try:
            imu_calibration_text = imu_calibration_text.decode('utf-8')
        except UnicodeDecodeError as e:
            self.popup_fail('Factory Calibration',
                            ("Factory calibration is malformed, please report this error to " +
                             "<a href='mailto:info@tinkerforge.com'>info@tinkerforge.com</a>:<br/><br/> {0}")
                            .format(html.escape(str(e))))
            return

        progress.cancel()

        self.text_edit.setPlainText(imu_calibration_text)

        try:
            parsed = parse_imu_calibration(imu_calibration_text)
        except (ValueError, TypeError):
            self.popup_fail('Factory Calibration',
                            "Factory calibration is malformed, please report this error to " +
                            "<a href='mailto:info@tinkerforge.com'>info@tinkerforge.com</a>")
            return

        try:
            for value in parsed:
                self.imu.set_calibration(value[0], value[1])
        except ip_connection.Error as e:
            self.popup_fail('Factory Calibration', 'Could not apply calibration: ' + e.description)
            return

        self.parent.refresh_values()

        self.popup_ok('Factory Calibration', 'Successfully restored factory calibration')

    def import_clicked(self):
        text = self.text_edit.toPlainText()

        try:
            for value in parse_imu_calibration(text):
                self.imu.set_calibration(value[0], value[1])
        except UnicodeDecodeError:
            message = """Could not parse data, please check the syntax:
Each line starts with "calibration type:"
followed by the x, y and z calibration, separated by a comma.
Multiplier and Divider are written as "mul/div" """
            self.popup_fail('Calibration Import', message)
            return
        except ip_connection.Error as e:
            self.popup_fail('Calibration Import', 'Could not import calibration: ' + e.description)
            return

        self.parent.refresh_values()

        self.popup_ok('Calibration Import', 'Successfully imported calibration')

    def export_clicked(self):
        text = """# Each line starts with "calibration type:"
# followed by the x, y and z calibration, separated by a comma.
# Multiplier and Divider are written as "mul/div"

"""
        c = []
        try:
            for i in range(6):
                c.append(self.imu.get_calibration(i))
        except ip_connection.Error as e:
            self.popup_fail('Calibration Export', 'Could not read calibration from IMU Brick: ' + e.description)
            return

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
