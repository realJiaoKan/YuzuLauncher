import sqlite3


def gendb():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS folder_cards (
        folder_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        icon_path TEXT,
        banner_path TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS app_cards (
        app_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        background_path TEXT,
        parent_folder_id INTEGER,
        command TEXT,
        parameters TEXT,
        FOREIGN KEY (parent_folder_id) REFERENCES folder_cards (folder_id)
    )
    ''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    gendb()
