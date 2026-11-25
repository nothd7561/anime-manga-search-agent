import sqlite3
from pathlib import Path
from transform import transform_all

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


def load_rows(db_path, media_rows, genre_rows, tag_rows):

    connection = sqlite3.connect(db_path)
    try:
        connection.execute('PRAGMA foreign_keys = ON')
        #pragma is per connection, so it has to be turned on again here

        connection.executemany(
            '''INSERT INTO media (
                id, type, title_romaji, title_english, description_raw, description_clean,
                episodes, chapters, average_score, popularity, country, format, status,
                is_adult, site_url, length_known
            ) VALUES (
                :id, :type, :title_romaji, :title_english, :description_raw, :description_clean,
                :episodes, :chapters, :average_score, :popularity, :country, :format, :status,
                :is_adult, :site_url, :length_known
            )''',
            media_rows,
        )
        #media rows are dicts, so the :name placeholders pull each value by key
        #media goes first because genres and tags reference media(id)

        connection.executemany(
            'INSERT INTO genres (media_id, genre) VALUES (?, ?)',
            genre_rows,
        )
        #genre rows are (media_id, genre) tuples

        connection.executemany(
            'INSERT INTO tags (media_id, tag, rank) VALUES (?, ?, ?)',
            tag_rows,
        )
        #tag rows are (media_id, tag, rank) tuples

        connection.commit()
        #commit once so either everything loads or nothing does
    finally:
        connection.close()
        #close the connection even if an insert fails (uncommitted inserts are rolled back)


if __name__ == '__main__':
    create_database(db_path)
    media_rows, genre_rows, tag_rows = transform_all(['anime', 'manga', 'manhwa'])
    load_rows(db_path, media_rows, genre_rows, tag_rows)



