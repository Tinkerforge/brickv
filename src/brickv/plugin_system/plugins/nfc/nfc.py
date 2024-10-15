# -*- coding: utf-8 -*-
"""
NFC Plugin
Copyright (C) 2017 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

nfc.py: NFC Plugin Implementation

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

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QTreeWidgetItem
from PyQt5.QtGui import QTextCursor

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.nfc.ui_nfc import Ui_NFC
from brickv.bindings.bricklet_nfc import BrickletNFC
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.spin_box_hex import SpinBoxHex
from brickv.utils import get_main_window
from brickv.bindings.ip_connection import Error as TinkerforgeError

class NFC(COMCUPluginBase, Ui_NFC):
    qtcb_state_changed_cardemu = pyqtSignal(int, bool)
    qtcb_state_changed_p2p = pyqtSignal(int, bool)
    qtcb_state_changed_reader = pyqtSignal(int, bool)

    MIFARE_OPERATION_READ = 1
    MIFARE_OPERATION_WRITE = 2

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletNFC, *args)

        self.setupUi(self)

        self.nfc = self.device

        self.has_simple_mode = None

        self.cbe_simple_tag_id = CallbackEmulator(self,
                                                  self.simple_get_tag_id_wrapper,
                                                  None,
                                                  self.cb_simple_tag_id_wrapper,
                                                  self.increase_error_count)

        self.current_mode = None
        self.current_mifare_operation = None
        self.current_tag_id = {'tag_id_type': None,
                               'tag_id': None}
        self.current_state = {'cardemu': None,
                              'p2p': None,
                              'reader': None}
        self.cardemu_start_discovery_clicked = False

        # This variable determines whether or not to actually ask the the
        # Bricklet to change operating mode.
        self.change_mode = False

        # NOTE: GUI updates from Tinkerforge binding callbacks must be done
        #       by emitting signals (in main GUI thread).
        self.qtcb_state_changed_p2p.connect(self.cb_state_changed_p2p)
        self.qtcb_state_changed_reader.connect(self.cb_state_changed_reader)
        self.qtcb_state_changed_cardemu.connect(self.cb_state_changed_cardemu)

        self.nfc.register_callback(self.nfc.CALLBACK_CARDEMU_STATE_CHANGED,
                                   lambda state, idle: self.qtcb_state_changed_cardemu.emit(state, idle))
        self.nfc.register_callback(self.nfc.CALLBACK_P2P_STATE_CHANGED,
                                   lambda state, idle: self.qtcb_state_changed_p2p.emit(state, idle))
        self.nfc.register_callback(self.nfc.CALLBACK_READER_STATE_CHANGED,
                                   lambda state, idle: self.qtcb_state_changed_reader.emit(state, idle))

        self.key_read_spinbox = []

        for i in range(6):
            sb = SpinBoxHex()
            sb.setRange(0, 255)
            self.key_read_spinbox.append(sb)
            self.widget_read_spinbox.layout().addWidget(sb)

        self.key_write_spinbox = []

        for i in range(16):
            sb = SpinBoxHex()
            sb.setRange(0, 255)
            self.key_write_spinbox.append(sb)
            if i < 4:
                self.layout_write1.addWidget(sb)
            elif i < 8:
                self.layout_write2.addWidget(sb)
            elif i < 12:
                self.layout_write3.addWidget(sb)
            else:
                self.layout_write4.addWidget(sb)

        self.read_page_clicked_first_page = 0
        self.read_page_clicked_page_range = ''
        self.write_page_clicked_first_page = 0
        self.write_page_clicked_data = []

        doc = self.textedit_read_page.document()
        font = doc.defaultFont()
        font.setFamily('Courier New')
        doc.setDefaultFont(font)

        self.button_read_page.clicked.connect(self.read_page_clicked)
        self.button_write_page.clicked.connect(self.write_page_clicked)
        self.combo_box_mode.currentIndexChanged.connect(self.mode_changed)
        self.button_initialize.clicked.connect(self.button_initialize_clicked)
        self.button_reader_scan_tag.clicked.connect(self.reader_scan_tag_clicked)
        self.button_p2p_discover.clicked.connect(self.button_p2p_discover_clicked)
        self.combo_reader_tag_type.currentIndexChanged.connect(self.reader_tag_type_changed)
        self.combo_p2p_operation.currentIndexChanged.connect(self.combo_p2p_operation_changed)
        self.button_cardemu_start_discovery.clicked.connect(lambda: self.button_cardemu_start_discovery_clicked(True))
        self.combo_cardemu_record_type.currentIndexChanged.connect(self.combo_cardemu_record_type_changed)
        self.combo_p2p_write_record_type.currentIndexChanged.connect(self.combo_p2p_write_record_type_changed)

        self.gui_elements_mifare_classic_auth = [self.widget_read_spinbox,
                                                 self.label_read_key,
                                                 self.combobox_read_key]

        self.reader_tag_type_changed(0)
        self.combo_p2p_operation_changed(0)
        self.combo_cardemu_record_type_changed(0)
        self.combo_p2p_write_record_type_changed(0)

        self.tree_simple_tags.header().resizeSection(0, 50)
        self.tree_simple_tags.header().resizeSection(1, 250)
        self.tree_simple_tags.header().resizeSection(2, 250)

    def pack_ndef_record_text(self, text_raw):
        payload_text = []

        for c in list(text_raw):
            payload_text.append(ord(c))

        # Only short records are supported.
        ndef_record_text = [
                                0xD1,                  # MB/ME/CF/SR=1/IL/TNF
                                0x01,                  # TYPE LENGTH
                                len(payload_text) + 3, # Length
                                ord('T'),              # TYPE
                                0x02,                  # Status
                                ord('e'), ord('n')     # Language
                           ]
        for d in payload_text:
            ndef_record_text.append(d)

        return ndef_record_text

    def pack_ndef_record_uri(self, uri_raw, uri_prefix):
        payload_uri = []

        for c in list(uri_raw):
            payload_uri.append(ord(c))

        # Only short records are supported.
        ndef_record_uri = [
                                0xD1,                 # MB/ME/CF/SR=1/IL/TNF
                                0x01,                 # TYPE LENGTH
                                len(payload_uri) + 1, # Length
                                ord('U'),             # Type
                                uri_prefix            # Status
                          ]

        for d in payload_uri:
            ndef_record_uri.append(d)

        return ndef_record_uri

    def update_gui_mode_changed(self, mode):
        if mode == self.nfc.MODE_OFF:
            self.frame_mode_p2p.hide()
            self.frame_mode_reader.hide()
            self.frame_mode_cardemu.hide()
            self.frame_mode_simple.hide()
            self.button_initialize.setEnabled(False)
            self.label_status.setText('NFC turned off')
        elif mode == self.nfc.MODE_CARDEMU:
            self.frame_mode_p2p.hide()
            self.frame_mode_reader.hide()
            self.frame_mode_cardemu.show()
            self.frame_mode_simple.hide()
            self.button_initialize.setEnabled(True)
        elif mode == self.nfc.MODE_P2P:
            self.frame_mode_p2p.show()
            self.frame_mode_reader.hide()
            self.frame_mode_cardemu.hide()
            self.frame_mode_simple.hide()
            self.button_initialize.setEnabled(True)
        elif mode == self.nfc.MODE_READER:
            self.frame_mode_p2p.hide()
            self.frame_mode_reader.show()
            self.frame_mode_cardemu.hide()
            self.frame_mode_simple.hide()
            self.label_reader_id.setText('')
            self.button_initialize.setEnabled(True)
            self.textedit_read_page.setPlainText('')
            self.group_box_reader_read_page.setEnabled(False)
            self.group_box_reader_write_page.setEnabled(False)
            self.combo_reader_tag_type.setCurrentIndex(self.nfc.TAG_TYPE_MIFARE_CLASSIC)
        elif mode == self.nfc.MODE_SIMPLE:
            self.frame_mode_p2p.hide()
            self.frame_mode_reader.hide()
            self.frame_mode_cardemu.hide()
            self.frame_mode_simple.setVisible(self.has_simple_mode)
            self.button_initialize.setEnabled(self.has_simple_mode)

    def mode_changed(self, index):
        self.label_status.setText('-')
        self.current_state['p2p'] = None
        self.current_state['reader'] = None
        self.current_state['cardemu'] = None

        if index == self.nfc.MODE_OFF:
            if self.change_mode:
                self.cbe_simple_tag_id.set_period(0)
                self.nfc.set_mode(self.nfc.MODE_OFF)

            self.current_mode = self.nfc.MODE_OFF
            self.update_gui_mode_changed(self.nfc.MODE_OFF)
        elif index == self.nfc.MODE_CARDEMU:
            if self.change_mode:
                self.cbe_simple_tag_id.set_period(0)
                self.nfc.set_mode(self.nfc.MODE_CARDEMU)

            self.current_mode = self.nfc.MODE_CARDEMU
            self.update_gui_mode_changed(self.nfc.MODE_CARDEMU)
        elif index == self.nfc.MODE_P2P:
            if self.change_mode:
                self.cbe_simple_tag_id.set_period(0)
                self.nfc.set_mode(self.nfc.MODE_P2P)

            self.current_mode = self.nfc.MODE_P2P
            self.update_gui_mode_changed(self.nfc.MODE_P2P)
        elif index == self.nfc.MODE_READER:
            if self.change_mode:
                self.cbe_simple_tag_id.set_period(0)
                self.nfc.set_mode(self.nfc.MODE_READER)

            self.current_mode = self.nfc.MODE_READER
            self.update_gui_mode_changed(self.nfc.MODE_READER)
        elif index == self.nfc.MODE_SIMPLE:
            if self.change_mode and self.has_simple_mode:
                self.nfc.set_mode(self.nfc.MODE_SIMPLE)
                self.cbe_simple_tag_id.set_period(250)

            self.current_mode = self.nfc.MODE_SIMPLE
            self.update_gui_mode_changed(self.nfc.MODE_SIMPLE)

            if self.has_simple_mode:
                self.label_status.setText('Simple: Scanning')
                self.button_initialize.setEnabled(True)
            else:
                self.label_status.setText('Simple: FW >= 2.0.6 required')
                self.button_initialize.setEnabled(False)

        if not self.change_mode:
            status_text = '-'
            mode = self.nfc.get_mode()

            if mode == self.nfc.MODE_OFF:
                self.cbe_simple_tag_id.set_period(0)

                status_text = 'NFC turned off'
            elif mode == self.nfc.MODE_CARDEMU:
                self.cbe_simple_tag_id.set_period(0)
                status_text = 'Card Emulator: '
                state = self.nfc.cardemu_get_state()

                if state.state == self.nfc.CARDEMU_STATE_INITIALIZATION:
                    status_text += 'Initialization'
                elif state.state == self.nfc.CARDEMU_STATE_IDLE:
                    status_text += 'Idle'
                elif state.state == self.nfc.CARDEMU_STATE_ERROR:
                    status_text += 'Error'
                elif state.state == self.nfc.CARDEMU_STATE_DISCOVER:
                    status_text += 'Discover'
                elif state.state == self.nfc.CARDEMU_STATE_DISCOVER_READY:
                    status_text += 'Discover ready'
                elif state.state == self.nfc.CARDEMU_STATE_DISCOVER_ERROR:
                    status_text += 'Discover error'
                elif state.state == self.nfc.CARDEMU_STATE_TRANSFER_NDEF:
                    status_text += 'Transfer NDEF'
                elif state.state == self.nfc.CARDEMU_STATE_TRANSFER_NDEF_READY:
                    status_text += 'Transfer NDEF ready'
                elif state.state == self.nfc.CARDEMU_STATE_TRANSFER_NDEF_ERROR:
                    status_text += 'Transfer NDEF error'
                else:
                    status_text += 'Unknown state'
            elif mode == self.nfc.MODE_P2P:
                self.cbe_simple_tag_id.set_period(0)

                status_text = 'P2P: '

                state = self.nfc.p2p_get_state()

                if state.state == self.nfc.P2P_STATE_INITIALIZATION:
                    status_text += 'Initialization'
                elif state.state == self.nfc.P2P_STATE_IDLE:
                    status_text += 'Idle'
                elif state.state == self.nfc.P2P_STATE_ERROR:
                    status_text += 'Error'
                elif state.state == self.nfc.P2P_STATE_DISCOVER:
                    status_text += 'Discover'
                elif state.state == self.nfc.P2P_STATE_DISCOVER_READY:
                    status_text += 'Discover ready'
                elif state.state == self.nfc.P2P_STATE_DISCOVER_ERROR:
                    status_text += 'Discover error'
                elif state.state == self.nfc.P2P_STATE_TRANSFER_NDEF:
                    status_text += 'Transfer NDEF'
                elif state.state == self.nfc.P2P_STATE_TRANSFER_NDEF_READY:
                    status_text += 'Transfer NDEF ready'
                elif state.state == self.nfc.P2P_STATE_TRANSFER_NDEF_ERROR:
                    status_text += 'Transfer NDEF error'
                else:
                    status_text += 'Unknown state'
            elif mode == self.nfc.MODE_READER:
                self.cbe_simple_tag_id.set_period(0)

                status_text = 'Reader: '
                state = self.nfc.reader_get_state()

                if state.state == self.nfc.READER_STATE_INITIALIZATION:
                    status_text += 'Initialization'
                elif state.state == self.nfc.READER_STATE_IDLE:
                    status_text += 'Idle'
                elif state.state == self.nfc.READER_STATE_ERROR:
                    status_text += 'Error'
                elif state.state == self.nfc.READER_STATE_REQUEST_TAG_ID:
                    status_text += 'Request tag ID'
                elif state.state == self.nfc.READER_STATE_REQUEST_TAG_ID_READY:
                    status_text += 'Request tag ID ready'
                elif state.state == self.nfc.READER_STATE_REQUEST_TAG_ID_ERROR:
                    status_text += 'Request tag ID error'
                elif state.state == self.nfc.READER_STATE_AUTHENTICATE_MIFARE_CLASSIC_PAGE:
                    status_text += 'Authenticate MIFARE classic page'
                elif state.state == self.nfc.READER_STATE_AUTHENTICATE_MIFARE_CLASSIC_PAGE_READY:
                    status_text += 'Authenticate MIFARE classic page ready'
                elif state.state == self.nfc.READER_STATE_AUTHENTICATE_MIFARE_CLASSIC_PAGE_ERROR:
                    status_text += 'Authenticate MIFARE classic page error'
                elif state.state == self.nfc.READER_STATE_WRITE_PAGE:
                    status_text += 'Write page'
                elif state.state == self.nfc.READER_STATE_WRITE_PAGE_READY:
                    status_text += 'Write page ready'
                elif state.state == self.nfc.READER_STATE_WRITE_PAGE_ERROR:
                    status_text += 'Write page error'
                elif state.state == self.nfc.READER_STATE_REQUEST_PAGE:
                    status_text += 'Request page'
                elif state.state == self.nfc.READER_STATE_REQUEST_PAGE_READY:
                    status_text += 'Request page ready'
                elif state.state == self.nfc.READER_STATE_REQUEST_PAGE_ERROR:
                    status_text += 'Request page error'
                elif state.state == self.nfc.READER_STATE_WRITE_NDEF:
                    status_text += 'Write NDEF'
                elif state.state == self.nfc.READER_STATE_WRITE_NDEF_READY:
                    status_text += 'Write NDEF ready'
                elif state.state == self.nfc.READER_STATE_WRITE_NDEF_ERROR:
                    status_text += 'Write NDEF error'
                elif state.state == self.nfc.READER_STATE_REQUEST_NDEF:
                    status_text += 'Request NDEF'
                elif state.state == self.nfc.READER_STATE_REQUEST_NDEF_READY:
                    status_text += 'Request NDEF ready'
                elif state.state == self.nfc.READER_STATE_REQUEST_NDEF_ERROR:
                    status_text += 'Request NDEF error'
                else:
                    status_text += 'Unknown state'
            elif mode == self.nfc.MODE_SIMPLE:
                self.cbe_simple_tag_id.set_period(250)

                status_text = 'Simple: Scanning'

            self.label_status.setText(status_text)

        self.change_mode = True

    def get_current_page_range(self):
        tt = self.combo_reader_tag_type.currentIndex()
        page = self.spinbox_read_page.value()
        page_range = ''

        if tt == self.nfc.TAG_TYPE_MIFARE_CLASSIC or tt == self.nfc.TAG_TYPE_TYPE3:
            page_range = '{0}'.format(page)
        elif tt == self.nfc.TAG_TYPE_TYPE1:
            page_range = '{0}-{1}'.format(page, page+1)
        elif tt == self.nfc.TAG_TYPE_TYPE2:
            page_range = '{0}-{1}'.format(page, page+3)
        elif tt == self.nfc.TAG_TYPE_TYPE5:
            page_range = '{0}-{1}'.format(page, page+3)

        return page_range

    def reader_tag_type_changed(self, index):
        self.label_reader_id.setText('')
        self.textedit_read_page.setPlainText('')

        self.current_tag_id['tag_id'] = None
        self.current_tag_id['tag_id_type'] = None

        if self.change_mode:
            self.nfc.set_mode(self.nfc.MODE_READER)

        self.frame_read.show()
        self.frame_write.show()
        self.frame_tag_type4.show()
        self.frame_write_type4.show()
        self.frame_reader_type4_read_length.show()

        for e in self.key_write_spinbox:
            e.show()

        if index == self.nfc.TAG_TYPE_MIFARE_CLASSIC:
            for e in self.gui_elements_mifare_classic_auth:
                e.show()
        else:
            for e in self.gui_elements_mifare_classic_auth:
                e.hide()

        self.group_box_reader_read_page.setEnabled(False)
        self.group_box_reader_write_page.setEnabled(False)

        for sp in self.key_write_spinbox:
            sp.setValue(0)
            sp.hide()

        self.write_page_label1.hide()
        self.write_page_label2.hide()
        self.write_page_label3.hide()
        self.write_page_label4.hide()

        if index == self.nfc.TAG_TYPE_MIFARE_CLASSIC:
            self.frame_read.show()
            self.frame_write.show()
            self.frame_tag_type4.hide()
            self.frame_write_type4.hide()
            self.write_page_label1.show()
            self.write_page_label2.show()
            self.write_page_label3.show()
            self.write_page_label4.show()
            self.frame_reader_type4_read_length.hide()

            for sp in self.key_write_spinbox:
                sp.show()
        elif index == self.nfc.TAG_TYPE_TYPE1:
            self.frame_read.show()
            self.frame_write.show()
            self.frame_tag_type4.hide()
            self.frame_write_type4.hide()
            self.write_page_label1.show()
            self.write_page_label2.show()
            self.frame_reader_type4_read_length.hide()

            for index, sp in enumerate(self.key_write_spinbox):
                if index > 7:
                    break

                sp.show()
        elif index == self.nfc.TAG_TYPE_TYPE2:
            self.frame_read.show()
            self.frame_write.show()
            self.frame_tag_type4.hide()
            self.frame_write_type4.hide()
            self.write_page_label1.show()
            self.frame_reader_type4_read_length.hide()

            for index, sp in enumerate(self.key_write_spinbox):
                if index > 3:
                    break

                sp.show()
        elif index == self.nfc.TAG_TYPE_TYPE3:
            self.frame_read.show()
            self.frame_write.show()
            self.frame_tag_type4.hide()
            self.frame_write_type4.hide()
            self.write_page_label1.show()
            self.write_page_label2.show()
            self.write_page_label3.show()
            self.write_page_label4.show()
            self.frame_reader_type4_read_length.hide()

            for sp in self.key_write_spinbox:
                sp.show()
        elif index == self.nfc.TAG_TYPE_TYPE4:
            self.frame_read.hide()
            self.frame_write.hide()
            self.frame_tag_type4.show()
            self.frame_write_type4.show()
            self.frame_reader_type4_read_length.show()
        elif index == self.nfc.TAG_TYPE_TYPE5:
            self.frame_read.show()
            self.frame_write.show()
            self.frame_tag_type4.hide()
            self.frame_write_type4.hide()
            self.write_page_label1.show()
            self.frame_reader_type4_read_length.hide()

            for index, sp in enumerate(self.key_write_spinbox):
                if index > 3:
                    break
                sp.show()

    def combo_p2p_operation_changed(self, index):
        if index == 0:
            self.frame_p2p_read.show()
            self.frame_p2p_write.hide()
        elif index == 1:
            self.frame_p2p_read.hide()
            self.frame_p2p_write.show()

    def button_cardemu_start_discovery_clicked(self, message_box_allowed):
        self.cardemu_start_discovery_clicked = True

        if self.combo_cardemu_record_type.currentIndex() == 0:
            text_raw = self.lineedit_cardemu_record_text_data.text()

            if text_raw == '':
                if message_box_allowed:
                    QMessageBox.critical(get_main_window(),
                                         self.base_name + ' | Error',
                                         'Input is empty. Please provide text input.')

                return

            try:
                self.nfc.cardemu_write_ndef(self.pack_ndef_record_text(text_raw))
                self.nfc.cardemu_start_discovery()
            except:
                if message_box_allowed:
                    QMessageBox.critical(get_main_window(),
                                         self.base_name + ' | Error',
                                         'Bricklet not in correct state to start discovery.')

                return
        elif self.combo_cardemu_record_type.currentIndex() == 1:
            uri_raw = self.lineedit_cardemu_record_uri_data.text()

            if uri_raw == '':
                if message_box_allowed:
                    QMessageBox.critical(get_main_window(),
                                         self.base_name + ' | Error',
                                         'Input is empty. Please provide URI.')

                return

            try:
                self.nfc.cardemu_write_ndef(self.pack_ndef_record_uri(uri_raw, self.combo_cardemu_record_uri_prefix.currentIndex()))
                self.nfc.cardemu_start_discovery()
            except:
                if message_box_allowed:
                    QMessageBox.critical(get_main_window(),
                                         self.base_name + ' | Error',
                                         'Bricklet not in correct state to start discovery.')

                return

    def combo_cardemu_record_type_changed(self, index):
        if index == 0:
            self.frame_cardemu_record_uri.hide()
            self.frame_cardemu_record_text.show()
        elif index == 1:
            self.frame_cardemu_record_uri.show()
            self.frame_cardemu_record_text.hide()

    def combo_p2p_write_record_type_changed(self, index):
        if index == 0:
            self.frame_p2p_write_data_uri.hide()
            self.frame_p2p_write_data_text.show()
        elif index == 1:
            self.frame_p2p_write_data_uri.show()
            self.frame_p2p_write_data_text.hide()

    def button_p2p_discover_clicked(self):
        if self.combo_p2p_operation.currentIndex() == 1:
            if self.combo_p2p_write_record_type.currentIndex() == 0:
                text_raw = self.lineedit_p2p_write_data_text.text()

                if text_raw == '':
                    QMessageBox.critical(get_main_window(),
                                         self.base_name + ' | Error',
                                         'Input is empty. Please provide text input.')

                    return

                try:
                    self.nfc.p2p_write_ndef(self.pack_ndef_record_text(text_raw))
                except:
                    QMessageBox.critical(get_main_window(),
                                         self.base_name + ' | Error',
                                         'Bricklet not in correct state to start discovery.')

                    return
            elif self.combo_p2p_write_record_type.currentIndex() == 1:
                uri_raw = self.lineedit_p2p_write_data_uri.text()

                if uri_raw == '':
                    QMessageBox.critical(get_main_window(),
                                         self.base_name + ' | Error',
                                         'Input is empty. Please provide URI.')

                    return

                try:
                    self.nfc.p2p_write_ndef(self.pack_ndef_record_uri(uri_raw, self.combo_p2p_write_uri_prefix.currentIndex()))
                except:
                    QMessageBox.critical(get_main_window(),
                                         self.base_name + ' | Error',
                                         'Bricklet not in correct state to start discovery.')

                    return

        try:
            self.nfc.p2p_start_discovery()
        except:
            QMessageBox.critical(get_main_window(),
                                 self.base_name + ' | Error',
                                 'Bricklet not in correct state to start discovery.')

    def cb_state_changed_cardemu(self, state, idle):
        if self.combo_box_mode.currentIndex() == self.nfc.MODE_CARDEMU:
            self.current_state['cardemu'] = state

        if self.current_mode != self.nfc.MODE_CARDEMU:
            return

        self.button_initialize.setEnabled(True)

        if state == self.nfc.CARDEMU_STATE_INITIALIZATION:
            self.frame_mode_cardemu.setEnabled(False)
            self.label_status.setText('Card Emulator: Initialization')
        elif state == self.nfc.CARDEMU_STATE_IDLE:
            if self.cardemu_start_discovery_clicked:
                self.button_cardemu_start_discovery_clicked(False)
            else:
                self.frame_mode_cardemu.setEnabled(True)

            self.label_status.setText('Card Emulator: Idle')
        elif state == self.nfc.CARDEMU_STATE_ERROR:
            self.frame_mode_cardemu.setEnabled(True)
            self.label_status.setText('Card Emulator: Error')
        elif state == self.nfc.CARDEMU_STATE_DISCOVER:
            self.frame_mode_cardemu.setEnabled(False)
            self.label_status.setText('Card Emulator: Discover')
        elif state == self.nfc.CARDEMU_STATE_DISCOVER_READY:
            self.nfc.cardemu_start_transfer(True)
            self.frame_mode_cardemu.setEnabled(False)
            self.label_status.setText('Card Emulator: Discover ready')
        elif state == self.nfc.CARDEMU_STATE_DISCOVER_ERROR:
            self.frame_mode_cardemu.setEnabled(True)
            self.label_status.setText('Card Emulator: Discover error')
        elif state == self.nfc.CARDEMU_STATE_TRANSFER_NDEF:
            self.frame_mode_cardemu.setEnabled(False)
            self.label_status.setText('Card Emulator: Transfer NDEF')
        elif state == self.nfc.CARDEMU_STATE_TRANSFER_NDEF_READY:
            self.frame_mode_cardemu.setEnabled(False)
            self.label_status.setText('Card Emulator: Transfer NDEF ready')

            if self.combo_box_mode.currentIndex() == self.nfc.MODE_CARDEMU:
                self.nfc.set_mode(self.nfc.MODE_CARDEMU)
        elif state == self.nfc.CARDEMU_STATE_TRANSFER_NDEF_ERROR:
            self.frame_mode_cardemu.setEnabled(True)
            self.label_status.setText('Card Emulator: Transfer NDEF error')
        else:
            self.frame_mode_cardemu.setEnabled(True)
            self.label_status.setText('Card Emulator: Unknown state')

    def cb_state_changed_p2p(self, state, idle):
        self.current_state['p2p'] = state

        if self.current_mode != self.nfc.MODE_P2P:
            return

        self.frame_mode_p2p.setEnabled(True)
        self.textedit_p2p_read.setEnabled(True)
        self.button_initialize.setEnabled(True)
        self.combo_p2p_operation.setEnabled(True)
        self.button_p2p_discover.setEnabled(True)

        if state == self.nfc.P2P_STATE_INITIALIZATION:
            self.frame_mode_p2p.setEnabled(False)
            self.label_status.setText('P2P: Initialization')
        elif state == self.nfc.P2P_STATE_IDLE:
            self.frame_mode_p2p.setEnabled(True)
            self.label_status.setText('P2P: Idle')
        elif state == self.nfc.P2P_STATE_ERROR:
            self.frame_mode_p2p.setEnabled(True)
            self.label_status.setText('P2P: Error')
        elif state == self.nfc.P2P_STATE_DISCOVER:
            if self.combo_p2p_operation.currentIndex() == 0:
                self.frame_mode_p2p.setEnabled(True)
                self.textedit_p2p_read.setEnabled(True)
                self.combo_p2p_operation.setEnabled(False)
                self.button_p2p_discover.setEnabled(False)
            else:
                self.frame_mode_p2p.setEnabled(False)

            self.label_status.setText('P2P: Discover')
        elif state == self.nfc.P2P_STATE_DISCOVER_READY:
            if self.combo_p2p_operation.currentIndex() == 0:
                self.frame_mode_p2p.setEnabled(True)
                self.textedit_p2p_read.setEnabled(True)
                self.combo_p2p_operation.setEnabled(False)
                self.button_p2p_discover.setEnabled(False)
            else:
                self.frame_mode_p2p.setEnabled(False)

            self.label_status.setText('P2P: Discover ready')

            if self.combo_p2p_operation.currentIndex() == 0:
                self.nfc.p2p_start_transfer(self.nfc.P2P_TRANSFER_READ)
            elif self.combo_p2p_operation.currentIndex() == 1:
                self.nfc.p2p_start_transfer(self.nfc.P2P_TRANSFER_WRITE)
        elif state == self.nfc.P2P_STATE_DISCOVER_ERROR:
            self.frame_mode_p2p.setEnabled(True)
            self.label_status.setText('P2P: Discover error')
        elif state == self.nfc.P2P_STATE_TRANSFER_NDEF:
            if self.combo_p2p_operation.currentIndex() == 0:
                self.frame_mode_p2p.setEnabled(True)
                self.textedit_p2p_read.setEnabled(True)
                self.combo_p2p_operation.setEnabled(False)
                self.button_p2p_discover.setEnabled(False)
            else:
                self.frame_mode_p2p.setEnabled(False)

            self.label_status.setText('P2P: Transfer NDEF')
        elif state == self.nfc.P2P_STATE_TRANSFER_NDEF_READY:
            self.frame_mode_p2p.setEnabled(True)
            self.label_status.setText('P2P: Transfer NDEF ready')

            if self.combo_box_mode.currentIndex() == self.nfc.MODE_P2P and \
               self.combo_p2p_operation.currentIndex() == 0:
                t = self.textedit_p2p_read.toPlainText()

                if t == '':
                    t = repr(map(chr, self.nfc.p2p_read_ndef()))
                else:
                    t += '\n\n' + repr(map(chr, self.nfc.p2p_read_ndef()))

                self.textedit_p2p_read.setText(t)
                self.textedit_p2p_read.moveCursor(QTextCursor.End)

            self.nfc.p2p_start_discovery()
        elif state == self.nfc.P2P_STATE_TRANSFER_NDEF_ERROR:
            if self.combo_p2p_operation.currentIndex() == 0:
                self.frame_mode_p2p.setEnabled(True)
                self.textedit_p2p_read.setEnabled(True)
                self.combo_p2p_operation.setEnabled(False)
                self.button_p2p_discover.setEnabled(False)
            else:
                self.frame_mode_p2p.setEnabled(False)

            self.label_status.setText('P2P: Transfer NDEF error. Try again')
            self.nfc.p2p_start_discovery()
        else:
            self.frame_mode_p2p.setEnabled(True)
            self.label_state.setText('P2P: Unknown state')

    def tag_id_as_byte_string(self, tag_id):
        tag_bytes_format = ' '.join("{{{}:02X}}".format(i) for i in range(0, len(tag_id)))

        return tag_bytes_format.format(*tag_id)

    def cb_state_changed_reader(self, state, idle):

        self.current_state['reader'] = state

        if self.current_mode != self.nfc.MODE_READER:
            return

        self.button_initialize.setEnabled(True)

        if state == self.nfc.READER_STATE_INITIALIZATION:
            self.frame_mode_reader.setEnabled(False)
            self.label_status.setText('Reader: Initializing')
        elif state == self.nfc.READER_STATE_IDLE:
            self.frame_mode_reader.setEnabled(True)
            self.label_status.setText('Reader: Idle')
        elif state == self.nfc.READER_STATE_ERROR:
            self.frame_mode_reader.setEnabled(True)
            self.label_status.setText('Reader: Error')
        elif state == self.nfc.READER_STATE_REQUEST_TAG_ID:
            self.label_reader_id.setText('')
            self.frame_mode_reader.setEnabled(False)
            self.label_status.setText('Reader: Request tag ID')
        elif state == self.nfc.READER_STATE_REQUEST_TAG_ID_READY:
            tag = ''
            self.current_tag_id['tag_id'] = None
            self.current_tag_id['tag_id_type'] = None

            self.frame_mode_reader.setEnabled(True)
            self.label_status.setText('Reader: Request tag ID ready')

            (tag_id_type, tag_id) = self.nfc.reader_get_tag_id()

            self.group_box_reader_read_page.setEnabled(False)
            self.group_box_reader_write_page.setEnabled(False)

            if tag_id_type > self.nfc.TAG_TYPE_TYPE5:
                tag = 'Found tag with unsupported ID'
            else:
                if self.combo_reader_tag_type.currentIndex() == tag_id_type:
                    self.current_tag_id['tag_id'] = tag_id
                    self.current_tag_id['tag_id_type'] = tag_id_type
                    tag_type_name = self.combo_reader_tag_type.currentText().replace("NFC Forum ", "")
                    tag = 'Found {} tag with ID <font color="green"><b>{}</b></font>'.format(tag_type_name, self.tag_id_as_byte_string(tag_id))
                    self.group_box_reader_read_page.setEnabled(True)
                    self.group_box_reader_write_page.setEnabled(True)
                else:
                    self.group_box_reader_read_page.setEnabled(False)
                    self.group_box_reader_write_page.setEnabled(False)

            self.label_reader_id.setText(tag)
        elif state == self.nfc.READER_STATE_REQUEST_TAG_ID_ERROR:
            self.frame_mode_reader.setEnabled(True)
            self.label_status.setText('Reader: Request tag ID error')
        elif state == self.nfc.READER_STATE_AUTHENTICATE_MIFARE_CLASSIC_PAGE:
            self.frame_mode_reader.setEnabled(False)
            self.label_status.setText('Reader: Authenticate MIFARE classic page')
        elif state == self.nfc.READER_STATE_AUTHENTICATE_MIFARE_CLASSIC_PAGE_READY:
            self.frame_mode_reader.setEnabled(True)
            self.label_status.setText('Reader: Authenticate MIFARE classic page ready')

            if self.current_mifare_operation == self.MIFARE_OPERATION_READ:
                self.nfc.reader_request_page(self.spinbox_read_page.value(), 16)

            if self.current_mifare_operation == self.MIFARE_OPERATION_WRITE:
                self.nfc.reader_write_page(self.spinbox_read_page.value(),
                                           self.write_page_clicked_data)
        elif state == self.nfc.READER_STATE_AUTHENTICATE_MIFARE_CLASSIC_PAGE_ERROR:
            self.frame_mode_reader.setEnabled(True)
            self.label_status.setText('Reader: Authenticate MIFARE classic page error')
        elif state == self.nfc.READER_STATE_WRITE_PAGE:
            self.frame_mode_reader.setEnabled(False)
            self.label_status.setText('Reader: Write page')
        elif state == self.nfc.READER_STATE_WRITE_PAGE_READY:
            self.frame_mode_reader.setEnabled(True)
            self.label_status.setText('Reader: Write page ready')

            if self.current_mode == self.nfc.MODE_READER and \
               self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE4:
                self.nfc.reader_request_tag_id()
        elif state == self.nfc.READER_STATE_WRITE_PAGE_ERROR:
            self.frame_mode_reader.setEnabled(True)
            self.label_status.setText('Reader: Write page error')
        elif state == self.nfc.READER_STATE_REQUEST_PAGE:
            self.frame_mode_reader.setEnabled(False)
            self.label_status.setText('Reader: Request page')
        elif state == self.nfc.READER_STATE_REQUEST_PAGE_READY:
            s = ''
            page = self.nfc.reader_read_page()
            page_index = self.spinbox_read_page.value()

            self.frame_mode_reader.setEnabled(True)
            self.label_status.setText('Reader: Request page ready')
            self.spinbox_write_page.setValue(self.spinbox_read_page.value())

            if self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_MIFARE_CLASSIC:
                s = '''<b>Page {page_index}:</b>
{byte_0}
{byte_1}
{byte_2}
{byte_3}
{byte_4}
{byte_5}
{byte_6}
{byte_7}
{byte_8}
{byte_9}
{byte_10}
{byte_11}
{byte_12}
{byte_13}
{byte_14}
{byte_15}'''.format(page_index=page_index,
                    byte_0=hex(page[0]),
                    byte_1=hex(page[1]),
                    byte_2=hex(page[2]),
                    byte_3=hex(page[3]),
                    byte_4=hex(page[4]),
                    byte_5=hex(page[5]),
                    byte_6=hex(page[6]),
                    byte_7=hex(page[7]),
                    byte_8=hex(page[8]),
                    byte_9=hex(page[9]),
                    byte_10=hex(page[10]),
                    byte_11=hex(page[11]),
                    byte_12=hex(page[12]),
                    byte_13=hex(page[13]),
                    byte_14=hex(page[14]),
                    byte_15=hex(page[15]))

                for index, sp in enumerate(self.key_write_spinbox):
                    sp.setValue(page[index])
            elif self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE1:
                s = '''<b>Page {page_index}:</b>
{byte_0}
{byte_1}
{byte_2}
{byte_3}
{byte_4}
{byte_5}
{byte_6}
{byte_7}'''.format(page_index=page_index,
                   byte_0=hex(page[0]),
                   byte_1=hex(page[1]),
                   byte_2=hex(page[2]),
                   byte_3=hex(page[3]),
                   byte_4=hex(page[4]),
                   byte_5=hex(page[5]),
                   byte_6=hex(page[6]),
                   byte_7=hex(page[7]))

                for index, sp in enumerate(self.key_write_spinbox):
                    if index > 7:
                        break

                    sp.setValue(page[index])
            elif self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE2:
                s = '''<b>Page {page_index}:</b>
{byte_0}
{byte_1}
{byte_2}
{byte_3}'''.format(page_index=page_index,
                   byte_0=hex(page[0]),
                   byte_1=hex(page[1]),
                   byte_2=hex(page[2]),
                   byte_3=hex(page[3]))

                for index, sp in enumerate(self.key_write_spinbox):
                    if index > 3:
                        break

                    sp.setValue(page[index])
            elif self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE3:
                s = '''<b>Page {page_index}:</b>
{byte_0}
{byte_1}
{byte_2}
{byte_3}
{byte_4}
{byte_5}
{byte_6}
{byte_7}
{byte_8}
{byte_9}
{byte_10}
{byte_11}
{byte_12}
{byte_13}
{byte_14}
{byte_15}'''.format(page_index=page_index,
                    byte_0=hex(page[0]),
                    byte_1=hex(page[1]),
                    byte_2=hex(page[2]),
                    byte_3=hex(page[3]),
                    byte_4=hex(page[4]),
                    byte_5=hex(page[5]),
                    byte_6=hex(page[6]),
                    byte_7=hex(page[7]),
                    byte_8=hex(page[8]),
                    byte_9=hex(page[9]),
                    byte_10=hex(page[10]),
                    byte_11=hex(page[11]),
                    byte_12=hex(page[12]),
                    byte_13=hex(page[13]),
                    byte_14=hex(page[14]),
                    byte_15=hex(page[15]))

                for index, sp in enumerate(self.key_write_spinbox):
                    sp.setValue(page[index])
            elif self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE4:
                v = []

                for i, b in enumerate(page):
                    v.append(hex(page[i]))

                s = ', '.join(v)

                if self.current_mode == self.nfc.MODE_READER:
                    self.nfc.reader_request_tag_id()
            elif self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE5:
                s = '''<b>Page {page_index}:</b>
{byte_0}
{byte_1}
{byte_2}
{byte_3}'''.format(page_index=page_index,
                   byte_0=hex(page[0]),
                   byte_1=hex(page[1]),
                   byte_2=hex(page[2]),
                   byte_3=hex(page[3]))

                for index, sp in enumerate(self.key_write_spinbox):
                    if index > 3:
                        break

                    sp.setValue(page[index])

            self.textedit_read_page.setText(s)
        elif state == self.nfc.READER_STATE_REQUEST_PAGE_ERROR:
            self.frame_mode_reader.setEnabled(True)
            self.label_status.setText('Reader: Request page error')
        elif state == self.nfc.READER_STATE_WRITE_NDEF:
            self.frame_mode_reader.setEnabled(False)
            self.label_status.setText('Reader: Write NDEF')
        elif state == self.nfc.READER_STATE_WRITE_NDEF_READY:
            self.frame_mode_reader.setEnabled(True)
            self.label_status.setText('Reader: Write NDEF ready')
        elif state == self.nfc.READER_STATE_WRITE_NDEF_ERROR:
            self.frame_mode_reader.setEnabled(True)
            self.label_status.setText('Reader: Write NDEF error')
        elif state == self.nfc.READER_STATE_REQUEST_NDEF:
            self.frame_mode_reader.setEnabled(False)
            self.label_status.setText('Reader: Request NDEF')
        elif state == self.nfc.READER_STATE_REQUEST_NDEF_READY:
            self.frame_mode_reader.setEnabled(True)
            self.label_status.setText('Reader: Request NDEF ready')
        elif state == self.nfc.READER_STATE_REQUEST_NDEF_ERROR:
            self.frame_mode_reader.setEnabled(True)
            self.label_status.setText('Reader: Request NDEF error')
        else:
            self.label_status.setText('Reader: Unknown state')
            self.frame_mode_reader.setEnabled(True)

    def reader_scan_tag_clicked(self):
        if self.current_mode == self.nfc.MODE_READER:
            self.nfc.reader_request_tag_id()

    def button_initialize_clicked(self):
        if self.combo_box_mode.currentIndex() == self.nfc.MODE_CARDEMU:
            self.change_mode = True
            self.cardemu_start_discovery_clicked = False
            self.button_initialize.setEnabled(False)
            self.mode_changed(self.nfc.MODE_CARDEMU)
        elif self.combo_box_mode.currentIndex() == self.nfc.MODE_P2P:
            self.change_mode = True
            self.button_initialize.setEnabled(False)
            self.mode_changed(self.nfc.MODE_P2P)
        elif self.combo_box_mode.currentIndex() == self.nfc.MODE_READER:
            self.change_mode = True
            self.button_initialize.setEnabled(False)
            self.mode_changed(self.nfc.MODE_READER)
        elif self.combo_box_mode.currentIndex() == self.nfc.MODE_SIMPLE:
            self.change_mode = True
            self.button_initialize.setEnabled(False)

            if self.has_simple_mode:
                self.mode_changed(self.nfc.MODE_SIMPLE)

                # clear tag history
                async_call(self.nfc.simple_get_tag_id, 255, None, self.increase_error_count)

    def read_page_clicked(self):
        page = self.spinbox_read_page.value()
        self.read_page_clicked_first_page = page
        self.read_page_clicked_page_range = self.get_current_page_range()

        if self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_MIFARE_CLASSIC:
            key = []
            key_number = self.combobox_read_key.currentIndex()

            for sb in self.key_read_spinbox:
                key.append(sb.value())

            self.current_mifare_operation = self.MIFARE_OPERATION_READ
            self.nfc.reader_authenticate_mifare_classic_page(page, key_number, key)
        else:
            if self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE1:
                self.nfc.reader_request_page(page, 8)
            elif self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE2:
                self.nfc.reader_request_page(page, 4)
            elif self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE3:
                self.nfc.reader_request_page(page, 16)
            elif self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE4:
                if self.combo_reader_type4_type.currentIndex() == 0:
                    self.nfc.reader_request_page(self.nfc.READER_REQUEST_TYPE4_CAPABILITY_CONTAINER,
                                                 self.spinbox_reader_type4_length.value())
                elif self.combo_reader_type4_type.currentIndex() == 1:
                    self.nfc.reader_request_page(self.nfc.READER_REQUEST_TYPE4_NDEF,
                                                 self.spinbox_reader_type4_length.value())
            elif self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE5:
                self.nfc.reader_request_page(page, 4)

    def write_page_clicked(self):
        del self.write_page_clicked_data[:]
        page = self.spinbox_read_page.value()

        if self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_MIFARE_CLASSIC:
            for sp in self.key_write_spinbox:
                self.write_page_clicked_data.append(sp.value())

            key = []
            key_number = self.combobox_read_key.currentIndex()

            for sb in self.key_read_spinbox:
                key.append(sb.value())

            self.current_mifare_operation = self.MIFARE_OPERATION_WRITE
            self.nfc.reader_authenticate_mifare_classic_page(page, key_number, key)
        elif self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE1:
            for index, sp in enumerate(self.key_write_spinbox):
                if index > 7:
                    break

                self.write_page_clicked_data.append(sp.value())

            self.nfc.reader_write_page(page, self.write_page_clicked_data)
        elif self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE2:
            for index, sp in enumerate(self.key_write_spinbox):
                if index > 3:
                    break

                self.write_page_clicked_data.append(sp.value())

            self.nfc.reader_write_page(page, self.write_page_clicked_data)
        elif self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE3:
            for sp in self.key_write_spinbox:
                self.write_page_clicked_data.append(sp.value())

            self.nfc.reader_write_page(page, self.write_page_clicked_data)
        elif self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE4:
            if self.textedit_reader_type4_write_values.toPlainText() == '':
                QMessageBox.critical(get_main_window(),
                                     self.base_name + ' | Error',
                                     'Input is empty. Please provide a comma seperated list of hexadecimal numbers.')

                return

            values_raw = self.textedit_reader_type4_write_values.toPlainText().split(',')

            for v in values_raw:
                try:
                    self.write_page_clicked_data.append(int(v.strip(), 16))
                except:
                    QMessageBox.critical(get_main_window(),
                                         self.base_name + ' | Error',
                                         'Invalid input. Please verify that the input is a comma seperated list of hexadecimal numbers.')

                    return

            if self.combo_reader_type4_type.currentIndex() == 0:
                self.nfc.reader_write_page(self.nfc.READER_REQUEST_TYPE4_CAPABILITY_CONTAINER,
                                           self.write_page_clicked_data)
            elif self.combo_reader_type4_type.currentIndex() == 1:
                self.nfc.reader_write_page(self.nfc.READER_REQUEST_TYPE4_NDEF,
                                           self.write_page_clicked_data)
        elif self.combo_reader_tag_type.currentIndex() == self.nfc.TAG_TYPE_TYPE5:
            for index, sp in enumerate(self.key_write_spinbox):
                if index > 3:
                    break

                self.write_page_clicked_data.append(sp.value())
            self.nfc.reader_write_page(page, self.write_page_clicked_data)

    def simple_get_tag_id_wrapper(self):
        if not self.has_simple_mode:
            return []

        tags = []

        for i in range(8):
            try:
                tag = self.nfc.simple_get_tag_id(i)
            except TinkerforgeError:
                tag = None

            tags.append(tag)

        return tags

    def cb_simple_tag_id_wrapper(self, tags):
        root = self.tree_simple_tags.invisibleRootItem()
        selected_i = None

        for i in range(root.childCount()):
            if root.child(i).isSelected():
                selected_i = i

        self.tree_simple_tags.clear()

        for i, tag in enumerate(tags):
            if tag == None:
                strings = ['-'] * 4
            elif len(tag.tag_id) == 0:
                break
            else:
                tag_type = self.combo_reader_tag_type.itemText(tag.tag_type)

                strings = [str(i + 1), tag_type, self.tag_id_as_byte_string(tag.tag_id), str(tag.last_seen // 1000)]

            item = QTreeWidgetItem(root, strings)

            if i == selected_i:
                item.setSelected(True)

    def get_mode_async(self, mode):
        if mode == self.nfc.MODE_OFF:
            self.change_mode = True

            if self.has_simple_mode:
                mode = self.nfc.MODE_SIMPLE
            else:
                mode = self.nfc.MODE_READER

            self.combo_box_mode.setCurrentIndex(mode)
        elif mode == self.nfc.MODE_CARDEMU:
            self.change_mode = False
            self.combo_box_mode.setCurrentIndex(self.nfc.MODE_CARDEMU)
        elif mode == self.nfc.MODE_P2P:
            self.change_mode = False
            self.combo_box_mode.setCurrentIndex(self.nfc.MODE_P2P)
        elif mode == self.nfc.MODE_READER:
            self.change_mode = False
            self.combo_box_mode.setCurrentIndex(self.nfc.MODE_READER)
        elif mode == self.nfc.MODE_SIMPLE:
            self.change_mode = False
            self.combo_box_mode.setCurrentIndex(self.nfc.MODE_SIMPLE)

    def start(self):
        # the firmware version might change between init and start of a Co-MCU
        # Bricklet plugin, because a Co-MCU Bricklet can be restarted without
        # recreating the plugin. therefore, the firmware version has to be checked
        # on every start
        self.has_simple_mode = self.firmware_version >= (2, 0, 6)

        self.combo_box_mode.setCurrentIndex(-1)
        async_call(self.nfc.get_mode, None, self.get_mode_async, self.increase_error_count)

    def stop(self):
        self.cbe_simple_tag_id.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletNFC.DEVICE_IDENTIFIER
