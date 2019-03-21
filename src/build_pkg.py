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
#       nsis
#       universal CRT

import sys
if (sys.hexversion & 0xFF000000) != 0x03000000:
    print('Python 3.x required')
    sys.exit(1)

import os
import shutil
import subprocess
from brickv.config import BRICKV_VERSION


def system(command):
    if subprocess.call(command) != 0:
        sys.exit(1)


def specialize_template(template_filename, destination_filename, replacements):
    template_file = open(template_filename, 'r')
    lines = []
    replaced = set()

    for line in template_file.readlines():
        for key in replacements:
            replaced_line = line.replace(key, replacements[key])

            if replaced_line != line:
                replaced.add(key)

            line = replaced_line

        lines.append(line)

    template_file.close()

    if replaced != set(replacements.keys()):
        raise Exception('Not all replacements for {0} have been applied'.format(template_filename))

    try:
        os.makedirs(os.path.dirname(destination_filename))
    except:
        pass
    destination_file = open(destination_filename, 'w+')
    destination_file.writelines(lines)
    destination_file.close()


def prepare_manifest(root_path, no_release=False):
    bindings_path = os.path.join(root_path, 'brickv', 'bindings')
    plugins_path = os.path.join(root_path, 'brickv', 'plugin_system', 'plugins')
    excluded_patterns = []

    if not no_release:
        for plugin_name in sorted(os.listdir(plugins_path)):
            if '__pycache__' in plugin_name:
                continue
            plugin_path = os.path.join(plugins_path, plugin_name)

            if not os.path.isdir(plugin_path):
                continue

            brick_binding = os.path.join(bindings_path, 'brick_{0}.py'.format(plugin_name))
            bricklet_binding = os.path.join(bindings_path, 'bricklet_{0}.py'.format(plugin_name))

            if os.path.isfile(brick_binding):
                with open(brick_binding, 'r') as f:
                    if '#### __DEVICE_IS_NOT_RELEASED__ ####' in f.read():
                        print('excluding unreleased plugin and binding: ' + plugin_name)
                        excluded_patterns.append('prune brickv/plugin_system/plugins/{0}'.format(plugin_name))
                        excluded_patterns.append('recursive-exclude brickv/bindings brick_{0}.py'.format(plugin_name))
            elif os.path.isfile(bricklet_binding):
                with open(bricklet_binding, 'r') as f:
                    if '#### __DEVICE_IS_NOT_RELEASED__ ####' in f.read():
                        print('excluding unreleased plugin and binding: ' + plugin_name)
                        excluded_patterns.append('prune brickv/plugin_system/plugins/{0}'.format(plugin_name))
                        excluded_patterns.append('recursive-exclude brickv/bindings bricklet_{0}.py'.format(plugin_name))
            else:
                raise Exception('No bindings found corresponding to plugin {0}'.format(plugin_name))

    specialize_template(os.path.join(root_path, 'MANIFEST.in.template'), os.path.join(root_path, 'MANIFEST.in'),
                        {'<<EXCLUDES>>': '\n'.join(excluded_patterns)})


def build_linux_pkg(no_release=False):
    print('building brickv Debian package')
    root_path = os.getcwd()

    print('removing old build directories')
    dist_path = os.path.join(root_path, 'dist')
    egg_info_path = os.path.join(root_path, 'brickv.egg-info')

    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)

    if os.path.exists(egg_info_path):
        shutil.rmtree(egg_info_path)

    if no_release:
        print('calling build_src.py')
        system(['python3', 'build_src.py'])
    else:
        print('calling build_src.py release')
        system(['python3', 'build_src.py', 'release'])

    print('preparing manifest')
    prepare_manifest(root_path, no_release)

    print('calling setup.py sdist')
    system(['python3', 'setup.py', 'sdist'])

    if not no_release:
        print('calling build_plugin_list.py to undo previous release run')
        system(['python3', 'build_plugin_list.py'])

    if os.path.exists(egg_info_path):
        shutil.rmtree(egg_info_path)

    print('copying build data')
    build_data_path = os.path.join(root_path, 'build_data', 'linux', 'brickv')
    linux_path = os.path.join(dist_path, 'linux')
    shutil.copytree(build_data_path, linux_path)

    print('unpacking sdist tar file')
    system(['tar', '-x', '-C', dist_path, '-f', '{0}/brickv-{1}.tar.gz'.format(dist_path, BRICKV_VERSION), 'brickv-{}/brickv'.format(BRICKV_VERSION)])

    print('copying unpacked brickv source')
    unpacked_path = os.path.join(dist_path, 'brickv-{0}'.format(BRICKV_VERSION), 'brickv')
    linux_share_path = os.path.join(linux_path, 'usr', 'share', 'brickv')
    shutil.copytree(unpacked_path, linux_share_path)

    print('creating DEBIAN/control from template')
    installed_size = int(subprocess.check_output(['du', '-s', '--exclude', 'dist/linux/DEBIAN', 'dist/linux']).split(b'\t')[0])
    control_path = os.path.join(linux_path, 'DEBIAN', 'control')
    specialize_template(control_path, control_path,
                        {'<<VERSION>>': BRICKV_VERSION,
                         '<<INSTALLED_SIZE>>': str(installed_size)})

    print('changing directory modes to 0755')
    system(['find', 'dist/linux', '-type', 'd', '-exec', 'chmod', '0755', '{}', ';'])

    print('changing file modes')
    system(['find', 'dist/linux', '-type', 'f', '-perm', '664', '-exec', 'chmod', '0644', '{}', ';'])
    system(['find', 'dist/linux', '-type', 'f', '-perm', '775', '-exec', 'chmod', '0755', '{}', ';'])

    print('changing owner to root')
    stat = os.stat('dist/linux')
    user, group = stat.st_uid, stat.st_gid
    system(['sudo', 'chown', '-R', 'root:root', 'dist/linux'])

    print('building Debian package')
    system(['dpkg', '-b', 'dist/linux', 'brickv-{0}_all{1}.deb'.format(BRICKV_VERSION, '_DO_NOT_RELEASE' if no_release else '')])

    print('changing owner back to original user')
    system(['sudo', 'chown', '-R', '{}:{}'.format(user, group), 'dist/linux'])

    if os.path.exists('/usr/bin/lintian'):
        print('checking Debian package')
        system(['lintian', '--pedantic', 'brickv-{0}_all.deb'.format(BRICKV_VERSION)])
    else:
        print('skipping lintian check')


BRICK_FLASH_VERSION = '1.0.1'

def build_linux_flash_pkg():
    print('building brick-flash Debian package')
    root_path = os.getcwd()

    print('removing old build directories')
    dist_path = os.path.join(root_path, 'dist')

    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)

    os.makedirs(dist_path)

    print('copying build data')
    build_data_path = os.path.join(root_path, 'build_data', 'linux', 'brick-flash')
    linux_path = os.path.join(dist_path, 'linux')
    shutil.copytree(build_data_path, linux_path)

    print('creating brick-flash from template')
    with open(os.path.join(root_path, 'brickv', 'brick-flash.template'), 'r') as f:
        template = f.read()

    with open(os.path.join(root_path, 'brickv', 'samba.py'), 'r') as f:
        samba_lines = f.readlines()

    while len(samba_lines) > 0 and not samba_lines[0].startswith('#### skip here for brick-flash ####'):
        del samba_lines[0]

    if len(samba_lines) > 0 and samba_lines[0].startswith('#### skip here for brick-flash ####'):
        del samba_lines[0]

    template = template.replace('<<VERSION>>', BRICK_FLASH_VERSION).replace('#### insert samba module here ####', ''.join(samba_lines))

    os.makedirs(os.path.join(linux_path, 'usr', 'bin'))

    with open(os.path.join(linux_path, 'usr', 'bin', 'brick-flash'), 'w') as f:
        f.write(template)

    print('creating DEBIAN/control from template')
    installed_size = int(subprocess.check_output(['du', '-s', '--exclude', 'dist/linux/DEBIAN', 'dist/linux']).split(b'\t')[0])
    control_path = os.path.join(linux_path, 'DEBIAN', 'control')
    specialize_template(control_path, control_path,
                        {'<<VERSION>>': BRICK_FLASH_VERSION,
                         '<<INSTALLED_SIZE>>': str(installed_size)})

    print('changing binary and directory modes to 0755')
    system(['chmod', '0755', 'dist/linux/usr/bin/brick-flash'])
    system(['find', 'dist/linux', '-type', 'd', '-exec', 'chmod', '0755', '{}', ';'])

    print('changing file modes')
    system(['find', 'dist/linux', '-type', 'f', '-perm', '664', '-exec', 'chmod', '0644', '{}', ';'])
    system(['find', 'dist/linux', '-type', 'f', '-perm', '775', '-exec', 'chmod', '0755', '{}', ';'])

    print('changing owner to root')
    stat = os.stat('dist/linux')
    user, group = stat.st_uid, stat.st_gid
    system(['sudo', 'chown', '-R', 'root:root', 'dist/linux'])

    print('building Debian package')
    system(['dpkg', '-b', 'dist/linux', 'brick-flash-{0}_all.deb'.format(BRICK_FLASH_VERSION)])

    print('changing owner back to original user')
    system(['sudo', 'chown', '-R', '{}:{}'.format(user, group), 'dist/linux'])

    if os.path.exists('/usr/bin/lintian'):
        print('checking Debian package')
        system(['lintian', '--pedantic', 'brick-flash-{0}_all.deb'.format(BRICK_FLASH_VERSION)])
    else:
        print('skipping lintian check')


BRICK_LOGGER_VERSION = '2.0.9'

def build_logger_zip():
    print('building brick-logger ZIP file')
    root_path = os.getcwd()

    print('removing old build directories')
    dist_path = os.path.join(root_path, 'dist')

    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)

    os.makedirs(dist_path)

    print('creating brick-logger.py from template')
    with open(os.path.join(root_path, 'brickv', 'data_logger', 'brick-logger.py.template'), 'r') as f:
        template = f.read()

    template = template.replace('<<VERSION>>', BRICK_LOGGER_VERSION)

    for module in ['configuration', 'data_logger', 'event_logger', 'loggable_devices', 'job', 'main', 'utils']:
        with open(os.path.join(root_path, 'brickv', 'data_logger', module + '.py'), 'r') as f:
            lines = f.readlines()

        while len(lines) > 0 and not lines[0].startswith('#### skip here for brick-logger ####'):
            del lines[0]

        if len(lines) > 0 and lines[0].startswith('#### skip here for brick-logger ####'):
            del lines[0]

        template = template.replace('#### insert {0} module here ####'.format(module), ''.join(lines))

    with open(os.path.join(dist_path, 'brick-logger.py'), 'w') as f:
        f.write(template)

    print('changing brick-logger.py mode to 0755')
    system(['chmod', '0755', 'dist/brick-logger.py'])

    print('building ZIP file')
    zip_name = 'brick_logger_{0}.zip'.format(BRICK_LOGGER_VERSION.replace('.', '_'))

    if os.path.exists(zip_name):
        os.remove(zip_name)

    os.chdir(dist_path)
    system(['zip', '-q', '../{}'.format(zip_name), 'brick-logger.py'])

# run 'python build_pkg.py' to build the windows/linux/macos package
if __name__ == '__main__':
    if sys.platform != 'win32' and os.geteuid() == 0:
        print('error: must not be started as root, exiting')
        sys.exit(1)

    if 'logger' in sys.argv:
        build_logger_zip()
    elif sys.platform.startswith('linux') and '--no-deb' not in sys.argv:
        if 'flash' in sys.argv:
            build_linux_flash_pkg()
        else:
            build_linux_pkg(no_release='--no-release' in sys.argv)
    elif sys.platform == 'win32' or sys.platform == 'darwin' or '--no-deb' in sys.argv:
        if '--no-deb' not in sys.argv:
            in_virtualenv = hasattr(sys, 'real_prefix')
            in_pyvenv = hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix

            if not in_virtualenv and not in_pyvenv:
                print('error: Please build Windows or macOS binaries in the correct virtualenv.')
                sys.exit(1)

        root_path = os.getcwd()
        os.chdir(os.path.join(root_path, 'brickv'))
        system(['pyinstaller', '--distpath', '../dist', '--workpath', '../build', 'main_folder.spec', '--'] + sys.argv)
        os.chdir(root_path)
    else:
        print('error: unsupported platform: ' + sys.platform)
        sys.exit(1)

    print('done')
