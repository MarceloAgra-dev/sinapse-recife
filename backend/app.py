"""API do Sinapse Recife - Hub de Inovação e Pesquisa de Recife.

Para rodar (na raiz do projeto):  python backend/app.py
"""
import os
from functools import wraps

from flask import Flask, jsonify, request, session
from werkzeug.security import check_password_hash

from db import close_db, get_db

PASTA_FRONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")

app = Flask(__name__, static_folder=PASTA_FRONT, static_url_path="")
app.secret_key = os.environ.get("SECRET_KEY", "chave-de-desenvolvimento")
app.json.ensure_ascii = False          # mostra acentos corretamente no JSON
app.teardown_appcontext(close_db)

TIPOS = ("Tese", "Dissertação", "Protótipo", "Patente", "Projeto")
INTERESSES = ("Parceria", "Projeto-piloto", "Informações")
NIVEIS = ("resumo", "resumo_objetivos", "completo")
STATUS = ("rascunho", "publicado")


# ----------------------------------------------------------------- utilitários
def erro(mensagem, codigo=400):
    return jsonify({"erro": mensagem}), codigo


def login_obrigatorio(funcao):
    @wraps(funcao)
    def interna(*args, **kwargs):
        if "pesquisador_id" not in session:
            return erro("Faça login para continuar.", 401)
        return funcao(*args, **kwargs)
    return interna


def lista_ods(texto):
    return [] if not texto else [f"ODS {n}" for n in sorted(int(x) for x in texto.split(","))]


SELECT_PROJETOS = """
    SELECT p.id, p.titulo, p.resumo, p.tipo, p.maturidade, p.status,
           a.nome AS area, i.sigla AS instituicao, pe.nome AS pesquisador,
           (SELECT group_concat(o.numero, ',')
              FROM projeto_ods po JOIN ods o ON o.id = po.ods_id
             WHERE po.projeto_id = p.id) AS ods
      FROM projetos p
      JOIN areas a          ON a.id  = p.area_id
      JOIN pesquisadores pe ON pe.id = p.pesquisador_id
      JOIN instituicoes i   ON i.id  = pe.instituicao_id
"""


def projeto_para_dict(linha):
    d = dict(linha)
    d["ods"] = lista_ods(d["ods"])
    return d


# ---------------------------------------------------------------------- páginas
@app.get("/")
def pagina_inicial():
    return app.send_static_file("index.html")


# ------------------------------------------------------------------- diagnóstico
@app.get("/api/saude")
def saude():
    """Confirma que a API está no ar e conectada ao banco."""
    get_db().execute("SELECT 1").fetchone()
    return jsonify({"status": "ok", "banco": "conectado"})


# ----------------------------------------------------------- listas para filtros
@app.get("/api/areas")
def listar_areas():
    linhas = get_db().execute("SELECT id, nome FROM areas ORDER BY nome").fetchall()
    return jsonify([dict(l) for l in linhas])


@app.get("/api/instituicoes")
def listar_instituicoes():
    linhas = get_db().execute("SELECT id, nome, sigla FROM instituicoes ORDER BY sigla").fetchall()
    return jsonify([dict(l) for l in linhas])


@app.get("/api/ods")
def listar_ods():
    linhas = get_db().execute("SELECT id, numero, nome FROM ods ORDER BY numero").fetchall()
    return jsonify([dict(l) for l in linhas])


@app.get("/api/indicadores")
def indicadores():
    """Números exibidos na página inicial e no painel."""
    db = get_db()
    um = lambda sql: db.execute(sql).fetchone()[0]
    return jsonify({
        "projetos": um("SELECT COUNT(*) FROM projetos WHERE status = 'publicado'"),
        "instituicoes": um("SELECT COUNT(*) FROM instituicoes"),
        "contatos": um("SELECT COUNT(*) FROM contatos"),
        "ods": um("SELECT COUNT(DISTINCT ods_id) FROM projeto_ods"),
    })


# --------------------------------------------------------------------- projetos
@app.get("/api/projetos")
def listar_projetos():
    """Lista projetos publicados. Filtros opcionais (na URL):
    ?q=texto &area=id &instituicao=id &tipo=Tese &ods=9
    """
    condicoes, params = ["p.status = 'publicado'"], []

    q = request.args.get("q", "").strip()
    if q:
        condicoes.append("(p.titulo LIKE ? OR p.resumo LIKE ?)")
        params += [f"%{q}%", f"%{q}%"]
    if request.args.get("area"):
        condicoes.append("p.area_id = ?")
        params.append(request.args["area"])
    if request.args.get("instituicao"):
        condicoes.append("i.id = ?")
        params.append(request.args["instituicao"])
    if request.args.get("tipo"):
        condicoes.append("p.tipo = ?")
        params.append(request.args["tipo"])
    if request.args.get("ods"):
        condicoes.append("EXISTS (SELECT 1 FROM projeto_ods po JOIN ods o ON o.id = po.ods_id "
                         "WHERE po.projeto_id = p.id AND o.numero = ?)")
        params.append(request.args["ods"])

    sql = SELECT_PROJETOS + " WHERE " + " AND ".join(condicoes) + " ORDER BY p.criado_em DESC, p.id DESC"
    linhas = get_db().execute(sql, params).fetchall()
    projetos = [projeto_para_dict(l) for l in linhas]
    return jsonify({"total": len(projetos), "projetos": projetos})


@app.get("/api/projetos/<int:projeto_id>")
def detalhar_projeto(projeto_id):
    """Perfil do projeto. Respeita o nível de detalhe escolhido pelo pesquisador (proteção da PI)."""
    db = get_db()
    linha = db.execute(
        SELECT_PROJETOS.replace("SELECT p.id,", "SELECT p.objetivos, p.aplicacoes, p.nivel_detalhe, "
                                "pe.departamento, p.id,") + " WHERE p.id = ? AND p.status = 'publicado'",
        (projeto_id,)).fetchone()
    if linha is None:
        return erro("Projeto não encontrado.", 404)

    projeto = projeto_para_dict(linha)
    nivel = projeto["nivel_detalhe"]
    if nivel == "resumo":                       # só o resumo é público
        projeto["objetivos"] = None
        projeto["aplicacoes"] = None
    elif nivel == "resumo_objetivos":           # resumo + objetivos
        projeto["aplicacoes"] = None
    projeto["detalhes_apos_contato"] = nivel != "completo"
    return jsonify(projeto)


@app.post("/api/projetos")
@login_obrigatorio
def criar_projeto():
    """Cadastro de projeto pelo pesquisador logado."""
    dados = request.get_json(silent=True) or {}
    titulo = (dados.get("titulo") or "").strip()
    resumo = (dados.get("resumo") or "").strip()
    tipo = dados.get("tipo")
    nivel = dados.get("nivel_detalhe", "resumo")
    status = dados.get("status", "publicado")
    ods_numeros = dados.get("ods", [])

    if not titulo or not resumo:
        return erro("Título e resumo em linguagem simples são obrigatórios.")
    if tipo not in TIPOS:
        return erro(f"Tipo inválido. Use um destes: {', '.join(TIPOS)}.")
    if nivel not in NIVEIS or status not in STATUS:
        return erro("Nível de detalhe ou status inválido.")
    if not isinstance(ods_numeros, list):
        return erro("O campo 'ods' deve ser uma lista de números.")

    db = get_db()
    if db.execute("SELECT 1 FROM areas WHERE id = ?", (dados.get("area_id"),)).fetchone() is None:
        return erro("Área do conhecimento inválida.")

    cursor = db.execute(
        "INSERT INTO projetos (titulo, resumo, objetivos, aplicacoes, tipo, maturidade, nivel_detalhe, "
        "status, area_id, pesquisador_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (titulo, resumo, dados.get("objetivos"), dados.get("aplicacoes"), tipo, dados.get("maturidade"),
         nivel, status, dados["area_id"], session["pesquisador_id"]))
    novo_id = cursor.lastrowid
    for numero in ods_numeros:
        db.execute("INSERT OR IGNORE INTO projeto_ods (projeto_id, ods_id) "
                   "SELECT ?, id FROM ods WHERE numero = ?", (novo_id, numero))
    db.commit()
    return jsonify({"id": novo_id, "mensagem": "Projeto cadastrado com sucesso."}), 201


# --------------------------------------------------------------------- contatos
@app.post("/api/contatos")
def criar_contato():
    """Formulário de contato: envia uma mensagem ao pesquisador responsável pelo projeto."""
    dados = request.get_json(silent=True) or {}
    obrigatorios = ("projeto_id", "nome", "email", "organizacao", "interesse", "mensagem")
    faltando = [c for c in obrigatorios if not str(dados.get(c, "")).strip()]
    if faltando:
        return erro(f"Campos obrigatórios ausentes: {', '.join(faltando)}.")
    if "@" not in dados["email"]:
        return erro("E-mail inválido.")
    if dados["interesse"] not in INTERESSES:
        return erro(f"Interesse inválido. Use um destes: {', '.join(INTERESSES)}.")

    db = get_db()
    existe = db.execute("SELECT 1 FROM projetos WHERE id = ? AND status = 'publicado'",
                        (dados["projeto_id"],)).fetchone()
    if existe is None:
        return erro("Projeto não encontrado.", 404)

    cursor = db.execute(
        "INSERT INTO contatos (projeto_id, nome, email, organizacao, interesse, mensagem) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (dados["projeto_id"], dados["nome"].strip(), dados["email"].strip(),
         dados["organizacao"].strip(), dados["interesse"], dados["mensagem"].strip()))
    db.commit()
    return jsonify({"id": cursor.lastrowid, "mensagem": "Mensagem enviada ao pesquisador."}), 201


# ------------------------------------------------------- área do pesquisador
@app.post("/api/login")
def login():
    dados = request.get_json(silent=True) or {}
    pesquisador = get_db().execute(
        "SELECT id, nome, email, senha_hash FROM pesquisadores WHERE email = ?",
        ((dados.get("email") or "").strip(),)).fetchone()
    if pesquisador is None or not check_password_hash(pesquisador["senha_hash"], dados.get("senha") or ""):
        return erro("E-mail ou senha incorretos.", 401)
    session["pesquisador_id"] = pesquisador["id"]
    return jsonify({"id": pesquisador["id"], "nome": pesquisador["nome"], "email": pesquisador["email"]})


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"mensagem": "Sessão encerrada."})


@app.get("/api/meus-projetos")
@login_obrigatorio
def meus_projetos():
    sql = SELECT_PROJETOS + " WHERE p.pesquisador_id = ? ORDER BY p.id DESC"
    linhas = get_db().execute(sql, (session["pesquisador_id"],)).fetchall()
    return jsonify([projeto_para_dict(l) for l in linhas])


@app.get("/api/meus-contatos")
@login_obrigatorio
def meus_contatos():
    """Pedidos de contato recebidos nos projetos do pesquisador logado."""
    linhas = get_db().execute(
        "SELECT c.id, c.nome, c.email, c.organizacao, c.interesse, c.mensagem, c.criado_em, "
        "       p.titulo AS projeto "
        "  FROM contatos c JOIN projetos p ON p.id = c.projeto_id "
        " WHERE p.pesquisador_id = ? ORDER BY c.criado_em DESC, c.id DESC",
        (session["pesquisador_id"],)).fetchall()
    return jsonify([dict(l) for l in linhas])


if __name__ == "__main__":
    app.run(debug=True, port=5001)
