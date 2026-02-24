# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2019 Erik Fleckstein <erik@tinkerforge.com>

urlopen.py: Patches urlopen to use tinkerforge.com's intermediate cert

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

import sys
import ssl
import urllib.request

def urlopen(*args, **kwargs):
    if 'context' in kwargs:
        raise ValueError("Don't pass an SSL context to this function, as it creates a custom one.")

    context = ssl.create_default_context()

    if sys.platform == 'darwin':
        # On some Macs Python doesn't load any CA store by default
        # Force it to load the system CA store
        try:
            context.load_verify_locations('/etc/ssl/cert.pem')
        except FileNotFoundError:
            pass

    return urllib.request.urlopen(*args, **kwargs, context=context)


