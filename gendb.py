import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS folder_cards (
    folder_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    icon_path TEXT,
    banner_path TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS app_cards (
    app_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    background_path TEXT,
    parent_folder_id INTEGER,
    command TEXT,
    FOREIGN KEY (parent_folder_id) REFERENCES folder_cards (folder_id)
)
''')

conn.commit()
conn.close()
