import pandas as pd
from pathlib import Path
import json
import re, html

file_dir = Path(__file__).resolve().parents[3]

json_dir = file_dir / 'data' / 'raw'

def read_raw_records(source_name: str):
    title_records = []
    #initialize an empty list to store all the title names

    for path in sorted((json_dir / source_name).glob('*.json')):
        #list the files in the source folder
        with open(path, encoding='utf-8') as f:
            #open every file
            data = json.load(f)

        for media in data['data']['Page']['media']:
            media['source'] = source_name #remember whether it's anime, manga, or manhwa
            title_records.append(media)

    return title_records

def clean_description(text: str):
    if text is None: #check if theres a description
        return None

    text = re.sub(r'<[^>]+>', ' ', text)
    #gets rid of the <br> in the text
    text = html.unescape(text)
    #gets rid of the html wording in the text
    text = ' '.join(text.split())
    #collapses whitespace

    if not text:
        return None

    return text

def is_length_known(record: dict, media_type: str):
    #record is like the status, episodes, chapters of the etc
    if media_type == 'ANIME':
        if record['episodes'] is not None:
            return 1
        return 0

    if media_type == 'MANGA':
        if record['chapters'] is not None and (record['status'] in ('FINISHED', 'CANCELLED')) :
            return 1
        return 0 
    raise ValueError(f'unknown type: {media_type}')

def transform_record(record: dict):
    media_dict = {}

    media_dict['id'] = record['id']
    media_dict['title_romaji'] = record['title']['romaji']
    media_dict['title_english'] = record['title']['english']
    media_dict['description_raw'] = record['description']
    media_dict['description_clean'] = clean_description(record['description'])
    media_dict['episodes'] = record['episodes']
    media_dict['chapters'] = record['chapters']
    media_dict['average_score'] = record['averageScore']
    media_dict['popularity'] = record['popularity']
    media_dict['country'] = record['countryOfOrigin']
    media_dict['format'] = record['format']
    media_dict['status'] = record['status']
    media_dict['is_adult'] = int(record['isAdult'])
    #SQLite has no boolean type, so store True/False as 1/0
    media_dict['site_url'] = record['siteUrl']

    media_type = 'ANIME' if record['source'] == 'anime' else 'MANGA'
    #the raw records have no type field, so derive it from source (manga and manhwa are both MANGA)
    media_dict['type'] = media_type
    media_dict['length_known'] = is_length_known(record, media_type)

    genre_rows = []
    for genre in record['genres']:
        genre_rows.append((record['id'], genre))

    tag_rows = []
    for tag in record['tags']:
        tag_rows.append((record['id'],tag['name'], tag['rank'], ))

    return media_dict, genre_rows, tag_rows

def transform_all(sources: list):
    media_rows = []
    genre_rows = []
    tag_rows = []

    for source in sources:
        title_records = read_raw_records(source)
        for title in title_records:
            media_dict, genre_list, tag_list = transform_record(title)

            media_rows.append(media_dict)
            genre_rows.extend(genre_list)
            tag_rows.extend(tag_list)
    return media_rows, genre_rows, tag_rows



if __name__ == "__main__":
    sources = ['anime', 'manga', 'manhwa']

    media_rows, genre_rows, tag_rows = transform_all(sources)

    print('rows (media, genres, tags):', len(media_rows), len(genre_rows), len(tag_rows))

    print('empty descriptions:', sum(1 for row in media_rows if row['description_clean'] is None))

    genre_ids = {row[0] for row in genre_rows}
    print('titles with no genres:', sum(1 for row in media_rows if row['id'] not in genre_ids))

    print('unique media ids:', len({row['id'] for row in media_rows}))
    print('duplicate genre rows:', len(genre_rows) - len(set(genre_rows)))

    tag_keys = {(row[0], row[1]) for row in tag_rows}
    print('duplicate tag rows:', len(tag_rows) - len(tag_keys))
    print('tags with no rank:', sum(1 for row in tag_rows if row[2] is None))

    for row in media_rows:
        if row['id'] not in genre_ids:
            print(row['id'], row['title_romaji'], row['type'], row['format'], row['site_url'])