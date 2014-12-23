# -*- coding: utf-8 -*-  
"""
NFC/RFID Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

nfc_rfid.py: NFC/RFID Plugin Implementation

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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.async_call import async_call

from PyQt4.QtGui import QSpinBox, QRegExpValidator
from PyQt4.QtCore import pyqtSignal, Qt, QRegExp
        
from brickv.bindings.bricklet_nfc_rfid import BrickletNFCRFID

from brickv.plugin_system.plugins.nfc_rfid.ui_nfc_rfid import Ui_NFCRFID

class SpinBoxHex(QSpinBox):
    def __init__(self, parent=None, default_value=255):
        super(SpinBoxHex, self).__init__(parent)
        self.validator = QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,2}"), self)
        self.setRange(0, 255)
        self.setValue(default_value)

    def fixCase(self, text):
        self.lineEdit().setText(text.toUpper())

    def validate(self, text, pos):
        return self.validator.validate(text, pos)

    def valueFromText(self, text):
        return text.toInt(16)[0]

    def textFromValue(self, value):
        s = hex(value).replace('0x', '').upper()
        if len(s) == 1:
            s = '0' + s

        return s

class NFCRFID(PluginBase, Ui_NFCRFID):
    qtcb_state = pyqtSignal(int, bool)
    
    def __init__ (self, *args):
        PluginBase.__init__(self, 'NFC/RFID Bricklet', BrickletNFCRFID, *args)
        
        self.setupUi(self)
        
        self.nfc = self.device
        
        self.qtcb_state.connect(self.cb_state)
        self.nfc.register_callback(self.nfc.CALLBACK_STATE_CHANGED,
                                   self.qtcb_state.emit)
        
        self.label_id.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        self.write_page_was_clicked = False
        
        self.key_read_spinbox = []
        for i in range(6):
            sb = SpinBoxHex()
            self.key_read_spinbox.append(sb)
            self.widget_read_spinbox.layout().addWidget(sb)
            
        self.key_write_spinbox = []
        for i in range(16):
            sb = SpinBoxHex(default_value=0)
            self.key_write_spinbox.append(sb)
            if i < 4:
                self.layout_write1.addWidget(sb)
            elif i < 8:
                self.layout_write2.addWidget(sb)
            elif i < 12:
                self.layout_write3.addWidget(sb)
            else:
                self.layout_write4.addWidget(sb)
        
        self.scan_clicked_type = -1
        self.read_page_clicked_first_page = 0
        self.read_page_clicked_page_range = ''
        self.write_page_clicked_first_page = 0
        self.write_page_clicked_page_range = ''
        self.write_page_clicked_data = []
        
        doc = self.textedit_read_page.document()
        font = doc.defaultFont()
        font.setFamily('Courier New')
        doc.setDefaultFont(font)
        
        self.button_scan.clicked.connect(self.scan_clicked)
        self.button_read_page.clicked.connect(self.read_page_clicked)
        self.button_write_page.clicked.connect(self.write_page_clicked)
        self.combo_box_tag_type.currentIndexChanged.connect(self.tag_type_changed)
        self.spinbox_read_page.valueChanged.connect(self.page_changed)
        
        self.index0_show = [self.widget_read_spinbox, self.label_read_key, self.combobox_read_key]
        self.index1_hide = [self.widget_read_spinbox, self.label_read_key, self.combobox_read_key]
        self.index2_hide = [self.widget_read_spinbox, self.label_read_key, self.combobox_read_key]
        
        self.disable = [self.widget_read_spinbox, self.label_read_key, self.combobox_read_key, self.label_read_page, self.spinbox_read_page, self.button_read_page, self.button_write_page]
        
        self.tag_type_changed(0)
        
    def get_current_page_range(self):
        tt = self.combo_box_tag_type.currentIndex()
        page = self.spinbox_read_page.value()
        page_range = ''

        if tt == self.nfc.TAG_TYPE_MIFARE_CLASSIC:
            page_range = '{0}'.format(page)
        elif tt == self.nfc.TAG_TYPE_TYPE1:
            page_range = '{0}-{1}'.format(page, page+1)
        elif tt == self.nfc.TAG_TYPE_TYPE2:
            page_range = '{0}-{1}'.format(page, page+3)

        return page_range

    def tag_type_changed(self, index):
        s  = ''
        self.label_id.setText(s)
        self.textedit_read_page.setPlainText(s)
        
        if index == self.nfc.TAG_TYPE_MIFARE_CLASSIC:
            for show in self.index0_show:
                show.show()
        elif index in (self.nfc.TAG_TYPE_TYPE1, self.nfc.TAG_TYPE_TYPE2):
            for hide in self.index1_hide:
                hide.hide()
                
        for sp in self.key_write_spinbox:
            sp.setEnabled(False) 
            
        for disable in self.disable:
            disable.setEnabled(False)
            
        self.page_changed(self.spinbox_read_page.value())
        
    def page_changed(self, page):
        text_read = 'Read Page ' + self.get_current_page_range()
        text_write = 'Write Page ' + self.get_current_page_range()

        self.button_read_page.setText(text_read)
        self.button_write_page.setText(text_write)
        
    def scan_clicked(self):
        t = self.combo_box_tag_type.currentIndex()
        self.scan_clicked_type = t
        self.nfc.request_tag_id(t)
        
    def read_page_clicked(self):
        page = self.spinbox_read_page.value()
        self.read_page_clicked_first_page = page
        self.read_page_clicked_page_range = self.get_current_page_range()
        if self.scan_clicked_type == self.nfc.TAG_TYPE_MIFARE_CLASSIC:
            key_number = self.combobox_read_key.currentIndex()
            key = []
            for sb in self.key_read_spinbox:
                key.append(sb.value())
                
            self.nfc.authenticate_mifare_classic_page(page, key_number, key)
        else:
            self.nfc.request_page(page)
        
    def write_page_clicked(self):
        self.write_page_was_clicked = True
        page = self.spinbox_read_page.value()
        self.write_page_clicked_first_page = page
        self.write_page_clicked_page_range = self.get_current_page_range()
        self.write_page_clicked_data = []

        for sp in self.key_write_spinbox:
            self.write_page_clicked_data.append(sp.value())
            
        if self.scan_clicked_type == self.nfc.TAG_TYPE_MIFARE_CLASSIC:
            key_number = self.combobox_read_key.currentIndex()
            key = []
            for sb in self.key_read_spinbox:
                key.append(sb.value())
                
            self.nfc.authenticate_mifare_classic_page(page, key_number, key)
        else:
            self.nfc.write_page(page, self.write_page_clicked_data)
        
    def start(self):
        pass
        
    def stop(self):
        pass
    
    def cb_state(self, state, idle):
        if state & (self.nfc.STATE_ERROR & ~self.nfc.STATE_IDLE):
            self.tag_type_changed(self.combo_box_tag_type.currentIndex())
            if (state & 0xF) == self.nfc.STATE_REQUEST_TAG_ID:
                s = 'Could not find {0} tag'.format(self.combo_box_tag_type.currentText())
                self.label_id.setText(s)
            elif (state & 0xF) == self.nfc.STATE_AUTHENTICATING_MIFARE_CLASSIC_PAGE:
                s = 'Error: Could not authenticate page {0}'.format(self.read_page_clicked_page_range)
                self.textedit_read_page.setPlainText(s)
            elif (state & 0xF) == self.nfc.STATE_WRITE_PAGE:
                self.write_page_was_clicked = False
                s = 'Error: Could not write page {0}'.format(self.write_page_clicked_page_range)
                self.textedit_read_page.setPlainText(s)
            elif (state & 0xF) == self.nfc.STATE_REQUEST_PAGE:
                s = 'Error: Could not read page {0}'.format(self.read_page_clicked_page_range)
                self.textedit_read_page.setPlainText(s)
        elif state & self.nfc.STATE_IDLE:
            if (state & 0xF) == self.nfc.STATE_REQUEST_TAG_ID:
                async_call(self.nfc.get_tag_id, None, self.cb_get_tag_id, self.increase_error_count)
            elif (state & 0xF) == self.nfc.STATE_AUTHENTICATING_MIFARE_CLASSIC_PAGE:
                if self.write_page_was_clicked:
                    self.write_page_was_clicked = False
                    self.nfc.write_page(self.write_page_clicked_first_page, self.write_page_clicked_data)
                else:
                    self.nfc.request_page(self.read_page_clicked_first_page)
            elif (state & 0xF) == self.nfc.STATE_REQUEST_PAGE:
                async_call(self.nfc.get_page, None, self.cb_get_page, self.increase_error_count)
            elif (state & 0xF) == self.nfc.STATE_WRITE_PAGE:
                self.write_page_was_clicked = False
                s = 'Successfully wrote page {0}'.format(self.write_page_clicked_page_range)
                self.textedit_read_page.setPlainText(s)

    def cb_get_page(self, page):
        if self.scan_clicked_type == self.nfc.TAG_TYPE_TYPE2:
            s  = 'Page {0}: '.format(self.read_page_clicked_first_page)
            s += '{0:02X} {1:02X} {2:02X} {3:02X}\n'.format(*page[0:4])
            s += 'Page {0}: '.format(self.read_page_clicked_first_page+1)
            s += '{0:02X} {1:02X} {2:02X} {3:02X}\n'.format(*page[4:8])
            s += 'Page {0}: '.format(self.read_page_clicked_first_page+2)
            s += '{0:02X} {1:02X} {2:02X} {3:02X}\n'.format(*page[8:12])
            s += 'Page {0}: '.format(self.read_page_clicked_first_page+3)
            s += '{0:02X} {1:02X} {2:02X} {3:02X}'.format(*page[12:16])
        elif self.scan_clicked_type == self.nfc.TAG_TYPE_TYPE1:
            s  = 'Page {0}: '.format(self.read_page_clicked_first_page)
            s += '{0:02X} {1:02X} {2:02X} {3:02X} {4:02X} {5:02X} {6:02X} {7:02X}\n'.format(*page[0:8])
            s += 'Page {0}: '.format(self.read_page_clicked_first_page+1)
            s += '{0:02X} {1:02X} {2:02X} {3:02X} {4:02X} {5:02X} {6:02X} {7:02X}'.format(*page[8:16])
        elif self.scan_clicked_type == self.nfc.TAG_TYPE_MIFARE_CLASSIC:
            s  = 'Page {0}: '.format(self.read_page_clicked_first_page)
            s += '{0:02X} {1:02X} {2:02X} {3:02X} {4:02X} {5:02X} {6:02X} {7:02X} {8:02X} {9:02X} {10:02X} {11:02X} {12:02X} {13:02X} {14:02X} {15:02X}'.format(*page[0:16])
        else:
            return

        self.textedit_read_page.setPlainText(s)
        
        for i, sp in enumerate(self.key_write_spinbox):
            sp.setValue(page[i])

    def cb_get_tag_id(self, ret):
        if self.scan_clicked_type != ret.tag_type:
            return

        if ret.tid_length == 4:
            s = 'Found tag with ID <b>{0:02X} {1:02X} {2:02X} {3:02X}</b>'.format(*ret.tid)
        elif ret.tid_length == 7:
            s = 'Found tag with ID <b>{0:02X} {1:02X} {2:02X} {3:02X} {4:02X} {5:02X} {6:02X}</b>'.format(*ret.tid)
        else:
            s = 'Found tag with unsupported ID length ({0})'.format(ret.tid_length)
        
        self.label_id.setText(s)
        
        for sp in self.key_write_spinbox:
            sp.setEnabled(True) 
        
        for disable in self.disable:
            disable.setEnabled(True)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletNFCRFID.DEVICE_IDENTIFIER

    def get_url_part(self):
        return 'nfc_rfid'
