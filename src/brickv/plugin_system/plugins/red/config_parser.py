# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

config_parser.py: Parses key=value configs from RED Brick

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

# Find the best implementation available
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

import ConfigParser


class FakeSectionHeadAndFile(object):
    def __init__(self, string):
        self.lines = string.splitlines()
        self.section_head = '[fake_section]\n'

    def readline(self):
        if self.section_head:
            try:
                return self.section_head
            finally:
                self.section_head = None
        else:
            while len(self.lines) > 0:
                line = self.lines[0]
                self.lines = self.lines[1:]
                if line.strip().startswith('#') or line.find('=') < 0:
                    continue
                
                return line
            return ""

def parse(data):
    if isinstance(data, list):
        string = str(bytearray(data))
    elif isinstance(data, str):
        string = data
    else:
        return None
    
    config = ConfigParser.ConfigParser()
    config.readfp(FakeSectionHeadAndFile(string))
    try:
        config = dict(config.items('fake_section'))
    except:
        return None
    
    return config
