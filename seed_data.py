"""
seed_data.py
------------
Lê os arquivos .json da pasta data/ (cada um com uma LISTA de
questões) e carrega tudo no banco de dados.

A função principal é importar_pasta(): ela LIMPA a tabela de questões
e recarrega, do zero, a partir de TODOS os arquivos .json da pasta
data/ (menos o modelo_novas_questoes.json). Isso roda automaticamente
sempre que o site sobe (ver app.py) — o banco nunca fica desatualizado
em relação ao que está no Git.

Uso manual (linha de comando):
    python3 seed_data.py                     -> reconstrói tudo (igual ao app.py faz sozinho)
    python3 seed_data.py data/novo_lote.json  -> testa só um arquivo novo, sem mexer no resto
"""

import glob
import json
import sys
from database import get_connection, init_db

PASTA_DADOS = "data"
ARQUIVO_MODELO = "modelo_novas_questoes.json"


def carregar_arquivo(caminho_json):
    with open(caminho_json, encoding="utf-8") as f:
        return json.load(f)


def inserir_questoes(cursor, questoes):
    total = 0
    for q in questoes:
        cursor.execute("""
            INSERT INTO questoes (
                disciplina, texto_base, enunciado,
                alternativa_a, alternativa_b, alternativa_c, alternativa_d,
                resposta_correta, explicacao, desenvolvimento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            q["disciplina"],
            q.get("texto_base") or None,
            q["enunciado"],
            q["alternativas"]["A"],
            q["alternativas"]["B"],
            q["alternativas"]["C"],
            q["alternativas"]["D"],
            q["resposta_correta"],
            q.get("explicacao", ""),
            q.get("desenvolvimento") or None,
        ))
        total += 1
    return total


def importar(caminho_json):
    init_db()
    questoes = carregar_arquivo(caminho_json)
    conn = get_connection()
    cursor = conn.cursor()
    total = inserir_questoes(cursor, questoes)
    conn.commit()
    conn.close()
    print(f"{total} questões importadas de '{caminho_json}'.")


def importar_pasta(pasta=PASTA_DADOS):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questoes")

    caminhos = sorted(glob.glob(f"{pasta}/*.json"))
    total_geral = 0
    arquivos_usados = 0

    for caminho in caminhos:
        if caminho.endswith(ARQUIVO_MODELO):
            continue
        questoes = carregar_arquivo(caminho)
        total = inserir_questoes(cursor, questoes)
        total_geral += total
        arquivos_usados += 1
        print(f"  {caminho}: {total} questões")

    conn.commit()
    conn.close()
    print(f"Banco reconstruído: {total_geral} questões, de {arquivos_usados} arquivo(s) em '{pasta}/'.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        importar(sys.argv[1])
    else:
        importar_pasta()
