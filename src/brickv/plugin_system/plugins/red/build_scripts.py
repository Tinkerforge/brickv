# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

build_script.py: Make _scripts.py from scripts/ folder and minify python code

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
import glob
import traceback

print("Adding RED Brick scripts:")

try:
    use_minified = True
    script_content = {}
    build_script_path = os.path.dirname(os.path.realpath(__file__))
    scripts = glob.glob(os.path.join(build_script_path, 'scripts', '*.py'))

    for script in scripts:
        lines = []

        with open(script) as f:
            for line in f.readlines():
                if line.startswith('### SCRIPT-INCLUDE: '):
                    include = line.replace('### SCRIPT-INCLUDE:', '').strip()
                    include = os.path.join(build_script_path, 'scripts', include)

                    with open(include) as i:
                        lines.extend(i.readlines())
                else:
                    lines.append(line)

        with open(script + '_prepared', 'w') as f:
            f.writelines(lines)

        if use_minified:
            if os.system('pyminifier ' + script + '_prepared > ' + script + '_minified') != 0:
                print('----> Could not minify scripts, please install https://github.com/liftoff/pyminifier if you want to make a release version.')
                print('----> I will use the non-minified versions for now.')
                use_minified = False

    scripts.extend(glob.glob(os.path.join(build_script_path, 'scripts', '*.sh')))

    for i, script in enumerate(scripts):
        if script.endswith('.py'):
            if use_minified:
                path = script + '_minified'
            else:
                path = script + '_prepared'
        else:
            path = script
        with open(path) as f:
            name = os.path.split(script)[-1][0:-3]
            file_ending = script[-3:]
            content = f.read()
            class Script:
                def __init__(self, script, file_ending, copied = False, file = None, script_instances = None):
                    self.script = script
                    self.file_ending = file_ending
                    self.copied = copied
                    self.file = file
                    if script_instances == None:
                        self.script_instances = []
                    else:
                        self.script_instances = script_instances

                def __repr__(self):
                    return 'Script(' + repr(self.script) + ', "' + str(self.file_ending) + '")'

            script_content[name] = Script(content, file_ending)
            print(" " + str(i) + ") " + name)

    with open(os.path.join(build_script_path, '_scripts.py'), 'w') as f:
        f.write('# -*- coding: utf-8 -*-\n')
        f.write('# This file is generated, don\'t edit it. Edit the files in the scripts/ folder.\n')
        f.write('\n')
        f.write('from threading import Lock\n')
        f.write('\n')
        f.write('class Script:\n')
        f.write('    def __init__(self, script, file_ending, copied = False, file = None, script_instances = None):\n')
        f.write('        self.script = script\n')
        f.write('        self.file_ending = file_ending\n')
        f.write('        self.copied = copied\n')
        f.write('        self.file = file\n')
        f.write('        if script_instances == None:\n')
        f.write('            self.script_instances = []\n')
        f.write('        else:\n')
        f.write('            self.script_instances = script_instances\n')
        f.write('        self.copy_lock = Lock()\n')
        f.write('\n')
        f.write('scripts = ')
        f.write(repr(script_content).replace('\\n# Created by pyminifier (https://github.com/liftoff/pyminifier)\\n\\n', ''))
except:
    print("Exception during script parsing, there will be no scripts available.")
    traceback.print_exc()

    build_script_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(build_script_path, '_scripts.py'), 'w') as f:
        f.write('# -*- coding: utf-8 -*-\n')
        f.write('# This file is generated, don\'t edit it. Edit the files in the scripts/ folder.\n')
        f.write('\n')
        f.write('# scripts dict is empty because of an exception during generation\n')
        f.write('scripts = {}')
