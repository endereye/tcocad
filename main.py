import sys

from PyQt5 import QtWidgets

import qtui.main_lg

if __name__ == '__main__':
    _app = QtWidgets.QApplication(sys.argv)
    _win = qtui.main_lg.Main()
    _win.show()
    sys.exit(_app.exec())
