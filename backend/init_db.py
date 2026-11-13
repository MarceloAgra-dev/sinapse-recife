"""Cria o banco de dados e carrega os dados de exemplo.

Uso (na raiz do projeto):  python backend/init_db.py
"""
import sqlite3

from db import caminho_banco, init_db

if __name__ == "__main__":
    init_db()
    con = sqlite3.connect(caminho_banco())
    print("Banco criado em:", caminho_banco())
    for tabela in ("instituicoes", "areas", "ods", "pesquisadores", "projetos", "projeto_ods", "contatos"):
        total = con.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
        print(f"  {tabela}: {total} registro(s)")
    con.close()
