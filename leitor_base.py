from pathlib import Path

pasta_base = Path(__file__).parent / "base-conhecimento"

arquivos = sorted(pasta_base.glob("*.txt"))

print(f"Encontrei {len(arquivos)} arquivos.\n")

for arquivo in arquivos:
    conteudo = arquivo.read_text(encoding="utf-8")

    print(f"📄 {arquivo.name}")
    print(conteudo[:120].replace("\n", " ") + "...")
    print("-" * 50)