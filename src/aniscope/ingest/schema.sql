CREATE TABLE media(
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('ANIME', 'MANGA')),
    title_romaji TEXT NOT NULL,
    title_english TEXT NULL,
    description_raw TEXT NULL,
    description_clean TEXT NULL,
    episodes INTEGER NULL,
    chapters INTEGER NULL,
    average_score INTEGER NULL,
    popularity INTEGER NOT NULL,
    country TEXT NOT NULL,
    format TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('FINISHED', 'RELEASING', 'NOT_YET_RELEASED', 'CANCELLED', 'HIATUS')),
    is_adult INTEGER NOT NULL CHECK (is_adult IN (0, 1)),
    site_url TEXT NOT NULL,
    length_known INTEGER NOT NULL CHECK (length_known IN (0,1))
);

CREATE TABLE tags (
    media_id INTEGER NOT NULL REFERENCES media(id),
    tag TEXT NOT NULL,
    rank INTEGER NOT NULL,
    PRIMARY KEY (media_id, tag)
);

CREATE TABLE genres (
    media_id INTEGER NOT NULL REFERENCES media(id),
    genre TEXT NOT NULL,
    PRIMARY KEY (media_id, genre)
);

