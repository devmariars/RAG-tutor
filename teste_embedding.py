from sentence_transformers import SentenceTransformer

modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

texto = "Embedding transforma o significado de um texto em números."

embedding = modelo.encode(texto)

print("Texto:")
print(texto)

print("\nQuantidade de números:")
print(len(embedding))

print("\nPrimeiros 10 números do embedding:")
print(embedding[:10])