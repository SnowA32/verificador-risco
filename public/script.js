const chave = "historico-risco-ia";
const nomes = { BAIXO: "Baixo", MEDIO: "Médio", ALTO: "Alto" };
const exemplos = [
  "Preciso de ajuda com o código-fonte do sistema. O servidor interno é 192.168.0.15, a senha: Admin@2024 e o token está no arquivo. O CPF do funcionário é 123.456.789-09 e o salário dele é R$ 8.500,00.",
  "O projeto Aurora tem cronograma até março e o orçamento da despesa de viagem ficou em R$ 15.000,00.",
  "Preciso entender uma mensagem de erro que apareceu no software de planilhas usado pelo setor."
];

const el = (id) => document.getElementById(id);
let historico = lerHistorico();

function lerHistorico() {
  try {
    const dados = JSON.parse(localStorage.getItem(chave));
    return Array.isArray(dados) ? dados : [];
  } catch (e) {
    return [];
  }
}

function gravarHistorico() {
  try {
    localStorage.setItem(chave, JSON.stringify(historico));
  } catch (e) {}
}

async function enviar(texto) {
  const resposta = await fetch("/api/analisar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto })
  });
  const dados = await resposta.json();
  if (!resposta.ok) throw new Error(dados.erro || "Não foi possível analisar o texto.");
  return dados;
}

function criarChip(gatilho) {
  const li = document.createElement("li");
  li.className = "chip " + gatilho.risco;
  li.textContent = gatilho.item;
  return li;
}

function mostrarResultado(r) {
  el("medidor").dataset.risco = r.risco;
  el("vazio").hidden = true;
  el("resultado").hidden = false;
  el("veredito").textContent = "Risco " + nomes[r.risco].toLowerCase();
  el("recomendacao").textContent = r.mensagem;
  const lista = el("gatilhos");
  lista.replaceChildren();
  if (r.gatilhos.length === 0) {
    const vazio = document.createElement("li");
    vazio.className = "apoio";
    vazio.textContent = "Nenhum item encontrado";
    lista.appendChild(vazio);
  }
  r.gatilhos.forEach((g) => lista.appendChild(criarChip(g)));
}

function desenharTotais() {
  const contar = (nivel) => historico.filter((h) => h.risco === nivel).length;
  const itens = [["Análises", historico.length], ["Alto", contar("ALTO")], ["Médio", contar("MEDIO")], ["Baixo", contar("BAIXO")]];
  const area = el("totais");
  area.replaceChildren();
  itens.forEach(([rotulo, valor]) => {
    const bloco = document.createElement("div");
    const numero = document.createElement("strong");
    numero.textContent = valor;
    bloco.append(numero, rotulo);
    area.appendChild(bloco);
  });
}

function criarLinha(item, i) {
  const tr = document.createElement("tr");
  const celula = (conteudo) => {
    const td = document.createElement("td");
    if (conteudo instanceof Node) td.appendChild(conteudo);
    else td.textContent = conteudo;
    tr.appendChild(td);
    return td;
  };

  celula(String(i + 1));
  celula(item.data);

  const selo = document.createElement("span");
  selo.className = "selo " + item.risco;
  selo.textContent = nomes[item.risco];
  celula(selo);

  celula(item.gatilhos.length ? item.gatilhos.join(", ") : "nenhum");

  const seletor = document.createElement("select");
  seletor.setAttribute("aria-label", "Alterar o risco da análise " + (i + 1));
  Object.keys(nomes).forEach((nivel) => {
    const op = document.createElement("option");
    op.value = nivel;
    op.textContent = nomes[nivel];
    op.selected = nivel === item.risco;
    seletor.appendChild(op);
  });
  seletor.addEventListener("change", () => {
    historico[i].risco = seletor.value;
    gravarHistorico();
    desenharHistorico();
  });

  const excluir = document.createElement("button");
  excluir.type = "button";
  excluir.className = "leve";
  excluir.textContent = "Excluir";
  excluir.addEventListener("click", () => {
    historico.splice(i, 1);
    gravarHistorico();
    desenharHistorico();
  });

  const acoes = celula(seletor);
  acoes.appendChild(excluir);
  return tr;
}

function desenharHistorico() {
  const corpo = el("hist");
  corpo.replaceChildren();
  historico.forEach((item, i) => corpo.appendChild(criarLinha(item, i)));
  const vazio = historico.length === 0;
  el("hist-vazio").hidden = !vazio;
  el("tabela").hidden = vazio;
  el("limpar").hidden = vazio;
  desenharTotais();
}

function mostrarErro(mensagem) {
  el("erro").textContent = mensagem;
  el("erro").hidden = mensagem === "";
}

el("analisar").addEventListener("click", async () => {
  const texto = el("texto").value.trim();
  mostrarErro("");
  if (texto === "") {
    mostrarErro("Cole um texto antes de analisar.");
    el("texto").focus();
    return;
  }
  const botao = el("analisar");
  botao.disabled = true;
  botao.textContent = "Analisando...";
  try {
    const r = await enviar(texto);
    mostrarResultado(r);
    historico.push({
      risco: r.risco,
      gatilhos: r.gatilhos.map((g) => g.item),
      data: new Date().toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" })
    });
    gravarHistorico();
    desenharHistorico();
  } catch (e) {
    mostrarErro(e.message);
  } finally {
    botao.disabled = false;
    botao.textContent = "Analisar texto";
  }
});

document.querySelectorAll("[data-exemplo]").forEach((botao) => {
  botao.addEventListener("click", () => {
    el("texto").value = exemplos[Number(botao.dataset.exemplo)];
    el("texto").focus();
  });
});

el("limpar").addEventListener("click", () => {
  historico = [];
  gravarHistorico();
  desenharHistorico();
});

desenharHistorico();
