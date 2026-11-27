from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')
vectors = model.encode(['revenge', 'vengeance', 'cooking'])
print(util.cos_sim(vectors, vectors))
print(vectors[0][5])