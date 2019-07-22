# -*- coding: utf-8 -*-
# ESP8266 ROM Bootloader Utility
# https://github.com/themadinventor/esptool
#
# Copyright (C) 2014-2016 Fredrik Ahlberg, Angus Gratton, other contributors as noted.
# Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
# Copyright (C) 2016 Matthias Bolte <matthias@tinkerforge.com>
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


# The code was taken from the repository above and made compatible to be used
# with Master Brick and Brick Viewer.
#
# We try to stay as compatible as possible to the class, so we can easily
# merge updates later on.

import hashlib
import json
import struct
import sys
import time

class ESPROM:
    # These are the currently known commands supported by the ROM
    ESP_FLASH_BEGIN = 0x02
    ESP_FLASH_DATA = 0x03
    ESP_FLASH_END = 0x04
    ESP_MEM_BEGIN = 0x05
    ESP_MEM_END = 0x06
    ESP_MEM_DATA = 0x07
    ESP_SYNC = 0x08
    ESP_WRITE_REG = 0x09
    ESP_READ_REG = 0x0a

    # Maximum block sized for RAM and Flash writes, respectively.
    ESP_RAM_BLOCK = 0x1800
    ESP_FLASH_BLOCK = 0x400

    # Default baudrate. The ROM auto-bauds, so we can use more or less whatever we want.
    ESP_ROM_BAUD = 115200

    # First byte of the application image
    ESP_IMAGE_MAGIC = 0xe9

    # Initial state for the checksum routine
    ESP_CHECKSUM_MAGIC = 0xef

    # OTP ROM addresses
    ESP_OTP_MAC0 = 0x3ff00050
    ESP_OTP_MAC1 = 0x3ff00054
    ESP_OTP_MAC3 = 0x3ff0005c

    # Flash sector size, minimum unit of erase.
    ESP_FLASH_SECTOR = 0x1000

    def __init__(self, master):
        self._port = TFSerial(master)
        self._slip_reader = slip_reader(self._port)

    """ Read a SLIP packet from the serial port """
    def read(self):
        return next(self._slip_reader)

    """ Write bytes to the serial port while performing SLIP escaping """
    def write(self, packet):
        buf = b'\xc0' + packet.replace(b'\xdb', b'\xdb\xdd').replace(b'\xc0', b'\xdb\xdc') + b'\xc0'
        self._port.write(buf)

    """ Write bytes to the serial port """
    def write_raw(self, data):
        self._port.write(data)

    """ Calculate checksum of a blob, as it is defined by the ROM """
    @staticmethod
    def checksum(data, state=ESP_CHECKSUM_MAGIC):
        for byte in data:
            state ^= byte

        return state

    """ Send a request and read the response """
    def command(self, op=None, data=None, chk=0):
        if op is not None:
            pkt = struct.pack('<BBHI', 0x00, op, len(data), chk) + data
            self.write(pkt)

        # tries to get a response until that response has the
        # same operation as the request or a retries limit has
        # exceeded. This is needed for some esp8266s that
        # reply with more sync responses than expected.
        for retry in range(100):
            p = self.read()

            if len(p) < 8:
                continue

            (resp, op_ret, len_ret, val) = struct.unpack('<BBHI', p[:8])

            if resp != 1:
                continue

            body = p[8:]

            if op is None or op_ret == op:
                return val, body  # valid response received

        raise FatalError("Response doesn't match request")

    """ Perform a connection test """
    def sync(self):
        self.command(ESPROM.ESP_SYNC, b'\x07\x07\x12\x20' + 32 * b'\x55')

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

            # worst-case latency timer should be 255ms (probably <20ms)
            self._port.timeout = 0.3

            for _ in range(10):
                try:
                    self._port.flushInput()
                    self._slip_reader = slip_reader(self._port)
                    self._port.flushOutput()
                    self.sync()
                    self._port.timeout = 3
                    return
                except:
                    time.sleep(0.05)

        raise FatalError('Failed to connect to ESP8266')

    """ Read memory address in target """
    def read_reg(self, addr):
        res = self.command(ESPROM.ESP_READ_REG, struct.pack('<I', addr))

        if res[1] != b"\0\0":
            raise FatalError('Failed to read target memory')

        return res[0]

    """ Write to memory address in target """
    def write_reg(self, addr, value, mask, delay_us=0):
        if self.command(ESPROM.ESP_WRITE_REG,
                        struct.pack('<IIII', addr, value, mask, delay_us))[1] != b"\0\0":
            raise FatalError('Failed to write target memory')

    """ Start downloading an application image to RAM """
    def mem_begin(self, size, blocks, blocksize, offset):
        if self.command(ESPROM.ESP_MEM_BEGIN,
                        struct.pack('<IIII', size, blocks, blocksize, offset))[1] != b"\0\0":
            raise FatalError('Failed to enter RAM download mode')

    """ Send a block of an image to RAM """
    def mem_block(self, data, seq):
        if self.command(ESPROM.ESP_MEM_DATA,
                        struct.pack('<IIII', len(data), seq, 0, 0) + data,
                        ESPROM.checksum(data))[1] != b"\0\0":
            raise FatalError('Failed to write to target RAM')

    """ Leave download mode and run the application """
    def mem_finish(self, entrypoint=0):
        if self.command(ESPROM.ESP_MEM_END,
                        struct.pack('<II', int(entrypoint == 0), entrypoint))[1] != b"\0\0":
            raise FatalError('Failed to leave RAM download mode')

    """ Start downloading to Flash (performs an erase) """
    def flash_begin(self, size, offset):
        old_tmo = self._port.timeout
        num_blocks = (size + ESPROM.ESP_FLASH_BLOCK - 1) // ESPROM.ESP_FLASH_BLOCK

        sectors_per_block = 16
        sector_size = self.ESP_FLASH_SECTOR
        num_sectors = (size + sector_size - 1) // sector_size
        start_sector = offset // sector_size

        head_sectors = sectors_per_block - (start_sector % sectors_per_block)

        if num_sectors < head_sectors:
            head_sectors = num_sectors

        if num_sectors < 2 * head_sectors:
            erase_size = (num_sectors + 1) // 2 * sector_size
        else:
            erase_size = (num_sectors - head_sectors) * sector_size

        self._port.timeout = 30
        result = self.command(ESPROM.ESP_FLASH_BEGIN,
                              struct.pack('<IIII', erase_size, num_blocks, ESPROM.ESP_FLASH_BLOCK, offset))[1]

        if result != b"\0\0":
            raise FatalError.WithResult('Failed to enter Flash download mode (result "{}")', result)

        self._port.timeout = old_tmo

    """ Write block to flash """
    def flash_block(self, data, seq):
        result = self.command(ESPROM.ESP_FLASH_DATA,
                              struct.pack('<IIII', len(data), seq, 0, 0) + data,
                              ESPROM.checksum(data))[1]

        if result != b"\0\0":
            raise FatalError.WithResult('Failed to write to target Flash after seq {} (got result {{}})'.format(seq), result)

    """ Leave flash mode and run/reboot """
    def flash_finish(self, reboot=False):
        pkt = struct.pack('<I', int(not reboot))

        if self.command(ESPROM.ESP_FLASH_END, pkt)[1] != b"\0\0":
            raise FatalError('Failed to leave Flash mode')

    """ Run application code in flash """
    def run(self, reboot=False):
        # Fake flash begin immediately followed by flash end
        self.flash_begin(0, 0)
        self.flash_finish(reboot)

    """ Read MAC from OTP ROM """
    def read_mac(self):
        mac0 = self.read_reg(self.ESP_OTP_MAC0)
        mac1 = self.read_reg(self.ESP_OTP_MAC1)
        mac3 = self.read_reg(self.ESP_OTP_MAC3)

        if mac3 != 0:
            oui = ((mac3 >> 16) & 0xff, (mac3 >> 8) & 0xff, mac3 & 0xff)
        elif ((mac1 >> 16) & 0xff) == 0:
            oui = (0x18, 0xfe, 0x34)
        elif ((mac1 >> 16) & 0xff) == 1:
            oui = (0xac, 0xd0, 0x74)
        else:
            raise FatalError("Unknown OUI")

        return oui + ((mac1 >> 8) & 0xff, mac1 & 0xff, (mac0 >> 24) & 0xff)

    """ Read Chip ID from OTP ROM - see http://esp8266-re.foogod.com/wiki/System_get_chip_id_%28IoT_RTOS_SDK_0.9.9%29 """
    def chip_id(self):
        id0 = self.read_reg(self.ESP_OTP_MAC0)
        id1 = self.read_reg(self.ESP_OTP_MAC1)

        return (id0 >> 24) | ((id1 & 0xffffff) << 8)

    """ Read SPI flash manufacturer and device id """
    def flash_id(self):
        self.flash_begin(0, 0)
        self.write_reg(0x60000240, 0x0, 0xffffffff)
        self.write_reg(0x60000200, 0x10000000, 0xffffffff)
        flash_id = self.read_reg(0x60000240)
        self.flash_finish(False)

        return flash_id

    """ Abuse the loader protocol to force flash to be left in write mode """
    def flash_unlock_dio(self):
        # Enable flash write mode
        self.flash_begin(0, 0)
        # Reset the chip rather than call flash_finish(), which would have
        # write protected the chip again (why oh why does it do that?!)
        self.mem_begin(0, 0, 0, 0x40100000)
        self.mem_finish(0x40000080)

    """ Perform a chip erase of SPI flash """
    def flash_erase(self):
        # Trick ROM to initialize SFlash
        self.flash_begin(0, 0)

        # This is hacky: we don't have a custom stub, instead we trick
        # the bootloader to jump to the SPIEraseChip() routine and then halt/crash
        # when it tries to boot an unconfigured system.
        self.mem_begin(0, 0, 0, 0x40100000)
        self.mem_finish(0x40004984)

        # Yup - there's no good way to detect if we succeeded.
        # It it on the other hand unlikely to fail.

    def run_stub(self, stub, params):
        stub = dict(stub)
        stub['code'] = unhexify(stub['code'])

        if 'data' in stub:
            stub['data'] = unhexify(stub['data'])

        if stub['num_params'] != len(params):
            raise FatalError('Stub requires %d params, %d provided'
                             % (stub['num_params'], len(params)))

        params = struct.pack('<' + ('I' * stub['num_params']), *params)
        pc = params + stub['code']

        # Upload
        self.mem_begin(len(pc), 1, len(pc), stub['params_start'])
        self.mem_block(pc, 0)

        if 'data' in stub:
            self.mem_begin(len(stub['data']), 1, len(stub['data']), stub['data_start'])
            self.mem_block(stub['data'], 0)

        self.mem_finish(stub['entry'])


class CesantaFlasher:
    # From stub_flasher.h
    CMD_FLASH_WRITE = 1
    CMD_FLASH_READ = 2
    CMD_FLASH_DIGEST = 3
    CMD_FLASH_ERASE_CHIP = 5
    CMD_BOOT_FW = 6

    def __init__(self, esp, baud_rate=0):
        if baud_rate <= ESPROM.ESP_ROM_BAUD:  # don't change baud rates if we already synced at that rate
            baud_rate = 0

        self._esp = esp
        esp.run_stub(json.loads(_CESANTA_FLASHER_STUB), [baud_rate])

        if baud_rate > 0:
            esp._port.baudrate = baud_rate

        # Read the greeting.
        p = esp.read()

        if p != b'OHAI':
            raise FatalError('Failed to connect to the flasher (got %s)' % hexify(p))

    def flash_write(self, addr, data, progress):
        assert addr % self._esp.ESP_FLASH_SECTOR == 0, 'Address must be sector-aligned'
        assert len(data) % self._esp.ESP_FLASH_SECTOR == 0, 'Length must be sector-aligned'

        self._esp.write(struct.pack('<B', self.CMD_FLASH_WRITE))
        self._esp.write(struct.pack('<III', addr, len(data), 1))
        num_sent, num_written = 0, 0

        while num_written < len(data):
            p = self._esp.read()

            if len(p) == 4:
                num_written = struct.unpack('<I', p)[0]
            elif len(p) == 1:
                status_code = struct.unpack('<B', p)[0]
                raise FatalError('Write failure, status: %x' % status_code)
            else:
                raise FatalError('Unexpected packet while writing: %s' % hexify(p))

            progress(num_written // self._esp.ESP_FLASH_BLOCK)

            while num_sent - num_written < 5120:
                self._esp.write_raw(data[num_sent:num_sent + 1024])
                num_sent += 1024

        p = self._esp.read()

        if len(p) != 16:
            raise FatalError('Expected digest, got: %s' % hexify(p))

        digest = hexify(p).upper()
        expected_digest = hashlib.md5(data).hexdigest().upper()

        if digest != expected_digest:
            raise FatalError('Digest mismatch: expected %s, got %s' % (expected_digest, digest))

        p = self._esp.read()

        if len(p) != 1:
            raise FatalError('Expected status, got: %s' % hexify(p))
        status_code = struct.unpack('<B', p)[0]

        if status_code != 0:
            raise FatalError('Write failure, status: %x' % status_code)

    def flash_read(self, addr, length, show_progress=False):
        sys.stdout.write('Reading %d @ 0x%x... ' % (length, addr))
        sys.stdout.flush()
        self._esp.write(struct.pack('<B', self.CMD_FLASH_READ))

        # USB may not be able to keep up with the read rate, especially at
        # higher speeds. Since we don't have flow control, this will result in
        # data loss. Hence, we use small packet size and only allow small
        # number of bytes in flight, which we can reasonably expect to fit in
        # the on-chip FIFO. max_in_flight = 64 works for CH340G, other chips may
        # have longer FIFOs and could benefit from increasing max_in_flight.
        self._esp.write(struct.pack('<IIII', addr, length, 32, 64))
        data = ''

        while True:
            p = self._esp.read()
            data += p
            self._esp.write(struct.pack('<I', len(data)))

            if show_progress and (len(data) % 1024 == 0 or len(data) == length):
                progress = '%d (%d %%)' % (len(data), len(data) * 100.0 / length)
                sys.stdout.write(progress + '\b' * len(progress))
                sys.stdout.flush()

            if len(data) == length:
                break

            if len(data) > length:
                raise FatalError('Read more than expected')

        p = self._esp.read()

        if len(p) != 16:
            raise FatalError('Expected digest, got: %s' % hexify(p))

        expected_digest = hexify(p).upper()
        digest = hashlib.md5(data).hexdigest().upper()

        if digest != expected_digest:
            raise FatalError('Digest mismatch: expected %s, got %s' % (expected_digest, digest))

        p = self._esp.read()

        if len(p) != 1:
            raise FatalError('Expected status, got: %s' % hexify(p))

        status_code = struct.unpack('<B', p)[0]

        if status_code != 0:
            raise FatalError('Write failure, status: %x' % status_code)

        return data

    def flash_digest(self, addr, length, digest_block_size=0):
        self._esp.write(struct.pack('<B', self.CMD_FLASH_DIGEST))
        self._esp.write(struct.pack('<III', addr, length, digest_block_size))
        digests = []

        while True:
            p = self._esp.read()

            if len(p) == 16:
                digests.append(p)
            elif len(p) == 1:
                status_code = struct.unpack('<B', p)[0]

                if status_code != 0:
                    raise FatalError('Write failure, status: %x' % status_code)

                break
            else:
                raise FatalError('Unexpected packet: %s' % hexify(p))

        return digests[-1], digests[:-1]

    def boot_fw(self):
        self._esp.write(struct.pack('<B', self.CMD_BOOT_FW))
        p = self._esp.read()

        if len(p) != 1:
            raise FatalError('Expected status, got: %s' % hexify(p))

        status_code = struct.unpack('<B', p)[0]

        if status_code != 0:
            raise FatalError('Boot failure, status: %x' % status_code)

    def flash_erase_chip(self):
        self._esp.write(struct.pack('<B', self.CMD_FLASH_ERASE_CHIP))
        otimeout = self._esp._port.timeout
        self._esp._port.timeout = 60
        p = self._esp.read()
        self._esp._port.timeout = otimeout

        if len(p) != 1:
            raise FatalError('Expected status, got: %s' % hexify(p))

        status_code = struct.unpack('<B', p)[0]

        if status_code != 0:
            raise FatalError('Erase chip failure, status: %x' % status_code)


def slip_reader(port):
    """Generator to read SLIP packets from a serial port.
    Yields one full SLIP packet at a time, raises exception on timeout or invalid data.

    Designed to avoid too many calls to serial.read(1), which can bog
    down on slow systems.
    """
    partial_packet = None
    in_escape = False

    while True:
        waiting = port.inWaiting()
        read_bytes = port.read(1 if waiting == 0 else waiting)

        if read_bytes == b'':
            raise FatalError("Timed out waiting for packet %s" % ("header" if partial_packet is None else "content"))

        for b in read_bytes:
            b = bytes([b])

            if partial_packet is None:  # waiting for packet header
                if b == b'\xc0':
                    partial_packet = b''
                else:
                    raise FatalError('Invalid head of packet (%r)' % b)
            elif in_escape:  # part-way through escape sequence
                in_escape = False

                if b == b'\xdc':
                    partial_packet += b'\xc0'
                elif b == b'\xdd':
                    partial_packet += b'\xdb'
                else:
                    raise FatalError('Invalid SLIP escape (%r%r)' % (b'\xdb', b))
            elif b == b'\xdb':  # start of escape sequence
                in_escape = True
            elif b == b'\xc0':  # end of packet
                yield partial_packet
                partial_packet = None
            else:  # normal byte in packet
                partial_packet += b


def hexify(s):
    if isinstance(s, str):
        return ''.join('%02X' % ord(c) for c in s)

    return ''.join('%02X' % c for c in s)


def unhexify(hs):
    s = []

    for i in range(0, len(hs) - 1, 2):
        s.append(int(hs[i] + hs[i + 1], 16))

    return bytes(s)


class FatalError(RuntimeError):
    """
    Wrapper class for runtime errors that aren't caused by internal bugs, but by
    ESP8266 responses or input content.
    """
    @staticmethod
    def WithResult(message, result):
        """
        Return a fatal error object that includes the hex values of
        'result' as a string formatted argument.
        """
        return FatalError(message.format(", ".join(hex(ord(x))) for x in result))


# This is "wrapped" stub_flasher.c, to  be loaded using run_stub.
_CESANTA_FLASHER_STUB = """\
{"code_start": 1074790404, "code": "080000601C000060000000601000006031FCFF71FCFF\
81FCFFC02000680332D218C020004807404074DCC48608005823C0200098081BA5A9239245005803\
1B555903582337350129230B446604DFC6F3FF21EEFFC0200069020DF0000000010078480040004A\
0040B449004012C1F0C921D911E901DD0209312020B4ED033C2C56C2073020B43C3C56420701F5FF\
C000003C4C569206CD0EEADD860300202C4101F1FFC0000056A204C2DCF0C02DC0CC6CCAE2D1EAFF\
0606002030F456D3FD86FBFF00002020F501E8FFC00000EC82D0CCC0C02EC0C73DEB2ADC46030020\
2C4101E1FFC00000DC42C2DCF0C02DC056BCFEC602003C5C8601003C6C4600003C7C08312D0CD811\
C821E80112C1100DF0000C180000140010400C0000607418000064180000801800008C1800008418\
0000881800009018000018980040880F0040A80F0040349800404C4A0040740F0040800F0040980F\
00400099004012C1E091F5FFC961CD0221EFFFE941F9310971D9519011C01A223902E2D1180C0222\
6E1D21E4FF31E9FF2AF11A332D0F42630001EAFFC00000C030B43C2256A31621E1FF1A2228022030\
B43C3256B31501ADFFC00000DD023C4256ED1431D6FF4D010C52D90E192E126E0101DDFFC0000021\
D2FF32A101C020004802303420C0200039022C0201D7FFC00000463300000031CDFF1A333803D023\
C03199FF27B31ADC7F31CBFF1A3328030198FFC0000056C20E2193FF2ADD060E000031C6FF1A3328\
030191FFC0000056820DD2DD10460800000021BEFF1A2228029CE231BCFFC020F51A33290331BBFF\
C02C411A332903C0F0F4222E1D22D204273D9332A3FFC02000280E27B3F721ABFF381E1A2242A400\
01B5FFC00000381E2D0C42A40001B3FFC0000056120801B2FFC00000C02000280EC2DC0422D2FCC0\
2000290E01ADFFC00000222E1D22D204226E1D281E22D204E7B204291E860000126E012198FF32A0\
042A21C54C003198FF222E1D1A33380337B202C6D6FF2C02019FFFC000002191FF318CFF1A223A31\
019CFFC00000218DFF1C031A22C549000C02060300003C528601003C624600003C72918BFF9A1108\
71C861D851E841F83112C1200DF00010000068100000581000007010000074100000781000007C10\
0000801000001C4B0040803C004091FDFF12C1E061F7FFC961E941F9310971D9519011C01A662906\
21F3FFC2D1101A22390231F2FF0C0F1A33590331EAFFF26C1AED045C2247B3028636002D0C016DFF\
C0000021E5FF41EAFF2A611A4469040622000021E4FF1A222802F0D2C0D7BE01DD0E31E0FF4D0D1A\
3328033D0101E2FFC00000561209D03D2010212001DFFFC000004D0D2D0C3D01015DFFC0000041D5\
FFDAFF1A444804D0648041D2FF1A4462640061D1FF106680622600673F1331D0FF10338028030C43\
853A002642164613000041CAFF222C1A1A444804202FC047328006F6FF222C1A273F3861C2FF222C\
1A1A6668066732B921BDFF3D0C1022800148FFC0000021BAFF1C031A2201BFFFC000000C02460300\
5C3206020000005C424600005C5291B7FF9A110871C861D851E841F83112C1200DF0B0100000C010\
0000D010000012C1E091FEFFC961D951E9410971F931CD039011C0ED02DD0431A1FF9C1422A06247\
B302062D0021F4FF1A22490286010021F1FF1A223902219CFF2AF12D0F011FFFC00000461C0022D1\
10011CFFC0000021E9FFFD0C1A222802C7B20621E6FF1A22F8022D0E3D014D0F0195FFC000008C52\
22A063C6180000218BFF3D01102280F04F200111FFC00000AC7D22D1103D014D0F010DFFC0000021\
D6FF32D110102280010EFFC0000021D3FF1C031A220185FFC00000FAEEF0CCC056ACF821CDFF317A\
FF1A223A310105FFC0000021C9FF1C031A22017CFFC000002D0C91C8FF9A110871C861D851E841F8\
3112C1200DF0000200600000001040020060FFFFFF0012C1E00C02290131FAFF21FAFF026107C961\
C02000226300C02000C80320CC10564CFF21F5FFC02000380221F4FF20231029010C432D010163FF\
C0000008712D0CC86112C1200DF00080FE3F8449004012C1D0C9A109B17CFC22C1110C13C51C0026\
1202463000220111C24110B68202462B0031F5FF3022A02802A002002D011C03851A0066820A2801\
32210105A6FF0607003C12C60500000010212032A01085180066A20F2221003811482105B3FF2241\
10861A004C1206FDFF2D011C03C5160066B20E280138114821583185CFFF06F7FF005C1286F5FF00\
10212032A01085140066A20D2221003811482105E1FF06EFFF0022A06146EDFF45F0FFC6EBFF0000\
01D2FFC0000006E9FF000C022241100C1322C110C50F00220111060600000022C1100C13C50E0022\
011132C2FA303074B6230206C8FF08B1C8A112C1300DF0000000000010404F484149007519031027\
000000110040A8100040BC0F0040583F0040CC2E00401CE20040D83900408000004021F4FF12C1E0\
C961C80221F2FF097129010C02D951C91101F4FFC0000001F3FFC00000AC2C22A3E801F2FFC00000\
21EAFFC031412A233D0C01EFFFC000003D0222A00001EDFFC00000C1E4FF2D0C01E8FFC000002D01\
32A004450400C5E7FFDD022D0C01E3FFC00000666D1F4B2131DCFF4600004B22C0200048023794F5\
31D9FFC0200039023DF08601000001DCFFC000000871C861D85112C1200DF000000012C1F0026103\
01EAFEC00000083112C1100DF000643B004012C1D0E98109B1C9A1D991F97129013911E2A0C001FA\
FFC00000CD02E792F40C0DE2A0C0F2A0DB860D00000001F4FFC00000204220E71240F7921C226102\
01EFFFC0000052A0DC482157120952A0DD571205460500004D0C3801DA234242001BDD3811379DC5\
C6000000000C0DC2A0C001E3FFC00000C792F608B12D0DC8A1D891E881F87112C1300DF00000", "\
entry": 1074792180, "num_params": 1, "params_start": 1074790400, "data": "FE0510\
401A0610403B0610405A0610407A061040820610408C0610408C061040", "data_start": 10736\
43520}
"""


from zipfile import ZipFile
from threading import Thread

from io import BytesIO as FileLike

from queue import Queue, Empty

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
        if len(self.read_buffer) < length:
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

        return bytes(ret)

    def inWaiting(self):
        return len(self.read_buffer)

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
        q = Queue()

        def run():
            try:
                files = []
                zf = ZipFile(FileLike(firmware), 'r')

                for name in zf.namelist():
                    files.append((int(name.replace('.bin', ''), 0), name))

                esp = ESPROM(self.master)
                esp.connect()

                flasher = CesantaFlasher(esp, ESPROM.ESP_ROM_BAUD)

                flash_mode = 0 # QIO
                flash_size_freq = 0x40 # flash size 4MB (0x4_) + flash freq 40m (0x_0)
                flash_info = struct.pack('BB', flash_mode, flash_size_freq)

                for i, f in enumerate(files):
                    address = f[0]
                    image = zf.read(f[1])

                    # Fix sflash config data
                    if address == 0 and image.startswith(b'\xe9'):
                        image = image[0:2] + flash_info + image[4:]

                    # Pad to sector size
                    if len(image) % esp.ESP_FLASH_SECTOR != 0:
                        image += b'\xff' * (esp.ESP_FLASH_SECTOR - (len(image) % esp.ESP_FLASH_SECTOR))

                    q.put(('reset', ('Writing flash section {0} of {1}'.format(i + 1, len(files)), len(image) // esp.ESP_FLASH_BLOCK)))

                    flasher.flash_write(address, image, lambda value: q.put(('update', (value,))))

                    q.put(('update', (len(image) // esp.ESP_FLASH_BLOCK,)))

                flasher.boot_fw()
            except Exception as e:
                q.put(('raise', e))

            q.put(('quit',))

        t = Thread(target=run)
        t.daemon = True
        t.start()

        while True:
            try:
                message = q.get(True, 0.025)
            except Empty:
                self.update_progress(None)
                continue

            if message[0] == 'quit':
                break
            elif message[0] == 'raise':
                raise message[1]
            elif message[0] == 'reset':
                self.reset_progress(*message[1])
            elif message[0] == 'update':
                self.update_progress(*message[1])

        t.join()
