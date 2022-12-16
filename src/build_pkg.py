#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012-2015 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2011 Bastian Nordmeyer <bastian@tinkerforge.com>

build_pkg.py: Package builder for Brick Viewer

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

# Windows:
#   dependencies:
#       python
#       pyinstaller
#       PyQt5
#       pyserial
#       pytz
#       nsis
#       universal CRT

import sys
if (sys.hexversion & 0xFF000000) != 0x03000000:
    print('Python 3.x required')
    sys.exit(1)

import os
import shutil
import subprocess

from build_pkg_utils import *
from brickv.config import BRICKV_VERSION

def remove_unreleased_plugins(utils):
    bindings_path = os.path.join(utils.unpacked_source_path, 'bindings')
    plugins_path = os.path.join(utils.unpacked_source_path, 'plugin_system', 'plugins')

    if not utils.internal:
        for plugin_name in sorted(os.listdir(plugins_path)):
            if '__pycache__' in plugin_name:
                continue

            plugin_path = os.path.join(plugins_path, plugin_name)

            if not os.path.isdir(plugin_path):
                continue

            for prefix in ['brick_', 'bricklet_', '']: # empty prefix for TNG
                binding_path = os.path.join(bindings_path, '{0}{1}.py'.format(prefix, plugin_name))

                try:
                    with open(binding_path, 'r') as f:
                        binding_data = f.read()
                except FileNotFoundError:
                    continue

                if '#### __DEVICE_IS_NOT_RELEASED__ ####' in binding_data:
                    print('removing unreleased plugin and binding: ' + plugin_name)

                    shutil.rmtree(plugin_path)
                    os.remove(binding_path)

                break
            else:
                raise Exception('No bindings found corresponding to plugin {0}'.format(plugin_name))

        for binding_name in sorted(os.listdir(bindings_path)):
            if '__pycache__' in binding_name or 'unknown' in binding_name:
                continue

            if binding_name.startswith('brick_') or binding_name.startswith('bricklet_') or binding_name.startswith('tng_'):
                binding_path = os.path.join(bindings_path, binding_name)

                try:
                    with open(binding_path, 'r') as f:
                        binding_data = f.read()
                except FileNotFoundError:
                    continue

                if '#### __DEVICE_IS_NOT_RELEASED__ ####' in binding_data:
                    print('removing unreleased binding: ' + binding_name)

                    os.remove(binding_path)

def write_marker_files_and_patch_plugins(utils):
    package_type = {'linux': 'deb', 'macos': 'dmg', 'windows': 'exe'}[utils.platform]
    with open(os.path.join(utils.unpacked_source_path, 'package_type'), 'w') as f:
        f.write(package_type)

    if utils.internal:
        kind = 'internal'
        commit_id = get_commit_id()

        with open(os.path.join(utils.unpacked_source_path, 'internal'), 'w') as f:
            f.write(commit_id)
    else:
        if utils.snapshot:
            kind = 'snapshot'
            commit_id = get_commit_id()

            with open(os.path.join(utils.unpacked_source_path, 'snapshot'), 'w') as f:
                f.write(commit_id)
        else:
            kind = None
            commit_id = None

        print('patching plugins list for release')

        shutil.copy(os.path.join(utils.root_path, 'released_plugins.py'), os.path.join(utils.unpacked_source_path, 'plugin_system', 'plugins', '__init__.py'))

    if kind != None:
        utils.version = BRICKV_VERSION + '+' + kind + '~' + commit_id

def build_linux_pkg():
    print('building brickv Debian package')

    utils = BuildPkgUtils('brickv', 'linux', BRICKV_VERSION)

    utils.run_sdist(prepare_script=os.path.join(utils.root_path, 'build_src.py'))
    utils.copy_build_data()
    utils.unpack_sdist()

    remove_unreleased_plugins(utils)
    write_marker_files_and_patch_plugins(utils)

    utils.build_debian_pkg()
    utils.copy_build_artifact()

def build_pyinstaller_pkg():
    platform_dict = {'win32': 'windows', 'darwin': 'macos'}

    utils = BuildPkgUtils('brickv', platform_dict[sys.platform], BRICKV_VERSION)

    utils.exit_if_not_venv()
    utils.build_pyinstaller_pkg(prepare_script=os.path.join(utils.root_path, 'build_src.py'),
                                pre_pyinstaller=lambda: [remove_unreleased_plugins(utils), write_marker_files_and_patch_plugins(utils), utils.copy_build_data()])
    utils.copy_build_artifact()

BRICK_FLASH_VERSION = '1.0.2'

def build_linux_flash_pkg():
    print('building brick-flash Debian package')

    utils = BuildPkgUtils('brick-flash', 'linux', BRICK_FLASH_VERSION)

    print('removing old build directories')

    if os.path.exists(utils.dist_path):
        shutil.rmtree(utils.dist_path)

    os.makedirs(utils.dist_path)

    utils.copy_build_data()

    print('creating brick-flash from template')
    os.makedirs(os.path.join(utils.build_data_dest_path, 'usr', 'bin'), exist_ok=True)

    with open(os.path.join(utils.root_path, 'brickv', 'samba.py'), 'r') as f:
        samba_lines = f.readlines()

    while len(samba_lines) > 0 and not samba_lines[0].startswith('#### skip here for brick-flash ####'):
        del samba_lines[0]

    if len(samba_lines) > 0 and samba_lines[0].startswith('#### skip here for brick-flash ####'):
        del samba_lines[0]

    specialize_template(os.path.join(utils.root_path, 'brickv', 'brick-flash.template'),
                        os.path.join(utils.build_data_dest_path, 'usr', 'bin', 'brick-flash'),
                        {'<<VERSION>>': BRICK_FLASH_VERSION,
                         '#### insert samba module here ####': ''.join(samba_lines)})

    print('changing binary mode to 0755')
    system(['chmod', '0755', os.path.join(utils.build_data_dest_path, 'usr', 'bin', 'brick-flash')])

    utils.build_debian_pkg()

BRICK_LOGGER_VERSION = '2.1.9'

def build_logger_zip():
    print('building brick-logger ZIP file')

    utils = BuildPkgUtils('brick-logger', 'linux', BRICK_LOGGER_VERSION)

    print('removing old build directories')

    if os.path.exists(utils.dist_path):
        shutil.rmtree(utils.dist_path)

    os.makedirs(utils.dist_path)

    print('creating brick-logger.py from template')

    replacements = {'<<VERSION>>': BRICK_LOGGER_VERSION}

    for module in ['configuration', 'data_logger', 'event_logger', 'loggable_devices', 'job', 'main', 'utils']:
        with open(os.path.join(utils.root_path, 'brickv', 'data_logger', module + '.py'), 'r') as f:
            lines = f.readlines()

        while len(lines) > 0 and not lines[0].startswith('#### skip here for brick-logger ####'):
            del lines[0]

        if len(lines) > 0 and lines[0].startswith('#### skip here for brick-logger ####'):
            del lines[0]
        replacements['#### insert {0} module here ####'.format(module)] = ''.join(lines)

    specialize_template(os.path.join(utils.root_path, 'brickv', 'data_logger', 'brick-logger.py.template'),
                        os.path.join(utils.dist_path, 'brick-logger.py'),
                        replacements)

    print('changing brick-logger.py mode to 0755')
    system(['chmod', '0755', 'dist/brick-logger.py'])

    print('building ZIP file')

    zip_name = 'brick_logger_{0}.zip'.format(BRICK_LOGGER_VERSION.replace('.', '_'))

    if os.path.exists(zip_name):
        os.remove(zip_name)

    os.chdir(utils.dist_path)
    system(['zip', '-q', '../{}'.format(zip_name), 'brick-logger.py'])

def main():
    if sys.platform != 'win32' and os.geteuid() == 0:
        print('error: must not be started as root, exiting')
        return 1

    if 'logger' in sys.argv:
        build_logger_zip()
        return 0

    if sys.platform.startswith('linux') and 'flash' in sys.argv:
        build_linux_flash_pkg()
        return 0

    if sys.platform.startswith('linux'):
        build_linux_pkg()
        return 0

    if sys.platform == 'win32' or sys.platform == 'darwin':
        build_pyinstaller_pkg()
        return 0

    print('error: unsupported platform: ' + sys.platform)
    return 1

# run 'python build_pkg.py' to build the windows/linux/macos package
if __name__ == '__main__':
    exit_code = main()

    if exit_code == 0:
        print('done')

    sys.exit(exit_code)
