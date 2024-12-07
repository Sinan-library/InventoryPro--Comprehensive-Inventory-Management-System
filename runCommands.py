import sqlite3

conn = sqlite3.connect('inventory.db')
c = conn.cursor()

c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin123'))

conn.commit()
