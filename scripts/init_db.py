import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "database.sqlite3"

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
row INTEGER PRIMARY KEY AUTOINCREMENT,
id INTEGER UNIQUE,
article TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS supplies(
supply_name TEXT PRIMARY KEY,
supplyId INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS art_supp(
article TEXT PRIMARY KEY ,
supply_name TEXT
)
''')

connection.commit()
connection.close()

