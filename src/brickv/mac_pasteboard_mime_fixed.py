# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2019 Matthias Bolte <matthias@tinkerforge.com>

mac_pasteboard_mime_fixed.py: Don't add UTF BOM when copying text to the clipboard

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

# https://bugreports.qt.io/browse/QTBUG-61562

from PyQt5.QtMacExtras import QMacPasteboardMime

class MacPasteboardMimeFixed(QMacPasteboardMime):
    def __init__(self):
        super().__init__(QMacPasteboardMime.MIME_CLIP)

    def convertorName(self):
        return 'UnicodeTextUtf8Default'

    def flavorFor(self, mime):
        if mime == 'text/plain':
            return 'public.utf8-plain-text'

        parts = mime.split('charset=', 1)

        if len(parts) > 1:
            charset = parts[1].split(';', 1)[0]

            if charset == 'system':
                return 'public.utf8-plain-text'

            if charset in ['iso-106464-ucs-2', 'utf16']:
                return 'public.utf16-plain-text'

        return None

    def canConvert(self, mime, flavor):
        return mime.startswith('text/plain') and flavor in ['public.utf8-plain-text', 'public.utf16-plain-text']

    def mimeFor(self, flavor):
        if flavor == 'public.utf8-plain-text':
            return 'text/plain'

        if flavor == 'public.utf16-plain-text':
            return 'text/plain;charset=utf16'

        return None

    def convertFromMime(self, mime, data, flavor):
        if flavor == 'public.utf8-plain-text':
            return [data.encode('utf-8')]

        if flavor == 'public.utf16-plain-text':
            return [data.encode('utf-16')]

        return []

    def convertToMime(self, mime, data, flavor):
        if len(data) > 1:
            raise ValueError('Cannot handle multiple data members')

        data = data[0]

        if flavor == 'public.utf8-plain-text':
            return data.decode('utf-8')

        if flavor == 'public.utf16-plain-text':
            return data.decode('utf-16')

        raise ValueError('Unhandled MIME type: {0}'.format(mime))
