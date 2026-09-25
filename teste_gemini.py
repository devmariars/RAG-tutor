import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

chave = os.getenv("GEMINI_API_KEY")

cliente = genai.Client(api_key=chave)

resposta = cliente.models.generate_content(
    model="gemini-3.6-flash",
    contents="Responda apenas: Conexão funcionando!"
)

print(resposta.text)