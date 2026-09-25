from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Caminho da nossa base de conhecimento
pasta_base = Path(__file__).parent / "base-conhecimento"

# Procura todos os arquivos .txt
arquivos = sorted(pasta_base.glob("*.txt"))

chunks = []

# Cada arquivo da nossa base será um chunk
for arquivo in arquivos:
    conteudo = arquivo.read_text(encoding="utf-8").strip()

    if conteudo:
        chunks.append({
            "texto": conteudo,
            "fonte": arquivo.name
        })

# Modelo de embeddings voltado para busca/retrieval
modelo = SentenceTransformer(
    "intfloat/multilingual-e5-small"
)

# Para o E5, avisamos que esses textos são possíveis respostas
textos = [
    "passage: " + chunk["texto"]
    for chunk in chunks
]

# Cria os embeddings da base
embeddings_chunks = modelo.encode(
    textos,
    normalize_embeddings=True
)

# Pergunta do usuário
pergunta = input("Faça uma pergunta: ").strip()

# Para o E5, avisamos que isso é uma pergunta de busca
embedding_pergunta = modelo.encode(
    ["query: " + pergunta],
    normalize_embeddings=True
)

# Compara a pergunta com todos os chunks
similaridades = cosine_similarity(
    embedding_pergunta,
    embeddings_chunks
)[0]

# Pega os 3 resultados mais semelhantes
melhores_indices = similaridades.argsort()[-3:][::-1]

# Melhor resultado encontrado
melhor_indice = melhores_indices[0]
melhor_similaridade = similaridades[melhor_indice]

# Limite provisório para considerar uma informação relevante
limite_minimo = 0.80

# Se nenhuma informação for suficientemente parecida
if melhor_similaridade < limite_minimo:
    print("\n⚠️ Não encontrei essa informação na minha base de conhecimento.")
    print(f"📊 Melhor similaridade encontrada: {melhor_similaridade:.3f}")

    # Registra a pergunta para revisão posterior
    arquivo_log = Path(__file__).parent / "perguntas-nao-respondidas.txt"

    with arquivo_log.open("a", encoding="utf-8") as arquivo:
        arquivo.write(
            f"Pergunta: {pergunta}\n"
            f"Similaridade: {melhor_similaridade:.3f}\n"
            f"{'-' * 50}\n"
        )

# Se houver informação relevante
else:
    print("\n🔎 Chunks mais relacionados:\n")

    for indice in melhores_indices:
        print(f"📄 Fonte: {chunks[indice]['fonte']}")
        print(f"🧩 Texto: {chunks[indice]['texto']}")
        print(f"📊 Similaridade: {similaridades[indice]:.3f}")
        print("-" * 50)