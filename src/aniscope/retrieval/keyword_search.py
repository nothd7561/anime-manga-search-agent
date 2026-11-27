from pathlib import Path
import sqlite3
from collections import defaultdict
import re
from rank_bm25 import BM25Okapi
###the normal baseline


def tokenize(text: str):
    #tokenize the text/descriptions

    text = text.lower() #convert all letters to lowercase
    text = re.findall(r'[a-z0-9]+', text) #separate words based off a code

    return text


def build_index(documents: dict):
    #take our dictionary of a title and its aspects (genre,tags,desc,etc), tokenize its inputs and builds an index

    ids = list(documents)
    #makes a list of the movie ids
    tokenized_docs = []

    for doc_id in ids:
        #loop through the movie ids
        text = documents[doc_id]
        tokenized_docs.append(tokenize(text)) #tokenize the combined text for each movie id, add it to a list

    index = BM25Okapi(tokenized_docs)
    #given a query's words, it returns a score for every document
    return ids, index

def search(index, ids: list, titles: dict, query: str, k: int):
    #turns a query into a ranked list of titles. give it words, gives you back the best matching titles

    query_tokens = tokenize(query)
    #tokenize what the user wants to search for

    scores = index.get_scores(query_tokens) #returns one score per document (the combined text) using BM250K
    top_positions = scores.argsort()[::-1][:k] #sorts the positions from highest score to lowest score ( a list)

    results = []
    for pos in top_positions:
        title_id = ids[pos]
        name = titles[title_id]
        score = round(float(scores[pos]),2)
        results.append((title_id, name, score))
        #one item per position
    return results   
    #returns the id of the series, the name, and the score for that title.
        



if __name__ == '__main__':
    documents, titles = load_documents(db_path, media_query, genre_query, tags_query, 15)
    ids, index = build_index(documents)

    queries = [
        'revenge dark fantasy',
        'time loop romance',
        'cooking competition',
        'reincarnated villain',
        'slow burn mystery',
        # paraphrases, to see where keyword search breaks
        'vengeance',
        'reborn as the antagonist',
    ]

    for query in queries:
        print(f'\n{query}')
        for title_id, name, score in search(index, ids, titles, query, 5):
            print(f'  {score:6.2f}  {name}  (id {title_id})')