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
    scripts = glob.glob(build_script_path + '/scripts/*.py')

    for script in scripts:
        ret = os.system('pyminifier ' + script + ' > ' + script + '_minified')
        if ret != 0:
            print('----> Could not minify scripts, please install https://github.com/liftoff/pyminifier if you want to make a release version.')
            print('----> I will use the non-minified versions for now.')
            use_minified = False
            break

    for i, script in enumerate(scripts):
        if use_minified:
            path = script + '_minified'
        else:
            path = script
        with open(path) as f:
            name = os.path.split(script)[-1][0:-3]
            content = f.read()
            class Script:
                def __init__(self, script, copied = False, stdout = None, stderr = None):
                    self.script = script
                    self.copied = copied
                    self.stdout = stdout
                    self.stderr = stderr
                    
                def __repr__(self):
                    return 'Script(' + repr(self.script) + ')'

            script_content[name] = Script(content)
            print(" " + str(i) + ") " + name)

    with open(os.path.join(build_script_path, '_scripts.py'), 'w') as f:
        f.write('# -*- coding: utf-8 -*-\n')
        f.write('# This file is generated, don\'t edit it. Edit the files in the scripts/ folder.\n')
        f.write('\n')
        f.write('class Script:\n')
        f.write('    def __init__(self, script, copied = False, stdout = None, stderr = None):\n')
        f.write('        self.script = script\n')
        f.write('        self.copied = copied\n')
        f.write('        self.stdout = stdout\n')
        f.write('        self.stderr = stderr\n\n')
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
