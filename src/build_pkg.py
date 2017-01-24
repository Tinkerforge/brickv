#!/usr/bin/env python
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
#       pythonxy (2.6)
#       py2exe
#       nsis
#       win redistributables vcredist under winxp

import sys
if (sys.hexversion & 0xFF000000) != 0x02000000:
    print 'Python 2.x required'
    sys.exit(1)

import os
import base64
import shutil
import struct
import subprocess
from brickv.config import BRICKV_VERSION


def system(command):
    if os.system(command) != 0:
        sys.exit(1)


def check_output(*args, **kwargs):
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden')

    process = subprocess.Popen(stdout=subprocess.PIPE, *args, **kwargs)
    output, error = process.communicate()
    exit_code = process.poll()

    if exit_code != 0:
        command = kwargs.get('args')

        if command == None:
            command = args[0]

        raise subprocess.CalledProcessError(exit_code, command, output=output)

    return output


def specialize_template(template_filename, destination_filename, replacements):
    template_file = open(template_filename, 'rb')
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

    destination_file = open(destination_filename, 'wb')
    destination_file.writelines(lines)
    destination_file.close()


def prepare_manifest(root_path):
    bindings_path = os.path.join(root_path, 'brickv', 'bindings')
    plugins_path = os.path.join(root_path, 'brickv', 'plugin_system', 'plugins')
    excluded_patterns = []

    for plugin_name in sorted(os.listdir(plugins_path)):
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
            raise Exception('No bindings found corresponding to plugin {0}'.format(plugin))

    specialize_template('MANIFEST.in.template', 'MANIFEST.in',
                        {'<<EXCLUDES>>': '\n'.join(excluded_patterns)})


def freeze_images():
    directory = 'brickv'
    image_files = []

    for root, dirnames, names in os.walk(directory):
        for name in names:
            full_name = os.path.join(root, name)

            if os.path.isfile(full_name):
                _, ext = os.path.splitext(name)
                ext = ext[1:]

                if ext in ['bmp', 'png', 'jpg']:
                    image_files.append([full_name.replace('\\', '/').replace(directory + '/', ''), ext])

    images = open(os.path.join(directory, 'frozen_images.py'), 'wb')
    images.write('image_data = {\n'.encode('utf-8'))

    for image_file in image_files:
        image_data = base64.b64encode(file(os.path.join(directory, image_file[0]), 'rb').read())
        images.write("'{0}': ['{1}', '{2}'],\n".format(image_file[0], image_file[1], image_data).encode('utf-8'))

    images.write('}\n'.encode('utf-8'))
    images.close()


def build_macosx_pkg():
    print('building brickv disk image')
    root_path = os.getcwd()

    print('removing old build directories')
    build_path = os.path.join(root_path, 'build')
    dist_path = os.path.join(root_path, 'dist')

    if os.path.exists(build_path):
        shutil.rmtree(build_path)

    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)

    print('freezing images')
    freeze_images()

    print('calling build_all_ui.py release')
    system('python build_all_ui.py release')

    print('preparing manifest')
    prepare_manifest(root_path)

    print('calling setup.py py2app build')
    system('python setup.py py2app build')

    print('calling build_plugin_list.py to undo previous release run')
    system('python build_plugin_list.py')

    print('copying build data')
    build_data_path = os.path.join(root_path, 'build_data', 'macosx', '*')
    resources_path = os.path.join(dist_path, 'Brickv.app', 'Contents', 'Resources')
    system('cp -R {0} {1}'.format(build_data_path, resources_path))

    print('patching __boot__.py')
    boot_path = os.path.join(resources_path, '__boot__.py')
    boot_prefix = 'import os\nimport sys\nos.environ["RESOURCEPATH"] = os.path.dirname(os.path.realpath(__file__))\n'

    with open(boot_path, 'rb') as f:
        boot = f.read()

    with open(boot_path, 'wb') as f:
        f.write(boot_prefix + boot)

    print('signing brickv binary')
    system('security unlock-keychain /Users/$USER/Library/Keychains/login.keychain')
    # NOTE: codesign_identity contains "Developer ID Application: ..."
    codesign_command = 'codesign --force --verify --verbose --sign "`cat codesign_identity`" {0}'
    frameworks_path = os.path.join(dist_path, 'Brickv.app', 'Contents', 'Frameworks')
    qtcore_framework = os.path.join(frameworks_path, 'QtCore.framework')
    qtgui_framework = os.path.join(frameworks_path, 'QtGui.framework')
    qtopengl_framework = os.path.join(frameworks_path, 'QtOpenGL.framework')

    os.unlink(os.path.join(qtcore_framework, 'QtCore'))
    shutil.move(os.path.join(qtcore_framework, 'QtCore.prl'), os.path.join(qtcore_framework, 'Versions', 'Current'))
    shutil.move(os.path.join(qtcore_framework, 'Contents'), os.path.join(qtcore_framework, 'Versions', 'Current'))

    os.unlink(os.path.join(qtgui_framework, 'QtGui'))
    os.unlink(os.path.join(qtgui_framework, 'Resources'))
    shutil.move(os.path.join(qtgui_framework, 'QtGui.prl'), os.path.join(qtgui_framework, 'Versions', 'Current'))
    shutil.move(os.path.join(qtgui_framework, 'Contents'), os.path.join(qtgui_framework, 'Versions', 'Current'))

    os.unlink(os.path.join(qtopengl_framework, 'QtOpenGL'))
    shutil.move(os.path.join(qtopengl_framework, 'QtOpenGL.prl'), os.path.join(qtopengl_framework, 'Versions', 'Current'))
    shutil.move(os.path.join(qtopengl_framework, 'Contents'), os.path.join(qtopengl_framework, 'Versions', 'Current'))

    system(codesign_command.format(os.path.join(frameworks_path, 'Python.framework')))
    system(codesign_command.format(os.path.join(frameworks_path, 'QtCore.framework')))
    system(codesign_command.format(os.path.join(frameworks_path, 'QtGui.framework')))
    system(codesign_command.format(os.path.join(frameworks_path, 'QtOpenGL.framework')))
    system(codesign_command.format(os.path.join(frameworks_path, 'libbz2.1.0.6.dylib')))
    system(codesign_command.format(os.path.join(frameworks_path, 'libcrypto.1.0.0.dylib')))
    system(codesign_command.format(os.path.join(frameworks_path, 'libdbus-1.3.dylib')))
    system(codesign_command.format(os.path.join(frameworks_path, 'libiconv.2.dylib')))
    system(codesign_command.format(os.path.join(frameworks_path, 'libintl.8.dylib')))
    system(codesign_command.format(os.path.join(frameworks_path, 'libncurses.6.dylib')))
    system(codesign_command.format(os.path.join(frameworks_path, 'libpng16.16.dylib')))
    system(codesign_command.format(os.path.join(frameworks_path, 'libssl.1.0.0.dylib')))
    system(codesign_command.format(os.path.join(frameworks_path, 'libtcl8.6.dylib')))
    system(codesign_command.format(os.path.join(frameworks_path, 'libtk8.6.dylib')))
    system(codesign_command.format(os.path.join(frameworks_path, 'libz.1.2.8.dylib')))
    system(codesign_command.format(os.path.join(dist_path, 'Brickv.app', 'Contents', 'MacOS', 'python')))
    system(codesign_command.format(os.path.join(dist_path, 'Brickv.app')))

    print('building disk image')
    dmg_name = 'brickv_macos_{0}.dmg'.format(BRICKV_VERSION.replace('.', '_'))

    if os.path.exists(dmg_name):
        os.remove(dmg_name)

    system('hdiutil create -fs HFS+ -volname "Brickv-{0}" -srcfolder dist {1}'.format(BRICKV_VERSION, dmg_name))


# https://github.com/rfk/www.rfk.id.au/blob/master/content/blog/entry/code-signing-py2exe/index.html
def sign_py2exe(exepath):
    # First, sign a *copy* of the file so that we know its final size.
    execopy = os.path.join(os.path.dirname(exepath), 'temp-' + os.path.basename(exepath))
    shutil.copy2(exepath, execopy)
    system('X:\\sign.bat ' + execopy)

    # Figure out the size of the appended signature.
    comment_size = os.stat(execopy).st_size - os.stat(exepath).st_size
    os.unlink(execopy)

    # Write the correct comment size as the last two bytes of the file.
    with open(exepath, "r+") as f:
        f.seek(-2, os.SEEK_END)
        f.write(struct.pack("<H", comment_size))

    # Now we can sign the file for real.
    system('X:\\sign.bat ' + exepath)


def build_windows_pkg():
    print('building brickv NSIS installer')
    root_path = os.getcwd()

    print('removing old build directories')
    build_path = os.path.join(root_path, 'build')
    dist_path = os.path.join(root_path, 'dist')

    if os.path.exists(build_path):
        shutil.rmtree(build_path)

    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)

    print('freezing images')
    freeze_images()

    print('calling build_all_ui.py release')
    system('python build_all_ui.py release')

    print('preparing manifest')
    prepare_manifest(root_path)

    print('calling setup.py py2exe')
    system('python setup.py py2exe')

    print('calling build_plugin_list.py to undo previous release run')
    system('python build_plugin_list.py')

    # FIXME: doesn't work yet
    #if os.path.exists('X:\\sign.bat'):
    #    sign_py2exe('dist\\brickv.exe')

    print('creating NSIS script from template')
    nsis_template_path = os.path.join(root_path, 'build_data', 'windows', 'nsis', 'brickv_installer.nsi.template')
    nsis_path = os.path.join(dist_path, 'nsis', 'brickv_installer.nsi')
    specialize_template(nsis_template_path, nsis_path,
                        {'<<BRICKV_DOT_VERSION>>': BRICKV_VERSION,
                         '<<BRICKV_UNDERSCORE_VERSION>>': BRICKV_VERSION.replace('.', '_')})

    print('building NSIS installer')
    system('"C:\\Program Files\\NSIS\\makensis.exe" dist\\nsis\\brickv_installer.nsi')
    installer = 'brickv_windows_{0}.exe'.format(BRICKV_VERSION.replace('.', '_'))

    if os.path.exists(installer):
        os.unlink(installer)

    shutil.move(os.path.join(dist_path, 'nsis', installer), root_path)

    if os.path.exists('X:\\sign.bat'):
        system('X:\\sign.bat ' + installer)


def build_linux_pkg():
    print('building brickv Debian package')
    root_path = os.getcwd()

    print('removing old build directories')
    dist_path = os.path.join(root_path, 'dist')
    egg_info_path = os.path.join(root_path, 'brickv.egg-info')

    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)

    if os.path.exists(egg_info_path):
        shutil.rmtree(egg_info_path)

    print('calling build_all_ui.py release')
    system('python build_all_ui.py release')

    print('preparing manifest')
    prepare_manifest(root_path)

    print('calling setup.py sdist')
    system('python setup.py sdist')

    print('calling build_plugin_list.py to undo previous release run')
    system('python build_plugin_list.py')

    if os.path.exists(egg_info_path):
        shutil.rmtree(egg_info_path)

    print('copying build data')
    build_data_path = os.path.join(root_path, 'build_data', 'linux', 'brickv')
    linux_path = os.path.join(dist_path, 'linux')
    shutil.copytree(build_data_path, linux_path)

    print('unpacking sdist tar file')
    system('tar -x -C {0} -f {0}/brickv-{1}.tar.gz brickv-{1}/brickv'.format(dist_path, BRICKV_VERSION))

    print('copying unpacked brickv source')
    unpacked_path = os.path.join(dist_path, 'brickv-{0}'.format(BRICKV_VERSION), 'brickv')
    linux_share_path = os.path.join(linux_path, 'usr', 'share', 'brickv')
    shutil.copytree(unpacked_path, linux_share_path)

    print('creating DEBIAN/control from template')
    installed_size = int(check_output(['du', '-s', '--exclude', 'dist/linux/DEBIAN', 'dist/linux']).split('\t')[0])
    control_path = os.path.join(linux_path, 'DEBIAN', 'control')
    specialize_template(control_path, control_path,
                        {'<<VERSION>>': BRICKV_VERSION,
                         '<<INSTALLED_SIZE>>': str(installed_size)})

    print('changing directory modes to 0755')
    system('find dist/linux -type d -exec chmod 0755 {} \;')

    print('changing owner to root')
    system('sudo chown -R root:root dist/linux')

    print('building Debian package')
    system('dpkg -b dist/linux brickv-{0}_all.deb'.format(BRICKV_VERSION))

    print('changing owner back to original user')
    system('sudo chown -R `logname`:`logname` dist/linux')

    #print('checking Debian package')
    #system('lintian --pedantic brickv-{0}_all.deb'.format(BRICKV_VERSION))


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
    with open(os.path.join(root_path, 'brickv', 'brick-flash.template'), 'rb') as f:
        template = f.read()

    with open(os.path.join(root_path, 'brickv', 'samba.py'), 'rb') as f:
        samba_lines = f.readlines()

    while len(samba_lines) > 0 and not samba_lines[0].startswith('#### skip here for brick-flash ####'):
        del samba_lines[0]

    if len(samba_lines) > 0 and samba_lines[0].startswith('#### skip here for brick-flash ####'):
        del samba_lines[0]

    template = template.replace('<<VERSION>>', BRICK_FLASH_VERSION).replace('#### insert samba module here ####', ''.join(samba_lines))

    os.makedirs(os.path.join(linux_path, 'usr', 'bin'))

    with open(os.path.join(linux_path, 'usr', 'bin', 'brick-flash'), 'wb') as f:
        f.write(template)

    print('creating DEBIAN/control from template')
    installed_size = int(check_output(['du', '-s', '--exclude', 'dist/linux/DEBIAN', 'dist/linux']).split('\t')[0])
    control_path = os.path.join(linux_path, 'DEBIAN', 'control')
    specialize_template(control_path, control_path,
                        {'<<VERSION>>': BRICK_FLASH_VERSION,
                         '<<INSTALLED_SIZE>>': str(installed_size)})

    print('changing binary and directory modes to 0755')
    system('chmod 0755 dist/linux/usr/bin/brick-flash')
    system('find dist/linux/usr -type d -exec chmod 0755 {} \;')

    print('changing owner to root')
    system('sudo chown -R root:root dist/linux/usr')

    print('building Debian package')
    system('dpkg -b dist/linux brick-flash-{0}_all.deb'.format(BRICK_FLASH_VERSION))

    print('changing owner back to original user')
    system('sudo chown -R `logname`:`logname` dist/linux/usr')

    #print('checking Debian package')
    #system('lintian --pedantic brick-flash-{0}_all.deb'.format(BRICK_FLASH_VERSION))


BRICK_LOGGER_VERSION = '2.0.3'

def build_logger_zip():
    print('building brick-logger ZIP file')
    root_path = os.getcwd()

    print('removing old build directories')
    dist_path = os.path.join(root_path, 'dist')

    if os.path.exists(dist_path):
        shutil.rmtree(dist_path)

    os.makedirs(dist_path)

    print('creating brick-logger.py from template')
    with open(os.path.join(root_path, 'brickv', 'data_logger', 'brick-logger.py.template'), 'rb') as f:
        template = f.read()

    template = template.replace('<<VERSION>>', BRICK_LOGGER_VERSION)

    for module in ['configuration', 'data_logger', 'event_logger', 'loggable_devices', 'job', 'main', 'utils']:
        with open(os.path.join(root_path, 'brickv', 'data_logger', module + '.py'), 'rb') as f:
            lines = f.readlines()

        while len(lines) > 0 and not lines[0].startswith('#### skip here for brick-logger ####'):
            del lines[0]

        if len(lines) > 0 and lines[0].startswith('#### skip here for brick-logger ####'):
            del lines[0]

        template = template.replace('#### insert {0} module here ####'.format(module), ''.join(lines))

    with open(os.path.join(dist_path, 'brick-logger.py'), 'wb') as f:
        f.write(template)

    print('changing brick-logger.py mode to 0755')
    system('chmod 0755 dist/brick-logger.py')

    print('building ZIP file')
    zip_name = 'brick_logger_{0}.zip'.format(BRICK_LOGGER_VERSION.replace('.', '_'))

    if os.path.exists(zip_name):
        os.remove(zip_name)

    system('cd {0}; zip -q ../{1} brick-logger.py'.format(dist_path, zip_name))


# run 'python build_pkg.py' to build the windows/linux/macosx package
if __name__ == '__main__':
    if sys.platform != 'win32' and os.geteuid() == 0:
        print('error: must not be started as root, exiting')
        sys.exit(1)

    if 'logger' in sys.argv:
        build_logger_zip()
    elif sys.platform.startswith('linux'):
        if 'flash' in sys.argv:
            build_linux_flash_pkg()
        else:
            build_linux_pkg()
    elif sys.platform == 'win32':
        build_windows_pkg()
    elif sys.platform == 'darwin':
        build_macosx_pkg()
    else:
        print('error: unsupported platform: ' + sys.platform)
        sys.exit(1)

    print('done')
