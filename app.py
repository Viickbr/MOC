"""
app.py
------
O "back-end": um servidor web pequeno que faz três coisas:
  1. Ao iniciar, reconstrói o banco de dados a partir dos arquivos
     .json da pasta data/ (ver seed_data.py) — assim o site sempre
     reflete o que está salvo no Git, sem passo manual.
  2. Entrega a página HTML (a interface que você vê no navegador).
  3. Responde pedidos de dados em formato JSON (a "API").

Rodar localmente com: python3 app.py
Depois abrir no navegador: http://localhost:5000
"""

import os
from flask import Flask, jsonify, request, render_template
from database import get_connection
from seed_data import importar_pasta

app = Flask(__name__)

# Roda sempre que este arquivo é carregado — local ou hospedado.
importar_pasta()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/questao/aleatoria")
def questao_aleatoria():
    """Devolve UMA questão aleatória. Manda o texto_base (se existir)
    porque ele é necessário PRA LER a questão — mas NÃO manda
    resposta_correta, explicacao nem desenvolvimento, que só são
    revelados depois que a pessoa responde (rota /responder)."""
    conn = get_connection()
    questao = conn.execute(
        "SELECT * FROM questoes ORDER BY RANDOM() LIMIT 1"
    ).fetchone()
    conn.close()

    if questao is None:
        return jsonify({"erro": "Nenhuma questão cadastrada ainda."}), 404

    return jsonify({
        "id": questao["id"],
        "disciplina": questao["disciplina"],
        "texto_base": questao["texto_base"],  # pode vir None/null — o front trata isso
        "enunciado": questao["enunciado"],
        "alternativas": {
            "A": questao["alternativa_a"],
            "B": questao["alternativa_b"],
            "C": questao["alternativa_c"],
            "D": questao["alternativa_d"],
        },
    })


@app.route("/api/questao/<int:questao_id>/responder", methods=["POST"])
def responder(questao_id):
    """Confere a resposta e devolve o resultado + explicação +
    desenvolvimento do cálculo (quando existir)."""
    corpo = request.get_json(silent=True) or {}
    resposta_usuario = (corpo.get("resposta") or "").strip().upper()

    conn = get_connection()
    questao = conn.execute(
        "SELECT * FROM questoes WHERE id = ?", (questao_id,)
    ).fetchone()
    conn.close()

    if questao is None:
        return jsonify({"erro": "Questão não encontrada."}), 404

    correta = resposta_usuario == questao["resposta_correta"]

    return jsonify({
        "correta": correta,
        "resposta_correta": questao["resposta_correta"],
        "explicacao": questao["explicacao"] or "Ainda não há explicação cadastrada para esta questão.",
        "desenvolvimento": questao["desenvolvimento"],  # pode vir None/null
    })


@app.route("/api/estatisticas")
def estatisticas():
    conn = get_connection()
    total_questoes = conn.execute("SELECT COUNT(*) AS total FROM questoes").fetchone()["total"]
    conn.close()
    return jsonify({"total_questoes": total_questoes})


if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", debug=True, port=porta)
