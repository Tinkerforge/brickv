from PyQt5.QtCore import QSortFilterProxyModel, Qt

class DevicesProxyModel(QSortFilterProxyModel):
    # overrides QSortFilterProxyModel.lessThan
    def lessThan(self, left, right):
        if left.column() != 2: # position
            return QSortFilterProxyModel.lessThan(self, left, right)

        # Sort letters before digits, so that Bricklets connected to a
        # Master Brick are shown before Bricks stacked on the Master.
        # Also sort extensions after letters (i.e Bricks), so they are shown last.
        def get_sort_key(data):
            if len(data) == 0: # Put empty string before everything
                return 0

            diff = ord('z') - ord('0') + 1 # Put digits after letters
            if 'Ext' in data:
                diff += 10 # Put digits of extensions after normal digits
                data = data[3:]
            return ord(data) + (diff if data.isdigit() else 0)

        # Compare by name if the position is the same
        if get_sort_key(left.data()) == get_sort_key(right.data()):
            return left.sibling(left.row(), 0).data() < right.sibling(right.row(), 0).data()

        return get_sort_key(left.data()) < get_sort_key(right.data())
