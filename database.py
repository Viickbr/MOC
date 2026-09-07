"""
database.py
-----------
Tudo que envolve o banco de dados fica aqui: conectar e criar a tabela.
Usamos SQLite porque ele não precisa de instalação de servidor — o banco
inteiro é um único arquivo (cfaq_moc.db) que aparece na pasta do projeto.

Só existe UMA tabela (questoes) — sem separação por prova, capitania
ou ano. Cada questão pode opcionalmente ter:
  - texto_base: um texto de apoio (ex: o artigo de uma questão de
    interpretação) — várias questões podem repetir o mesmo texto_base,
    já que muitas vezes uma mesma leitura embasa várias perguntas.
  - desenvolvimento: o passo a passo do cálculo (pra questões de
    Matemática), mostrado só depois que a pessoa responde.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "cfaq_moc.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disciplina TEXT NOT NULL,       -- "Português" ou "Matemática"
            texto_base TEXT,                -- texto de apoio, opcional (pode repetir entre questões)
            enunciado TEXT NOT NULL,
            alternativa_a TEXT NOT NULL,
            alternativa_b TEXT NOT NULL,
            alternativa_c TEXT NOT NULL,
            alternativa_d TEXT NOT NULL,
            resposta_correta TEXT NOT NULL, -- "A", "B", "C" ou "D"
            explicacao TEXT,                -- resumo de por que a resposta está certa
            desenvolvimento TEXT             -- passo a passo do cálculo, opcional (Matemática)
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Banco de dados pronto em: {DB_PATH}")
