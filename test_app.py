import unittest

from app import app, analisar, tirar_acentos


def itens(resultado):
    return [gatilho["item"] for gatilho in resultado["gatilhos"]]


class TestAnalise(unittest.TestCase):
    def test_risco_alto(self):
        texto = "O servidor é 192.168.0.15, a senha: Admin@2024. CPF 123.456.789-09, salário R$ 8.500,00."
        resultado = analisar(texto)
        self.assertEqual(resultado["risco"], "ALTO")
        for esperado in ["servidor", "senha", "cpf", "salario", "CPF", "Endereço IP", "Senha informada", "Valor em R$"]:
            self.assertIn(esperado, itens(resultado))

    def test_risco_medio(self):
        resultado = analisar("O projeto Aurora tem cronograma e orçamento de R$ 15.000,00.")
        self.assertEqual(resultado["risco"], "MEDIO")
        self.assertNotIn("ALTO", resultado["risco"])

    def test_risco_baixo(self):
        resultado = analisar("Mensagem de erro no software do setor.")
        self.assertEqual(resultado["risco"], "BAIXO")
        self.assertEqual(itens(resultado), ["setor", "software", "mensagem de erro"])

    def test_texto_sem_nada_e_baixo(self):
        resultado = analisar("Bom dia, tudo bem?")
        self.assertEqual(resultado["risco"], "BAIXO")
        self.assertEqual(resultado["gatilhos"], [])

    def test_cpf_so_com_numeros(self):
        resultado = analisar("Segue 52998224725 para o cadastro.")
        self.assertEqual(resultado["risco"], "ALTO")
        self.assertEqual(itens(resultado), ["CPF"])

    def test_cartao(self):
        resultado = analisar("Cartão 4111 1111 1111 1111")
        self.assertIn("Cartão", itens(resultado))

    def test_banco_de_dados_nao_dispara(self):
        resultado = analisar("Vou fazer o backup do banco de dados amanhã.")
        self.assertEqual(resultado["risco"], "BAIXO")

    def test_banco_sozinho_dispara(self):
        resultado = analisar("Os dados do banco Itaú estão na planilha.")
        self.assertEqual(resultado["risco"], "ALTO")

    def test_acentos_e_maiusculas(self):
        resultado = analisar("INFORMAÇÕES SOBRE O SALÁRIO E A ESTRATÉGIA")
        self.assertEqual(resultado["risco"], "ALTO")
        self.assertIn("salario", itens(resultado))
        self.assertIn("estrategia", itens(resultado))

    def test_ip_invalido(self):
        resultado = analisar("Número de versão 300.1.2.3")
        self.assertNotIn("Endereço IP", itens(resultado))

    def test_ip_valido(self):
        resultado = analisar("Acesse 10.0.0.1")
        self.assertIn("Endereço IP", itens(resultado))

    def test_palavra_dentro_de_outra_nao_dispara(self):
        resultado = analisar("O tipo de recipiente é plástico.")
        self.assertNotIn("IP", itens(resultado))

    def test_tirar_acentos(self):
        self.assertEqual(tirar_acentos("Ação Órgão Çá"), "acao orgao ca")


class TestRotas(unittest.TestCase):
    def setUp(self):
        self.cliente = app.test_client()

    def test_pagina_inicial(self):
        self.assertEqual(self.cliente.get("/").status_code, 200)

    def test_analisar_ok(self):
        resposta = self.cliente.post("/api/analisar", json={"texto": "senha: abc123"})
        self.assertEqual(resposta.status_code, 200)
        dados = resposta.get_json()
        self.assertEqual(dados["risco"], "ALTO")
        self.assertIn("mensagem", dados)

    def test_texto_vazio(self):
        resposta = self.cliente.post("/api/analisar", json={"texto": "   "})
        self.assertEqual(resposta.status_code, 400)
        self.assertIn("erro", resposta.get_json())

    def test_texto_grande_demais(self):
        resposta = self.cliente.post("/api/analisar", json={"texto": "a" * 5001})
        self.assertEqual(resposta.status_code, 400)

    def test_corpo_sem_json(self):
        resposta = self.cliente.post("/api/analisar", data="texto solto")
        self.assertEqual(resposta.status_code, 400)

    def test_texto_nao_e_string(self):
        resposta = self.cliente.post("/api/analisar", json={"texto": 123})
        self.assertEqual(resposta.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
