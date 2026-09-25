from pathlib import Path

pasta_base = Path(__file__).parent / "base-conhecimento"

arquivos = sorted(pasta_base.glob("*.txt"))

chunks = []

for arquivo in arquivos:
    conteudo = arquivo.read_text(encoding="utf-8")

    paragrafos = [
        paragrafo.strip()
        for paragrafo in conteudo.split("\n\n")
        if paragrafo.strip()
    ]

    # Se existir apenas um parágrafo, ele vira um chunk sozinho
    if len(paragrafos) == 1:
        chunks.append({
            "texto": paragrafos[0],
            "fonte": arquivo.name
        })
        continue

    # Junta 2 parágrafos por chunk
    # e repete 1 deles no próximo chunk (overlap)
    for i in range(len(paragrafos) - 1):
        texto_chunk = paragrafos[i] + " " + paragrafos[i + 1]

        chunks.append({
            "texto": texto_chunk,
            "fonte": arquivo.name
        })

print(f"Foram criados {len(chunks)} chunks.\n")

for numero, chunk in enumerate(chunks, start=1):
    print(f"🧩 Chunk {numero}")
    print(f"📄 Fonte: {chunk['fonte']}")
    print(chunk["texto"])
    print("-" * 50)