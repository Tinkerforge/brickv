# -*- coding: utf-8 -*-
"""
IMU 2.0 Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2015-2016 Matthias Bolte <matthias@tinkerforge.com>

imu_v2.py: IMU 2.0 Plugin implementation

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

from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtWidgets import QVBoxLayout, QFrame, QDialog, QAction, QWidget
from PyQt5.QtGui import QColor, QPalette, QPainter, QBrush

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.imu_v2.imu_v2_gl_widget import IMUV2GLWidget
from brickv.plugin_system.plugins.imu_v2.ui_imu_v2 import Ui_IMUV2
from brickv.plugin_system.plugins.imu_v2.ui_calibration import Ui_Calibration
from brickv.bindings.brick_imu_v2 import BrickIMUV2
from brickv.async_call import async_call
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import get_modeless_dialog_flags
from brickv import config

class Calibration(QDialog, Ui_Calibration):
    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())

        self.setupUi(self)

        self.text_browser.setHtml("""
<p><b>General:</b> The IMU does continous self-calibration during usage.
It is not necessary to start a specific calibration process.</p>
<p>Accelerometer and gyroscope are factory calibrated and are less susceptible
to external disturbances. As a result the offsets can be seen as negligble and
calibration is not important. For the magnetometer on the other hand calibration
is mandatory after each &quot;power on reset&quot;.</p>
<p>To make this easier we allow to save the calibration to the flash of the
IMU Brick and load the calibration on each startup. This way there is no
&quot;startup phase&quot; that is necessary until the IMU Brick has calibrated
itself.</p>
<p><b>Calibration values:</b> Saving a calibration is only possible if all
sensors are fully calibrated.</p>
<ul>
<li>green = fully calibrated,</li>
<li>yellow = calibration OK,</li>
<li>orange = calibration recommended and</li>
<li>red = not calibrated.</li>
</ul>
<p><b>Accelerometer:</b> Place the IMU Brick in 6 different stable position for
a period of a few seconds. Use slow movement between stable positions. Use at
least one position that is perpendicular to the x, y and z axis.</p>
<p><b>Magnetometer:</b> Make random movements (e.g. write a figure 8 in air).</p>
<p><b>Gyroscope:</b> Place the IMU Brick in a single stable position for a
period of several seconds.</p>
<p><b>System:</b> Wait for the system to stabilize. Use only small movements
during stabilization.</p>""")

        self.parent = parent
        self.ipcon = parent.ipcon
        self.imu = parent.imu

        self.acc_color = ColorFrame()
        self.mag_color = ColorFrame()
        self.gyr_color = ColorFrame()
        self.sys_color = ColorFrame()

        self.grid.addWidget(self.acc_color, 2, 2)
        self.grid.addWidget(self.mag_color, 3, 2)
        self.grid.addWidget(self.gyr_color, 4, 2)
        self.grid.addWidget(self.sys_color, 5, 2)

        self.save_calibration.clicked.connect(self.save_calibration_clicked)

    def save_calibration_clicked(self):
        async_call(self.imu.save_calibration, None, self.async_save_calibration, self.parent.increase_error_count)

    def async_save_calibration(self, calibration_done):
        if calibration_done:
            self.save_calibration.setText('Save Calibration Again')

    def closeEvent(self, _event):
        self.parent.button_calibration.setEnabled(True)
        self.parent.calibration = None

class ColorFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = Qt.red
        self.setMinimumSize(15, 15)
        self.setMaximumSize(15, 15)

    def set_color(self, color):
        self.color = color
        self.repaint()

    def paintEvent(self, _event):
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QBrush(self.color))
        qp.setPen(self.color)
        qp.drawRect(0, 0, 15, 15)
        qp.setBrush(Qt.NoBrush)
        qp.setPen(Qt.black)
        qp.drawRect(1, 1, 14, 14)
        qp.end()

class WrapperWidget(QWidget):
    def __init__(self, plugin):
        super().__init__()

        self.plugin = plugin

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setMinimumSize(200, 200)
        self.glWidget = IMUV2GLWidget()
        self.layout().addWidget(self.glWidget)
        self.setWindowTitle('IMU Brick 2.0 - 3D View - Brick Viewer ' + config.BRICKV_VERSION)

    def closeEvent(self, _event):
        self.plugin.imu_gl_wrapper = None
        self.plugin.button_detach_3d_view.setEnabled(True)

        # Under macOS (and sometimes under Linux) closing this window will cause a segmentation fault.
        # Somehow this is fixed by deleteLater.
        self.deleteLater()

    def minimumSizeHint(self):
        return QSize(500, 500)

    def sizeHint(self):
        return QSize(500, 500)

class IMUV2(PluginBase, Ui_IMUV2):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickIMUV2, *args)

        self.setupUi(self)

        self.imu = self.device

        self.cbe_all_data = CallbackEmulator(self.imu.get_all_data,
                                             self.all_data_callback,
                                             self.increase_error_count)

        self.imu_gl = IMUV2GLWidget(self)
        self.imu_gl.setFixedSize(200, 200)

        self.imu_gl_wrapper = None

        self.data_plot_widget = []

        self.sensor_data = [CurveValueWrapper() for i in range(23)]

        self.data_labels = [self.label_acceleration_x, self.label_acceleration_y, self.label_acceleration_z,
                            self.label_magnetic_field_x, self.label_magnetic_field_y, self.label_magnetic_field_z,
                            self.label_angular_velocity_x, self.label_angular_velocity_y, self.label_angular_velocity_z,
                            self.label_euler_angle_heading, self.label_euler_angle_roll, self.label_euler_angle_pitch,
                            self.label_quaternion_w, self.label_quaternion_x, self.label_quaternion_y, self.label_quaternion_z,
                            self.label_linear_acceleration_x, self.label_linear_acceleration_y, self.label_linear_acceleration_z,
                            self.label_gravity_vector_x, self.label_gravity_vector_y, self.label_gravity_vector_z,
                            self.label_temperature]

        self.data_rows = [[self.label_acceleration_11, self.label_acceleration_21, self.label_acceleration_22, self.label_acceleration_23, self.label_acceleration_41, self.label_acceleration_42, self.label_acceleration_43, self.label_acceleration_x, self.label_acceleration_y, self.label_acceleration_z],
                          [self.label_magnetic_field_11, self.label_magnetic_field_21, self.label_magnetic_field_22, self.label_magnetic_field_23, self.label_magnetic_field_41, self.label_magnetic_field_42, self.label_magnetic_field_43, self.label_magnetic_field_x, self.label_magnetic_field_y, self.label_magnetic_field_z],
                          [self.label_angular_velocity_11, self.label_angular_velocity_21, self.label_angular_velocity_22, self.label_angular_velocity_23, self.label_angular_velocity_41, self.label_angular_velocity_42, self.label_angular_velocity_43, self.label_angular_velocity_x, self.label_angular_velocity_y, self.label_angular_velocity_z],
                          [self.label_euler_angle_11, self.label_euler_angle_21, self.label_euler_angle_22, self.label_euler_angle_23, self.label_euler_angle_41, self.label_euler_angle_42, self.label_euler_angle_43, self.label_euler_angle_roll, self.label_euler_angle_pitch, self.label_euler_angle_heading],
                          [self.label_quaternion_11, self.label_quaternion_21, self.label_quaternion_22, self.label_quaternion_23, self.label_quaternion_24, self.label_quaternion_41, self.label_quaternion_42, self.label_quaternion_43, self.label_quaternion_44, self.label_quaternion_w, self.label_quaternion_x, self.label_quaternion_y, self.label_quaternion_z],
                          [self.label_linear_acceleration_11, self.label_linear_acceleration_21, self.label_linear_acceleration_22, self.label_linear_acceleration_23, self.label_linear_acceleration_41, self.label_linear_acceleration_42, self.label_linear_acceleration_43, self.label_linear_acceleration_x, self.label_linear_acceleration_y, self.label_linear_acceleration_z],
                          [self.label_gravity_vector_11, self.label_gravity_vector_21, self.label_gravity_vector_22, self.label_gravity_vector_23, self.label_gravity_vector_41, self.label_gravity_vector_42, self.label_gravity_vector_43, self.label_gravity_vector_x, self.label_gravity_vector_y, self.label_gravity_vector_z],
                          [self.label_temperature_11, self.label_temperature_21, self.label_temperature_41, self.label_temperature]]

        even_color = QColor(240, 240, 240)
        odd_color = QColor(255, 255, 255)

        self.data_color = [(Qt.red, even_color), (Qt.darkGreen, even_color), (Qt.blue, even_color),
                           (Qt.red, odd_color), (Qt.darkGreen, odd_color), (Qt.blue, odd_color),
                           (Qt.red, even_color), (Qt.darkGreen, even_color), (Qt.blue, even_color),
                           (Qt.red, odd_color), (Qt.darkGreen, odd_color), (Qt.blue, odd_color),
                           (Qt.magenta, even_color), (Qt.red, even_color), (Qt.darkGreen, even_color), (Qt.blue, even_color),
                           (Qt.red, odd_color), (Qt.darkGreen, odd_color), (Qt.blue, odd_color),
                           (Qt.red, even_color), (Qt.darkGreen, even_color), (Qt.blue, even_color),
                           (Qt.magenta, odd_color)]


        even_palette = QPalette()
        even_palette.setColor(QPalette.Window, even_color)
        odd_palette = QPalette()
        odd_palette.setColor(QPalette.Window, odd_color)

        for i, row in enumerate(self.data_rows):
            for label in row:
                if i % 2:
                    label.setPalette(odd_palette)
                else:
                    label.setPalette(even_palette)

                label.setAutoFillBackground(True)

        self.plot_timer = QTimer(self)
        self.plot_timer.start(100)

        for i in range(23):
            self.data_plot_widget.append(PlotWidget("",
                                                    [("", self.data_color[i][0], self.sensor_data[i], str)],
                                                    clear_button=self.clear_graphs,
                                                    x_scale_visible=False,
                                                    y_scale_visible=False,
                                                    curve_outer_border_visible=False,
                                                    curve_motion_granularity=1,
                                                    canvas_color=self.data_color[i][1],
                                                    external_timer=self.plot_timer,
                                                    curve_start='right',
                                                    key=None,
                                                    y_resolution=0.01))

        for w in self.data_plot_widget:
            w.setMinimumHeight(15)
            w.setMaximumHeight(25)

        for i in range(23):
            self.data_grid.addWidget(self.data_plot_widget[i], i, 4)

        self.data_grid.setColumnMinimumWidth(2, 75)

        self.gl_layout = QVBoxLayout()
        self.gl_layout.addWidget(self.imu_gl)

        self.v_layout = QVBoxLayout()
        self.layout_bottom.addLayout(self.gl_layout)

        self.save_orientation.clicked.connect(self.imu_gl.save_orientation)
        self.checkbox_leds.stateChanged.connect(self.led_clicked)
        self.button_calibration.clicked.connect(self.calibration_clicked)
        self.button_detach_3d_view.clicked.connect(self.detach_3d_view_clicked)
        self.calibration_color = [Qt.red, QColor(0xFF, 0xA0, 0x00), Qt.yellow, Qt.darkGreen]

        self.calibration = None
        self.alive = True
        self.callback_counter = 0

        self.status_led_action = QAction('Status LED', self)
        self.status_led_action.setCheckable(True)
        self.status_led_action.toggled.connect(lambda checked: self.imu.enable_status_led() if checked else self.imu.disable_status_led())
        self.set_configs([(0, None, [self.status_led_action])])

        reset = QAction('Reset', self)
        reset.triggered.connect(self.imu.reset)
        self.set_actions([(0, None, [reset])])

    def restart_gl(self):
        state = self.imu_gl.get_state()
        self.imu_gl.hide()

        self.imu_gl = IMUV2GLWidget()
        self.imu_gl.setFixedSize(200, 200)
        self.gl_layout.addWidget(self.imu_gl)
        self.imu_gl.show()

        self.save_orientation.clicked.connect(self.imu_gl.save_orientation)
        self.imu_gl.set_state(state)

    def start(self):
        if not self.alive:
            return

        self.parent().set_callback_post_untab(lambda x: self.restart_gl())
        self.parent().set_callback_post_tab(lambda x: self.restart_gl())

        async_call(self.imu.is_status_led_enabled, None, self.status_led_action.setChecked, self.increase_error_count)
        async_call(self.imu.are_leds_on, None, self.checkbox_leds.setChecked, self.increase_error_count)

        self.gl_layout.activate()
        self.cbe_all_data.set_period(50)

        for w in self.data_plot_widget:
            w.stop = False

    def stop(self):
        for w in self.data_plot_widget:
            w.stop = True

        if self.imu_gl_wrapper == None:
            self.cbe_all_data.set_period(0)

    def destroy(self):
        self.alive = False

        # Stop callback to fix deadlock with callback emulation thread.
        self.cbe_all_data.set_period(0)
        if self.calibration:
            self.calibration.close()
        if self.imu_gl_wrapper:
            self.imu_gl_wrapper.close()

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickIMUV2.DEVICE_IDENTIFIER

    def calibration_clicked(self):
        if self.calibration is None:
            self.calibration = Calibration(self)

        self.button_calibration.setEnabled(False)
        self.calibration.show()

    def detach_3d_view_clicked(self):
        if self.imu_gl_wrapper != None:
            self.imu_gl_wrapper.close()

        self.button_detach_3d_view.setEnabled(False)

        self.imu_gl_wrapper = WrapperWidget(self)
        self.imu_gl_wrapper.glWidget.set_state(self.imu_gl.get_state())
        self.save_orientation.clicked.connect(self.imu_gl_wrapper.glWidget.save_orientation)

        self.imu_gl_wrapper.show()

    def all_data_callback(self, data):
        self.callback_counter += 1

        if self.callback_counter == 2:
            self.callback_counter = 0

            self.sensor_data[0].value  = data.acceleration[0] / 100.0
            self.sensor_data[1].value  = data.acceleration[1] / 100.0
            self.sensor_data[2].value  = data.acceleration[2] / 100.0
            self.sensor_data[3].value  = data.magnetic_field[0] / 16.0
            self.sensor_data[4].value  = data.magnetic_field[1] / 16.0
            self.sensor_data[5].value  = data.magnetic_field[2] / 16.0
            self.sensor_data[6].value  = data.angular_velocity[0] / 16.0
            self.sensor_data[7].value  = data.angular_velocity[1] / 16.0
            self.sensor_data[8].value  = data.angular_velocity[2] / 16.0
            self.sensor_data[9].value  = data.euler_angle[0] / 16.0
            self.sensor_data[10].value = data.euler_angle[1] / 16.0
            self.sensor_data[11].value = data.euler_angle[2] / 16.0
            self.sensor_data[12].value = data.quaternion[0] / (2 ** 14 - 1)
            self.sensor_data[13].value = data.quaternion[1] / (2 ** 14 - 1)
            self.sensor_data[14].value = data.quaternion[2] / (2 ** 14 - 1)
            self.sensor_data[15].value = data.quaternion[3] / (2 ** 14 - 1)
            self.sensor_data[16].value = data.linear_acceleration[0] / 100.0
            self.sensor_data[17].value = data.linear_acceleration[1] / 100.0
            self.sensor_data[18].value = data.linear_acceleration[2] / 100.0
            self.sensor_data[19].value = data.gravity_vector[0] / 100.0
            self.sensor_data[20].value = data.gravity_vector[1] / 100.0
            self.sensor_data[21].value = data.gravity_vector[2] / 100.0
            self.sensor_data[22].value = data.temperature

            for i in range(23):
                self.data_labels[i].setText("{0:.2f}".format(self.sensor_data[i].value))

            self.imu_gl.update(self.sensor_data[12].value,
                               self.sensor_data[13].value,
                               self.sensor_data[14].value,
                               self.sensor_data[15].value)

            if self.imu_gl_wrapper is not None:
                self.imu_gl_wrapper.glWidget.update(self.sensor_data[12].value,
                                                    self.sensor_data[13].value,
                                                    self.sensor_data[14].value,
                                                    self.sensor_data[15].value)

            cal_mag = data.calibration_status & 3
            cal_acc = (data.calibration_status & (3 << 2)) >> 2
            cal_gyr = (data.calibration_status & (3 << 4)) >> 4
            cal_sys = (data.calibration_status & (3 << 6)) >> 6

            if self.calibration != None:
                self.calibration.save_calibration.setEnabled(data.calibration_status == 0xFF)

                self.calibration.mag_color.set_color(self.calibration_color[cal_mag])
                self.calibration.acc_color.set_color(self.calibration_color[cal_acc])
                self.calibration.gyr_color.set_color(self.calibration_color[cal_gyr])
                self.calibration.sys_color.set_color(self.calibration_color[cal_sys])
        else:
            self.imu_gl.update(data.quaternion[0] / (2 ** 14 - 1),
                               data.quaternion[1] / (2 ** 14 - 1),
                               data.quaternion[2] / (2 ** 14 - 1),
                               data.quaternion[3] / (2 ** 14 - 1))

            if self.imu_gl_wrapper is not None:
                self.imu_gl_wrapper.glWidget.update(data.quaternion[0] / (2 ** 14 - 1),
                                                    data.quaternion[1] / (2 ** 14 - 1),
                                                    data.quaternion[2] / (2 ** 14 - 1),
                                                    data.quaternion[3] / (2 ** 14 - 1))

    def led_clicked(self, state):
        if state == Qt.Checked:
            self.imu.leds_on()
        else:
            self.imu.leds_off()
