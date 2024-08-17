import sys
from PyQt5.QtWidgets import QApplication
from gui.ui import AIMLApp

def main():
    app = QApplication(sys.argv)
    window = AIMLApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
