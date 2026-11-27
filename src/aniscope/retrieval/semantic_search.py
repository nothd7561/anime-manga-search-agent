from pathlib import Path
import sqlite3




def embed_documents(documents: str):
    #runs the trained model (MiniLM) over every combined text and returns the embedding array
    pass


def build_faiss_index(embedding: list):
    #run faiss over the vectors. faiss is a vector search up algorithm for large datasets
    pass
def search_semantic():
    #embed the query, ask FAISS for the top k results, return the (id, name, score)
    pass