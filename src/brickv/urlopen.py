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

import ssl
import urllib.request

from brickv.utils import get_resources_path

# On Windows, Python ignores the intermediate certificate sent by the tinkerforge.com server.
# To be able to verify the cert chain, we package the intermediate cert and load it here.
def urlopen(*args, **kwargs):
    if 'context' in kwargs:
        raise ValueError("Don't pass an SSL context to this function, as it creates a custom one.")

    cert_path = get_resources_path('AlphaSSLCA-SHA256-G2.crt', warn_on_missing_file=True)
    context = ssl.create_default_context()
    context.load_verify_locations(cert_path)

    return urllib.request.urlopen(*args, **kwargs, context=context)


