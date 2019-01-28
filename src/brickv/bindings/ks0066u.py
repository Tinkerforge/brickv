# -*- coding: utf-8 -*-
"""
KS0066U Utilities
Copyright (C) 2012-2015 Matthias Botle <matthias@tinkerforge.com>

ks0066u.py: KS0066U LCD Charset Converter

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

def unicode_to_ks0066u(string):
    byte = lambda x: bytes([x])
    ks0066u = bytes()
    code_points = string

    for code_point in code_points:
        code_point = ord(code_point)

        # ASCII subset from JIS X 0201
        if code_point >= 0x0020 and code_point <= 0x007e:
            # The LCD charset doesn't include '\' and '~', use similar characters instead
            mapping = {
                0x005c : byte(0xa4), # REVERSE SOLIDUS maps to IDEOGRAPHIC COMMA
                0x007e : byte(0x2d)  # TILDE maps to HYPHEN-MINUS
            }

            try:
                c = mapping[code_point]
            except KeyError:
                c = byte(code_point)
        # Katakana subset from JIS X 0201
        elif code_point >= 0xff61 and code_point <= 0xff9f:
            c = byte(code_point - 0xfec0)
        # Special characters
        else:
            mapping = {
                0x00a5 : byte(0x5c), # YEN SIGN
                0x2192 : byte(0x7e), # RIGHTWARDS ARROW
                0x2190 : byte(0x7f), # LEFTWARDS ARROW
                0x00b0 : byte(0xdf), # DEGREE SIGN maps to KATAKANA SEMI-VOICED SOUND MARK
                0x03b1 : byte(0xe0), # GREEK SMALL LETTER ALPHA
                0x00c4 : byte(0xe1), # LATIN CAPITAL LETTER A WITH DIAERESIS
                0x00e4 : byte(0xe1), # LATIN SMALL LETTER A WITH DIAERESIS
                0x00df : byte(0xe2), # LATIN SMALL LETTER SHARP S
                0x03b5 : byte(0xe3), # GREEK SMALL LETTER EPSILON
                0x00b5 : byte(0xe4), # MICRO SIGN
                0x03bc : byte(0xe4), # GREEK SMALL LETTER MU
                0x03c2 : byte(0xe5), # GREEK SMALL LETTER FINAL SIGMA
                0x03c1 : byte(0xe6), # GREEK SMALL LETTER RHO
                0x221a : byte(0xe8), # SQUARE ROOT
                0x00b9 : byte(0xe9), # SUPERSCRIPT ONE maps to SUPERSCRIPT (minus) ONE
                0x00a4 : byte(0xeb), # CURRENCY SIGN
                0x00a2 : byte(0xec), # CENT SIGN
                0x2c60 : byte(0xed), # LATIN CAPITAL LETTER L WITH DOUBLE BAR
                0x00f1 : byte(0xee), # LATIN SMALL LETTER N WITH TILDE
                0x00d6 : byte(0xef), # LATIN CAPITAL LETTER O WITH DIAERESIS
                0x00f6 : byte(0xef), # LATIN SMALL LETTER O WITH DIAERESIS
                0x03f4 : byte(0xf2), # GREEK CAPITAL THETA SYMBOL
                0x221e : byte(0xf3), # INFINITY
                0x03a9 : byte(0xf4), # GREEK CAPITAL LETTER OMEGA
                0x00dc : byte(0xf5), # LATIN CAPITAL LETTER U WITH DIAERESIS
                0x00fc : byte(0xf5), # LATIN SMALL LETTER U WITH DIAERESIS
                0x03a3 : byte(0xf6), # GREEK CAPITAL LETTER SIGMA
                0x03c0 : byte(0xf7), # GREEK SMALL LETTER PI
                0x0304 : byte(0xf8), # COMBINING MACRON
                0x00f7 : byte(0xfd), # DIVISION SIGN
                0x25a0 : byte(0xff)  # BLACK SQUARE
            }

            try:
                c = mapping[code_point]
            except KeyError:
                c = byte(min(code_point, 0xff))

        # Special handling for 'x' followed by COMBINING MACRON
        if c == byte(0xf8):
            if len(ks0066u) == 0 or not ks0066u.endswith(byte(0x78)):
                c = byte(0xff) # BLACK SQUARE

            if len(ks0066u) > 0:
                ks0066u = ks0066u[:-1]

        ks0066u += c

    return ks0066u
