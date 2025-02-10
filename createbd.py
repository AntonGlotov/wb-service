import sqlite3

connection = sqlite3.connect('database.sqlite3')
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

