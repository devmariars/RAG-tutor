import os
from dotenv import load_dotenv

load_dotenv()

chave = os.getenv("GEMINI_API_KEY")

if chave:
    print("✅ Chave encontrada com sucesso!")
else:
    print("❌ Chave não encontrada.")