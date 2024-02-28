import os.path
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


def add_app(name, background_path, parent_folder_id, command, parameters):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        insert into app_cards (name, background_path, parent_folder_id, command, parameters) 
        values (?, ?, ?, ?, ?)
        ''', (name, background_path, parent_folder_id, command, parameters))
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


def modify_folder(self: ModifyFolderWindow):
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute(f"update folder_cards set name = ?, icon_path = ?, banner_path = ? where folder_id = ?",
                       (self.column1.text() if self.column1.text() != '' else None,
                        self.column2.text() if self.column2.text() != '' else None,
                        self.column3.text() if self.column3.text() != '' else None,
                        self.id))
        conn.commit()
        conn.close()
        refresh_folders()
        self.close()
    except Exception as e:
        QMessageBox.warning(self, "Error", str(e))


def remove_folder(self, human_triggered=True):
    try:
        if human_triggered:
            recheck = QMessageBox.question(self, '',
                                           f'Are you sure to remove {self.title}',
                                           QMessageBox.Yes | QMessageBox.No,
                                           QMessageBox.No)
            if recheck == QMessageBox.No:
                return
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute(f"delete from folder_cards where folder_id = ?", (self.id,))
        conn.commit()
        conn.close()
        if human_triggered:
            QMessageBox.information(self, '', f"Removed {self.title}")
            refresh_folders()
    except Exception as e:
        QMessageBox.warning(self, 'Error', str(e))


def save_apps(self):
    try:
        for row in self.rows:
            row_data = []
            for i in range(row.count()):
                widget = row.itemAt(i).widget()
                if isinstance(widget, QLineEdit):
                    row_data.append(widget.text() if widget.text() != '' else None)
            add_app(row_data[0], row_data[1], window.folder_id, row_data[2], row_data[3])
        refresh_apps(type('_', (object,), {
            'id': window.folder_id
        })())
        self.close()
    except Exception as e:
        QMessageBox.warning(self, "Error", str(e))


def modify_app(self: ModifyAppWindow):
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute(
            f"update app_cards set name = ?, background_path = ?, parent_folder_id = ?, command = ?, parameters = ? where app_id = ?",
            (self.column1.text() if self.column1.text() != '' else None,
             self.column2.text() if self.column2.text() != '' else None,
             window.folder_id,
             self.column3.text() if self.column3.text() != '' else None,
             self.column4.text() if self.column4.text() != '' else None,
             self.id))
        conn.commit()
        conn.close()
        refresh_apps(type('_', (object,), {
            'id': window.folder_id
        })())
        self.close()
    except Exception as e:
        QMessageBox.warning(self, "Error", str(e))


def remove_app(self, human_trigger=True):
    try:
        if human_trigger:
            recheck = QMessageBox.question(self, '',
                                           f'Are you sure to remove {self.title}',
                                           QMessageBox.Yes | QMessageBox.No,
                                           QMessageBox.No)
            if recheck == QMessageBox.No:
                return
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute(f"delete from app_cards where app_id = ?", (self.id,))
        conn.commit()
        conn.close()
        if human_trigger:
            QMessageBox.information(self, '', f"Removed {self.title}")
            refresh_apps(type('_', (object,), {
                'id': window.folder_id
            })())
    except Exception as e:
        QMessageBox.warning(self, 'Error', str(e))


def refresh_folders(reverse_order=False):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute(f"select * from folder_cards order by name {'desc' if reverse_order else ''}")
    data = cursor.fetchall()
    conn.close()

    folderCards = []
    for id, name, icon_path, banner_path in data:
        folderCard = FolderCard(id, name, icon_path, banner_path, 'default')
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
        appCard = AppCard(id, name, background_path, parent_folder_id, [command], parameters, 'default')
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


AddFolderWindow.saveData = save_folders
ModifyFolderWindow.saveData = modify_folder
FolderCard.remove = remove_folder
AddAppWindow.saveData = save_apps
ModifyAppWindow.saveData = modify_app
AppCard.remove = remove_app
FolderCard.clicked = refresh_apps
AppCard.clicked = run_command

if sys.platform == 'win32':
    from importdb import process_folders_and_shortcuts


    def import_from_dic(self):
        try:
            path = self.path.text()
            assert os.path.isdir(path)
            process_folders_and_shortcuts(path)
            refresh_folders()
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))


    Import.saveData = import_from_dic
