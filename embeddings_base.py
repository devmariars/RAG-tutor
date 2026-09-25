from pathlib import Path
from sentence_transformers import SentenceTransformer

# Use aqui exatamente o mesmo nome de pasta que funcionou no seu chunking.py
pasta_base = Path(__file__).parent / "base-conhecimento"

arquivos = sorted(pasta_base.glob("*.txt"))

chunks = []

for arquivo in arquivos:
    conteudo = arquivo.read_text(encoding="utf-8")
    paragrafos = conteudo.split("\n\n")

    for paragrafo in paragrafos:
        paragrafo = paragrafo.strip()

        if paragrafo:
            chunks.append({
                "texto": paragrafo,
                "fonte": arquivo.name
            })

modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

textos = [chunk["texto"] for chunk in chunks]

embeddings = modelo.encode(textos)

print(f"Chunks encontrados: {len(chunks)}")
print(f"Embeddings criados: {len(embeddings)}")
print(f"Números em cada embedding: {len(embeddings[0])}")