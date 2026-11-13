# Sinapse Recife - Hub de Inovação e Pesquisa de Recife

Projeto AV2 da disciplina **Desenvolvimento de Aplicações para Internet** (ADS, UNINASSAU, Turma A - Noite).
Desafio do Banco de Oportunidades da Prefeitura do Recife (Plataforma Coreto).

> Quando o conhecimento se conecta, a cidade pensa melhor.

O Hub reúne projetos e pesquisas das universidades de Recife em um só lugar, com busca e filtros, perfil
padronizado de cada projeto e contato direto com os pesquisadores.

## Equipe

| Integrante | Matrícula |
|---|---|
| Marcelo de Freitas Agra Filho | 01873792 |
| Natalia Torres Florentino | 01866152 |

## Tecnologias

- **Front-end:** HTML, CSS e JavaScript (Checkpoint 3)
- **Back-end:** Python + Flask (API REST)
- **Banco de dados:** SQLite
- **Protótipo (AV1):** Figma

## Estrutura do repositório

```
sinapse-recife/
├── backend/        API Flask (app.py), conexão com o banco (db.py) e script de criação (init_db.py)
├── database/       schema.sql (DDL), seed.sql (dados de exemplo) e modelagem.md (diagrama)
├── frontend/       Interface web (página provisória por enquanto)
├── tests/          Testes automáticos da API
├── requirements.txt
└── README.md
```

## Pré-requisitos

- Python 3.10 ou superior (<https://www.python.org/downloads/>)
- Um terminal (Terminal no Mac/Linux; PowerShell ou Prompt de Comando no Windows)

## Como rodar

Abra o terminal dentro da pasta do projeto e execute os comandos do seu sistema.

**Mac / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python backend/init_db.py
python backend/app.py
```

**Windows (Prompt de Comando)**

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python backend/init_db.py
python backend/app.py
```

No PowerShell, a ativação do ambiente virtual é `venv\Scripts\Activate.ps1`. Se o Windows bloquear a execução do script, rode antes `Set-ExecutionPolicy -Scope Process RemoteSigned`.

O comando `init_db.py` cria o arquivo do banco (`database/sinapse.db`) e carrega os dados de exemplo. Rodá-lo de novo recria o banco do zero.

Com a API em execução, acesse <http://127.0.0.1:5001/api/saude>. A resposta deve mostrar `"banco": "conectado"`. Para encerrar, pressione `Ctrl + C` no terminal.

## Testes

Com o ambiente virtual ativado (o mesmo comando vale para todos os sistemas):

```bash
python -m unittest discover -s tests -v
```

## Endpoints principais

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/saude` | Verifica API e conexão com o banco |
| GET | `/api/projetos` | Lista projetos publicados. Filtros: `?q=` `&area=` `&instituicao=` `&tipo=` `&ods=` |
| GET | `/api/projetos/<id>` | Perfil do projeto (respeita o nível de detalhe público) |
| POST | `/api/projetos` | Cadastra projeto (pesquisador logado) |
| POST | `/api/contatos` | Envia mensagem ao pesquisador |
| POST | `/api/login` · `/api/logout` | Acesso do pesquisador |
| GET | `/api/meus-projetos` · `/api/meus-contatos` | Painel do pesquisador (logado) |
| GET | `/api/areas` · `/api/instituicoes` · `/api/ods` | Listas para os filtros |
| GET | `/api/indicadores` | Números da página inicial |

Os dados do banco são fictícios. Login de exemplo para testar a área do pesquisador: `silva@exemplo.br` / `senha123`.

## Andamento (AV2)

- [x] **Checkpoint 1:** repositório e modelagem lógica / DDL do banco (`database/`)
- [x] **Checkpoint 2:** endpoints principais e conexão com o banco funcionando (`backend/`)
- [ ] **Checkpoint 3:** front-end consumindo o back-end (MVP integrado)
- [ ] **Apresentação final:** 01/12 a 08/12/2026
