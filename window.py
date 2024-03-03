import sys

from PySide6.QtWidgets import QApplication
import qdarkstyle

from ui import *

app = QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())
app.setWindowIcon(QIcon("default_icon.png"))
window = MainWindow()
window.show()
