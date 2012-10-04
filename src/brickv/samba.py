# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012 Matthias Bolte <matthias@tinkerforge.com>

samba.py: Atmel SAM-BA flash protocol implementation

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

import os
import sys
import errno
import glob
import struct
import math
from PyQt4.QtGui import QApplication
from serial import Serial, SerialException

if sys.platform == 'linux2':
    def get_serial_ports():
        ports = []
        for tty in glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*'):
            ports.append((tty, tty, tty))
        return ports
elif sys.platform == 'darwin':
    def get_serial_ports():
        ports = []
        for tty in glob.glob('/dev/tty.*'):
            ports.append((tty, tty, tty))
        return ports
elif sys.platform == 'win32':
    import win32com.client
    def get_serial_ports():
        wmi = win32com.client.GetObject('winmgmts:')
        ports = []
        for port in wmi.InstancesOf('Win32_SerialPort'):
            ports.append((port.DeviceID, port.Name, ''))
        return ports
else:
    def get_serial_ports():
        return []

CHIPID_CIDR = 0x400e0740

ATSAM3SxB = 0x89
ATSAM3SxC = 0x8A

EEFC_FMR = 0x400E0A00
EEFC_FCR = 0x400E0A04
EEFC_FSR = 0x400E0A08
EEFC_FRR = 0x400E0A0C

EEFC_FSR_FRDY   = 0b0001
EEFC_FSR_FCMDE  = 0b0010
EEFC_FSR_FLOCKE = 0b0100

EEFC_FCR_FKEY = 0x5A

EEFC_FCR_FCMD_WP   = 0x01 # Write Page
EEFC_FCR_FCMD_EA   = 0x05 # Erase All
EEFC_FCR_FCMD_SLB  = 0x08 # Set Lock Bit
EEFC_FCR_FCMD_CLB  = 0x09 # Clear Lock Bit
EEFC_FCR_FCMD_GLB  = 0x0A # Get Lock Bit
EEFC_FCR_FCMD_SGPB = 0x0B # Set GPNVM Bit
EEFC_FCR_FCMD_CGPB = 0x0C # Clear GPNVM Bit
EEFC_FCR_FCMD_GGPB = 0x0D # Get GPNVM Bit

RSTC_CR = 0x400E1400

class SAMBAException(Exception):
    pass

class SAMBA:
    def __init__(self, port_name):
        try:
            self.port = Serial(port_name, 115200, timeout=5)
        except SerialException, e:
            if '[Errno 13]' in str(e):
                raise SAMBAException("No permission to open serial port")
            else:
                raise e

        self.port.write('N#')

        if self.port.read(2) != '\n\r':
            raise SAMBAException('No Brick in Bootloader found')

        chipid = self.readUInt(CHIPID_CIDR)
        arch = (chipid >> 20) & 0b11111111

        if arch == ATSAM3SxB:
            self.flash_base = 0x400000
            self.flash_size = 0x20000
            self.flash_page_count = 512
            self.flash_page_size = 256
            self.flash_lockbit_count = 8
        elif arch == ATSAM3SxC:
            self.flash_base = 0x400000
            self.flash_size = 0x40000
            self.flash_page_count = 1024
            self.flash_page_size = 256
            self.flash_lockbit_count = 16
        else:
            raise SAMBAException('Brick with unknown SAM3S architecture: 0x%X' % arch)

    def flash(self, firmware, progress):
        # Split firmware into pages
        firmware_pages = []
        offset = 0

        while offset < len(firmware):
            page = firmware[offset:offset + self.flash_page_size]

            if len(page) < self.flash_page_size:
                page += '\xff' * (self.flash_page_size - len(page))

            firmware_pages.append(page)
            offset += self.flash_page_size

        # Flash Programming Erata: FWS must be 6
        self.writeUInt(EEFC_FMR, 0x06 << 8)

        # Unlock
        for region in range(self.flash_lockbit_count):
            self.waitForFlashReady()
            page_num = (region * self.flash_page_count) / self.flash_lockbit_count
            self.writeFlashCommand(EEFC_FCR_FCMD_CLB, page_num)

        # Erase All
        self.waitForFlashReady()
        self.writeFlashCommand(EEFC_FCR_FCMD_EA, 0)
        self.waitForFlashReady()

        # Write
        progress.setLabelText('Writing firmware')
        progress.setMaximum(len(firmware_pages))
        progress.setValue(0)
        progress.show()

        page_num = 0

        for page in firmware_pages:
            offset = 0

            while offset < len(page):
                addr = self.flash_base + page_num * self.flash_page_size + offset
                self.writeWord(addr, page[offset:offset + 4])
                offset += 4

            self.waitForFlashReady()
            self.writeFlashCommand(EEFC_FCR_FCMD_WP, page_num)
            self.waitForFlashReady()

            page_num += 1
            progress.setValue(page_num)
            QApplication.processEvents()

        # Lock
        for region in range(int(math.ceil((float(len(firmware_pages)) / self.flash_page_count) * self.flash_lockbit_count))):
            self.waitForFlashReady()
            page_num = (region * self.flash_page_count) / self.flash_lockbit_count
            self.writeFlashCommand(EEFC_FCR_FCMD_SLB, page_num)

        self.waitForFlashReady()

        # Set Boot-from-Flash bit
        self.waitForFlashReady()
        self.writeFlashCommand(EEFC_FCR_FCMD_SGPB, 1)
        self.waitForFlashReady()

        # Verify
        progress.setLabelText('Verifying written firmware')
        progress.setMaximum(len(firmware_pages))
        progress.setValue(0)
        progress.show()

        offset = 0
        page_num = 0

        for page in firmware_pages:
            read_page = ''
            while len(read_page) < self.flash_page_size:
                read_page += self.readWord(self.flash_base + offset)
                offset += 4

            if read_page != page:
                raise SAMBAException('Verification error')

            page_num += 1
            progress.setValue(page_num)
            QApplication.processEvents()

        # Boot
        self.reset()

    def readWord(self, address):
        try:
            self.port.write('w%08X,4#' % address)
            return self.port.read(4)
        except:
            raise SAMBAException('Read error')

    def writeWord(self, address, value):
        self.writeUInt(address, struct.unpack('<I', value)[0])

    def readUInt(self, address):
        return struct.unpack('<I', self.readWord(address))[0]

    def writeUInt(self, address, value):
        try:
            self.port.write('W%08X,%08X#' % (address, value))
        except:
            raise SAMBAException('Write error')

    def reset(self):
        try:
            self.writeUInt(RSTC_CR + 0x08, 1 << 0 | 1 << 4 | 10 << 8 | 0xA5 << 24)
            self.writeUInt(RSTC_CR, 1 << 0 | 1 << 2 | 0xA5 << 24)
        except:
            raise SAMBAException('Reset error')

    def go(self, address):
        try:
            self.port.write('G%08X#' % address)
        except:
            raise SAMBAException('Execution error')

    def waitForFlashReady(self):
        for i in range(1000):
            fsr = self.readUInt(EEFC_FSR)

            if (fsr & EEFC_FSR_FLOCKE) != 0:
                raise SAMBAException('Flash locking error')

            if (fsr & EEFC_FSR_FCMDE) != 0:
                raise SAMBAException('Flash command error')

            if (fsr & EEFC_FSR_FRDY) != 0:
                break
        else:
            raise SAMBAException('Flash timeout')

    def writeFlashCommand(self, command, argument):
        self.writeUInt(EEFC_FCR, (EEFC_FCR_FKEY << 24) | (argument << 8) | command)
