from pathlib import Path
from collections import defaultdict
import sqlite3

file_dir = Path(__file__).resolve().parents[3]

db_path = file_dir / 'data' / 'processed' / 'aniscope.db'

media_query = '''
    SELECT id, title_romaji, title_english, description_clean
    FROM media
    '''
genre_query = '''
    SELECT media_id, genre
    FROM genres'''
tags_query = '''
    SELECT media_id, tag
    FROM tags
    ORDER BY media_id, rank DESC'''

def load_documents(db_path, media_query, genre_query, tags_query, top_tags: int):
    #creates a dictionary of each titles id (key) mapped to its combined text

    connection = sqlite3.connect(db_path)
    try:
        media = connection.execute(media_query).fetchall()
        #execute the first query
        genre_rows = connection.execute(genre_query).fetchall()
        #execute the second query
        tag_rows = connection.execute(tags_query).fetchall()
        #execute the third query
    finally:
        connection.close()

    genres_by_id = defaultdict(list)
    for media_id, genre in genre_rows:
        genres_by_id[media_id].append(genre)

    tags_by_id = defaultdict(list)
    for media_id, tag in tag_rows:
        if len(tags_by_id[media_id]) < top_tags:
            #rows arrive best-rank first, limits the number of ranks for tags   
            tags_by_id[media_id].append(tag)

    documents = {}
    titles = {}
    for media_id, romaji, english, description in media:
        parts = [romaji, english or '',
            ' '.join(genres_by_id[media_id]),
            ' '.join(tags_by_id[media_id]),
            description or '',]
        documents[media_id] = ' '.join(part for part in parts if part)
        titles[media_id] = romaji
    
    return documents, titles