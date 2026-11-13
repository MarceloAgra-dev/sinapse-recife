"""Testes automáticos da API.  Rodar na raiz do projeto:  python -m unittest discover -s tests -v"""
import os
import sys
import tempfile
import unittest

# Usa um banco temporário, para não mexer no banco real
ARQUIVO_TEMP = os.path.join(tempfile.mkdtemp(), "teste.db")
os.environ["SINAPSE_DB"] = ARQUIVO_TEMP
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import app          # noqa: E402
from db import init_db       # noqa: E402


class TesteAPI(unittest.TestCase):
    def setUp(self):
        init_db()                       # banco novo e limpo a cada teste
        self.cliente = app.test_client()

    def test_saude_conecta_no_banco(self):
        r = self.cliente.get("/api/saude")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["banco"], "conectado")

    def test_lista_apenas_projetos_publicados(self):
        dados = self.cliente.get("/api/projetos").get_json()
        self.assertEqual(dados["total"], 6)          # o 7º é rascunho

    def test_filtros(self):
        self.assertEqual(self.cliente.get("/api/projetos?tipo=Tese").get_json()["total"], 2)
        self.assertEqual(self.cliente.get("/api/projetos?ods=9").get_json()["total"], 3)
        self.assertEqual(self.cliente.get("/api/projetos?q=sensores").get_json()["total"], 1)
        self.assertEqual(self.cliente.get("/api/projetos?instituicao=1").get_json()["total"], 2)

    def test_detalhe_respeita_nivel_de_detalhe(self):
        completo = self.cliente.get("/api/projetos/1").get_json()
        self.assertIsNotNone(completo["aplicacoes"])
        so_resumo = self.cliente.get("/api/projetos/3").get_json()
        self.assertIsNone(so_resumo["objetivos"])
        self.assertTrue(so_resumo["detalhes_apos_contato"])

    def test_projeto_inexistente_ou_rascunho(self):
        self.assertEqual(self.cliente.get("/api/projetos/999").status_code, 404)
        self.assertEqual(self.cliente.get("/api/projetos/7").status_code, 404)

    def test_criar_contato(self):
        corpo = {"projeto_id": 1, "nome": "Maria", "email": "maria@x.com", "organizacao": "Empresa X",
                 "interesse": "Parceria", "mensagem": "Olá!"}
        r = self.cliente.post("/api/contatos", json=corpo)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.cliente.get("/api/indicadores").get_json()["contatos"], 4)

    def test_contato_invalido(self):
        r = self.cliente.post("/api/contatos", json={"projeto_id": 1, "nome": "Maria"})
        self.assertEqual(r.status_code, 400)

    def test_login_e_cadastro_de_projeto(self):
        novo = {"titulo": "Teste", "resumo": "Resumo simples", "tipo": "Protótipo", "area_id": 1, "ods": [9]}
        self.assertEqual(self.cliente.post("/api/projetos", json=novo).status_code, 401)   # sem login
        self.assertEqual(self.cliente.post("/api/login", json={"email": "silva@exemplo.br", "senha": "errada"}).status_code, 401)
        self.assertEqual(self.cliente.post("/api/login", json={"email": "silva@exemplo.br", "senha": "senha123"}).status_code, 200)
        r = self.cliente.post("/api/projetos", json=novo)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(len(self.cliente.get("/api/meus-projetos").get_json()), 4)
        self.assertEqual(len(self.cliente.get("/api/meus-contatos").get_json()), 2)


if __name__ == "__main__":
    unittest.main()
