# Caderno de Bordo — Estudo CFAQ-MOC

Site de estudo: mostra uma questão, você responde, e ele mostra se
acertou + a explicação. Todas as questões ficam misturadas num banco
só — não há separação por prova, capitania ou ano.

O banco de dados é **reconstruído automaticamente** toda vez que o
site inicia, a partir de todos os arquivos `.json` da pasta `data/`.

## Painel de apoio (lateral)

Cada questão pode opcionalmente ter:

- **`texto_base`** — um texto de referência (ex: o artigo de uma
  questão de interpretação). Aparece no painel lateral **desde o
  início**, porque é preciso ler pra responder. Várias questões podem
  repetir o mesmo `texto_base` — é assim que várias perguntas usam o
  mesmo texto sem duplicar o enunciado.
- **`desenvolvimento`** — o passo a passo do cálculo (pra questões de
  Matemática). Só aparece no painel **depois que você responde** —
  senão entregaria a resposta de graça.

Se a questão não tiver nenhum dos dois campos, o painel simplesmente
não aparece, e a tela volta a ser de uma coluna só.

## Como rodar localmente

```bash
cd cfaq-moc-quiz
pip3 install -r requirements.txt --break-system-packages
python3 app.py
```

Abra **http://localhost:5000**. Pra parar: `Ctrl + C`.

### Acessar de outro aparelho na mesma rede Wi-Fi

1. `hostname -I` → pega o IP do seu PC (ex: 192.168.0.15).
2. No celular/notebook, na mesma rede: `http://SEU_IP:5000`
3. Se não conectar: `sudo ufw allow 5000`

## Hospedagem (Render — grátis, acessível de qualquer lugar)

1. Suba o projeto pro GitHub (`git add .`, `git commit`, `git push`).
2. Crie conta em render.com (pode usar login do GitHub).
3. New + → Web Service → conecte o repositório `cfaq-moc-quiz`.
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app:app`
6. Plano: Free.
7. Você recebe um link tipo `https://seu-app.onrender.com`.

**Atenção:** o plano grátis "dorme" após um tempo sem uso; a primeira
visita depois de um tempo parado demora uns 30-50s pra acordar.

## Como adicionar questões novas

1. Copie `data/modelo_novas_questoes.json` para um novo arquivo em
   `data/`, ex: `data/portugues_lote3.json`.
2. Preencha: `disciplina`, `enunciado`, as 4 `alternativas`,
   `resposta_correta` e `explicacao`.
3. Se a questão usa um texto de apoio (interpretação de texto):
   preencha `texto_base` com o texto completo. Se várias questões
   usam o MESMO texto, repita o mesmo conteúdo em `texto_base` em
   cada uma delas.
4. Se for uma questão de Matemática: preencha `desenvolvimento` com o
   passo a passo do cálculo, linha por linha (use `\n` pra pular
   linha dentro da string JSON). Se a questão não precisar (ex: uma
   questão de Português sem cálculo), pode apagar esse campo ou
   deixar como `""`.
5. Pra mais de uma questão no mesmo arquivo: depois do `}` que fecha
   uma questão, vírgula `,`, e cole outro bloco `{ ... }`. A última
   questão do arquivo não leva vírgula depois do `}`.
6. Salve. Localmente, rodar `python3 app.py` de novo já recarrega tudo.
7. Pra colocar no ar: `git add .`, `git commit -m "..."`, `git push`
   — o Render redeploya sozinho.

Pra testar um arquivo novo isoladamente antes de reiniciar o site
inteiro: `python3 seed_data.py data/seuarquivo.json`

### Conferir o total de questões
`curl http://localhost:5000/api/estatisticas`

## Estrutura do projeto

```
cfaq-moc-quiz/
├── app.py                              → back-end (Flask): rotas + reconstrói o banco ao iniciar
├── database.py                          → conexão com o banco + criação da tabela
├── seed_data.py                          → lê os .json de data/ e carrega no banco
├── requirements.txt                      → dependências (Flask + gunicorn)
├── .gitignore                            → arquivos que não vão pro Git
├── data/
│   ├── modelo_novas_questoes.json        → modelo vazio, copie pra criar questões novas
│   ├── questoes_exemplo.json             → questões de exemplo
│   ├── questoes_matematica_1.json        → 1º lote (matemática)
│   └── portugues_matematica_lote2.json   → 2º lote (interpretação de texto + matemática)
├── templates/
│   └── index.html                        → estrutura HTML: card da questão + painel de apoio
└── static/
    ├── style.css                          → visual, incluindo o layout de 2 colunas do painel
    └── script.js                          → lógica: busca questão, mostra/esconde o painel certo
```
