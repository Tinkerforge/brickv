# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2019 Erik Fleckstein <erik@tinkerforge.com>
Copyright (C) 2019 Matthias Bolte <matthias@tinkerforge.com>

pyinstaller_utils.py: PyInstaller utilities

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
import shutil
import sys
import subprocess

import PyInstaller.config

def specialize_template(template_filename, destination_filename, replacements):
    lines = []
    replaced = set()

    with open(template_filename, 'r') as f:
        for line in f.readlines():
            for key in replacements:
                replaced_line = line.replace(key, replacements[key])

                if replaced_line != line:
                    replaced.add(key)

                line = replaced_line

            lines.append(line)

    if replaced != set(replacements.keys()):
        raise Exception('Not all replacements for {0} have been applied'.format(template_filename))

    os.makedirs(os.path.dirname(destination_filename), exist_ok=True)

    with open(destination_filename, 'w+') as f:
        f.writelines(lines)

def system(command, stdout=None):
    if subprocess.call(command, stdout=stdout) != 0:
        sys.exit(1)

def by_ext(exts):
    def fn(full_name):
        if os.path.isfile(full_name):
            _, ext = os.path.splitext(full_name)
            ext = ext[1:]

            return ext in exts

    return fn

def by_name(name):
    return lambda full_name: os.path.basename(full_name) == name

def win_sign(exe_path):
    system([
        "C:\\Program Files (x86)\\Windows Kits\\10\\bin\\x86\\signtool.exe", "sign",
        "/v",
        "/tr", "http://rfc3161timestamp.globalsign.com/advanced",
        "/td", "sha256",
        "/n", "Tinkerforge GmbH",
        exe_path])
    system(["C:\\Program Files (x86)\\Windows Kits\\10\\bin\\x86\\signtool.exe", "verify", "/v", "/pa", exe_path])

class PyinstallerUtils:
    def __init__(self, name_words, version):
        self.UNDERSCORE_NAME = '_'.join(name_words)
        self.CAMEL_CASE_NAME = ' '.join([w.title() for w in name_words])
        self.VERSION = version

        self.root_path = os.getcwd()
        self.build_path = PyInstaller.config.CONF['workpath']
        self.dist_path = PyInstaller.config.CONF['distpath']

        build_data_base_path = ''
        for arg in sys.argv:
            if arg.startswith('--build-data-path='):
                build_data_base_path = arg.replace('--build-data-path=', '')

        self.build_data_path = os.path.normpath(os.path.join(build_data_base_path))

        self.windows = sys.platform == 'win32'
        self.macos = sys.platform == 'darwin'
        self.linux = not self.windows and not self.macos

        self.win_dll_path = 'C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\ucrt\\DLLs\\x86'

        if self.windows:
            self.pathex = [self.root_path, self.win_dll_path]
        else:
            self.pathex = [self.root_path]


        if self.windows:
            self.icon = os.path.join(self.build_data_path, self.UNDERSCORE_NAME+'-icon.ico')
        elif self.linux:
            self.icon = self.UNDERSCORE_NAME+'-icon.png'
        else:
            self.icon = os.path.join(self.build_data_path, self.UNDERSCORE_NAME+'-icon.icns')

        self.datas = []

    def path_rel_to_root(self, path):
        return path.replace('\\', '/').replace(self.root_path.replace('\\', '/') + '/', '')

    def collect_data(self, pred):
        print("Collecting data")

        result = []

        for dirpath, _directories, files in os.walk(self.root_path):
            for file_ in files:
                full_name = os.path.join(dirpath, file_)

                if pred(full_name):
                    path_rel_to_root = self.path_rel_to_root(full_name)
                    result.append((path_rel_to_root, path_rel_to_root, 'DATA'))

        return result

    def win_build_installer(self):
        nsis_template_path = os.path.join(self.build_data_path, 'nsis', self.UNDERSCORE_NAME + '_installer.nsi.template')
        nsis_path = os.path.join(self.dist_path, 'nsis', self.UNDERSCORE_NAME + '.nsi')

        specialize_template(nsis_template_path, nsis_path,
                            {'<<DOT_VERSION>>': self.VERSION,
                             '<<UNDERSCORE_VERSION>>': self.VERSION.replace('.', '_')})

        system(['C:\\Program Files (x86)\\NSIS\\makensis.exe', nsis_path])

        installer = '{}_windows_{}.exe'.format(self.UNDERSCORE_NAME, self.VERSION.replace('.', '_'))
        installer_target_path = os.path.join(self.root_path, '..', installer)

        if os.path.exists(installer_target_path):
            os.remove(installer_target_path)

        shutil.move(os.path.join(self.dist_path, 'nsis', installer), installer_target_path)

        return os.path.join(self.root_path, '..', installer)

    def prepare(self, prepare_script_working_dir=None, prepare_script=None):
        print('removing old dist directory')

        if os.path.exists(self.dist_path):
            shutil.rmtree(self.dist_path)

        if prepare_script is not None:
            if prepare_script_working_dir is not None:
                os.chdir(prepare_script_working_dir)

            print('calling {}'.format(prepare_script))
            system([sys.executable, prepare_script], stdout=subprocess.DEVNULL)

            if prepare_script_working_dir is not None:
                os.chdir(self.root_path)

        self.datas = self.collect_data(by_ext(['bmp', 'jpg', 'png', 'svg']))
        self.datas += self.collect_data(by_name('internal'))

    def strip_binaries(self, binaries, patterns):
        return [x for x in binaries if all(pattern not in x[0].lower() for pattern in patterns)]

    def post_generate(self):
        if self.windows:
            self.post_generate_windows()
        elif self.macos:
            self.post_generate_macos()

    def post_generate_windows(self):
        exe_path = os.path.join(self.dist_path, self.UNDERSCORE_NAME+'.exe')

        if '--no-sign' not in sys.argv:
            win_sign(exe_path)
        else:
            print("skipping win_sign")

        installer_exe_path = self.win_build_installer()

        if '--no-sign' not in sys.argv:
            win_sign(installer_exe_path)
        else:
            print("skipping win_sign for installer")

    def post_generate_macos(self):
        build_data = os.path.join(self.build_data_path, '*')
        app_name = self.CAMEL_CASE_NAME + '.app'
        resources_path = os.path.join(self.dist_path, app_name, 'Contents', 'Resources')
        system(['bash', '-c', 'cp -R {} {}'.format(build_data.replace(" ", "\\ "), resources_path.replace(" ", "\\ "))])

        if '--no-sign' not in sys.argv:
            system(['bash', '-c', 'security unlock-keychain /Users/$USER/Library/Keychains/login.keychain'])
            system(['codesign', '--deep', '--force', '--verify', '--verbose=1', '--sign', 'Developer ID Application: Tinkerforge GmbH (K39N76HTZ4)', os.path.join(self.dist_path, app_name)])
            system(['codesign', '--verify', '--deep', '--verbose=1', os.path.join(self.dist_path, app_name)])
        else:
            print("skipping codesign")

        print('building disk image')

        dmg_path = os.path.join(self.dist_path, '..', '{}_macos_{}.dmg'.format(self.UNDERSCORE_NAME, self.VERSION.replace('.', '_')))

        if os.path.exists(dmg_path):
            os.remove(dmg_path)

        os.mkdir(os.path.join(self.dist_path, 'dmg'))

        shutil.move(os.path.join(self.dist_path, app_name), os.path.join(self.dist_path, 'dmg'))
        system(['hdiutil', 'create', '-fs', 'HFS+', '-volname', '{}-{}'.format(self.CAMEL_CASE_NAME.replace(" ", "-"), self.VERSION), '-srcfolder', os.path.join(self.dist_path, 'dmg'), dmg_path])
