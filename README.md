# Verificador de risco para IA

Sistema que classifica o risco de um texto corporativo antes de ele ser enviado a uma inteligência artificial pública. O usuário cola o conteúdo, e o verificador indica se o risco é **baixo**, **médio** ou **alto** e mostra uma recomendação do que fazer.

Projeto desenvolvido para minha Faculdade de Cibersegurança na Cesar School, com o objetivo de reduzir o vazamento de informações da empresa por meio de ferramentas de IA.

## Como funciona

A análise combina duas técnicas:

- **Palavras-chave:** termos como `senha`, `salário`, `faturamento` ou `estratégia`.
- **Padrões (regex):** formatos como CPF, número de cartão, endereço IP, chave de API e valores em reais, mesmo quando o texto não diz o que são.

Antes da busca, o texto é convertido para minúsculas e os acentos são removidos, para que "Salário" e "salario" sejam tratados da mesma forma.

### Regra de classificação

| Situação encontrada | Resultado |
|---|---|
| Pelo menos um item de risco alto | Risco alto |
| Nenhum alto, mas pelo menos um médio | Risco médio |
| Apenas itens de baixo risco, ou nenhum | Risco baixo |

### Itens analisados por área

| Área | Baixo | Médio | Alto |
|---|---|---|---|
| RH | nome, cargo | | CPF, salário, dados bancários |
| Financeiro | setor | despesa, orçamento | faturamento, dados bancários |
| TI | software, mensagem de erro | | IP, servidor, código-fonte, senha, credencial, token, chave de API |
| Jurídico | fornecedor | número de contrato | valor de contrato, cláusulas |
| Projetos e estratégias | | projeto, cronograma | produto não lançado, estratégia de negócio |

## Funcionalidades

- Análise do texto com resultado visual por nível de risco.
- Lista dos itens que motivaram a classificação.
- Histórico de análises com alteração do risco, exclusão e contagem por nível.
- Histórico privado, salvo apenas no navegador de quem usa.
- Interface responsiva com fundo animado.

## Tecnologias

- Python 3 e Flask (backend)
- HTML, CSS e JavaScript (front-end)
- Vercel (hospedagem)

## Estrutura do projeto

```
verificador-risco/
├── app.py
├── requirements.txt
├── test_app.py
├── LICENSE
├── README.md
└── public/
    ├── index.html
    ├── estilo.css
    ├── script.js
    └── fundo.js
```

| Arquivo | Função |
|---|---|
| `app.py` | Regras de análise em Python e a rota da API |
| `requirements.txt` | Dependências do Python |
| `public/index.html` | Estrutura da página |
| `public/estilo.css` | Visual |
| `public/script.js` | Comunicação com a API e histórico |
| `public/fundo.js` | Animação de fundo |

## Como executar localmente

Com o Python instalado, abra um terminal na pasta do projeto e rode:

```
py -m pip install -r requirements.txt
py app.py
```

Em Linux ou macOS, use `python3` no lugar de `py`. Depois, abra `http://127.0.0.1:5000` no navegador.

## Como publicar na Vercel

1. Envie os arquivos do projeto para um repositório no GitHub, com `app.py` e `requirements.txt` na raiz.
2. Em [vercel.com](https://vercel.com), entre com a conta do GitHub.
3. Clique em **Add New... > Project** e importe o repositório.
4. Mantenha as configurações sugeridas (a Vercel detecta o Flask sozinha) e clique em **Deploy**.

## API

### `POST /api/analisar`

Corpo da requisição:

```json
{ "texto": "O CPF do funcionário é 123.456.789-09" }
```

Resposta:

```json
{
  "risco": "ALTO",
  "mensagem": "Esta informação contém dados confidenciais...",
  "gatilhos": [
    { "item": "cpf", "risco": "alto" },
    { "item": "CPF", "risco": "alto" }
  ]
}
```

Em caso de texto vazio ou acima de 5000 caracteres, a resposta tem status `400` e o campo `erro`.

## Privacidade

O texto é enviado ao servidor apenas para a análise e não é gravado. O histórico guarda somente o nível de risco e os itens encontrados, e fica salvo no navegador do usuário (`localStorage`). Cada pessoa vê apenas as próprias análises. Em demonstrações, use dados fictícios.

## Limitações

- O sistema trabalha com palavras e padrões, então não entende o contexto do texto.
- Pode gerar alarmes falsos. Foi pensado para errar para o lado da cautela.
- Conceitos como "estratégia de negócio" só são detectados quando as palavras da lista aparecem.
- Serve como apoio à decisão, não substitui uma política de segurança da informação.

## Base dos critérios

As leis e orientações consultadas não trazem uma tabela que classifique cada item como baixo, médio ou alto. Por isso, o grupo definiu critérios próprios, fundamentados em:

- Lei Geral de Proteção de Dados Pessoais (LGPD), Lei nº 13.709/2018
- Guia Orientativo sobre Segurança da Informação para Agentes de Tratamento de Pequeno Porte, da ANPD
- Orientação de Segurança da Informação e Cibernética OSIC 06/2023, do GSI

## Licença

Todos os direitos reservados. O código pode ser visualizado para fins de avaliação e estudo, mas não pode ser copiado, modificado, distribuído ou usado comercialmente sem autorização por escrito dos autores. Consulte o arquivo [LICENSE](LICENSE).

## Autoria

Feito por SalonSec.
