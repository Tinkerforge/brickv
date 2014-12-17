# -*- coding: utf-8 -*-
"""
Master Plugin
Copyright (C) 2010-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012-2014 Matthias Bolte <matthias@tinkerforge.com>

wifi.py: Wifi for Master Plugin implementation

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

from PyQt4.QtGui import QWidget, QMessageBox, QFileDialog, QProgressDialog, QLineEdit
from PyQt4.QtCore import Qt

import os
import time
import sys

from brickv.plugin_system.plugins.master.ui_wifi import Ui_Wifi

from brickv.plugin_system.plugins.master.wifi_status import WifiStatus
from brickv.async_call import async_call

class Wifi(QWidget, Ui_Wifi):
    def __init__(self, parent):
        QWidget.__init__(self)

        self.setupUi(self)

        self.parent = parent
        self.master = parent.master

        self.update_data_counter = 0
        self.connection = 0

        self.wifi_key.setEchoMode(QLineEdit.Password)
        self.wifi_key_show.stateChanged.connect(self.wifi_key_show_state_changed)

        self.wifi_password.setEchoMode(QLineEdit.Password)
        self.wifi_password_show.stateChanged.connect(self.wifi_password_show_state_changed)

        if parent.firmware_version >= (1, 3, 0):
            if parent.firmware_version < (1, 3, 3):
                # AP and Ad Hoc was added in 1.3.3
                while self.wifi_connection.count() > 2:
                    self.wifi_connection.removeItem(self.wifi_connection.count() - 1)

            async_call(self.master.get_wifi_configuration, None, self.get_wifi_configuration_async, self.parent.increase_error_count)
            async_call(self.master.get_wifi_certificate, 0xFFFF, self.update_username_async, self.parent.increase_error_count)
            async_call(self.master.get_wifi_certificate, 0xFFFE, self.update_password_async, self.parent.increase_error_count)
            async_call(self.master.get_wifi_power_mode, None, self.wifi_power_mode.setCurrentIndex, self.parent.increase_error_count)

            if parent.firmware_version >= (1, 3, 4):
                async_call(self.master.get_wifi_regulatory_domain, None, self.wifi_domain.setCurrentIndex, self.parent.increase_error_count)
            else:
                self.wifi_domain.setEnabled(False)
                self.wifi_domain.clear()
                self.wifi_domain.addItem("FW Version >= 1.3.4 required")

            async_call(self.master.get_wifi_encryption, None, self.get_wifi_encryption_async, self.parent.increase_error_count)

            if parent.firmware_version < (2, 0, 5):
                self.wifi_hostname.setDisabled(True)
                self.wifi_hostname.setMaxLength(50)
                self.wifi_hostname.setText("FW Version >= 2.0.5 required")
                self.wifi_hostname_label.setDisabled(True)
            else:
                async_call(self.master.get_wifi_hostname, None, self.get_wifi_hostname_async, self.parent.increase_error_count)

        if parent.firmware_version >= (2, 2, 0):
            self.wifi_use_auth.stateChanged.connect(self.wifi_auth_changed)
            self.wifi_show_characters.stateChanged.connect(self.wifi_show_characters_changed)

            self.wifi_show_characters.hide()
            self.wifi_secret_label.hide()
            self.wifi_secret.hide()

            async_call(self.master.get_wifi_authentication_secret, None, self.get_wifi_authentication_secret_async, self.parent.increase_error_count)
        else:
            self.wifi_use_auth.setText("Use Authentication (FW Version >= 2.2.0 required)")
            self.wifi_use_auth.setDisabled(True)
            self.wifi_show_characters.hide()
            self.wifi_secret_label.hide()
            self.wifi_secret.hide()

        self.wifi_status = None

    def destroy(self):
        if self.wifi_status:
            self.wifi_status.close()

    def get_wifi_authentication_secret_async(self, secret):
        self.wifi_secret.setText(secret)
        if secret == '':
            self.wifi_show_characters.hide()
            self.wifi_secret_label.hide()
            self.wifi_secret.hide()
            self.wifi_use_auth.setChecked(Qt.Unchecked)
        else:
            self.wifi_show_characters.show()
            self.wifi_secret_label.show()
            self.wifi_secret.show()
            self.wifi_use_auth.setChecked(Qt.Checked)
            if self.wifi_show_characters.isChecked():
                self.wifi_secret.setEchoMode(QLineEdit.Normal)
            else:
                self.wifi_secret.setEchoMode(QLineEdit.Password)

    def wifi_auth_changed(self, state):
        if state == Qt.Checked:
            self.wifi_show_characters.show()
            self.wifi_secret_label.show()
            self.wifi_secret.show()
            if self.wifi_show_characters.isChecked():
                self.wifi_secret.setEchoMode(QLineEdit.Normal)
            else:
                self.wifi_secret.setEchoMode(QLineEdit.Password)
        else:
            self.wifi_show_characters.hide()
            self.wifi_secret_label.hide()
            self.wifi_secret.hide()
            self.wifi_secret.setText('')

    def wifi_show_characters_changed(self, state):
        if state == Qt.Checked:
            self.wifi_secret.setEchoMode(QLineEdit.Normal)
        else:
            self.wifi_secret.setEchoMode(QLineEdit.Password)

    def update_username_async(self, username):
        username = ''.join(map(chr, username[0][:username[1]]))
        self.wifi_username.setText(username)

    def update_password_async(self, password):
        password = ''.join(map(chr, password[0][:password[1]]))
        self.wifi_password.setText(password)

    def get_wifi_hostname_async(self, hostname):
        self.wifi_hostname.setText(hostname)

    def get_long_wifi_key_async(self, key):
        self.wifi_key.setText(key)

    def get_wifi_encryption_async(self, enc):
        encryption, key, key_index, eap_options, ca_certificate_length, client_certificate_length, private_key_length = enc

        if self.connection in (2, 3, 4, 5):
            encryption -= 2

        eap_outer = eap_options & 0b00000011
        eap_inner = (eap_options & 0b00000100) >> 2
        key = key.replace('\0', '')

        self.wifi_eap_outer_auth.setCurrentIndex(eap_outer)
        self.wifi_eap_inner_auth.setCurrentIndex(eap_inner)
        self.wifi_encryption.setCurrentIndex(encryption)

        if key == '-' and self.parent.firmware_version >= (2, 0, 2):
            async_call(self.master.get_long_wifi_key, None, self.get_long_wifi_key_async, self.parent.increase_error_count)
        else:
            self.wifi_key.setText(key)

        self.wifi_key_index.setValue(key_index)

        self.wifi_connection.currentIndexChanged.connect(self.connection_changed)
        self.wifi_encryption.currentIndexChanged.connect(self.encryption_changed)
        self.wifi_save.clicked.connect(self.save_clicked)
        self.wifi_show_status.clicked.connect(self.show_status_clicked)
        self.wifi_ca_certificate_browse.clicked.connect(self.ca_certificate_browse_clicked)
        self.wifi_client_certificate_browse.clicked.connect(self.client_certificate_browse_clicked)
        self.wifi_private_key_browse.clicked.connect(self.private_key_browse_clicked)

        self.connection_changed(0)
        self.encryption_changed(0)
        self.wifi_encryption.setCurrentIndex(encryption) # ensure that the correct encryption is displayed

    def get_wifi_configuration_async(self, configuration):
        ssid, connection, ip, sub, gw, port = configuration

        ssid = ssid.replace('\0', '')
        self.connection = connection

        self.wifi_ssid.setText(ssid)
        self.wifi_connection.setCurrentIndex(connection)
        self.wifi_ip1.setValue(ip[0])
        self.wifi_ip2.setValue(ip[1])
        self.wifi_ip3.setValue(ip[2])
        self.wifi_ip4.setValue(ip[3])
        self.wifi_sub1.setValue(sub[0])
        self.wifi_sub2.setValue(sub[1])
        self.wifi_sub3.setValue(sub[2])
        self.wifi_sub4.setValue(sub[3])
        self.wifi_gw1.setValue(gw[0])
        self.wifi_gw2.setValue(gw[1])
        self.wifi_gw3.setValue(gw[2])
        self.wifi_gw4.setValue(gw[3])
        self.wifi_port.setValue(port)

    def wifi_key_show_state_changed(self, state):
        if state == Qt.Checked:
            self.wifi_key.setEchoMode(QLineEdit.Normal)
        else:
            self.wifi_key.setEchoMode(QLineEdit.Password)

    def wifi_password_show_state_changed(self, state):
        if state == Qt.Checked:
            self.wifi_password.setEchoMode(QLineEdit.Normal)
        else:
            self.wifi_password.setEchoMode(QLineEdit.Password)

    def ca_certificate_browse_clicked(self):
        last_dir = ''
        if len(self.wifi_ca_certificate_url.text()) > 0:
            last_dir = os.path.dirname(os.path.realpath(unicode(self.wifi_ca_certificate_url.text().toUtf8(), 'utf-8')))

        file_name = QFileDialog.getOpenFileName(self,
                                                'Open CA Certificate',
                                                last_dir)
        if len(file_name) > 0:
            self.wifi_ca_certificate_url.setText(file_name)

    def client_certificate_browse_clicked(self):
        last_dir = ''
        if len(self.wifi_client_certificate_url.text()) > 0:
            last_dir = os.path.dirname(os.path.realpath(unicode(self.wifi_client_certificate_url.text().toUtf8(), 'utf-8')))

        file_name = QFileDialog.getOpenFileName(self,
                                                'Open Client Certificate',
                                                last_dir)
        if len(file_name) > 0:
            self.wifi_client_certificate_url.setText(file_name)

    def private_key_browse_clicked(self):
        last_dir = ''
        if len(self.wifi_private_key_url.text()) > 0:
            last_dir = os.path.dirname(os.path.realpath(unicode(self.wifi_private_key_url.text().toUtf8(), 'utf-8')))

        file_name = QFileDialog.getOpenFileName(self,
                                                'Open Private Key',
                                                last_dir)
        if len(file_name) > 0:
            self.wifi_private_key_url.setText(file_name)

    def encryption_changed(self, index):
        if str(self.wifi_encryption.currentText()) in 'WPA/WPA2':
            if self.parent.firmware_version >= (2, 0, 2):
                self.wifi_key.setMaxLength(63)
            else:
                self.wifi_key.setMaxLength(50)

            self.wifi_key.setVisible(True)
            self.wifi_key_label.setVisible(True)
            self.wifi_key_show.setVisible(True)

            self.wifi_key_index.setVisible(False)
            self.wifi_key_index_label.setVisible(False)

            self.wifi_eap_inner_auth.setVisible(False)
            self.wifi_eap_inner_auth_label.setVisible(False)

            self.wifi_eap_outer_auth.setVisible(False)
            self.wifi_eap_outer_auth_label.setVisible(False)

            self.wifi_username.setVisible(False)
            self.wifi_username_label.setVisible(False)

            self.wifi_password.setVisible(False)
            self.wifi_password_label.setVisible(False)
            self.wifi_password_show.setVisible(False)

            self.wifi_ca_certificate_url.setVisible(False)
            self.wifi_ca_certificate_browse.setVisible(False)
            self.wifi_ca_certificate_label.setVisible(False)
            self.wifi_client_certificate_url.setVisible(False)
            self.wifi_client_certificate_browse.setVisible(False)
            self.wifi_client_certificate_label.setVisible(False)
            self.wifi_private_key_url.setVisible(False)
            self.wifi_private_key_browse.setVisible(False)
            self.wifi_private_key_label.setVisible(False)
        elif str(self.wifi_encryption.currentText()) in 'WPA Enterprise':
            self.wifi_key.setVisible(False)
            self.wifi_key_label.setVisible(False)
            self.wifi_key_show.setVisible(False)

            self.wifi_key_index.setVisible(False)
            self.wifi_key_index_label.setVisible(False)

            self.wifi_eap_inner_auth.setVisible(True)
            self.wifi_eap_inner_auth_label.setVisible(True)

            self.wifi_eap_outer_auth.setVisible(True)
            self.wifi_eap_outer_auth_label.setVisible(True)

            self.wifi_username.setVisible(True)
            self.wifi_username_label.setVisible(True)

            self.wifi_password.setVisible(True)
            self.wifi_password_label.setVisible(True)
            self.wifi_password_show.setVisible(True)

            self.wifi_ca_certificate_url.setVisible(True)
            self.wifi_ca_certificate_browse.setVisible(True)
            self.wifi_ca_certificate_label.setVisible(True)
            self.wifi_client_certificate_url.setVisible(True)
            self.wifi_client_certificate_browse.setVisible(True)
            self.wifi_client_certificate_label.setVisible(True)
            self.wifi_private_key_url.setVisible(True)
            self.wifi_private_key_browse.setVisible(True)
            self.wifi_private_key_label.setVisible(True)
        elif str(self.wifi_encryption.currentText()) in 'WEP':
            self.wifi_key.setMaxLength(26)
            self.wifi_key.setVisible(True)
            self.wifi_key_label.setVisible(True)
            self.wifi_key_show.setVisible(True)

            self.wifi_key_index.setVisible(True)
            self.wifi_key_index_label.setVisible(True)

            self.wifi_eap_inner_auth.setVisible(False)
            self.wifi_eap_inner_auth_label.setVisible(False)

            self.wifi_eap_outer_auth.setVisible(False)
            self.wifi_eap_outer_auth_label.setVisible(False)

            self.wifi_username.setVisible(False)
            self.wifi_username_label.setVisible(False)

            self.wifi_password.setVisible(False)
            self.wifi_password_label.setVisible(False)
            self.wifi_password_show.setVisible(False)

            self.wifi_ca_certificate_url.setVisible(False)
            self.wifi_ca_certificate_browse.setVisible(False)
            self.wifi_ca_certificate_label.setVisible(False)
            self.wifi_client_certificate_url.setVisible(False)
            self.wifi_client_certificate_browse.setVisible(False)
            self.wifi_client_certificate_label.setVisible(False)
            self.wifi_private_key_url.setVisible(False)
            self.wifi_private_key_browse.setVisible(False)
            self.wifi_private_key_label.setVisible(False)
        else:
            self.wifi_key.setVisible(False)
            self.wifi_key_label.setVisible(False)
            self.wifi_key_show.setVisible(False)

            self.wifi_key_index.setVisible(False)
            self.wifi_key_index_label.setVisible(False)

            self.wifi_eap_inner_auth.setVisible(False)
            self.wifi_eap_inner_auth_label.setVisible(False)

            self.wifi_eap_outer_auth.setVisible(False)
            self.wifi_eap_outer_auth_label.setVisible(False)

            self.wifi_username.setVisible(False)
            self.wifi_username_label.setVisible(False)

            self.wifi_password.setVisible(False)
            self.wifi_password_label.setVisible(False)
            self.wifi_password_show.setVisible(False)

            self.wifi_ca_certificate_url.setVisible(False)
            self.wifi_ca_certificate_browse.setVisible(False)
            self.wifi_ca_certificate_label.setVisible(False)
            self.wifi_client_certificate_url.setVisible(False)
            self.wifi_client_certificate_browse.setVisible(False)
            self.wifi_client_certificate_label.setVisible(False)
            self.wifi_private_key_url.setVisible(False)
            self.wifi_private_key_browse.setVisible(False)
            self.wifi_private_key_label.setVisible(False)

    def connection_changed(self, index):
        if self.wifi_connection.currentIndex() in (0, 2, 4):
            self.wifi_ip1.setVisible(False)
            self.wifi_ip2.setVisible(False)
            self.wifi_ip3.setVisible(False)
            self.wifi_ip4.setVisible(False)
            self.wifi_sub1.setVisible(False)
            self.wifi_sub2.setVisible(False)
            self.wifi_sub3.setVisible(False)
            self.wifi_sub4.setVisible(False)
            self.wifi_gw1.setVisible(False)
            self.wifi_gw2.setVisible(False)
            self.wifi_gw3.setVisible(False)
            self.wifi_gw4.setVisible(False)

            self.wifi_port.setVisible(True)
            self.wifi_port_label.setVisible(True)

            self.wifi_ip_label.setVisible(False)
            self.wifi_gw_label.setVisible(False)
            self.wifi_sub_label.setVisible(False)

            self.wifi_dot1.setVisible(False)
            self.wifi_dot2.setVisible(False)
            self.wifi_dot3.setVisible(False)
            self.wifi_dot4.setVisible(False)
            self.wifi_dot5.setVisible(False)
            self.wifi_dot6.setVisible(False)
            self.wifi_dot7.setVisible(False)
            self.wifi_dot8.setVisible(False)
            self.wifi_dot9.setVisible(False)
        else:
            self.wifi_ip1.setVisible(True)
            self.wifi_ip2.setVisible(True)
            self.wifi_ip3.setVisible(True)
            self.wifi_ip4.setVisible(True)
            self.wifi_sub1.setVisible(True)
            self.wifi_sub2.setVisible(True)
            self.wifi_sub3.setVisible(True)
            self.wifi_sub4.setVisible(True)
            self.wifi_gw1.setVisible(True)
            self.wifi_gw2.setVisible(True)
            self.wifi_gw3.setVisible(True)
            self.wifi_gw4.setVisible(True)

            self.wifi_port.setVisible(True)
            self.wifi_port_label.setVisible(True)

            self.wifi_ip_label.setVisible(True)
            self.wifi_gw_label.setVisible(True)
            self.wifi_sub_label.setVisible(True)

            self.wifi_dot1.setVisible(True)
            self.wifi_dot2.setVisible(True)
            self.wifi_dot3.setVisible(True)
            self.wifi_dot4.setVisible(True)
            self.wifi_dot5.setVisible(True)
            self.wifi_dot6.setVisible(True)
            self.wifi_dot7.setVisible(True)
            self.wifi_dot8.setVisible(True)
            self.wifi_dot9.setVisible(True)

        current = str(self.wifi_encryption.currentText())

        if self.wifi_connection.currentIndex() in (2, 3, 4, 5):
            self.wifi_encryption.clear()
            self.wifi_encryption.addItem('WEP')
            self.wifi_encryption.addItem('No Encryption')
        else:
            self.wifi_encryption.clear()
            self.wifi_encryption.addItem('WPA/WPA2')
            self.wifi_encryption.addItem('WPA Enterprise')
            self.wifi_encryption.addItem('WEP')
            self.wifi_encryption.addItem('No Encryption')

        index = self.wifi_encryption.findText(current)
        if index >= 0:
            self.wifi_encryption.setCurrentIndex(index)

    def popup_ok(self, message='Successfully saved configuration.\nNew configuration will be used after reset of the Master Brick.'):
        QMessageBox.information(self, 'Configuration', message, QMessageBox.Ok)

    def popup_fail(self, message='Could not save configuration.'):
        QMessageBox.critical(self, 'Configuration', message, QMessageBox.Ok)

    def show_status_clicked(self):
        if self.wifi_status is None:
            self.wifi_status = WifiStatus(self)

        self.wifi_status.show()

    def create_progress_bar(self, title):
        progress = QProgressDialog(self)
        progress.setAutoClose(False)
        progress.setWindowTitle(title)
        progress.setCancelButton(None)
        progress.setWindowModality(Qt.WindowModal)

        return progress

    def get_certificate(self, url_edit):
        cert_path = url_edit.text()
        cert_path = unicode(cert_path.toUtf8(), 'utf-8').encode(sys.getfilesystemencoding())
        try:
            if os.path.isfile(cert_path):
                certificate_file = map(ord, file(cert_path, 'rb').read()) # Convert certificate to list of bytes
                certificate_length = len(certificate_file)
                if certificate_length > 6*1024:
                    QMessageBox.critical(self, "Save", "Certificate too big (max size: 6kB).", QMessageBox.Ok)
                    return []

                return certificate_file
        except:
            return []

        return []

    def write_certificate(self, certificate, typ):
        try:
            chunks = []
            progress = self.create_progress_bar("Configuration")
            progress.setLabelText('Saving Certificate...')
            progress.setMaximum(1000)
            progress.setValue(0)
            progress.update()
            progress.show()

            position = 0
            length_certificate = len(certificate)
            while len(certificate) > 0:
                cert_chunk = certificate[:32]
                certificate = certificate[32:]
                length = len(cert_chunk)
                mod = length % 32
                if mod != 0:
                    cert_chunk += [0] * (32 - mod)

                time.sleep(0.01)
                self.master.set_wifi_certificate(10000*typ + position,
                                                 cert_chunk,
                                                 length)
                chunks.append(cert_chunk)

                position += 1
                progress.setValue(1000*position/(length_certificate/32))

            progress.setLabelText('Verifying Certificate...')
            progress.setValue(0)

            time.sleep(0.1)

            chunk_length = len(chunks)
            for i in range(chunk_length):
                old_chunk = list(self.master.get_wifi_certificate(10000*typ + i)[0])
                if old_chunk != chunks[i]:
                    progress.cancel()
                    return False
                progress.setValue(1000*i/chunk_length)

            progress.cancel()
        except:
            progress.cancel()
            return False

        return True

    def save_clicked(self):
        encryption = self.wifi_encryption.currentIndex()

        try:
            secret = str(self.wifi_secret.text()).encode('ascii')
        except:
            self.popup_fail('Secret cannot contain non-ASCII characters')
            return

        try:
            hostname = str(self.wifi_hostname.text()).encode('ascii')
        except:
            self.popup_fail('Hostname cannot contain non-ASCII characters')
            return

        try:
            key = str(self.wifi_key.text()).encode('ascii')
        except:
            self.popup_fail('Key cannot contain non-ASCII characters')
            return

        if '"' in key:
            self.popup_fail('Key cannot contain quotation mark')
            return

        if str(self.wifi_encryption.currentText()) in 'WEP':
            if len(key) == 0:
                self.popup_fail('WEP key cannot be empty')
                return

            try:
                int(key, 16)
            except:
                self.popup_fail('WEP key has to be in hexadecimal notation')
                return

            if len(key) != 10 and len(key) != 26:
                self.popup_fail('WEP key has to be either 10 or 26 hexadecimal digits long')
                return

        long_key = key
        if str(self.wifi_encryption.currentText()) in 'WPA/WPA2':
            if len(key) < 8:
                self.popup_fail('WPA/WPA2 key has to be at least 8 chars long')
                return

            if self.parent.firmware_version >= (2, 0, 2) and len(key) > 50:
                key = '-'

        key_index = self.wifi_key_index.value()
        eap_outer = self.wifi_eap_outer_auth.currentIndex()
        eap_inner = self.wifi_eap_inner_auth.currentIndex()

        eap_options = eap_outer | (eap_inner << 2)

        try:
            ssid = str(self.wifi_ssid.text()).encode('ascii')
        except:
            self.popup_fail('SSID cannot contain non-ASCII characters')
            return
        if len(ssid) == 0:
            self.popup_fail('SSID cannot be empty')
            return
        if '"' in ssid:
            self.popup_fail('SSID cannot contain quotation mark')
            return

        connection = self.wifi_connection.currentIndex()

        if connection in (2, 3, 4, 5):
            encryption += 2

        ip = (self.wifi_ip1.value(), self.wifi_ip2.value(),
              self.wifi_ip3.value(), self.wifi_ip4.value())
        sub = (self.wifi_sub1.value(), self.wifi_sub2.value(),
               self.wifi_sub3.value(), self.wifi_sub4.value())
        gw = (self.wifi_gw1.value(), self.wifi_gw2.value(),
              self.wifi_gw3.value(), self.wifi_gw4.value())
        port = self.wifi_port.value()

        power_mode = self.wifi_power_mode.currentIndex()
        ca_cert = self.get_certificate(self.wifi_ca_certificate_url)
        ca_certificate_length = len(ca_cert)
        client_cert = self.get_certificate(self.wifi_client_certificate_url)
        client_certificate_length = len(client_cert)
        priv_key = self.get_certificate(self.wifi_private_key_url)
        private_key_length = len(priv_key)

        previous_power_mode = self.master.get_wifi_power_mode()
        self.master.set_wifi_power_mode(power_mode)
        self.master.set_wifi_encryption(encryption, key, key_index, eap_options, ca_certificate_length, client_certificate_length, private_key_length)
        self.master.set_wifi_configuration(ssid, connection, ip, sub, gw, port)
        if self.parent.firmware_version >= (2, 0, 2):
            self.master.set_long_wifi_key(long_key)
        if self.parent.firmware_version >= (2, 0, 5):
            self.master.set_wifi_hostname(hostname)
        if self.parent.firmware_version >= (2, 2, 0):
            self.master.set_wifi_authentication_secret(secret)

        power_mode_old = self.master.get_wifi_power_mode()
        encryption_old, key_old, key_index_old, eap_options_old, ca_certificate_length_old, client_certificate_length_old, private_key_length_old = self.master.get_wifi_encryption()
        ssid_old, connection_old, ip_old, sub_old, gw_old, port_old = self.master.get_wifi_configuration()
        long_key_old = long_key
        if self.parent.firmware_version >= (2, 0, 2):
            long_key_old = self.master.get_long_wifi_key()
        hostname_old = hostname
        if self.parent.firmware_version >= (2, 0, 5):
            hostname_old = self.master.get_wifi_hostname()
        secret_old = secret
        if self.parent.firmware_version >= (2, 2, 0):
            secret_old = self.master.get_wifi_authentication_secret()

        test_ok = False

        if power_mode == power_mode_old and \
           encryption == encryption_old and key == key_old and \
           ssid == ssid_old and connection == connection_old and \
           ip == ip_old and sub == sub_old and gw == gw_old and \
           port == port_old and key_index == key_index_old and \
           eap_options == eap_options_old and \
           ca_certificate_length == ca_certificate_length_old and \
           client_certificate_length == client_certificate_length_old and \
           private_key_length == private_key_length_old and \
           long_key == long_key_old and \
           hostname == hostname_old and \
           secret == secret_old:
            test_ok = True

        if test_ok and encryption == 1:
            test_ok = False
            username = str(self.wifi_username.text())
            password = str(self.wifi_password.text())
            self.master.set_wifi_certificate(0xFFFF, map(ord, username) + [0] * (32 - len(username)), len(username))
            self.master.set_wifi_certificate(0xFFFE, map(ord, password) + [0] * (32 - len(password)), len(password))
            username_old = self.master.get_wifi_certificate(0xFFFF)
            username_old = ''.join(map(chr, username_old[0][:username_old[1]]))
            password_old = self.master.get_wifi_certificate(0xFFFE)
            password_old = ''.join(map(chr, password_old[0][:password_old[1]]))

            if username_old == username and password_old == password:
                test_ok = True

        if self.parent.firmware_version >= (1, 3, 4) and test_ok:
            self.master.set_wifi_regulatory_domain(self.wifi_domain.currentIndex())
            if self.master.get_wifi_regulatory_domain() != self.wifi_domain.currentIndex():
                test_ok = False

        if test_ok:
            if len(ca_cert) > 0:
                test_ok = self.write_certificate(ca_cert, 0)
        if test_ok:
            if len(client_cert) > 0:
                test_ok = self.write_certificate(client_cert, 1)
        if test_ok:
            if len(priv_key) > 0:
                test_ok = self.write_certificate(priv_key, 2)

        if test_ok:
            if previous_power_mode != power_mode and power_mode == 1:
                self.popup_ok('Successfully saved configuration.\nPower Mode is not changed permanently, it will automatically switch back to Full Speed on reset.')
            else:
                self.popup_ok()
        else:
            self.popup_fail()

    def update_data(self):
        self.update_data_counter += 1
        if self.wifi_status is not None:
            if self.wifi_status.isVisible():
                if self.update_data_counter % 100 == 0:
                    self.master.refresh_wifi_status()
                elif self.update_data_counter % 100 == 50:
                    self.wifi_status.update_status()
