"""Conexão com o banco de dados SQLite."""
import os
import sqlite3
from pathlib import Path

from flask import g

RAIZ = Path(__file__).resolve().parent.parent
PASTA_BANCO = RAIZ / "database"


def caminho_banco():
    # Pode ser trocado pela variável de ambiente SINAPSE_DB (usado nos testes)
    return os.environ.get("SINAPSE_DB", str(PASTA_BANCO / "sinapse.db"))


def get_db():
    """Abre (uma vez por requisição) a conexão com o banco."""
    if "db" not in g:
        g.db = sqlite3.connect(caminho_banco())
        g.db.row_factory = sqlite3.Row          # permite acessar colunas pelo nome
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(erro=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Cria as tabelas (schema.sql) e insere os dados de exemplo (seed.sql)."""
    conexao = sqlite3.connect(caminho_banco())
    for arquivo in ("schema.sql", "seed.sql"):
        conexao.executescript((PASTA_BANCO / arquivo).read_text(encoding="utf-8"))
    conexao.commit()
    conexao.close()
