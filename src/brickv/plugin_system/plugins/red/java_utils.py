# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

java_utils.py: Java Utils

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

# totally stripped down version of the python-javatools (LGPL) package
# by Christopher O'Brien <obriencj@gmail.com>
#
# https://github.com/obriencj/python-javatools

import zipfile
import struct

def decode_utf8(value):
    try:
        return value.decode("utf8")
    except UnicodeDecodeError:
        return value.replace("\xC0\x80", "\x00").decode("utf8")

unpack_B_ = struct.Struct('>B').unpack
unpack_H_ = struct.Struct('>H').unpack
unpack_i_ = struct.Struct('>i').unpack
unpack_q_ = struct.Struct('>q').unpack
unpack_f_ = struct.Struct('>f').unpack
unpack_d_ = struct.Struct('>d').unpack
unpack_BH_ = struct.Struct('>BH').unpack
unpack_HI_ = struct.Struct('>HI').unpack
unpack_HH_ = struct.Struct('>HH').unpack
unpack_HHH_ = struct.Struct('>HHH').unpack

unpack_B = lambda f: unpack_B_(f.read(1))[0]
unpack_H = lambda f: unpack_H_(f.read(2))[0]
unpack_i = lambda f: unpack_i_(f.read(4))[0]
unpack_q = lambda f: unpack_q_(f.read(8))[0]
unpack_f = lambda f: unpack_f_(f.read(4))[0]
unpack_d = lambda f: unpack_d_(f.read(8))[0]
unpack_BH = lambda f: unpack_BH_(f.read(3))
unpack_HI = lambda f: unpack_HI_(f.read(6))
unpack_HH = lambda f: unpack_HH_(f.read(4))
unpack_HHH = lambda f: unpack_HHH_(f.read(6))
#unpack_utf8 = lambda f: decode_utf8(f.read(unpack_H(f)))
unpack_utf8 = lambda f: f.read(unpack_H(f))

CONST_UTF8 = 1
CONST_INTEGER = 3
CONST_FLOAT = 4
CONST_LONG = 5
CONST_DOUBLE = 6
CONST_CLASS = 7
CONST_STRING = 8
CONST_FIELDREF = 9
CONST_METHODREF = 10
CONST_INTERFACEMETHODREF = 11
CONST_NAMEANDTYPE = 12
CONST_MODULEID = 13
CONST_METHODHANDLE = 15
CONST_METHODTYPE = 16
CONST_INVOKEDYNAMIC = 18

ACCESS_PUBLIC = 0x0001
ACCESS_STATIC = 0x0008
ACCESS_PUBLIC_STATIC = ACCESS_PUBLIC | ACCESS_STATIC

unpack_cpool_value_by_type = [
    None,
    unpack_utf8,
    None,
    unpack_i,
    unpack_f,
    unpack_q,
    unpack_d,
    unpack_H,
    unpack_H,
    unpack_HH,
    unpack_HH,
    unpack_HH,
    unpack_HH,
    unpack_BH,
    unpack_HH,
    unpack_HH,
    unpack_H,
    None,
    unpack_HH
]

def unpack_cpool(class_file):
    count = unpack_H(class_file) - 1
    items = [(None, None)]
    skip_types = (CONST_LONG, CONST_DOUBLE)
    skip = False
    main_ref = None

    for i in xrange(count):
        if skip:
            skip = False
            items.append((None, None))
        else:
            type_ = unpack_B(class_file)
            value = unpack_cpool_value_by_type[type_](class_file)

            items.append((type_, value))

            if main_ref == None and type_ == CONST_UTF8 and value == 'main':
                main_ref = i + 1

            skip = type_ in skip_types

    return items, main_ref

def has_main_method(class_file):
    # check magic
    if class_file.read(4) != '\xCA\xFE\xBA\xBE':
        return None

    # skip version
    if len(class_file.read(4)) != 4:
        return None

    # unpack constant pool
    cpool, main_ref = unpack_cpool(class_file)

    if main_ref == None:
        return None

    # unpack meta info
    access_flags, this_ref, super_ref = unpack_HHH(class_file)

    if (access_flags & ACCESS_PUBLIC) != ACCESS_PUBLIC:
        return None

    class_name = decode_utf8(cpool[cpool[this_ref][1]][1]).replace('/', '.')

    # skip interfaces
    interface_count = unpack_H(class_file)

    if len(class_file.read(interface_count * 2)) != interface_count * 2:
        return None

    # skip fields
    field_count = unpack_H(class_file)

    for i in xrange(field_count):
        access_flags, name_ref, descriptor_ref = unpack_HHH(class_file)

        # skip attributes
        attribute_count = unpack_H(class_file)

        for i in xrange(attribute_count):
            attribute_name, attribute_size = unpack_HI(class_file)

            if len(class_file.read(attribute_size)) != attribute_size:
                return None

    # unpack methods
    methods_count = unpack_H(class_file)

    for i in xrange(methods_count):
        access_flags, name_ref, descriptor_ref = unpack_HHH(class_file)

        if main_ref == name_ref and \
           (access_flags & ACCESS_PUBLIC_STATIC) == ACCESS_PUBLIC_STATIC and \
           cpool[descriptor_ref][1] == '([Ljava/lang/String;)V':
            return class_name

        # skip attributes
        attribute_count = unpack_H(class_file)

        for i in xrange(attribute_count):
            attribute_name, attribute_size = unpack_HI(class_file)

            if len(class_file.read(attribute_size)) != attribute_size:
                return None

    return None

def get_jar_file_main_classes(filename, abort_ref=None):
    if abort_ref == None:
        abort_ref = [False]

    with zipfile.ZipFile(filename, 'r') as jar_file:
        main_classes = []

        for entry in jar_file.namelist():
            if abort_ref[0]:
                break

            if not entry.endswith('.class'):
                continue

            class_file = jar_file.open(entry, 'r')
            class_name = has_main_method(class_file)

            if class_name != None:
                main_classes.append(class_name)

            class_file.close()

        return main_classes

def get_class_file_main_classes(filename):
    with open(filename, 'r') as class_file:
        class_name = has_main_method(class_file)

        if class_name != None:
            return [class_name]
        else:
            return []
