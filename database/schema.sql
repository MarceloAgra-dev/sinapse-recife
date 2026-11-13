-- =====================================================================
-- Sinapse Recife - Hub de Inovação e Pesquisa de Recife
-- DDL (criação do banco de dados) - SQLite
-- =====================================================================
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS contatos;
DROP TABLE IF EXISTS projeto_ods;
DROP TABLE IF EXISTS projetos;
DROP TABLE IF EXISTS pesquisadores;
DROP TABLE IF EXISTS ods;
DROP TABLE IF EXISTS areas;
DROP TABLE IF EXISTS instituicoes;

-- Instituições de ensino e pesquisa parceiras (UFPE, UPE, IFPE, CESAR School...)
CREATE TABLE instituicoes (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    nome  TEXT NOT NULL UNIQUE,
    sigla TEXT NOT NULL UNIQUE
);

-- Áreas do conhecimento (filtro da busca)
CREATE TABLE areas (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

-- Objetivos de Desenvolvimento Sustentável da ONU
CREATE TABLE ods (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    numero INTEGER NOT NULL UNIQUE CHECK (numero BETWEEN 1 AND 17),
    nome   TEXT NOT NULL
);

-- Pesquisadores: usuários que cadastram projetos (área do pesquisador)
CREATE TABLE pesquisadores (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    nome           TEXT NOT NULL,
    email          TEXT NOT NULL UNIQUE,
    senha_hash     TEXT NOT NULL,
    departamento   TEXT,
    instituicao_id INTEGER NOT NULL,
    FOREIGN KEY (instituicao_id) REFERENCES instituicoes (id)
);

-- Projetos e pesquisas publicados no Hub
CREATE TABLE projetos (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo         TEXT NOT NULL,
    resumo         TEXT NOT NULL,                 -- linguagem simples (obrigatório)
    objetivos      TEXT,
    aplicacoes     TEXT,
    tipo           TEXT NOT NULL
                   CHECK (tipo IN ('Tese','Dissertação','Protótipo','Patente','Projeto')),
    maturidade     TEXT,                          -- ex.: ideia, protótipo, piloto
    nivel_detalhe  TEXT NOT NULL DEFAULT 'resumo' -- proteção da propriedade intelectual
                   CHECK (nivel_detalhe IN ('resumo','resumo_objetivos','completo')),
    status         TEXT NOT NULL DEFAULT 'rascunho'
                   CHECK (status IN ('rascunho','publicado')),
    area_id        INTEGER NOT NULL,
    pesquisador_id INTEGER NOT NULL,
    criado_em      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (area_id)        REFERENCES areas (id),
    FOREIGN KEY (pesquisador_id) REFERENCES pesquisadores (id)
);

-- Relação N:N entre projetos e ODS
CREATE TABLE projeto_ods (
    projeto_id INTEGER NOT NULL,
    ods_id     INTEGER NOT NULL,
    PRIMARY KEY (projeto_id, ods_id),
    FOREIGN KEY (projeto_id) REFERENCES projetos (id) ON DELETE CASCADE,
    FOREIGN KEY (ods_id)     REFERENCES ods (id)
);

-- Pedidos de contato enviados a um projeto (formulário de contato)
CREATE TABLE contatos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id  INTEGER NOT NULL,
    nome        TEXT NOT NULL,
    email       TEXT NOT NULL,
    organizacao TEXT NOT NULL,
    interesse   TEXT NOT NULL
                CHECK (interesse IN ('Parceria','Projeto-piloto','Informações')),
    mensagem    TEXT NOT NULL,
    criado_em   TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (projeto_id) REFERENCES projetos (id) ON DELETE CASCADE
);

-- Índices para acelerar buscas e filtros
CREATE INDEX idx_projetos_area    ON projetos (area_id);
CREATE INDEX idx_projetos_status  ON projetos (status);
CREATE INDEX idx_projetos_pesq    ON projetos (pesquisador_id);
CREATE INDEX idx_contatos_projeto ON contatos (projeto_id);
