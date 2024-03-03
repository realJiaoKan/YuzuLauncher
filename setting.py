import os, shutil, json

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QGridLayout, QVBoxLayout, QLabel, QPushButton,
                               QLineEdit, QMessageBox)

from gendb import gendb


class Setting:
    def __init__(self):
        self.fontPath = {
            'default': "TekitouPoem.ttf"
        }
        self.font = {
        }
        self.fontSize = {
            'folder_card': 20,
            'app_card': 30
        }
        self.platform = {
            'enable_sudo': False,
            'password': ''
        }
        self.background = "default_background.png"
        self.background_mask = "background-color: rgba(0, 0, 0, 0.8);"
        self.mode = 'dark'
        self.load_from_file()

    def create_default_file(self):
        default_data = {
            'fontPath': self.fontPath,
            'fontSize': self.fontSize,
            'platform': self.platform,
            'background': self.background,
            'background_mask': self.background_mask,
            'mode': self.mode
        }
        with open('settings.json', 'w') as f:
            json.dump(default_data, f, indent=4)

    def save_to_file(self):
        data = {
            'fontPath': self.fontPath,
            'fontSize': self.fontSize,
            'platform': self.platform,
            'background': self.background,
            'background_mask': self.background_mask,
            'mode': self.mode
        }
        with open('settings.json', 'w') as f:
            json.dump(data, f, indent=4)

    def load_from_file(self):
        if not os.path.exists('settings.json'):
            self.create_default_file()
        with open('settings.json', 'r') as f:
            data = json.load(f)
        self.fontPath = data.get('font', {
            'default': "TekitouPoem.ttf"
        })
        self.fontSize = data.get('fontSize', {
            'folder_card': 20,
            'app_card': 25
        })
        self.platform = data.get('platform', {
            'enable_sudo': False,
            'password': ''
        })
        self.background = data.get('background', "default_background.png")
        self.background_mask = data.get('background_mask', "background-color: rgba(0, 0, 0, 0.8);")
        self.mode = data.get('mode', 'dark')


setting = Setting()


class SettingMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Setting")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.appearance = QGridLayout()
        self.title1 = QLabel("Appearance")
        self.title2 = QLabel("Base Font Size:")
        self.title3 = QLabel("Mode:")
        self.title4 = QLabel("Background:")
        self.title5 = QLabel("Mask:")
        self.base_font_size = QLineEdit()
        self.base_font_size.setText(str(setting.fontSize['folder_card']))
        self.mode = QLineEdit()
        self.mode.setText(setting.mode)
        self.background = QLineEdit()
        self.background.setText(setting.background)
        self.background.setDragEnabled(True)
        self.background.setAcceptDrops(True)
        self.background_mask = QLineEdit()
        self.background_mask.setText(setting.background_mask)
        self.background_mask.setFixedWidth(300)
        self.appearance.addWidget(self.title1, 0, 0)
        self.appearance.addWidget(self.title2, 1, 0)
        self.appearance.addWidget(self.base_font_size, 1, 1)
        self.appearance.addWidget(self.title3, 1, 2)
        self.appearance.addWidget(self.mode, 1, 3)
        self.appearance.addWidget(self.title4, 2, 0)
        self.appearance.addWidget(self.background, 2, 1)
        self.appearance.addWidget(self.title5, 2, 2)
        self.appearance.addWidget(self.background_mask, 2, 3)

        self.database = QHBoxLayout()
        self.backup = QPushButton("Backup")
        self.clear_all = QPushButton("Clear All")
        self.database.addWidget(self.backup)
        self.database.addWidget(self.clear_all)

        self.end = QHBoxLayout()
        self.cancel = QPushButton("Cancel")
        self.save = QPushButton("Save")
        self.end.addStretch()
        self.end.addWidget(self.cancel)
        self.end.addWidget(self.save)

        self.backup.clicked.connect(self.backup_db)
        self.clear_all.clicked.connect(self.clear_db)
        self.cancel.clicked.connect(self.exit)
        self.save.clicked.connect(self.saveData)

        self.layout.addLayout(self.appearance)
        self.layout.addSpacing(30)
        self.layout.addWidget(QLabel("Database"))
        self.layout.addLayout(self.database)
        self.layout.addLayout(self.end)

    def backup_db(self):
        try:
            shutil.copyfile("data.db", "data.db.bak")
            QMessageBox.information(self, '', "Backup finished, filename is data.db.bak")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def clear_db(self):
        try:
            recheck = QMessageBox.question(self, '',
                                           'Are you sure to delete ALL DATA in the database?',
                                           QMessageBox.Yes | QMessageBox.No,
                                           QMessageBox.No)
            if recheck == QMessageBox.No:
                return
            os.remove("data.db")
            gendb()
            QMessageBox.information(self, '', "Database is now cleared")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def exit(self):
        self.close()

    def saveData(self):
        setting.fontSize['folder_card'] = int(self.base_font_size.text())
        setting.fontSize['app_card'] = round(int(self.base_font_size.text()) * 1.5)
        setting.mode = self.mode.text()
        setting.background = self.background.text()
        setting.background_mask = self.background_mask.text()
        setting.save_to_file()
        self.close()
