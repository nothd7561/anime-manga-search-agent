import sqlite3
con = sqlite3.connect('data/processed/aniscope.db')
print(con.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall())
con.close()