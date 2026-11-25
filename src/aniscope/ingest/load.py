import sqlite3
from pathlib import Path

file_dir = Path(__file__).resolve().parents[3]
sql_path = Path(__file__).parent / 'schema.sql'

db_path = file_dir / 'data' / 'processed' / 'aniscope.db'
#establish path for the database

def create_database(db_path):

    if db_path.exists(): 
        db_path.unlink()

    db_path.parent.mkdir(parents=True, exist_ok=True)
    query = sql_path.read_text()
    #convert our sqlite query into a string

    with sqlite3.connect(db_path) as connection:
        connection.execute('PRAGMA foreign_keys = ON')
        connection.executescript(query)
        #execute our db creation query

    connection.close()
    #close the connection


if __name__ == '__main__':
    create_database(db_path)




