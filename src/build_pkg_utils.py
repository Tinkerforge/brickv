# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2019 Erik Fleckstein <erik@tinkerforge.com>
Copyright (C) 2019 Matthias Bolte <matthias@tinkerforge.com>

build_pkg_utils.py: Package builder utils

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
import subprocess
import sys
import zipfile
from collections import namedtuple

def system(command):
        if subprocess.call(command) != 0:
            sys.exit(1)

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

def get_commit_id():
    try:
        commit_id = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8')[:7]
    except Exception:
        commit_id = 'unknown'

    return commit_id

class BuildPkgUtils:
    def __init__(self, executable_name, platform, version):
        self.executable_name = executable_name
        self.platform = platform
        self.version = version
        self.internal = '--internal' in sys.argv
        self.snapshot = '--snapshot' in sys.argv
        self.root_path = os.path.realpath(os.path.dirname(__file__))
        self.dist_path = os.path.join(self.root_path, 'dist')
        self.build_data_src_path = os.path.join(self.root_path, 'build_data', platform, executable_name)
        self.build_data_dest_path = os.path.join(self.dist_path, platform)

        assert not (self.internal and self.snapshot)

        if platform == 'linux':
            self.unpacked_source_path = os.path.join(self.build_data_dest_path, 'usr', 'share', executable_name)
        else:
            self.unpacked_source_path = os.path.join(self.build_data_dest_path, executable_name)

        self.source_path = os.path.join(self.root_path, executable_name)

        if sys.platform == 'darwin' and '--no-sign' not in sys.argv:
            print("Unlocking code sign keychain")
            system(['bash', '-c', 'security unlock-keychain /Users/$USER/Library/Keychains/login.keychain'])

        os.chdir(self.root_path)

    @property
    def underscore_version(self):
        return self.version.replace('.', '_').replace('+', '_').replace('~', '_')

    def copy_build_data(self):
        print('copying build data')

        shutil.copytree(self.build_data_src_path, self.build_data_dest_path)

    def unpack_sdist(self):
        if self.platform == 'windows':
            print('unpacking sdist zip file')

            with zipfile.ZipFile(os.path.join(self.dist_path, '{}-{}.zip'.format(self.executable_name, self.version))) as f:
                f.extractall(os.path.join(self.dist_path))
        else:
            print('unpacking sdist tar file')

            system(['tar', '-x', '-C', self.dist_path, '-f',
                    os.path.join(self.dist_path, '{}-{}.tar.gz'.format(self.executable_name, self.version)),
                    os.path.join('{}-{}'.format(self.executable_name, self.version), self.executable_name)])

        print('copying unpacked {} source'.format(self.executable_name))

        unpacked_path = os.path.join(self.dist_path, '{}-{}'.format(self.executable_name, self.version), self.executable_name)
        shutil.copytree(unpacked_path, self.unpacked_source_path)

    def run_sdist(self, pre_sdist=lambda: None, prepare_script=None, build_manifest_from_template=False):
        print('removing old build directories')

        egg_info_path = self.source_path + '.egg-info'

        if os.path.exists(self.dist_path):
            shutil.rmtree(self.dist_path)

        if os.path.exists(egg_info_path):
            shutil.rmtree(egg_info_path)

        if prepare_script is not None:
            print('calling ' + prepare_script)

            if self.platform == 'windows':
                system(['python', prepare_script])
            else:
                system(['python3', prepare_script])

        pre_sdist()

        print('calling setup.py sdist')

        if self.platform == 'windows':
            system(['python', os.path.join(self.root_path, 'setup.py'), 'sdist', '--formats=zip'])
        else:
            system(['python3', os.path.join(self.root_path, 'setup.py'), 'sdist'])

        if os.path.exists(egg_info_path):
            shutil.rmtree(egg_info_path)

    def build_pyinstaller_pkg(self, prepare_script=None, pre_sdist=lambda: None, pre_pyinstaller=lambda: None):
        if self.platform not in ['macos', 'windows']:
            print('Building a {} package with pyinstaller is not supported.'.format(self.platform))
            sys.exit(1)

        print('building {} {} package'.format(self.executable_name, self.platform))
        self.run_sdist(prepare_script=prepare_script, pre_sdist=pre_sdist)

        self.unpack_sdist()

        pre_pyinstaller()

        print('copying pyinstaller spec-file')
        shutil.copy(os.path.join(self.source_path, 'main_folder.spec'), os.path.join(self.unpacked_source_path, 'main_folder.spec'))

        print('running pyinstaller')
        os.chdir(self.unpacked_source_path)
        system(['pyinstaller', '--distpath', '../dist', '--workpath', '../build', 'main_folder.spec', '--'] + sys.argv + ['--build-data-path=' + self.build_data_src_path, '--version=' + self.version])
        os.chdir(self.root_path)

    def build_debian_pkg(self):
        print('creating DEBIAN/control from template')

        installed_size = int(subprocess.check_output(['du', '-s', '--exclude', 'dist/linux/DEBIAN', 'dist/linux']).split(b'\t')[0])
        control_path = os.path.join(self.build_data_dest_path, 'DEBIAN', 'control')
        specialize_template(control_path, control_path,
                            {'<<VERSION>>': self.version,
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

        deb_name = '{}-{}_all.deb'.format(self.executable_name, self.version)

        system(['dpkg', '-b', 'dist/linux', deb_name])

        print('changing owner back to original user')
        system(['sudo', 'chown', '-R', '{}:{}'.format(user, group), 'dist/linux'])

        if os.path.exists('/usr/bin/lintian'):
            print('checking Debian package')
            system(['lintian', '--pedantic', deb_name])
        else:
            print('skipping lintian check')

    def copy_build_artifact(self):
        installer = os.path.join(self.build_data_dest_path,
                                '{}_{}_{}.{}'.format(self.executable_name,
                                                     self.platform,
                                                     self.underscore_version,
                                                     'exe' if self.platform == 'windows' else 'dmg'))

        shutil.copy(installer, self.root_path)

    def exit_if_not_venv(self):
        in_virtualenv = hasattr(sys, 'real_prefix')
        in_pyvenv = hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix

        if not in_virtualenv and not in_pyvenv:
            print('error: Please build Windows or macOS binaries in the correct virtualenv.')
            sys.exit(1)
