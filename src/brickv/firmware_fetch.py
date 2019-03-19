# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2019 Erik Fleckstein <erik@tinkerforge.com>

firmware_fetch.py: General latest_versions.txt handling

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

import urllib
import threading

from PyQt5.QtCore import QObject, pyqtSignal

from brickv import infos

LATEST_VERSIONS_URL = 'http://download.tinkerforge.com/latest_versions.txt'

ERROR_DOWNLOAD = 1
ERROR_PARSE_SPLIT = 2
ERROR_PARSE_VERSION_SPLIT = 3
ERROR_PARSE_VERSION_INTS = 4
ERROR_SERVER_ERROR = 5

def refresh_firmware_info(url_part, latest_version):
    name = url_part

    if name.endswith('_v2'):
        name = name.replace('_v2', '_2.0')
    elif name.endswith('_v3'):
        name = name.replace('_v3', '_3.0')

    if name in ['dc', 'imu', 'imu_2.0']:
        name = name.upper()

    words = name.split('_')
    parts = []

    for word in words:
        parts.append(word[0].upper() + word[1:])

    name = ' '.join(parts)

    firmware_info = infos.FirmwareInfo()
    firmware_info.name = name
    firmware_info.url_part = url_part
    firmware_info.firmware_version_latest = latest_version

    return firmware_info

def refresh_plugin_info(url_part, latest_version):
    name = url_part

    if name.endswith('_v2'):
        name = name.replace('_v2', '_2.0')
    elif name.endswith('_v3'):
        name = name.replace('_v3', '_3.0')

    if name in ['gps', 'gps_2.0', 'ptc', 'ptc_2.0', 'rs232', 'rs232_2.0', 'rs485', 'co2', 'can', 'can_2.0', 'rgb_led', 'dmx', 'nfc']:
        name = name.upper()
    elif name.startswith('lcd_'):
        name = name.replace('lcd_', 'LCD_')
        if url_part.startswith('lcd_20x4_'):
            name = name.replace('_v11', '_1.1').replace('_v12', '_1.2')
    elif name.startswith('io'):
        name = name.replace('io', 'IO-')
    elif name.endswith('_ir'):
        name = name.replace('_ir', '_IR')
    elif name.endswith('_ir_2.0'):
        name = name.replace('_ir_2.0', '_IR_2.0')
    elif name.endswith('_us'):
        name = name.replace('_us', '_US')
    elif name.endswith('_us_2.0'):
        name = name.replace('_us_2.0', '_US_2.0')
    elif name.startswith('led_'):
        name = name.replace('led_', 'LED_')
    elif name.startswith('oled_'):
        name = name.replace('oled_', 'OLED_')
    elif name.startswith('uv_'):
        name = name.replace('uv_', 'UV_')
    elif name.startswith('rgb_led_'):
        name = name.replace('rgb_led_', 'RGB_LED_')
    elif name.startswith('rgb_'):
        name = name.replace('rgb_', 'RGB_')
    elif name.startswith('midi_'):
        name = name.replace('midi_', 'MIDI_')

    words = name.split('_')
    parts = []

    for word in words:
        parts.append(word[0].upper() + word[1:])

    name = ' '.join(parts)
    name = name.replace('Voltage Current', 'Voltage/Current')
    name = name.replace('Nfc Rfid', 'NFC/RFID')
    name = name.replace('0 20ma', '0-20mA')
    name = name.replace('Real Time', 'Real-Time')

    plugin_info = infos.PluginInfo()
    plugin_info.name = name
    plugin_info.url_part = url_part
    plugin_info.firmware_version_latest = latest_version

    return plugin_info

def refresh_extension_firmware_info(url_part, latest_version):
    name = url_part

    if name.endswith('_v2'):
        name = name.replace('_v2', '_2.0')
    elif name.endswith('_v3'):
        name = name.replace('_v3', '_3.0')

    if name in ['wifi_2.0']:
        name = name.upper()

    words = name.split('_')
    parts = []

    for word in words:
        parts.append(word[0].upper() + word[1:])

    name = ' '.join(parts)

    extension_firmware_info = infos.ExtensionFirmwareInfo()
    extension_firmware_info.name = name
    extension_firmware_info.url_part = url_part
    extension_firmware_info.firmware_version_latest = latest_version

    return extension_firmware_info

def refresh_red_image_info(url_part, latest_version):
    red_image_info = infos.BrickREDInfo()
    red_image_info.name = "RED Brick Image (" + url_part + ")"
    red_image_info.url_part = url_part
    red_image_info.firmware_version_latest = latest_version

    return red_image_info



# Returns None if the binding is not supported on the red brick
def refresh_binding_info(url_part, latest_version):
    red_image_info = infos.BindingInfo()
    red_image_info.name = infos.get_bindings_name(url_part)
    if red_image_info.name is None:
        return None
    red_image_info.url_part = url_part
    red_image_info.firmware_version_latest = latest_version

    return red_image_info

def fetch_latest_fw_versions(report_error_fn):
    result = infos.LatestFirmwares({}, {}, {}, {}, {}, {})
    try:
        response = urllib.request.urlopen(LATEST_VERSIONS_URL, timeout=10)
        latest_versions_data = response.read().decode('utf-8')
        response.close()
    except urllib.error.HTTPError:
        report_error_fn(ERROR_SERVER_ERROR)
    except urllib.error.URLError:
        report_error_fn(ERROR_DOWNLOAD)
        return None

    for line in latest_versions_data.split('\n'):
        line = line.strip()

        if len(line) < 1:
            continue

        parts = line.split(':')

        if len(parts) != 3:
            report_error_fn(ERROR_PARSE_SPLIT)
            return None

        latest_version_parts = parts[2].split('.')

        if len(latest_version_parts) != 3:
            report_error_fn(ERROR_PARSE_VERSION_SPLIT)
            return None

        try:
            latest_version = int(latest_version_parts[0]), int(latest_version_parts[1]), int(latest_version_parts[2])
        except:
            report_error_fn(ERROR_PARSE_VERSION_INTS)
            return None

        if parts[0] == 'tools':
            tool_info = infos.ToolInfo()
            tool_info.firmware_version_latest = latest_version

            result.tool_infos[parts[1]] = tool_info
        elif parts[0] == 'bricks':
            result.firmware_infos[parts[1]] = refresh_firmware_info(parts[1], latest_version)
        elif parts[0] == 'bricklets':
            result.plugin_infos[parts[1]] = refresh_plugin_info(parts[1], latest_version)
        elif parts[0] == 'extensions':
            result.extension_firmware_infos[parts[1]] = refresh_extension_firmware_info(parts[1], latest_version)
        elif parts[0] == 'red_images':
            result.red_image_infos[parts[1]] = refresh_red_image_info(parts[1], latest_version)
        elif parts[0] == 'bindings':
            info = refresh_binding_info(parts[1], latest_version)
            if info is not None:
                result.binding_infos[parts[1]] = info
    return result

class LatestFWVersionFetcher(QObject):
    fw_versions_avail = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._abort = False
        self.sleep_event = threading.Event()

    def run(self):
        while not self._abort:
            new_data = fetch_latest_fw_versions(self.fw_versions_avail.emit)
            if new_data is not None:
                self.fw_versions_avail.emit(new_data)

            self.sleep_event.clear()
            self.sleep_event.wait(60 * 60)

        self.finished.emit()

    def fetch_now(self):
        if self._abort:
            new_data = fetch_latest_fw_versions(self.fw_versions_avail.emit)
            if new_data is not None:
                self.fw_versions_avail.emit(new_data)
        else:
            self.sleep_event.set()

    def abort(self):
        self._abort = True
        self.sleep_event.set()

    def reset(self):
        self._abort = False
        self.sleep_event = threading.Event()
