import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('../users.db')
cursor = conn.cursor()

# List tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:", tables)

conn.close()
