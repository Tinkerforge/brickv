# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012-2016 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

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

import sys
import glob
import struct
import time
import serial
import serial.tools.list_ports
import collections

from brickv.bindings.ip_connection import base58encode

SerialPort = collections.namedtuple('SerialPort', 'path description opaque')

def get_serial_ports(vid=None, pid=None, opaque=None):
    ports = []

    for info in serial.tools.list_ports.comports():
        if info.vid == None or info.pid == None:
            continue # ignore non-USB based serial ports

        if vid != None and info.vid != vid:
            continue # no VID match

        if pid != None and info.pid != pid:
            continue # no PID match

        path = info.device
        description = info.device
        if info.serial_number == None:
            serial_number = ''
        else:
            serial_number = info.serial_number.lower() # ignore case, because Windows reports the serial number as all uppercase

        if info.vid == 0x10c4 and info.pid == 0xea60 and serial_number.startswith('tinkerforge_'):
            parts = serial_number.split('_')
            product_name = ' '.join([x.capitalize() for x in parts[1:-2]]).replace('Esp32', 'ESP32')
            description += ' - ' + product_name
            uid = base58encode(int(parts[-1]))
            description += ' [' + uid + ']'
        elif info.description != 'n/a' and info.description != info.name:
            if info.description == 'RED Brick - CDC Abstract Control Model (ACM)':
                description += ' - RED Brick (ACM)'
            else:
                description += ' - ' + info.description

        ports.append(SerialPort(path, description, opaque))

    return ports

#### skip here for brick-flash ####

CHIPID_CIDR = 0x400E0740

CHIPID_CIDR_ATSAM3S2B_A = 0x289A0760
CHIPID_CIDR_ATSAM3S4C_A = 0x28A00960
CHIPID_CIDR_ATSAM4S2B_A = 0x289B07E0
CHIPID_CIDR_ATSAM4S2B_B = 0x289B07E1
CHIPID_CIDR_ATSAM4S4C_A = 0x28AB09E0
CHIPID_CIDR_ATSAM4S4C_B = 0x28AB09E1
CHIPID_CIDR_ATSAM4S16C_A = 0x28AC0CE0
CHIPID_CIDR_ATSAM4S16C_B = 0x28AC0CE1
CHIPID_CIDR_ATSAM4E8C_A = 0xA3CC0CE0
CHIPID_CIDR_ATSAM4E8C_B = 0xA3CC0CE1
CHIPID_CIDR_ATSAM4E16E_A = 0xA3CC0CE0
CHIPID_CIDR_ATSAM4E16E_B = 0xA3CC0CE1
CHIPID_CIDR_ATSAM4E16E_C = 0xA3CC0CE0

CHIPID_EXID = 0x400E0744

CHIPID_EXID_ATSAM4E8C_A = 0x00120209
CHIPID_EXID_ATSAM4E8C_B = 0x00120209
CHIPID_EXID_ATSAM4E16E_A = 0x00120200
CHIPID_EXID_ATSAM4E16E_B = 0x00120200
CHIPID_EXID_ATSAM4E16E_C = 0x00120201

EEFC_FMR = 0x400E0A00
EEFC_FCR = 0x400E0A04
EEFC_FSR = 0x400E0A08
EEFC_FRR = 0x400E0A0C

EEFC_FSR_FRDY   = 0b0001
EEFC_FSR_FCMDE  = 0b0010
EEFC_FSR_FLOCKE = 0b0100
EEFC_FSR_FLERR  = 0b1000 # SAM4 only

EEFC_FCR_FKEY = 0x5A

EEFC_FCR_FCMD_WP   = 0x01 # Write Page
EEFC_FCR_FCMD_EA   = 0x05 # Erase All
EEFC_FCR_FCMD_SLB  = 0x08 # Set Lock Bit
EEFC_FCR_FCMD_CLB  = 0x09 # Clear Lock Bit
EEFC_FCR_FCMD_GLB  = 0x0A # Get Lock Bit
EEFC_FCR_FCMD_SGPB = 0x0B # Set GPNVM Bit
EEFC_FCR_FCMD_CGPB = 0x0C # Clear GPNVM Bit
EEFC_FCR_FCMD_GGPB = 0x0D # Get GPNVM Bit
EEFC_FCR_FCMD_STUI = 0x0E # Start Read Unique Identifier
EEFC_FCR_FCMD_SPUI = 0x0F # Stop Read Unique Identifier

RSTC_CR = 0x400E1400
RSTC_MR = 0x400E1408

RSTC_CR_PROCRST = 0b0001
RSTC_CR_PERRST  = 0b0100
RSTC_CR_EXTRST  = 0b1000

RSTC_MR_URSTEN  = 0b0001
RSTC_MR_URSTIEN = 0b1000

RSTC_CR_KEY        = 0xA5
RSTC_CR_KEY_OFFSET = 24

RSTC_MR_KEY        = 0xA5
RSTC_MR_KEY_OFFSET = 24

RSTC_MR_ERSTL_OFFSET = 8

# http://www.varsanofiev.com/inside/at91_sam_ba.htm
# http://sourceforge.net/p/lejos/wiki-nxt/SAM-BA%20Protocol/
# http://sourceforge.net/p/b-o-s-s-a/code/ci/master/tree/

class SAMBAException(Exception):
    def __str__(self):
        message = super().__str__()

        if self.__cause__ != None:
            return '{0} (cause: {1})'.format(message, self.__cause__)

        return message

class SAMBARebootError(SAMBAException):
    pass

class SAMBA:
    def __init__(self, port_name, progress=None, application_name='Brick Viewer'):
        self.r_command_bug = False
        self.sam_series = None
        self.current_mode = None
        self.progress = progress

        try:
            self.port = serial.Serial(port_name, 115200, timeout=5)
        except serial.SerialException as e:
            str_e = str(e)

            if '[Errno 13]' in str_e or 'Zugriff verweigert' in str_e:
                if sys.platform.startswith('linux'):
                    raise SAMBAException("No permission to open serial port, try starting {0} as root".format(application_name))
                elif sys.platform == 'win32':
                    raise SAMBAException("No permission to open serial port, try starting {0} as Administrator".format(application_name))
                else:
                    raise SAMBAException("No permission to open serial port")
            else:
                raise SAMBAException('Could not open serial port: {0}'.format(e))

        try:
            self.change_mode('T')
            self.change_mode('N')
        except Exception as e:
            raise SAMBAException('No Brick in Bootloader found') from e

        chipid_cidr = self.read_uint32(CHIPID_CIDR)
        chipid_exid = self.read_uint32(CHIPID_EXID)

        # SAM3
        if chipid_cidr == CHIPID_CIDR_ATSAM3S2B_A:
            self.sam_series = 3
            self.flash_base = 0x400000
            self.flash_page_count = 512
            self.flash_page_size = 256
            self.flash_lockbit_count = 8
        elif chipid_cidr == CHIPID_CIDR_ATSAM3S4C_A:
            self.sam_series = 3
            self.flash_base = 0x400000
            self.flash_page_count = 1024
            self.flash_page_size = 256
            self.flash_lockbit_count = 16

        # SAM4S
        elif chipid_cidr in [CHIPID_CIDR_ATSAM4S2B_A, CHIPID_CIDR_ATSAM4S2B_B]:
            self.sam_series = 4
            self.flash_base = 0x400000
            self.flash_page_count = 256
            self.flash_page_size = 512
            self.flash_lockbit_count = 16
        elif chipid_cidr in [CHIPID_CIDR_ATSAM4S4C_A, CHIPID_CIDR_ATSAM4S4C_B]:
            self.sam_series = 4
            self.flash_base = 0x400000
            self.flash_page_count = 512
            self.flash_page_size = 512
            self.flash_lockbit_count = 32
        elif chipid_cidr in [CHIPID_CIDR_ATSAM4S16C_A, CHIPID_CIDR_ATSAM4S16C_B]:
            self.sam_series = 4
            self.flash_base = 0x400000
            self.flash_page_count = 2048
            self.flash_page_size = 512
            self.flash_lockbit_count = 128

        # SAM4E
        elif chipid_cidr in [CHIPID_CIDR_ATSAM4E8C_A, CHIPID_CIDR_ATSAM4E8C_B] and \
             chipid_exid in [CHIPID_EXID_ATSAM4E8C_A, CHIPID_EXID_ATSAM4E8C_B]:
            self.sam_series = 4
            self.flash_base = 0x400000
            self.flash_page_count = 1024
            self.flash_page_size = 512
            self.flash_lockbit_count = 64
        elif chipid_cidr in [CHIPID_CIDR_ATSAM4E16E_A, CHIPID_CIDR_ATSAM4E16E_B, CHIPID_CIDR_ATSAM4E16E_C] and \
             chipid_exid in [CHIPID_EXID_ATSAM4E16E_A, CHIPID_EXID_ATSAM4E16E_B, CHIPID_EXID_ATSAM4E16E_C]:
            self.sam_series = 4
            self.flash_base = 0x400000
            self.flash_page_count = 2048
            self.flash_page_size = 512
            self.flash_lockbit_count = 128

        # unknown
        else:
            raise SAMBAException('Brick has unknown CHIPID: 0x%08X / 0x%08X' % (chipid_cidr, chipid_exid))

        self.flash_size = self.flash_page_count * self.flash_page_size
        self.flash_lockregion_size = self.flash_size // self.flash_lockbit_count
        self.flash_pages_per_lockregion = self.flash_lockregion_size // self.flash_page_size

    def change_mode(self, mode):
        if self.current_mode == mode:
            return

        try:
            self.port.write((mode + '#').encode('ascii'))
        except Exception as e:
            raise SAMBAException('Write error during mode change') from e

        if mode == 'T':
            while True:
                try:
                    response = self.port.read(1)
                except Exception as e:
                    raise SAMBAException('Read error during mode change') from e

                if len(response) == 0:
                    raise SAMBAException('Read timeout during mode change')

                if response == b'>':
                    break
        else:
            try:
                response = self.port.read(2)
            except Exception as e:
                raise SAMBAException('Read error during mode change') from e

            if len(response) == 0:
                raise SAMBAException('Read timeout during mode change')

            if response != b'\n\r':
                raise SAMBAException('Protocol error during mode change')

        self.current_mode = mode

    def read_uid64(self):
        self.write_flash_command(EEFC_FCR_FCMD_STUI, 0)
        self.wait_for_flash_ready('while reading UID', ready=False)

        uid1 = self.read_uint32(self.flash_base + 8)
        uid2 = self.read_uint32(self.flash_base + 12)

        self.write_flash_command(EEFC_FCR_FCMD_SPUI, 0)
        self.wait_for_flash_ready('after reading UID')

        return uid2 << 32 | uid1

    def flash(self, firmware, imu_calibration, lock_imu_calibration_pages, reboot=True):
        # Split firmware into pages
        firmware_pages = []
        offset = 0

        while offset < len(firmware):
            page = firmware[offset:offset + self.flash_page_size]

            if len(page) < self.flash_page_size:
                page += b'\xff' * (self.flash_page_size - len(page))

            firmware_pages.append(page)
            offset += self.flash_page_size

        if self.sam_series == 3:
            # SAM3S flash programming errata: FWS must be 6
            self.write_uint32(EEFC_FMR, 0x06 << 8)

        # Unlock
        self.reset_progress('Unlocking flash pages', 0)
        self.wait_for_flash_ready('before unlocking flash pages')

        for region in range(self.flash_lockbit_count):
            page_num = (region * self.flash_page_count) // self.flash_lockbit_count
            self.write_flash_command(EEFC_FCR_FCMD_CLB, page_num)
            self.wait_for_flash_ready('while unlocking flash pages')

        # Erase All
        self.reset_progress('Erasing flash pages', 0)
        self.write_flash_command(EEFC_FCR_FCMD_EA, 0)
        self.wait_for_flash_ready('while erasing flash pages', timeout=10000, update_progress=True)

        # Write firmware
        self.write_pages(firmware_pages, 0, 'Writing firmware')

        # Write IMU calibration
        if imu_calibration is not None:
            self.reset_progress('Writing IMU calibration', 0)

            ic_relative_address = self.flash_size - 0x1000 * 2 - 12 - 0x400
            ic_prefix_length = ic_relative_address % self.flash_page_size
            ic_prefix_address = self.flash_base + ic_relative_address - ic_prefix_length
            ic_prefix = b''
            offset = 0

            while len(ic_prefix) < ic_prefix_length:
                ic_prefix += self.read_word(ic_prefix_address + offset)
                offset += 4

            prefixed_imu_calibration = ic_prefix + imu_calibration

            # Split IMU calibration into pages
            imu_calibration_pages = []
            offset = 0

            while offset < len(prefixed_imu_calibration):
                page = prefixed_imu_calibration[offset:offset + self.flash_page_size]

                if len(page) < self.flash_page_size:
                    page += b'\xff' * (self.flash_page_size - len(page))

                imu_calibration_pages.append(page)
                offset += self.flash_page_size

            # Write IMU calibration
            page_num_offset = (ic_relative_address - ic_prefix_length) // self.flash_page_size

            self.write_pages(imu_calibration_pages, page_num_offset, 'Writing IMU calibration')

        # Lock firmware
        self.reset_progress('Locking flash pages', 0)
        self.lock_pages(0, len(firmware_pages))

        # Lock IMU calibration
        if imu_calibration is not None and lock_imu_calibration_pages:
            first_page_num = (ic_relative_address - ic_prefix_length) // self.flash_page_size
            self.lock_pages(first_page_num, len(imu_calibration_pages))

        # Verify firmware
        self.verify_pages(firmware_pages, 0, 'firmware', imu_calibration is not None)

        # Verify IMU calibration
        if imu_calibration is not None:
            page_num_offset = (ic_relative_address - ic_prefix_length) // self.flash_page_size
            self.verify_pages(imu_calibration_pages, page_num_offset, 'IMU calibration', True)

        # Set Security flag. Without this a Brick will not correctly boot from
        # flash after reset if it entered bootloader-mode by holding the erase
        # button during a power-cycle. In that case the Brick has to be power-
        # cycled to boot again, just pressing the reset button is not enough.
        #
        # But this has the downside for SAM3/4S that entering bootloader-mode
        # by holding the erase button during a power-cycle now results in the
        # Brick being in an zombie state between bootloader and firmware for 15
        # seconds before it properly enters bootloader-mode.
        #
        # An additional downside: entering bootloader-mode by holding the erase
        # button during a power-cycle doesn't work anymore for SAM4E. Enterging
        # bootloader-mode only works by pressing the reset button while holding
        # the erase button. This is a critical problem for devices without a
        # reset button.
        #
        # Because the problems outweigh the gains the Security flag is not set.
        if False:
            self.reset_progress('Setting Security flag', 0)

            self.wait_for_flash_ready('before setting Security flag')
            self.write_flash_command(EEFC_FCR_FCMD_SGPB, 0)
            self.wait_for_flash_ready('after setting Security flag')

        # Set Boot-from-Flash flag. Retry this up to 5 times, becasue on SAM4
        # series chips this might fail with a flash-memory-error on the first try
        self.reset_progress('Setting Boot-from-Flash flag', 0)

        success = False

        for _ in range(5):
            self.write_flash_command(EEFC_FCR_FCMD_SGPB, 1)

            success = self.wait_for_flash_ready('after setting Boot-from-Flash flag', return_on_flerr=True)

            if success:
                break

            time.sleep(0.25)

        if not success:
            raise SAMBAException('Flash memory error after setting Boot-from-Flash flag')

        # Reboot
        if reboot:
            try:
                self.reset()
            except SAMBAException as e:
                raise SAMBARebootError(str(e))

    def reset_progress(self, title, length):
        if self.progress != None:
            self.progress.reset(title, length)

    def update_progress(self, value):
        if self.progress != None:
            self.progress.update(value)

    def write_pages(self, pages, page_num_offset, title):
        self.reset_progress(title, len(pages))

        page_num = 0

        for page in pages:
            # FIXME: the S command used by the write_bytes function doesn't
            #        write the data correctly. instead use the write_word function
            if False:
                address = self.flash_base + (page_num_offset + page_num) * self.flash_page_size
                self.write_bytes(address, page)
            else:
                offset = 0

                while offset < len(page):
                    address = self.flash_base + (page_num_offset + page_num) * self.flash_page_size + offset
                    self.write_word(address, page[offset:offset + 4])
                    offset += 4

            self.wait_for_flash_ready('while writing flash pages')
            self.write_flash_command(EEFC_FCR_FCMD_WP, page_num_offset + page_num)
            self.wait_for_flash_ready('while writing flash pages')

            page_num += 1
            self.update_progress(page_num)

    def verify_pages(self, pages, page_num_offset, title, title_in_error):
        self.reset_progress('Verifying written ' + title, len(pages))

        offset = page_num_offset * self.flash_page_size
        page_num = 0

        for page in pages:
            read_page = self.read_bytes(self.flash_base + offset, len(page))
            offset += len(page)

            if read_page != page:
                if title_in_error:
                    raise SAMBAException('Verification error ({0})'.format(title))
                else:
                    raise SAMBAException('Verification error')

            page_num += 1
            self.update_progress(page_num)

    def lock_pages(self, page_num, page_count):
        start_page_num = page_num - (page_num % self.flash_pages_per_lockregion)
        end_page_num = page_num + page_count

        if (end_page_num % self.flash_pages_per_lockregion) != 0:
            end_page_num += self.flash_pages_per_lockregion - (end_page_num % self.flash_pages_per_lockregion)

        self.wait_for_flash_ready('before locking flash pages')

        for region in range(start_page_num // self.flash_pages_per_lockregion,
                            end_page_num // self.flash_pages_per_lockregion):
            page_num = (region * self.flash_page_count) // self.flash_lockbit_count
            self.write_flash_command(EEFC_FCR_FCMD_SLB, page_num)
            self.wait_for_flash_ready('while locking flash pages')

    def read_word(self, address): # 4 bytes
        self.change_mode('N')

        try:
            self.port.write(('w%X,4#' % address).encode('ascii'))
        except Exception as e:
            raise SAMBAException('Write error while reading from address 0x%08X' % address) from e

        try:
            response = self.port.read(4)
        except Exception as e:
            raise SAMBAException('Read error while reading from address 0x%08X' % address) from e

        if len(response) == 0:
            raise SAMBAException('Timeout while reading from address 0x%08X' % address)

        if len(response) != 4:
            raise SAMBAException('Length error while reading from address 0x%08X' % address)

        return response

    def write_word(self, address, value): # 4 bytes
        self.write_uint32(address, struct.unpack('<I', value)[0])

    def read_uint32(self, address):
        return struct.unpack('<I', self.read_word(address))[0]

    def write_uint32(self, address, value):
        self.change_mode('N')

        try:
            self.port.write(('W%X,%X#' % (address, value)).encode('ascii'))
        except Exception as e:
            raise SAMBAException('Write error while writing to address 0x%08X' % address) from e

    def read_bytes(self, address, length):
        # according to the BOSSA flash program, SAM-BA can have a bug regarding
        # reading more than 32 bytes at a time if the amount to be read is a
        # power of 2. to work around this split the read operation in two steps
        prefix = b''

        if self.r_command_bug and length > 32 and length & (length - 1) == 0:
            prefix = self.read_word(address)
            address += 4
            length -= 4

        self.change_mode('T')

        try:
            self.port.write(('R%X,%X#' % (address, length)).encode('ascii'))
        except Exception as e:
            raise SAMBAException('Write error while reading from address 0x%08X' % address) from e

        try:
            response = self.port.read(length + 3)
        except Exception as e:
            raise SAMBAException('Read error while reading from address 0x%08X' % address) from e

        if len(response) == 0:
            raise SAMBAException('Timeout while reading from address 0x%08X' % address)

        if len(response) != length + 3:
            raise SAMBAException('Length error while reading from address 0x%08X' % address)

        if not response.startswith(b'\n\r') or not response.endswith(b'>'):
            raise SAMBAException('Protocol error while reading from address 0x%08X' % address)

        return prefix + response[2:-1]

    def write_bytes(self, address, bytes_):
        self.change_mode('T')

        # FIXME: writes '33337777BBBBFFFF' instead of '0123456789ABCDEF'
        try:
            # according to the BOSSA flash program, SAM-BA can get confused if
            # the command and the data to be written is received in the same USB
            # packet. to work around this, flush the serial port in between the
            # command and the data
            self.port.write(('S%X,%X#' % (address, len(bytes_))).encode('ascii'))
            self.port.flush()
            self.port.write(bytes_)
        except Exception as e:
            raise SAMBAException('Write error while writing to address 0x%08X' % address) from e

        try:
            response = self.port.read(3)
        except Exception as e:
            raise SAMBAException('Read error while writing to address 0x%08X' % address) from e

        if len(response) == 0:
            raise SAMBAException('Timeout while writing to address 0x%08X' % address)

        if response != b'\n\r>':
            raise SAMBAException('Protocol error while writing to address 0x%08X' % address)

    def reset(self):
        self.reset_progress('Triggering Brick reset', 0)

        try:
            self.write_uint32(RSTC_MR, (RSTC_MR_KEY << RSTC_MR_KEY_OFFSET) | (10 << RSTC_MR_ERSTL_OFFSET) | RSTC_MR_URSTEN)
            self.write_uint32(RSTC_CR, (RSTC_CR_KEY << RSTC_CR_KEY_OFFSET) | RSTC_CR_EXTRST | RSTC_CR_PERRST | RSTC_CR_PROCRST)
        except Exception as e:
            raise SAMBAException('Write error while triggering reset') from e

    def go(self, address):
        self.change_mode('N')

        try:
            # according to the BOSSA flash program, SAM-BA can get confused if
            # another command is received in the same USB packet as the G
            # command. to work around this, flush the serial port afterwards
            self.port.write(('G%X#' % address).encode('ascii'))
            self.port.flush()
        except Exception as e:
            raise SAMBAException('Write error while executing code at address 0x%08X' % address) from e

    def wait_for_flash_ready(self, message, timeout=2000, ready=True, update_progress=False, return_on_flerr=False):
        for _ in range(timeout):
            fsr = self.read_uint32(EEFC_FSR)

            if (fsr & EEFC_FSR_FLOCKE) != 0:
                raise SAMBAException('Flash locking error ' + message)

            if (fsr & EEFC_FSR_FCMDE) != 0:
                raise SAMBAException('Flash command error ' + message)

            if self.sam_series == 4 and (fsr & EEFC_FSR_FLERR) != 0:
                if return_on_flerr:
                    return False
                else:
                    raise SAMBAException('Flash memory error ' + message)

            if ready:
                if (fsr & EEFC_FSR_FRDY) != 0:
                    break
            else:
                if (fsr & EEFC_FSR_FRDY) == 0:
                    break

            time.sleep(0.001)

            if update_progress:
                self.update_progress(0)
        else:
            raise SAMBAException('Flash timeout ' + message)

        return True

    def write_flash_command(self, command, argument):
        self.write_uint32(EEFC_FCR, (EEFC_FCR_FKEY << 24) | (argument << 8) | command)
