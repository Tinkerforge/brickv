from PyQt4.QtGui import QWidget, QSpinBox, QRegExpValidator
from PyQt4.QtCore import QRegExp, QString, Qt

class SpinBoxHex(QSpinBox):
    def __init__(self, parent=None):
        super(SpinBoxHex, self).__init__(parent)
        self.validator = QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,2}"), self)
        self.setRange(0, 255)

    def fixCase(self, text):
        self.lineEdit().setText(text.toUpper())


    def validate(self, text, pos):
        return self.validator.validate(text, pos)

    def valueFromText(self, text):
        return text.toInt(16)[0]

    def textFromValue(self, value):
        s = QString.number(value, base=16).toUpper()
        if len(s) == 1:
            s = '0' + s
        return s
