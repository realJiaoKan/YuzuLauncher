import subprocess
import sqlite3

from ui import *
from setting import setting
from window import window

sudo = ['sudo', '-S']


def add_folder(name, icon_path, banner_path):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        insert into folder_cards (name, icon_path, banner_path) 
        values (?, ?, ?)
        ''', (name, icon_path, banner_path))
    conn.commit()
    conn.close()


def add_app(name, background_path, parent_folder_id, command):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        insert into app_cards (name, background_path, parent_folder_id, command) 
        values (?, ?, ?, ?)
        ''', (name, background_path, parent_folder_id, command))
    conn.commit()
    conn.close()


def save_folders(self):
    try:
        for row in self.rows:
            row_data = []
            for i in range(row.count()):
                widget = row.itemAt(i).widget()
                if isinstance(widget, QLineEdit):
                    row_data.append(widget.text() if widget.text() != '' else None)
            add_folder(row_data[0], row_data[1], row_data[2])
        refresh_folders()
        self.close()
    except Exception as e:
        QMessageBox.warning(self, "Error", str(e))


def save_apps(self):
    try:
        for row in self.rows:
            row_data = []
            for i in range(row.count()):
                widget = row.itemAt(i).widget()
                if isinstance(widget, QLineEdit):
                    row_data.append(widget.text() if widget.text() != '' else None)
            add_app(row_data[0], row_data[1], window.folder_id, row_data[2])
        refresh_apps(type('_', (object,), {
            'id': window.folder_id
        })())
        self.close()
    except Exception as e:
        QMessageBox.warning(self, "Error", str(e))


def remove_folder():
    pass


def remove_app():
    pass


def refresh_folders(reverse_order=False):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute(f"select * from folder_cards order by name {'desc' if reverse_order else ''}")
    data = cursor.fetchall()
    conn.close()

    folderCards = []
    for id, name, icon_path, banner_path in data:
        folderCard = FolderCard(id, name, icon_path, banner_path)
        folderCards.append(folderCard)

    window.folderList.refresh(folderCards)


def refresh_apps(self):
    window.folder_id = self.id
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute(f"select * from app_cards where parent_folder_id={self.id} order by app_id")
    data = cursor.fetchall()
    conn.close()

    appCards = []
    for id, name, background_path, parent_folder_id, command, parameters in data:
        if command is None:
            command = ''
        if parameters is None:
            parameters = ''
        parameters = parameters.split()
        appCard = AppCard(name, background_path, parent_folder_id, [command], parameters)
        appCards.append(appCard)

    window.appList.refresh(appCards)


def run_command(self):
    self.command.extend(self.parameters)
    if setting.platform['enable_sudo']:
        print('[run_command] Run:', sudo + self.command)
        subprocess.run(sudo + self.command, text=True, input=setting.platform['password'])
    else:
        print('[run_command] Run:', self.command)
        subprocess.run(self.command)


FolderCard.clicked = refresh_apps
AppCard.clicked = run_command
AddFolderWindow.saveData = save_folders
AddAppWindow.saveData = save_apps
