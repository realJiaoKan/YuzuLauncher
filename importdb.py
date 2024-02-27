import os
import sqlite3
import win32com.client


def get_shortcut_target(file):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(file)
    return shortcut.Targetpath


def insert_folder(conn, name):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO folder_cards (name) VALUES (?)", (name,))
    return cursor.lastrowid


def insert_app_card(conn, name, command, parent_folder_id):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO app_cards (name, command, parent_folder_id) VALUES (?, ?, ?)",
        (name[:-4], command, parent_folder_id))
    return cursor.lastrowid


def process_folders_and_shortcuts(root_folder, db_path):
    conn = sqlite3.connect(db_path)
    for folder_name in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder_name)
        if os.path.isdir(folder_path):
            folder_id = insert_folder(conn, folder_name)
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if file_path.endswith(".lnk"):  # Assuming shortcut files end with .lnk
                    target_path = get_shortcut_target(file_path)
                    insert_app_card(conn, file, target_path, folder_id)
    conn.commit()
    conn.close()


# Example usage
db_path = 'data.db'  # Your database file path
root_folder = 'Game/Galgame'  # Your root folder path
process_folders_and_shortcuts(root_folder, db_path)
