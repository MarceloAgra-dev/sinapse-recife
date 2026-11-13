# Modelagem do Banco de Dados - Sinapse Recife

Banco: **SQLite** · Scripts: [`schema.sql`](schema.sql) (criação) e [`seed.sql`](seed.sql) (dados de exemplo).

## Modelo lógico (diagrama entidade-relacionamento)

```mermaid
erDiagram
    INSTITUICOES ||--o{ PESQUISADORES : "tem"
    PESQUISADORES ||--o{ PROJETOS : "cadastra"
    AREAS ||--o{ PROJETOS : "classifica"
    PROJETOS ||--o{ PROJETO_ODS : "possui"
    ODS ||--o{ PROJETO_ODS : "aparece em"
    PROJETOS ||--o{ CONTATOS : "recebe"

    INSTITUICOES {
        int id PK
        text nome UK
        text sigla UK
    }
    AREAS {
        int id PK
        text nome UK
    }
    ODS {
        int id PK
        int numero UK
        text nome
    }
    PESQUISADORES {
        int id PK
        text nome
        text email UK
        text senha_hash
        text departamento
        int instituicao_id FK
    }
    PROJETOS {
        int id PK
        text titulo
        text resumo
        text objetivos
        text aplicacoes
        text tipo
        text maturidade
        text nivel_detalhe
        text status
        int area_id FK
        int pesquisador_id FK
        text criado_em
    }
    PROJETO_ODS {
        int projeto_id PK, FK
        int ods_id PK, FK
    }
    CONTATOS {
        int id PK
        int projeto_id FK
        text nome
        text email
        text organizacao
        text interesse
        text mensagem
        text criado_em
    }
```

## Dicionário de dados (resumo)

| Tabela | Finalidade | Relacionamentos |
|---|---|---|
| `instituicoes` | Universidades e centros parceiros (UFPE, UPE, IFPE, CESAR School) | 1 instituição : N pesquisadores |
| `areas` | Áreas do conhecimento usadas nos filtros | 1 área : N projetos |
| `ods` | Objetivos de Desenvolvimento Sustentável da ONU | N:N com projetos (`projeto_ods`) |
| `pesquisadores` | Usuários que cadastram projetos; senha guardada como hash | 1 pesquisador : N projetos |
| `projetos` | Pesquisas publicadas no Hub | N:N com ODS; 1 projeto : N contatos |
| `projeto_ods` | Tabela associativa entre projetos e ODS | chave composta (`projeto_id`, `ods_id`) |
| `contatos` | Pedidos de contato enviados aos pesquisadores | N contatos : 1 projeto |

## Regras de negócio no banco

- `projetos.tipo` aceita apenas: Tese, Dissertação, Protótipo, Patente, Projeto.
- `projetos.status`: `rascunho` ou `publicado` (só publicados aparecem na busca).
- `projetos.nivel_detalhe` (`resumo`, `resumo_objetivos`, `completo`) controla o que fica público, protegendo a propriedade intelectual.
- `contatos.interesse` aceita: Parceria, Projeto-piloto, Informações.
- Chaves estrangeiras ativas (`PRAGMA foreign_keys = ON`); apagar um projeto apaga seus contatos e vínculos com ODS.
- A instituição do projeto é obtida pelo pesquisador responsável, evitando dado repetido (3ª forma normal).
