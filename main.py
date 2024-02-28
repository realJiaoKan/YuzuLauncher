import sys
import os

from PySide6.QtGui import QFontDatabase

from window import app
from slots import refresh_folders
from gendb import gendb
from setting import setting

if __name__ == "__main__":
    if not os.path.exists("data.db"):
        gendb()
    for key, value in setting.fontPath.items():
        fontId = QFontDatabase.addApplicationFont(os.path.abspath(value))
        fontFamilies = QFontDatabase.applicationFontFamilies(fontId)
        setting.font[key] = fontFamilies[0]
    refresh_folders()
    sys.exit(app.exec())
