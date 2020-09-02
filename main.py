import sys
from PyQt5 import QtWidgets
from src.mainWindow import mainWindow


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = mainWindow()
    window.show()
    sys.exit(app.exec_())
