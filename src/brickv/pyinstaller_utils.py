import os
import shutil
import sys
import subprocess
import traceback

import PyInstaller.config

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

        self.linux_build_data_path =   os.path.normpath(os.path.join(self.root_path, '..', 'build_data', 'linux'))
        self.mac_build_data_path =     os.path.normpath(os.path.join(self.root_path, '..', 'build_data', 'macos'))
        self.windows_build_data_path = os.path.normpath(os.path.join(self.root_path, '..', 'build_data', 'windows'))

        self.windows = sys.platform == 'win32'
        self.macos = sys.platform == 'darwin'
        self.linux = not self.windows and not self.macos

        self.win_dll_path = 'C:\\Program Files (x86)\\Windows Kits\\10\\Redist\\ucrt\\DLLs\\x86'

        if self.windows:
            self.pathex = [self.root_path, self.win_dll_path]
        else:
            self.pathex = [self.root_path]

        if self.windows:
            self.icon = os.path.join(self.windows_build_data_path, self.UNDERSCORE_NAME+'-icon.ico')
        elif self.linux:
            self.icon = self.UNDERSCORE_NAME+'-icon.png'
        else:
            self.icon = os.path.join(self.mac_build_data_path, self.UNDERSCORE_NAME+'-icon.icns')

    def get_unreleased_bindings(self):
        print("Searching unreleased devices.")
        to_exclude = ['brickv.build_ui', 'brickv.build_scripts']
        counter = 0
        for dirpath, _directories, files in os.walk(self.root_path):
            if os.path.basename(dirpath) == '__pycache__':
                continue

            dirname = os.path.basename(dirpath)
            if "bindings" not in dirname and "tinkerforge" not in dirname:
                continue

            for file in files:
                if "brick" not in file:
                    continue
                full_name = os.path.join(dirpath, file)
                with open(full_name, 'r') as f:
                    if '#### __DEVICE_IS_NOT_RELEASED__ ####' in f.read():
                        module_name = self.path_rel_to_root(full_name).replace("\\", "/").replace("/", ".").replace(".py", "")
                        to_exclude.append(module_name)
                        to_exclude.append(module_name.replace("bricklet_", "").replace("brick_", "").replace(".bindings", ".plugin_system.plugins"))
                        counter += 1
        print("Excluded {} unreleased devices.".format(counter))
        return to_exclude

    def path_rel_to_root(self, path):
        return path.replace('\\', '/').replace(self.root_path.replace('\\', '/') + '/', '')

    def collect_data(self, pred):
        print("Collecting data")
        result = []
        for dirpath, _directories, files in os.walk(self.root_path):
            for file in files:
                full_name = os.path.join(dirpath, file)

                if pred(full_name):
                    path_rel_to_root = self.path_rel_to_root(full_name)
                    result.append((path_rel_to_root, path_rel_to_root, 'DATA'))
        return result

    def win_build_installer(self):
        nsis_template_path = os.path.join(self.windows_build_data_path, 'nsis', self.UNDERSCORE_NAME + '_installer.nsi.template')
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
        return os.path.join(self.root_path, installer)

    def prepare(self, prepare_script_working_dir = None, prepare_script = None):
        print('removing old dist directory')
        if os.path.exists(self.dist_path):
            shutil.rmtree(self.dist_path)

        if prepare_script is not None:
            if prepare_script_working_dir is not None:
                os.chdir(prepare_script_working_dir)

            print('calling {} release'.format(prepare_script))
            system([sys.executable, prepare_script, 'release'], stdout=subprocess.DEVNULL)

            if prepare_script_working_dir is not None:
                os.chdir(self.root_path)

        self.datas = self.collect_data(by_ext(['bmp', 'jpg', 'png', 'svg']))

    def strip_binaries(self, binaries, patterns):
        return [x for x in binaries if all([pattern not in x[0].lower() for pattern in patterns])]

    def post_generate(self, undo_script_working_dir = None, undo_script = None):

        if undo_script is not None:
            if undo_script_working_dir is not None:
                os.chdir(undo_script_working_dir)

            print('calling {} to undo previous release run'.format(undo_script))
            system([sys.executable, undo_script], stdout=subprocess.DEVNULL)

            if undo_script_working_dir is not None:
                os.chdir(self.root_path)

        if self.windows:
            self.post_generate_windows()
        elif self.macos:
            self.post_generate_macos()

    def post_generate_windows(self):
        exe_path = os.path.join(self.root_path, 'dist', self.UNDERSCORE_NAME+'.exe')
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
        build_data = os.path.join(self.mac_build_data_path, '*')
        app_name = self.UNDERSCORE_NAME + '.app'
        resources_path = os.path.join(self.dist_path, app_name, 'Contents', 'Resources')
        system(['bash', '-c', 'cp -R {} {}'.format(build_data, resources_path)])

        if '--no-sign' not in sys.argv:
            system(['bash', '-c', 'security unlock-keychain /Users/$USER/Library/Keychains/login.keychain'])
            system(['bash', '-c', 'codesign --deep --force --verify --verbose=1 --sign "Developer ID Application: Tinkerforge GmbH (K39N76HTZ4)" ' + os.path.join(self.dist_path, app_name)])
            system(['codesign', '--verify', '--deep', '--verbose=1', os.path.join(self.dist_path, app_name)])
        else:
            print("skipping codesign")

        print('building disk image')
        dmg_path = os.path.join(self.dist_path, '..', '{}_macos_{}.dmg'.format(self.UNDERSCORE_NAME, self.VERSION.replace('.', '_')))

        if os.path.exists(dmg_path):
            os.remove(dmg_path)
        os.mkdir(os.path.join(self.dist_path, 'dmg'))

        shutil.move(os.path.join(self.dist_path, app_name), os.path.join(self.dist_path, 'dmg'))
        system(['hdiutil', 'create', '-fs', 'HFS+', '-volname', '{}-{}'.format(self.UNDERSCORE_NAME, self.VERSION), '-srcfolder', os.path.join(self.dist_path, 'dmg'), dmg_path])
