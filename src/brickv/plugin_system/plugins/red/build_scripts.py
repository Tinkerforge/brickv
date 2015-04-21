# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

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
from pprint import pformat

print("Adding RED Brick scripts:")

try:
    use_minified = True
    script_data = []
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
            name, extension = os.path.splitext(os.path.split(script)[-1])
            content = f.read().replace('\n# Created by pyminifier (https://github.com/liftoff/pyminifier)\n\n', '')

            script_data.append((name, extension, content))

            print(" " + str(i) + ") " + name)

    with open(os.path.join(build_script_path, 'script_data.py'), 'w') as f:
        f.write('# -*- coding: utf-8 -*-\n')
        f.write('# This file is generated, don\'t edit it. Edit the files in the scripts/ folder.\n')
        f.write('\n')
        f.write('script_data = ')
        f.write(pformat(script_data))
except:
    print("Exception during script parsing, there will be no scripts available.")
    traceback.print_exc()

    build_script_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(build_script_path, 'script_data.py'), 'w') as f:
        f.write('# -*- coding: utf-8 -*-\n')
        f.write('# This file is generated, don\'t edit it. Edit the files in the scripts/ folder.\n')
        f.write('\n')
        f.write('# script data list is empty because of an exception during generation\n')
        f.write('script_data = []')
