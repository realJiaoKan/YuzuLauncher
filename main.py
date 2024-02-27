import sys

from window import app
from slots import refresh_folders

if __name__ == "__main__":
    refresh_folders()
    sys.exit(app.exec())
