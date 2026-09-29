import os

import re

import unicodedata

from pathlib import Path



from dotenv import load_dotenv

from google import genai

from google.genai import errors


# No Render gratuito, evitamos carregar PyTorch/SentenceTransformers
# para manter o processo abaixo do limite de 512 MB de RAM.
MODO_RENDER = bool(
    os.getenv("RENDER")
    or os.getenv("RENDER_SERVICE_ID")
)

if not MODO_RENDER:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity





# =========================================================

# 1. CONFIGURAÇÃO

# =========================================================



load_dotenv()



chave = os.getenv("GEMINI_API_KEY")



cliente = (

    genai.Client(api_key=chave)

    if chave

    else None

)





# =========================================================

# 2. NORMALIZA TEXTO

# =========================================================



def normalizar_texto(texto):



    texto = texto.lower().strip()



    texto = unicodedata.normalize(

        "NFD",

        texto

    )



    texto = "".join(

        caractere

        for caractere in texto

        if unicodedata.category(caractere) != "Mn"

    )



    texto = re.sub(

        r"[^\w\s]",

        " ",

        texto

    )



    texto = re.sub(

        r"\s+",

        " ",

        texto

    )



    return texto.strip()





# =========================================================

# 3. SEPARA AS SEÇÕES DOS ARQUIVOS

# =========================================================



def separar_secoes(texto):



    nomes_secoes = [

        "TÍTULO:",

        "EXPLICAÇÃO:",

        "EXPLICAÇÃO SIMPLES:",

        "EXEMPLO:",

        "RESUMO:",

        "TERMOS RELACIONADOS:"

    ]



    secoes = {}



    for indice, secao in enumerate(

        nomes_secoes

    ):



        inicio = texto.find(secao)



        if inicio == -1:

            secoes[secao] = ""

            continue



        inicio += len(secao)



        if indice + 1 < len(nomes_secoes):



            proxima_secao = (

                nomes_secoes[indice + 1]

            )



            fim = texto.find(

                proxima_secao,

                inicio

            )



            if fim == -1:

                fim = len(texto)



        else:

            fim = len(texto)



        secoes[secao] = (

            texto[inicio:fim]

            .strip()

        )



    return {

        "titulo": secoes["TÍTULO:"],

        "explicacao": secoes["EXPLICAÇÃO:"],

        "explicacao_simples": secoes[

            "EXPLICAÇÃO SIMPLES:"

        ],

        "exemplo": secoes["EXEMPLO:"],

        "resumo": secoes["RESUMO:"],

        "termos": secoes[

            "TERMOS RELACIONADOS:"

        ]

    }





# =========================================================

# 4. CONVERSA SOCIAL

# =========================================================



def identificar_conversa_social(pergunta):



    texto = normalizar_texto(pergunta)



    agradecimentos = [

        "obrigada",

        "obrigado",

        "obg",

        "valeu",

        "vlw",

        "brigada",

        "brigado",



        "muito obrigada",

        "muito obrigado",



        "obrigada chat",

        "obrigado chat",

        "valeu chat",



        "perfeito",

        "perfeito obrigada",

        "perfeito obrigado",



        "entendi obrigada",

        "entendi obrigado",



        "agora entendi",

        "agora eu entendi"

    ]



    cumprimentos = [

        "oi",

        "ola",

        "oie",



        "oi chat",

        "ola chat",



        "bom dia",

        "boa tarde",

        "boa noite"

    ]



    despedidas = [

        "tchau",

        "ate mais",

        "ate depois",

        "falou",

        "fui"

    ]



    if texto in agradecimentos:

        return "agradecimento"



    if texto in cumprimentos:

        return "cumprimento"



    if texto in despedidas:

        return "despedida"



    return None





def responder_conversa_social(tipo):



    if tipo == "agradecimento":

        return "Por nada! 💜"



    if tipo == "cumprimento":

        return (

            "Oi! 💜 Pode me perguntar "

            "qualquer coisa sobre RAG."

        )



    if tipo == "despedida":

        return "Até mais! 💜"



    return None





# =========================================================

# 5. IDENTIFICA INTENÇÃO LOCALMENTE

# =========================================================



def identificar_intencao(pergunta):



    texto = normalizar_texto(pergunta)





    # -----------------------------------------------------

    # EXEMPLO

    # -----------------------------------------------------



    palavras_exemplo = [

        "exemplo",

        "exemplos",



        "me de um exemplo",

        "da um exemplo",



        "outro exemplo",

        "mais um exemplo",



        "tem exemplo",

        "tem um exemplo",



        "me mostra um exemplo",

        "mostra um exemplo",



        "consegue dar um exemplo",

        "consegue me dar um exemplo",



        "exemplifica",

        "exemplifique"

    ]





    # -----------------------------------------------------

    # RESUMO

    # -----------------------------------------------------



    palavras_resumo = [

        "resuma",

        "resume",

        "resumo",



        "resumidamente",

        "resumido",

        "resumida",



        "em poucas palavras",

        "em uma frase",

        "em poucas linhas",



        "de uma maneira curta",

        "de maneira curta",

        "de forma curta",



        "de uma maneira mais curta",

        "de maneira mais curta",

        "de forma mais curta",



        "mais curto",

        "mais curta",



        "mais resumido",

        "mais resumida",



        "menos texto",

        "menos detalhes",



        "sem tantos detalhes",

        "sem muito detalhe",



        "explica resumidamente",

        "explique resumidamente",



        "explica de forma resumida",

        "explique de forma resumida",



        "encurta",

        "encurte",



        "encurta isso",

        "encurte isso",



        "faz menor",

        "deixa menor",



        "bem curto",

        "bem resumido",



        "rapidinho",

        "bem rapido"

    ]





    # -----------------------------------------------------

    # EXPLICAÇÃO SIMPLES

    # -----------------------------------------------------



    palavras_simples = [

        "nao entendi",



        "explica melhor",

        "explique melhor",



        "explica mais facil",

        "explique mais facil",



        "mais simples",



        "de forma simples",

        "de maneira simples",



        "simplifica",

        "simplifique",



        "mais mastigado",

        "mais mastigadinho",



        "explica como se eu fosse crianca",

        "explique como se eu fosse crianca",



        "explica de outro jeito",

        "explique de outro jeito",



        "nao ficou claro",

        "nao consegui entender",



        "fala de um jeito mais facil",



        "explica pra leigo",

        "explique pra leigo"

    ]





    # -----------------------------------------------------

    # INTERPRETAÇÃO / CONFIRMAÇÃO

    # -----------------------------------------------------



    palavras_interpretacao = [

        "seria tipo",

        "seria como",



        "seria parecido",

        "seria parecida",



        "entao seria",

        "entao e tipo",

        "entao e como",



        "quer dizer que",

        "isso quer dizer",



        "posso pensar como",

        "posso entender como",



        "seria uma",

        "seria um",



        "e tipo uma",

        "e tipo um",



        "e como uma",

        "e como um",



        "basicamente seria",

        "basicamente e",



        "eu posso dizer que",

        "eu posso pensar que",



        "faz sentido dizer que",

        "faz sentido pensar que",



        "entendi certo",

        "entendi direito",



        "e isso",

        "seria isso"

    ]





    # -----------------------------------------------------

    # DECISÃO

    # -----------------------------------------------------



    if any(

        expressao in texto

        for expressao in palavras_exemplo

    ):

        return "exemplo"



    if any(

        expressao in texto

        for expressao in palavras_resumo

    ):

        return "resumo"



    if any(

        expressao in texto

        for expressao in palavras_simples

    ):

        return "explicacao_simples"



    if any(

        expressao in texto

        for expressao in palavras_interpretacao

    ):

        return "interpretacao"



    return "explicacao"





# =========================================================

# 6. PERGUNTA DIRETA

# =========================================================



def eh_pergunta_direta(pergunta):



    texto = normalizar_texto(pergunta)



    inicios_diretos = [

        "o que e ",

        "o que sao ",



        "explique ",

        "explica ",



        "defina ",

        "definicao de ",



        "para que serve ",

        "pra que serve ",



        "como funciona ",

        "como funcionam ",



        "qual a funcao de ",

        "qual e a funcao de "

    ]



    return any(

        texto.startswith(inicio)

        for inicio in inicios_diretos

    )





# =========================================================

# 7. MENSAGEM MUITO AMBÍGUA

# =========================================================



def mensagem_ambigua(pergunta):



    texto = normalizar_texto(pergunta)



    frases_ambiguas = [

        "isso ai funciona como",

        "isso funciona como",

        "como assim",

        "e isso",

        "e aquilo",

        "fala disso",

        "explica isso"

    ]



    return texto in frases_ambiguas





# =========================================================

# 8. BASE DE CONHECIMENTO

# =========================================================



pasta_base = (

    Path(__file__).parent

    / "base-conhecimento"

)



arquivos = sorted(

    pasta_base.glob("*.txt")

)



chunks = []



for arquivo in arquivos:



    conteudo = arquivo.read_text(

        encoding="utf-8"

    ).strip()



    if not conteudo:

        continue



    secoes = separar_secoes(

        conteudo

    )



    chunks.append({

        "texto": conteudo,

        "fonte": arquivo.name,



        "titulo": secoes[

            "titulo"

        ],



        "explicacao": secoes[

            "explicacao"

        ],



        "explicacao_simples": secoes[

            "explicacao_simples"

        ],



        "exemplo": secoes[

            "exemplo"

        ],



        "resumo": secoes[

            "resumo"

        ],



        "termos": secoes[

            "termos"

        ]

    })





# =========================================================

# 9. EMBEDDINGS / MODO LEVE

# =========================================================



modelo = None
embeddings_chunks = None

if not MODO_RENDER:
    print("🧠 MODO LOCAL: carregando multilingual-e5-small")

    modelo = SentenceTransformer(
        "intfloat/multilingual-e5-small"
    )

    textos = [
        "passage: " + chunk["texto"]
        for chunk in chunks
    ]

    embeddings_chunks = modelo.encode(
        textos,
        normalize_embeddings=True
    )
else:
    print("🌐 MODO RENDER: retrieval lexical leve ativado")





# =========================================================

# 10. BUSCA CHUNK POR FONTE

# =========================================================



def buscar_chunk_por_fonte(fonte):



    for indice, chunk in enumerate(

        chunks

    ):



        if chunk["fonte"] == fonte:

            return indice



    return None





# =========================================================

# 11. RETRIEVAL

# =========================================================



def fazer_retrieval(

    pergunta,

    quantidade=3

):



    if not MODO_RENDER:
        embedding_pergunta = modelo.encode(
            [
                "query: " + pergunta
            ],
            normalize_embeddings=True
        )

        similaridades = cosine_similarity(
            embedding_pergunta,
            embeddings_chunks
        )[0]

        melhores_indices = (
            similaridades
            .argsort()[
                -quantidade:
            ][::-1]
        )

        melhor_indice = melhores_indices[0]
        melhor_similaridade = similaridades[melhor_indice]

        return (
            melhores_indices,
            melhor_indice,
            melhor_similaridade
        )



    # -----------------------------------------------------
    # RENDER: retrieval lexical leve, sem PyTorch
    # -----------------------------------------------------

    stopwords = {
        "a", "ao", "aos", "as", "o", "os", "de", "da", "das",
        "do", "dos", "e", "em", "no", "na", "nos", "nas", "um",
        "uma", "uns", "umas", "para", "pra", "por", "que", "como",
        "qual", "quais", "me", "eu", "isso", "isto", "esse", "essa",
        "é", "ser", "serve", "funciona", "funcionam", "explique",
        "explica", "defina", "definicao"
    }

    def tokens_relevantes(texto):
        normalizado = normalizar_texto(texto)
        return {
            palavra
            for palavra in normalizado.split()
            if len(palavra) > 2
            and palavra not in stopwords
        }

    tokens_pergunta = tokens_relevantes(pergunta)

    if not tokens_pergunta:
        tokens_pergunta = set(
            normalizar_texto(pergunta).split()
        )

    pontuacoes = []

    for indice, chunk in enumerate(chunks):
        titulo = chunk.get("titulo", "")
        termos = chunk.get("termos", "")

        texto_busca = " ".join([
            titulo,
            termos,
            chunk.get("resumo", ""),
            chunk.get("explicacao_simples", ""),
            chunk.get("explicacao", ""),
            chunk.get("texto", "")
        ])

        tokens_documento = tokens_relevantes(texto_busca)
        tokens_titulo = tokens_relevantes(titulo)
        tokens_termos = tokens_relevantes(termos)

        total = max(len(tokens_pergunta), 1)

        cobertura = (
            len(tokens_pergunta & tokens_documento)
            / total
        )

        cobertura_titulo = (
            len(tokens_pergunta & tokens_titulo)
            / total
        )

        cobertura_termos = (
            len(tokens_pergunta & tokens_termos)
            / total
        )

        pergunta_normalizada = normalizar_texto(pergunta)
        documento_normalizado = normalizar_texto(texto_busca)

        bonus_frase = (
            0.10
            if pergunta_normalizada
            and pergunta_normalizada in documento_normalizado
            else 0.0
        )

        pontuacao = min(
            1.0,
            (0.65 * cobertura)
            + (0.20 * cobertura_titulo)
            + (0.15 * cobertura_termos)
            + bonus_frase
        )

        pontuacoes.append((indice, pontuacao))

    pontuacoes.sort(
        key=lambda item: item[1],
        reverse=True
    )

    melhores = pontuacoes[:quantidade]
    melhores_indices = [
        indice
        for indice, _ in melhores
    ]

    melhor_indice = melhores_indices[0]
    melhor_similaridade = melhores[0][1]

    return (
        melhores_indices,
        melhor_indice,
        melhor_similaridade
    )





# =========================================================

# 12. ESCOLHE RESPOSTA ESTRUTURADA

# =========================================================



def resposta_da_secao(

    chunk,

    intencao

):



    if intencao == "resumo":



        return (

            chunk["resumo"]

            or chunk["explicacao"]

        )



    if intencao == "exemplo":



        return (

            chunk["exemplo"]

            or chunk["explicacao"]

        )



    if (

        intencao

        == "explicacao_simples"

    ):



        return (

            chunk[

                "explicacao_simples"

            ]

            or chunk["resumo"]

            or chunk["explicacao"]

        )



    return chunk["explicacao"]





# =========================================================

# 13. CONTEXTO CURTO PARA GEMINI

# =========================================================



def montar_contexto_curto(chunk):



    partes = []



    if chunk["titulo"]:

        partes.append(

            "TÍTULO:\n"

            + chunk["titulo"]

        )



    if chunk["explicacao"]:

        partes.append(

            "EXPLICAÇÃO:\n"

            + chunk["explicacao"]

        )



    if chunk["explicacao_simples"]:

        partes.append(

            "EXPLICAÇÃO SIMPLES:\n"

            + chunk[

                "explicacao_simples"

            ]

        )



    if chunk["resumo"]:

        partes.append(

            "RESUMO:\n"

            + chunk["resumo"]

        )



    if chunk["termos"]:

        partes.append(

            "TERMOS RELACIONADOS:\n"

            + chunk["termos"]

        )



    return "\n\n".join(partes)





# =========================================================

# 14. CHAMADA ÚNICA AO GEMINI

# =========================================================



def chamar_gemini(

    pergunta,

    contexto,

    fontes,

    topico

):



    if cliente is None:



        return {

            "status": "limitado",

            "modo": "limite",

            "resposta": (

                "Não consegui usar a camada "

                "de interpretação neste momento."

            ),

            "fontes": fontes,

            "topico": topico

        }



    prompt = f"""

Você é o RAG Tutor.



Responda SOMENTE com base no contexto abaixo.



CONTEXTO:

{contexto}



USUÁRIO:

{pergunta}



REGRAS:



- Não use conhecimento externo.

- Não invente informações.

- Não complete lacunas.

- Se a base não permitir responder,

  diga isso claramente.

- Se a mensagem estiver ambígua,

  peça esclarecimento.

- Seja breve.

- Não repita conteúdo desnecessariamente.

"""



    print(

        "🤖 GEMINI FOI CHAMADO:",

        pergunta

    )



    try:



        resposta = (

            cliente.models.generate_content(

                model="gemini-3.6-flash",

                contents=prompt

            )

        )



        print(

            "✅ GEMINI RESPONDEU"

        )



        return {

            "status": "ok",

            "modo": "geracao",

            "resposta": resposta.text,

            "fontes": fontes,

            "topico": topico

        }



    except errors.ServerError:



        print(

            "⚠️ GEMINI INDISPONÍVEL"

        )



        return None



    except errors.ClientError as erro:



        if erro.code == 429:



            print(

                "⚠️ COTA 429"

            )



            return None



        raise





# =========================================================

# 15. INTERPRETAÇÃO LOCAL

# =========================================================



def responder_interpretacao_local(

    pergunta,

    chunk

):



    explicacao = (

        chunk["explicacao_simples"]

        or chunk["resumo"]

        or chunk["explicacao"]

    )



    return (

        "Pela minha base, este conceito é descrito assim:\n\n"

        f"{explicacao}\n\n"

        "A base não traz uma equivalência explícita "

        f"para confirmar totalmente a comparação "

        f"“{pergunta.strip()}”. "

        "Então prefiro não afirmar além do que está documentado."

    )





# =========================================================

# 16. FUNÇÃO PRINCIPAL

# =========================================================



def responder_pergunta(

    pergunta,

    ultimo_topico=None

):



    pergunta = pergunta.strip()



    if not pergunta:



        return {

            "status": "precisa_esclarecimento",

            "modo": "limite",

            "resposta": (

                "Pode escrever sua pergunta "

                "sobre RAG para eu tentar ajudar."

            ),

            "fontes": [],

            "topico": ultimo_topico

        }





    # =====================================================

    # A. CONVERSA SOCIAL

    # =====================================================



    social = identificar_conversa_social(

        pergunta

    )



    if social:



        print(

            "💬 CONVERSA SOCIAL:",

            pergunta

        )



        return {

            "status": "ok",

            "modo": "social",

            "resposta": (

                responder_conversa_social(

                    social

                )

            ),

            "fontes": [],

            "topico": ultimo_topico

        }





    # =====================================================

    # B. IDENTIFICA INTENÇÃO

    # =====================================================



    intencao = identificar_intencao(

        pergunta

    )





    # =====================================================

    # C. CONTINUAÇÃO ESTRUTURADA

    # =====================================================



    if (

        ultimo_topico

        and intencao in [

            "resumo",

            "exemplo",

            "explicacao_simples"

        ]

    ):



        indice = buscar_chunk_por_fonte(

            ultimo_topico

        )



        if indice is not None:



            chunk = chunks[indice]



            resposta = resposta_da_secao(

                chunk,

                intencao

            )



            print(

                "📚 CONTINUAÇÃO DIRETA:",

                pergunta,

                "→",

                chunk["fonte"],

                "|",

                intencao

            )



            return {

                "status": "ok",

                "modo": "recuperacao",

                "resposta": resposta,

                "fontes": [

                    chunk["fonte"]

                ],

                "topico": (

                    chunk["fonte"]

                )

            }





    # =====================================================

    # D. INTERPRETAÇÃO DO TÓPICO ANTERIOR

    #

    # IMPORTANTE:

    # não chama Gemini automaticamente.

    # Isso deixa a resposta instantânea.

    # =====================================================



    if (

        ultimo_topico

        and intencao

        == "interpretacao"

    ):



        indice = buscar_chunk_por_fonte(

            ultimo_topico

        )



        if indice is not None:



            chunk = chunks[indice]



            print(

                "🧠 INTERPRETAÇÃO LOCAL:",

                pergunta,

                "→",

                chunk["fonte"]

            )



            return {

                "status": "ok",

                "modo": "recuperacao",

                "resposta": (

                    responder_interpretacao_local(

                        pergunta,

                        chunk

                    )

                ),

                "fontes": [

                    chunk["fonte"]

                ],

                "topico": (

                    chunk["fonte"]

                )

            }





    # =====================================================

    # E. FRASE AMBÍGUA COM TÓPICO ANTERIOR

    #

    # Aqui o Gemini pode ajudar a interpretar.

    # Uma única chamada.

    # =====================================================



    if (

        ultimo_topico

        and mensagem_ambigua(

            pergunta

        )

    ):



        indice = buscar_chunk_por_fonte(

            ultimo_topico

        )



        if indice is not None:



            chunk = chunks[indice]



            contexto = (

                montar_contexto_curto(

                    chunk

                )

            )



            resultado = chamar_gemini(

                pergunta=pergunta,

                contexto=contexto,

                fontes=[

                    chunk["fonte"]

                ],

                topico=chunk["fonte"]

            )



            if resultado is not None:

                return resultado



            return {

                "status": "precisa_esclarecimento",

                "modo": "limite",

                "resposta": (

                    "Não consegui entender com "

                    "segurança o que você quis dizer. "

                    "Pode reformular a pergunta?"

                ),

                "fontes": [],

                "topico": ultimo_topico

            }





    # =====================================================

    # F. RETRIEVAL

    # =====================================================



    (

        melhores_indices,

        melhor_indice,

        melhor_similaridade

    ) = fazer_retrieval(

        pergunta,

        quantidade=3

    )



    limite_minimo = (
        0.42
        if MODO_RENDER
        else 0.80
    )





    # =====================================================

    # G. FORA DA BASE

    # =====================================================



    if (

        melhor_similaridade

        < limite_minimo

    ):



        print(

            "❌ FORA DA BASE:",

            pergunta,

            "| similaridade:",

            round(

                float(

                    melhor_similaridade

                ),

                3

            )

        )



        return {

            "status": "limitado",

            "modo": "limite",

            "resposta": (

                "Não encontrei informação "

                "suficiente na minha base de "

                "conhecimento para responder isso."

            ),

            "fontes": [],

            "topico": None

        }





    # =====================================================

    # H. TÓPICO PRINCIPAL

    # =====================================================



    chunk_principal = chunks[

        melhor_indice

    ]



    topico_atual = (

        chunk_principal["fonte"]

    )





    # =====================================================

    # I. PERGUNTA DIRETA

    # =====================================================



    if eh_pergunta_direta(

        pergunta

    ):



        resposta = resposta_da_secao(

            chunk_principal,

            intencao

        )



        print(

            "📚 RECUPERAÇÃO DIRETA:",

            pergunta,

            "→",

            chunk_principal[

                "fonte"

            ],

            "| similaridade:",

            round(

                float(

                    melhor_similaridade

                ),

                3

            )

        )



        return {

            "status": "ok",

            "modo": "recuperacao",

            "resposta": resposta,

            "fontes": [

                chunk_principal[

                    "fonte"

                ]

            ],

            "topico": topico_atual

        }





    # =====================================================

    # J. PERGUNTA LIVRE

    #

    # Só agora Gemini entra.

    # =====================================================



    melhores_para_contexto = (

        melhores_indices[:2]

    )



    contexto = "\n\n---\n\n".join(

        montar_contexto_curto(

            chunks[indice]

        )

        for indice

        in melhores_para_contexto

    )



    fontes = [

        chunks[indice]["fonte"]

        for indice

        in melhores_para_contexto

    ]



    resultado = chamar_gemini(

        pergunta=pergunta,

        contexto=contexto,

        fontes=fontes,

        topico=topico_atual

    )



    if resultado is not None:

        return resultado





    # =====================================================

    # K. FALLBACK

    # =====================================================



    print(

        "⚠️ FALLBACK LOCAL:",

        pergunta

    )



    return {

        "status": "fallback",

        "modo": "recuperacao",

        "resposta": (

            resposta_da_secao(

                chunk_principal,

                "explicacao_simples"

            )

        ),

        "fontes": [

            chunk_principal[

                "fonte"

            ]

        ],

        "topico": topico_atual

    }