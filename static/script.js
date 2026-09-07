/*
 * script.js
 * ---------
 * Roda no navegador. Busca as questões na API do Flask e controla
 * o que aparece na tela — incluindo o painel de apoio lateral:
 *   - Se a questão tem texto_base, ele aparece no painel IMEDIATAMENTE
 *     (antes de responder), porque é preciso ler pra responder.
 *   - Se a questão tem desenvolvimento (cálculo), ele só aparece no
 *     painel DEPOIS de responder — senão entregaria a resposta.
 */

const elAreaConteudo = document.getElementById("area-conteudo");
const elCarregando = document.getElementById("carregando");
const elCorpoQuestao = document.getElementById("corpo-questao");
const elEtiquetaDisciplina = document.getElementById("etiqueta-disciplina");
const elEnunciado = document.getElementById("enunciado");
const elAlternativas = document.getElementById("alternativas");
const elBotaoResponder = document.getElementById("botao-responder");
const elPainelFeedback = document.getElementById("painel-feedback");
const elFeedbackStatus = document.getElementById("feedback-status");
const elFeedbackExplicacao = document.getElementById("feedback-explicacao");
const elBotaoProxima = document.getElementById("botao-proxima");
const elContagemAcertos = document.getElementById("contagem-acertos");
const elContagemErros = document.getElementById("contagem-erros");

const elPainelApoio = document.getElementById("painel-apoio");
const elPainelTextoBase = document.getElementById("painel-texto-base");
const elPainelTextoBaseConteudo = document.getElementById("painel-texto-base-conteudo");
const elPainelDesenvolvimento = document.getElementById("painel-desenvolvimento");
const elPainelDesenvolvimentoConteudo = document.getElementById("painel-desenvolvimento-conteudo");

let questaoAtualId = null;
let letraSelecionada = null;
let acertos = 0;
let erros = 0;

function atualizarPainelApoio() {
  // O painel (a coluna lateral) só aparece se pelo menos um dos dois
  // blocos (texto-base ou desenvolvimento) estiver visível.
  const algumBlocoVisivel =
    !elPainelTextoBase.classList.contains("oculto") ||
    !elPainelDesenvolvimento.classList.contains("oculto");

  elPainelApoio.classList.toggle("oculto", !algumBlocoVisivel);
  elAreaConteudo.classList.toggle("com-painel", algumBlocoVisivel);
}

async function buscarNovaQuestao() {
  elCorpoQuestao.classList.add("oculto");
  elPainelFeedback.classList.add("oculto");
  elCarregando.classList.remove("oculto");
  elCarregando.textContent = "Carregando questão…";
  letraSelecionada = null;

  // Reseta os dois blocos do painel a cada nova questão.
  elPainelTextoBase.classList.add("oculto");
  elPainelDesenvolvimento.classList.add("oculto");
  atualizarPainelApoio();

  const resposta = await fetch("/api/questao/aleatoria");
  const dados = await resposta.json();

  if (!resposta.ok) {
    elCarregando.textContent = dados.erro || "Não foi possível carregar uma questão.";
    return;
  }

  questaoAtualId = dados.id;
  elEtiquetaDisciplina.textContent = dados.disciplina;
  elEnunciado.textContent = dados.enunciado;

  if (dados.texto_base) {
    elPainelTextoBaseConteudo.textContent = dados.texto_base;
    elPainelTextoBase.classList.remove("oculto");
  }
  atualizarPainelApoio();

  montarAlternativas(dados.alternativas);

  elBotaoResponder.disabled = true;
  elCarregando.classList.add("oculto");
  elCorpoQuestao.classList.remove("oculto");
}

function montarAlternativas(alternativas) {
  elAlternativas.innerHTML = "";

  for (const letra of ["A", "B", "C", "D"]) {
    const texto = alternativas[letra];
    if (!texto) continue;

    const item = document.createElement("li");
    item.className = "alternativa";
    item.dataset.letra = letra;
    item.innerHTML = `
      <span class="alternativa-letra">${letra}</span>
      <span class="alternativa-texto">${texto}</span>
    `;
    item.addEventListener("click", () => selecionarAlternativa(letra));
    elAlternativas.appendChild(item);
  }
}

function selecionarAlternativa(letra) {
  letraSelecionada = letra;
  document.querySelectorAll(".alternativa").forEach((el) => {
    el.classList.toggle("selecionada", el.dataset.letra === letra);
  });
  elBotaoResponder.disabled = false;
}

async function enviarResposta() {
  if (!letraSelecionada || questaoAtualId === null) return;
  elBotaoResponder.disabled = true;

  const resposta = await fetch(`/api/questao/${questaoAtualId}/responder`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resposta: letraSelecionada }),
  });
  const dados = await resposta.json();

  marcarAlternativas(dados.resposta_correta);
  mostrarFeedback(dados);
  atualizarPlacar(dados.correta);

  if (dados.desenvolvimento) {
    elPainelDesenvolvimentoConteudo.textContent = dados.desenvolvimento;
    elPainelDesenvolvimento.classList.remove("oculto");
    atualizarPainelApoio();
  }
}

function marcarAlternativas(letraCorreta) {
  document.querySelectorAll(".alternativa").forEach((el) => {
    const letra = el.dataset.letra;
    if (letra === letraCorreta) {
      el.classList.add("correta");
    } else if (letra === letraSelecionada) {
      el.classList.add("incorreta");
    }
  });
}

function mostrarFeedback(dados) {
  elFeedbackStatus.textContent = dados.correta
    ? "✔ Você acertou!"
    : `✘ Você errou. A resposta certa era ${dados.resposta_correta}.`;
  elFeedbackStatus.className = "feedback-status " + (dados.correta ? "certo" : "errado");
  elFeedbackExplicacao.textContent = dados.explicacao;
  elPainelFeedback.classList.remove("oculto");
}

function atualizarPlacar(acertou) {
  if (acertou) {
    acertos += 1;
    elContagemAcertos.textContent = acertos;
  } else {
    erros += 1;
    elContagemErros.textContent = erros;
  }
}

elBotaoResponder.addEventListener("click", enviarResposta);
elBotaoProxima.addEventListener("click", buscarNovaQuestao);

buscarNovaQuestao();
