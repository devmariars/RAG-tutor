import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# CONFIGURAÇÃO DO GEMINI
# =========================================================

# Carrega as variáveis do arquivo .env
load_dotenv()

# Busca a chave da API
chave = os.getenv("GEMINI_API_KEY")

# Cria a conexão com o Gemini
cliente = genai.Client(api_key=chave)


# =========================================================
# BASE DE CONHECIMENTO
# =========================================================

# Caminho da nossa base
pasta_base = Path(__file__).parent / "base-conhecimento"

# Procura todos os arquivos .txt
arquivos = sorted(pasta_base.glob("*.txt"))

chunks = []

# Cada arquivo será um chunk
for arquivo in arquivos:
    conteudo = arquivo.read_text(encoding="utf-8").strip()

    if conteudo:
        chunks.append({
            "texto": conteudo,
            "fonte": arquivo.name
        })

print(f"✅ Base carregada: {len(chunks)} chunks.")


# =========================================================
# EMBEDDINGS DA BASE
# =========================================================

# Carrega o modelo de embeddings
modelo = SentenceTransformer(
    "intfloat/multilingual-e5-small"
)

# O E5 recebe os documentos como "passage"
textos = [
    "passage: " + chunk["texto"]
    for chunk in chunks
]

# Transforma a base em embeddings
embeddings_chunks = modelo.encode(
    textos,
    normalize_embeddings=True
)

print(f"✅ Embeddings criados: {len(embeddings_chunks)}.")


# =========================================================
# PERGUNTA DO USUÁRIO
# =========================================================

pergunta = input("\nFaça uma pergunta: ").strip()

# Transforma a pergunta em embedding
embedding_pergunta = modelo.encode(
    ["query: " + pergunta],
    normalize_embeddings=True
)

print("✅ Pergunta transformada em embedding.")


# =========================================================
# RETRIEVAL
# =========================================================

# Compara a pergunta com todos os chunks
similaridades = cosine_similarity(
    embedding_pergunta,
    embeddings_chunks
)[0]

# Seleciona os 3 melhores resultados
melhores_indices = similaridades.argsort()[-3:][::-1]

print("\n🔎 Informações encontradas:")

for indice in melhores_indices:
    print(
        f"📄 {chunks[indice]['fonte']} "
        f"— similaridade: {similaridades[indice]:.3f}"
    )


# =========================================================
# VERIFICA SE A BASE TEM INFORMAÇÃO SUFICIENTE
# =========================================================

melhor_indice = melhores_indices[0]
melhor_similaridade = similaridades[melhor_indice]

limite_minimo = 0.80

if melhor_similaridade >= limite_minimo:

    print("\n✅ Informação suficiente encontrada.")

    # Junta os 3 melhores chunks para formar o contexto
    contexto = "\n\n".join(
        chunks[indice]["texto"]
        for indice in melhores_indices
    )

    print("✅ Contexto preparado para o Gemini.")


    # =====================================================
    # PROMPT DO TUTOR
    # =====================================================

    prompt = f"""
Você é um tutor especializado em RAG.

Responda de forma natural, didática e conversacional, como um professor
explicando o assunto diretamente para o aluno.

Adapte a explicação à forma como a pergunta foi feita.
Evite apenas copiar ou repetir o contexto.
Use exemplos simples quando eles ajudarem na compreensão.

Use SOMENTE as informações presentes no contexto fornecido.
Não invente informações e não utilize conhecimento externo.

Se o contexto não contiver informação suficiente para responder,
diga de forma natural que não encontrou essa informação na base de conhecimento.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}
"""


    # =====================================================
    # GEMINI
    # =====================================================

    try:
        resposta = cliente.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        print("\n🤖 Resposta:")
        print(resposta.text)

        print("\n📚 Fontes utilizadas:")

        for indice in melhores_indices:
            print(f"• {chunks[indice]['fonte']}")

    except errors.ServerError:
        print("\n⚠️ O serviço de IA está temporariamente indisponível.")
        print("Tente novamente em alguns instantes.")


else:
    print("\n⚠️ Não encontrei informação suficiente na base.")