# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2019 Erik Fleckstein <erik@tinkerforge.com>

devicesproxymodel.py: Common QSortFilterProxyModel for devices

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

from PyQt5.QtCore import QSortFilterProxyModel, Qt

class DevicesProxyModel(QSortFilterProxyModel):
    # overrides QSortFilterProxyModel.lessThan
    def lessThan(self, left, right):
        if left.column() != 2: # position
            return QSortFilterProxyModel.lessThan(self, left, right)

        # Sort letters before digits, so that Bricklets connected to a
        # Master Brick are shown before Bricks stacked on the Master.
        # Also sort extensions after letters (i.e Bricks), so they are shown last.
        # Also sort slave stacks, having position 0, (i.e. from a RS485 Extension)
        # behind Bricks stacked on the Master.
        def get_sort_key(data):
            if len(data) == 0: # Put empty string before everything
                return 0

            diff = ord('z') - ord('0') + 1 # Put digits after letters

            if data.isdigit(): # Swap 0 behind 1-9
                if data == '0':
                    diff += 9
                else:
                    diff -= 1

            if 'Ext' in data:
                diff += 10 # Put digits of extensions after normal digits
                data = data[3:]
            return ord(data) + (diff if data.isdigit() else 0)

        # Compare by name if the position is the same
        if get_sort_key(left.data()) == get_sort_key(right.data()):
            return left.sibling(left.row(), 0).data() < right.sibling(right.row(), 0).data()

        return get_sort_key(left.data()) < get_sort_key(right.data())
