"""Load every saved AniList page into one table and run data-quality checks.

Read-only: makes no API requests and writes no files.
Run:  python src/aniscope/ingest/inspect_raw.py
"""

import json
from pathlib import Path

import pandas as pd

project_dir = Path(__file__).resolve().parents[3]
raw_dir = project_dir / 'data' / 'raw'
SOURCES = ['anime', 'manga', 'manhwa']

pd.set_option('display.width', 200)
pd.set_option('display.max_columns', None)


def load_source(source):
    records = []
    for path in sorted((raw_dir / source).glob('*.json')):
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        records.extend(data['data']['Page']['media'])
    df = pd.json_normalize(records)  # title.romaji / title.english become their own columns
    df['source'] = source
    return df


df = pd.concat([load_source(s) for s in SOURCES], ignore_index=True)
print(f'Loaded {len(df)} records:')
print(df['source'].value_counts().to_string(), '\n')


# 1. Null rates, per field and per source
print('=== 1. Null rate by source ===')
null_rates = df.drop(columns='source').isna().groupby(df['source']).mean().T
print(null_rates.to_string(float_format='{:.1%}'.format), '\n')

# isna() doesn't count empty lists or strings, so check those separately
empty_cols = ['genres', 'tags', 'description']
empty = df[empty_cols].apply(lambda s: s.map(lambda v: v == [] or v == '')).groupby(df['source']).mean().T
print('Empty ([] or "") rate by source:')
print(empty.to_string(float_format='{:.1%}'.format), '\n')


# 2. Duplicate ids within each source
print('=== 2. Duplicate ids within each source ===')
print(df.groupby('source')['id'].apply(lambda s: s.duplicated().sum()).to_string(), '\n')


# 3. Id overlap across sources
print('=== 3. Id overlap across sources ===')
ids = {s: set(df.loc[df['source'] == s, 'id']) for s in SOURCES}
print(f"anime & manga : {len(ids['anime'] & ids['manga'])}")
print(f"anime & manhwa: {len(ids['anime'] & ids['manhwa'])}")
print(f"manga & manhwa: {len(ids['manga'] & ids['manhwa'])}  (both type MANGA, should be 0)\n")


# 4. Format counts for manga and manhwa
print('=== 4. Format counts ===')
for source in ['manga', 'manhwa']:
    print(f'-- {source} --')
    print(df.loc[df['source'] == source, 'format'].value_counts(dropna=False).to_string(), '\n')


# 5. Is a null length explained by status = RELEASING?
print('=== 5. Null length vs status ===')
length_col = {'anime': 'episodes', 'manga': 'chapters', 'manhwa': 'chapters'}
for source, col in length_col.items():
    sub = df[df['source'] == source]
    is_null = sub[col].isna()
    print(f'-- {source} ({col}): {is_null.sum()} null of {len(sub)} --')
    # among the nulls, what status are they? (does RELEASING explain the nulls?)
    print('status of null records:')
    print(sub.loc[is_null, 'status'].value_counts().to_string())
    # within each status, what share is null? (can status predict "length unknown"?)
    print(f'share of {col} null within each status:')
    by_status = is_null.groupby(sub['status']).agg(['sum', 'count', 'mean'])
    by_status.columns = ['null', 'total', 'null_rate']
    print(by_status.to_string(formatters={'null_rate': '{:.1%}'.format}), '\n')
