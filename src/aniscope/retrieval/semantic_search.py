from pathlib import Path
import sqlite3
from sentence_transformers import SentenceTransformer
from documents import load_documents, db_path, media_query, genre_query, tags_query
import numpy as np
import json
import faiss

project_dir = Path(__file__).resolve().parents[3]

emb_path = project_dir / 'data' / 'processed' / 'embeddings.npy'
ids_path = project_dir / 'data' / 'processed' / 'embedding_ids.json'

def embed_documents(documents: dict):
    #runs the trained model (MiniLM) over every combined text and returns the embedding array
    
    ids = list(documents) #creates a list of the title ids
    texts = [documents[doc_id] for doc_id in ids] #creates a list of combined strings

    model = SentenceTransformer('all-MiniLM-L6-v2') #create an object for our trained model
    embeddings = model.encode(texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True)
    #encodes 64 texts at a time, into vectors, shows the progress bar 

    return ids, embeddings
    #embeddings should be a table of 7000, 384. 7000 texts, 384 columns with vectors

def save_embeddings(emb_path, ids_path, ids: list, embeddings: np.ndarray):
    #save the ids and the embeddings from the specified path
    np.save(emb_path, embeddings)

    with open(ids_path, 'w') as f:
            json.dump(ids, f) 

def load_embeddings(emb_path, ids_path):
    #load the ids and the embeddings from the specified path
    embeddings = np.load(emb_path)
    
    with open(ids_path) as f:
        loaded_ids = json.load(f)

    return loaded_ids, embeddings

def load_or_build_embeddings(emb_path, ids_path, documents: dict):
    if emb_path.exists() and ids_path.exists():
        return load_embeddings(emb_path, ids_path)
    
    ids, embeddings = embed_documents(documents)
    save_embeddings(emb_path, ids_path, ids, embeddings)
    return ids, embeddings

def build_faiss_index(embedding: list):
    #run faiss over the vectors. faiss is a vector search up algorithm for large datasets
    
    dim = embeddings.shape[1]            #returns the column dimension (384)
    index = faiss.IndexFlatIP(dim)       #an empty index for vectors of length 384
    index.add(embeddings)                #load all 7,000 vectors into the empty index
    
    return index

def search_semantic():
    #embed the query, ask FAISS for the top k results, return the (id, name, score)
    pass

if __name__ == "__main__":
    documents, titles = load_documents(db_path, media_query, genre_query, tags_query, 15)
    ids, embeddings = load_or_build_embeddings(emb_path, ids_path, documents)
    print(len(ids), embeddings.shape)