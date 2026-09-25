import os

from flask import Flask, render_template, request, jsonify, session
from rag_engine import responder_pergunta

app = Flask(__name__)

# Chave usada pelo Flask para proteger os dados da sessão.
# Se não existir uma chave no .env, usamos esta apenas
# para o projeto local de portfólio.
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "rag-tutor-chave-local"
)


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@app.route("/")
def inicio():

    return render_template("index.html")


# =========================================================
# PERGUNTAS PARA O RAG
# =========================================================

@app.route("/perguntar", methods=["POST"])
def perguntar():

    dados = request.get_json()

    pergunta = dados["pergunta"]

    # Recupera o último tópico desta conversa, se existir.
    ultimo_topico = session.get("ultimo_topico")

    # Envia a pergunta e o tópico anterior para o RAG.
    resultado = responder_pergunta(
        pergunta,
        ultimo_topico
    )

    # Se o RAG identificou um tópico, guarda para
    # possíveis perguntas de continuação.
    if resultado.get("topico"):
        session["ultimo_topico"] = resultado["topico"]

    return jsonify(resultado)


# =========================================================
# INICIA O FLASK
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)