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

def system(command, **kwargs):
    subprocess.check_call(command, **kwargs)

def specialize_template(template_filename, destination_filename, replacements, remove_template=False):
    lines = []
    replaced = set()

    # intentionally use mode=rb and decode/encode to be able to enforce UTF-8
    # in an ASCII environment even with Python2 where the open function doesn't
    # have an encoding parameter
    with open(template_filename, 'rb') as f:
        for line in f.readlines():
            line = line.decode('utf-8')

            for key in replacements:
                replaced_line = line.replace(key, replacements[key])

                if replaced_line != line:
                    replaced.add(key)

                line = replaced_line

            lines.append(line.encode('utf-8'))

    if replaced != set(replacements.keys()):
        raise Exception('Not all replacements for {0} have been applied'.format(template_filename))

    with open(destination_filename, 'wb') as f:
        f.writelines(lines)

    if remove_template:
        os.remove(template_filename)

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

        assert not (self.internal and self.snapshot)

        if platform == 'linux':
            self.build_data_dest_path = os.path.join(self.dist_path, 'tinkerforge-{}-{}'.format(executable_name, version))
            self.unpacked_source_path = os.path.join(self.build_data_dest_path, 'usr', 'share', executable_name)
        else:
            self.build_data_dest_path = os.path.join(self.dist_path, platform)
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

        shutil.copytree(self.build_data_src_path, self.build_data_dest_path, dirs_exist_ok=True)

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

    def run_sdist(self, prepare_script=None, pre_sdist=lambda: None):
        print('removing old build directories')

        egg_info_path = self.source_path + '.egg-info'

        if os.path.exists(self.dist_path):
            shutil.rmtree(self.dist_path)

        if os.path.exists(egg_info_path):
            shutil.rmtree(egg_info_path)

        if prepare_script is not None:
            print('calling ' + prepare_script)

            system([sys.executable, prepare_script])

        pre_sdist()

        print('calling setup.py sdist')

        setup_py_args = [sys.executable, os.path.join(self.root_path, 'setup.py'), 'sdist']

        if self.platform == 'windows':
            setup_py_args.append('--formats=zip')

        system(setup_py_args)

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
        system(['pyinstaller', '--distpath', '../dist', '--workpath', '../build', 'main_folder.spec', '--'] + sys.argv + ['--build-data-path=' + self.build_data_src_path, '--version=' + self.version],
               cwd=self.unpacked_source_path)

    def build_debian_pkg(self):
        print('changing directory modes to 0755')
        system(['find', self.build_data_dest_path, '-type', 'd', '-exec', 'chmod', '0755', '{}', ';'])

        print('changing file modes')
        system(['find', self.build_data_dest_path, '-type', 'f', '-perm', '664', '-exec', 'chmod', '0644', '{}', ';'])
        system(['find', self.build_data_dest_path, '-type', 'f', '-perm', '775', '-exec', 'chmod', '0755', '{}', ';'])

        print('building Debian package')
        specialize_template(os.path.join(self.build_data_dest_path, 'debian/changelog.template'),
                            os.path.join(self.build_data_dest_path, 'debian/changelog'),
                            {'<<VERSION>>': self.version,
                             '<<DATE>>': subprocess.check_output(['date', '-R']).decode('utf-8').strip()},
                            remove_template=True)

        with open(os.path.join(self.build_data_dest_path, 'debian', 'install'), 'w') as f:
            for root, dirs, files in sorted(os.walk(self.build_data_dest_path)):
                for name in files:
                    path = os.path.relpath(os.path.join(root, name), self.build_data_dest_path)

                    if path.startswith('debian'):
                        continue

                    if ' ' in path:
                        print('Paths with spaces are not supported:', path)
                        sys.exit(1)

                    f.write(path + '\n')

        dpkg_args = ['dpkg-buildpackage', '-us', '-uc']

        if '--dpkg-no-check-builddeps' in sys.argv:
            dpkg_args.append('-d')

        system(dpkg_args, cwd=self.build_data_dest_path)

        if os.path.exists('/usr/bin/lintian'):
            system(['lintian', '--verbose', '--pedantic','--no-tag-display-limit', '--suppress-tags', 'changelog-file-missing-in-native-package,no-copyright-file,binary-without-manpage', os.path.join(self.dist_path, '{}_{}_all.deb'.format(self.executable_name, self.version))])
        else:
            print('skipping lintian check')

    def copy_build_artifact(self):
        if self.platform == 'linux':
            shutil.copy(os.path.join(self.dist_path, '{}_{}_all.deb'.format(self.executable_name, self.version)), self.root_path)
            shutil.copy(os.path.join(self.dist_path, 'tinkerforge-{}_{}.dsc'.format(self.executable_name, self.version)), self.root_path)
            shutil.copy(os.path.join(self.dist_path, 'tinkerforge-{}_{}.tar.xz'.format(self.executable_name, self.version)), self.root_path)
        else:
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
