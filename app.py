import re
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="public", static_url_path="")

limite_texto = 5000

palavras_chave = [
    ["nome", "baixo"],
    ["cargo", "baixo"],
    ["cpf", "alto"],
    ["salario", "alto"],
    ["bancario", "alto"],
    ["conta bancaria", "alto"],
    ["setor", "baixo"],
    ["despesa", "medio"],
    ["orcamento", "medio"],
    ["faturamento", "alto"],
    ["software", "baixo"],
    ["mensagem de erro", "baixo"],
    ["servidor", "alto"],
    ["codigo-fonte", "alto"],
    ["codigo fonte", "alto"],
    ["senha", "alto"],
    ["credencial", "alto"],
    ["token", "alto"],
    ["api key", "alto"],
    ["chave de api", "alto"],
    ["fornecedor", "baixo"],
    ["contrato", "medio"],
    ["valor do contrato", "alto"],
    ["clausula", "alto"],
    ["projeto", "medio"],
    ["cronograma", "medio"],
    ["produto nao lancado", "alto"],
    ["lancamento", "alto"],
    ["estrategia", "alto"],
    ["plano de expansao", "alto"],
    ["meta de vendas", "alto"],
    ["concorrente", "alto"],
]

octeto = r"(?:25[0-5]|2[0-4]\d|1?\d?\d)"

padroes = [
    ["CPF", r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "alto"],
    ["Cartão", r"\b(?:\d{4}[ -]?){3}\d{4}\b", "alto"],
    ["IP", r"\bip\b", "alto"],
    ["Endereço IP", r"\b(?:" + octeto + r"\.){3}" + octeto + r"\b", "alto"],
    ["Banco", r"\bbanco\b(?!\s+de\s+dados)", "alto"],
    ["Chave de API", r"\b(?:sk|pk)[-_][a-z0-9_-]{16,}\b|\bakia[a-z0-9]{16}\b|\bghp_[a-z0-9]{20,}\b", "alto"],
    ["Senha informada", r"\b(?:senha|password|pwd)\s*[:=]\s*\S+", "alto"],
    ["Agência", r"\bagencia\s*:?\s*\d{3,5}", "alto"],
    ["Conta", r"\bconta\s*(?:corrente\s*)?:?\s*\d{4,}", "alto"],
    ["Número de contrato", r"\bcontrato\D{0,12}\d{3,}", "medio"],
    ["Valor em R$", r"r\$\s*\d[\d.,]*", "medio"],
]

mensagens = {
    "BAIXO": "Não foram identificados os tipos de informações corporativas analisados pelo sistema. Ainda assim, revise o conteúdo antes de compartilhá-lo.",
    "MEDIO": "Esta informação contém dados internos que podem apresentar riscos à empresa. Evite compartilhar informações desnecessárias e verifique as regras de uso de IA da empresa antes do compartilhamento.",
    "ALTO": "Esta informação contém dados confidenciais, pessoais, estratégicos ou relacionados à segurança da empresa. Não compartilhe com uma IA pública. Remova os dados sensíveis ou utilize uma ferramenta de IA corporativa autorizada.",
}

com_acento = "áàãâéêíóõôúç"
sem_acento = "aaaaeeiooouc"


def tirar_acentos(texto):
    resultado = ""
    for letra in texto.lower():
        posicao = com_acento.find(letra)
        if posicao != -1:
            letra = sem_acento[posicao]
        resultado = resultado + letra
    return resultado


def buscar_palavras(texto):
    achados = []
    for palavra, risco in palavras_chave:
        if re.search(r"\b" + re.escape(palavra), texto):
            achados.append({"item": palavra, "risco": risco})
    return achados


def buscar_padroes(texto):
    achados = []
    for nome, regex, risco in padroes:
        if re.search(regex, texto):
            achados.append({"item": nome, "risco": risco})
    return achados


def definir_risco(achados):
    riscos = [achado["risco"] for achado in achados]
    if "alto" in riscos:
        return "ALTO"
    if "medio" in riscos:
        return "MEDIO"
    return "BAIXO"


def analisar(texto):
    limpo = tirar_acentos(texto)
    achados = buscar_palavras(limpo) + buscar_padroes(limpo)
    risco = definir_risco(achados)
    return {"risco": risco, "mensagem": mensagens[risco], "gatilhos": achados}


@app.route("/")
def inicio():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/analisar", methods=["POST"])
def rota_analisar():
    dados = request.get_json(silent=True) or {}
    texto = dados.get("texto", "")
    if not isinstance(texto, str) or texto.strip() == "":
        return jsonify({"erro": "Envie um texto para analisar."}), 400
    if len(texto) > limite_texto:
        return jsonify({"erro": "O texto passou do limite de 5000 caracteres."}), 400
    return jsonify(analisar(texto))


if __name__ == "__main__":
    app.run(debug=True)
