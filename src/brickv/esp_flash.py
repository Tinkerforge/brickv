# ESP8266 ROM Bootloader Utility
# https://github.com/themadinventor/esptool
#
# Copyright (C) 2014 Fredrik Ahlberg
# Copyright (C) 2015 Olaf Lueke <olaf@tinkerforge.com>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#
#
# The ESPROM class was taken from the repository above and made compatible to be used
# with Master Brick and Brick Viewer.
#
# We try to stay as compatible as possible to the class, so we can easily
# merge updates later on.

import struct
import time
import math
import sys
from zipfile import ZipFile

try:
    from StringIO import StringIO as FileLike
except ImportError:
    from io import BytesIO as FileLike

class TFSerial:
    def __init__(self, master):
        self.master = master
        self.timeout = 1
        self.read_buffer = []
        self.baudrate = None
        time.sleep(1)

    # Implement Serial functions that we don't need
    def setDTR(self, _): pass
    def flushInput(self): pass
    def flushOutput(self): pass

    # We misuse the setRTS call to start the bootloader mode (and flush everyting etc)
    def setRTS(self, value):
        if value:
            self.master.start_wifi2_bootloader()

    def write(self, data):
        try:
            if type(data) == str:
                data = map(ord, data) # Python 2
            else:
                data = list(data) # Python 3

            while data != []:
                data_chunk = data[:60]
                length = len(data_chunk)
                data_chunk.extend([0]*(60-length))
                self.master.write_wifi2_serial_port(data_chunk, length)
                data = data[60:]
        except:
            raise Exception('Failed to write data')

    def read(self, length):
        if len(self.read_buffer) >= length:
            ret = self.read_buffer[:length]
            self.read_buffer = self.read_buffer[length:]
            if sys.hexversion < 0x03000000:
                return ''.join(map(chr, ret))
            else:
                return bytes(ret)

        try:
            t = time.time()
            while len(self.read_buffer) < length:
                data, l = self.master.read_wifi2_serial_port(60)
                data = data[:l]
                self.read_buffer.extend(data)
                if len(self.read_buffer) < length:
                    time.sleep(0.1)
                if time.time() - t > self.timeout:
                    break

        except:
            raise Exception('Failed to read data')

        ret = self.read_buffer[:length]
        self.read_buffer = self.read_buffer[length:]
        if sys.hexversion < 0x03000000:
            return ''.join(map(chr, ret))
        else:
            return bytes(ret)

class ESPROM:

    # These are the currently known commands supported by the ROM
    ESP_FLASH_BEGIN = 0x02
    ESP_FLASH_DATA  = 0x03
    ESP_FLASH_END   = 0x04
    ESP_MEM_BEGIN   = 0x05
    ESP_MEM_END     = 0x06
    ESP_MEM_DATA    = 0x07
    ESP_SYNC        = 0x08
    ESP_WRITE_REG   = 0x09
    ESP_READ_REG    = 0x0a

    # Maximum block sized for RAM and Flash writes, respectively.
    ESP_RAM_BLOCK   = 0x1800
    ESP_FLASH_BLOCK = 0x400

    # Default baudrate. The ROM auto-bauds, so we can use more or less whatever we want.
    ESP_ROM_BAUD    = 115200

    # First byte of the application image
    ESP_IMAGE_MAGIC = 0xe9

    # Initial state for the checksum routine
    ESP_CHECKSUM_MAGIC = 0xef

    # OTP ROM addresses
    ESP_OTP_MAC0    = 0x3ff00050
    ESP_OTP_MAC1    = 0x3ff00054

    # Sflash stub: an assembly routine to read from spi flash and send to host
    SFLASH_STUB     = b"\x80\x3c\x00\x40\x1c\x4b\x00\x40\x21\x11\x00\x40\x00\x80" \
            b"\xfe\x3f\xc1\xfb\xff\xd1\xf8\xff\x2d\x0d\x31\xfd\xff\x41\xf7\xff\x4a" \
            b"\xdd\x51\xf9\xff\xc0\x05\x00\x21\xf9\xff\x31\xf3\xff\x41\xf5\xff\xc0" \
            b"\x04\x00\x0b\xcc\x56\xec\xfd\x06\xff\xff\x00\x00"

    def __init__(self, master):
        self._port = TFSerial(master)

    """ Read bytes from the serial port while performing SLIP unescaping """
    def read(self, length = 1):
        b = b''
        while len(b) < length:
            c = self._port.read(1)
            if c == b'\xdb':
                c = self._port.read(1)
                if c == b'\xdc':
                    b = b + b'\xc0'
                elif c == b'\xdd':
                    b = b + b'\xdb'
                else:
                    raise Exception('Invalid SLIP escape')
            else:
                b = b + c
        return b

    """ Write bytes to the serial port while performing SLIP escaping """
    def write(self, packet):
        buf = b'\xc0'+(packet.replace(b'\xdb',b'\xdb\xdd').replace(b'\xc0',b'\xdb\xdc'))+b'\xc0'
        self._port.write(buf)

    """ Calculate checksum of a blob, as it is defined by the ROM """
    @staticmethod
    def checksum(data, state = ESP_CHECKSUM_MAGIC):
        for b in data:
            state ^= ord(b) if sys.hexversion < 0x03000000 else b
        return state

    """ Send a request and read the response """
    def command(self, op = None, data = None, chk = 0):
        if op:
            # Construct and send request
            pkt = struct.pack('<BBHI', 0x00, op, len(data), chk) + data
            self.write(pkt)

        # Read header of response and parse
        if self._port.read(1) != b'\xc0':
            raise Exception('Invalid head of packet')
        hdr = self.read(8)
        (resp, op_ret, len_ret, val) = struct.unpack('<BBHI', hdr)
        if resp != 0x01 or (op and op_ret != op):
            raise Exception('Invalid response')

        # The variable-length body
        body = self.read(len_ret)

        # Terminating byte
        if self._port.read(1) != b'\xc0':
            raise Exception('Invalid end of packet')

        return val, body

    """ Perform a connection test """
    def sync(self):
        self.command(ESPROM.ESP_SYNC, b'\x07\x07\x12\x20'+32*b'\x55')
        for _ in range(7):
            self.command()

    """ Try connecting repeatedly until successful, or giving up """
    def connect(self):
        for _ in range(10):
            # issue reset-to-bootloader:
            # RTS = either CH_PD or nRESET (both active low = chip in reset)
            # DTR = GPIO0 (active low = boot to flasher)
            self._port.setDTR(False)
            self._port.setRTS(True)
            time.sleep(0.05)
            self._port.setDTR(True)
            self._port.setRTS(False)
            time.sleep(0.05)
            self._port.setDTR(False)

            self._port.timeout = 0.3 # worst-case latency timer should be 255ms (probably <20ms)
            for _ in range(3):
                try:
                    self._port.flushInput()
                    self._port.flushOutput()
                    self.sync()
                    self._port.timeout = 5
                    return
                except:
                    time.sleep(0.05)
        raise Exception('Failed to connect')

    """ Read memory address in target """
    def read_reg(self, addr):
        res = self.command(ESPROM.ESP_READ_REG, struct.pack('<I', addr))
        if res[1] != "\0\0":
            raise Exception('Failed to read target memory')
        return res[0]

    """ Write to memory address in target """
    def write_reg(self, addr, value, mask, delay_us = 0):
        if self.command(ESPROM.ESP_WRITE_REG,
                struct.pack('<IIII', addr, value, mask, delay_us))[1] != b"\0\0":
            raise Exception('Failed to write target memory')

    """ Start downloading an application image to RAM """
    def mem_begin(self, size, blocks, blocksize, offset):
        if self.command(ESPROM.ESP_MEM_BEGIN,
                struct.pack('<IIII', size, blocks, blocksize, offset))[1] != b"\0\0":
            raise Exception('Failed to enter RAM download mode')

    """ Send a block of an image to RAM """
    def mem_block(self, data, seq):
        if self.command(ESPROM.ESP_MEM_DATA,
                struct.pack('<IIII', len(data), seq, 0, 0)+data, ESPROM.checksum(data))[1] != b"\0\0":
            raise Exception('Failed to write to target RAM')

    """ Leave download mode and run the application """
    def mem_finish(self, entrypoint = 0):
        if self.command(ESPROM.ESP_MEM_END,
                struct.pack('<II', int(entrypoint == 0), entrypoint))[1] != b"\0\0":
            raise Exception('Failed to leave RAM download mode')

    """ Start downloading to Flash (performs an erase) """
    def flash_begin(self, size, offset):
        old_tmo = self._port.timeout
        num_blocks = (size + ESPROM.ESP_FLASH_BLOCK - 1) // ESPROM.ESP_FLASH_BLOCK
        self._port.timeout = 10
        if self.command(ESPROM.ESP_FLASH_BEGIN,
                struct.pack('<IIII', size, num_blocks, ESPROM.ESP_FLASH_BLOCK, offset))[1] != b"\0\0":
            raise Exception('Failed to enter Flash download mode')
        self._port.timeout = old_tmo

    """ Write block to flash """
    def flash_block(self, data, seq):
        if self.command(ESPROM.ESP_FLASH_DATA,
                struct.pack('<IIII', len(data), seq, 0, 0)+data, ESPROM.checksum(data))[1] != b"\0\0":
            raise Exception('Failed to write to target Flash')

    """ Leave flash mode and run/reboot """
    def flash_finish(self, reboot = False):
        pkt = struct.pack('<I', int(not reboot))
        if self.command(ESPROM.ESP_FLASH_END, pkt)[1] != b"\0\0":
            raise Exception('Failed to leave Flash mode')

    """ Run application code in flash """
    def run(self, reboot = False):
        # Fake flash begin immediately followed by flash end
        self.flash_begin(0, 0)
        self.flash_finish(reboot)

    """ Read SPI flash """
    def flash_read(self, offset, size, count = 1):
        # Create a custom stub
        stub = struct.pack('<III', offset, size, count) + self.SFLASH_STUB

        # Trick ROM to initialize SFlash
        self.flash_begin(0, 0)

        # Download stub
        self.mem_begin(len(stub), 1, len(stub), 0x40100000)
        self.mem_block(stub, 0)
        self.mem_finish(0x4010001c)

        # Fetch the data
        data = ''
        for _ in range(count):
            if self._port.read(1) != b'\xc0':
                raise Exception('Invalid head of packet (sflash read)')

            data += self.read(size)

            if self._port.read(1) != b'\xc0':
                raise Exception('Invalid end of packet (sflash read)')

        return data

    """ Abuse the loader protocol to force flash to be left in write mode """
    def flash_unlock_dio(self):
        # Enable flash write mode
        self.flash_begin(0, 0)
        # Reset the chip rather than call flash_finish(), which would have
        # write protected the chip again (why oh why does it do that?!)
        self.mem_begin(0,0,0,0x40100000)
        self.mem_finish(0x40000080)

    """ Perform a chip erase of SPI flash """
    def flash_erase(self):
        # Trick ROM to initialize SFlash
        self.flash_begin(0, 0)

        # This is hacky: we don't have a custom stub, instead we trick
        # the bootloader to jump to the SPIEraseChip() routine and then halt/crash
        # when it tries to boot an unconfigured system.
        self.mem_begin(0,0,0,0x40100000)
        self.mem_finish(0x40004984)

        # Yup - there's no good way to detect if we succeeded.
        # It it on the other hand unlikely to fail.

class ESPFlash:
    def __init__(self, master, progress=None):
        self.master = master
        self.progress = progress

    def reset_progress(self, title, length):
        if self.progress != None:
            self.progress.reset(title, length)

    def update_progress(self, value):
        if self.progress != None:
            self.progress.update(value)

    def flash(self, firmware):
        files = []
        zf = ZipFile(FileLike(firmware), 'r')

        for name in zf.namelist():
            files.append((int(name.replace('.bin', ''), 0), name))

        esp = ESPROM(self.master)
        esp.connect()

        flash_mode = 0
        flash_size_freq = 64
        flash_info = struct.pack('BB', flash_mode, flash_size_freq)

        for i, f in enumerate(files):
            address = f[0]
            image = zf.read(f[1])
            self.reset_progress('Erasing flash ({0}/{1})'.format(i+1, len(files)), 0)
            self.update_progress(0)
            blocks = math.ceil(len(image)/float(esp.ESP_FLASH_BLOCK))
            esp.flash_begin(blocks*esp.ESP_FLASH_BLOCK, address)
            seq = 0

            self.reset_progress('Writing flash ({0}/{1})'.format(i+1, len(files)), blocks)
            while len(image) > 0:
                self.update_progress(seq)
                block = image[0:esp.ESP_FLASH_BLOCK]

                # Fix sflash config data
                if address == 0 and seq == 0 and block[0] == b'\xe9':
                    block = block[0:2] + flash_info + block[4:]

                # Pad the last block
                block = block + b'\xff' * (esp.ESP_FLASH_BLOCK-len(block))
                esp.flash_block(block, seq)

                image = image[esp.ESP_FLASH_BLOCK:]
                seq += 1

            self.update_progress(blocks)

        esp.flash_finish(False)
