import sqlite3

connection = sqlite3.connect('databasereport.sqlite3')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS supplies (
id TEXT UNIQUE PRIMARY KEY,
name TEXT, 
createdAt TEXT,
closedAt TEXT,
scanDt TEXT,
rejectDt TEXT,
done BOOLEAN
)
''')

connection.commit()
connection.close()