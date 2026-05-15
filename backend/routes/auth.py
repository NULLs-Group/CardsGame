"""
Rotas de Autenticação - Login, Cadastro, Logout, Perfil
Sistema seguro com sessão e validação
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash
from datetime import datetime
from database import db
from models.usuario import Usuario
from models.aluno import Aluno

auth_bp = Blueprint("auth", __name__)

# ==================== VALIDAÇÕES ====================

def validar_email(email: str) -> bool:
    """Validar formato de email"""
    import re
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None

def validar_senha(senha: str) -> tuple[bool, str]:
    """Validar força da senha"""
    if len(senha) < 8:
        return False, "Senha deve ter no mínimo 8 caracteres"
    if not any(c.isupper() for c in senha):
        return False, "Senha deve conter pelo menos uma letra maiúscula"
    if not any(c.isdigit() for c in senha):
        return False, "Senha deve conter pelo menos um número"
    if not any(c in "!@#$%^&*" for c in senha):
        return False, "Senha deve conter pelo menos um caractere especial (!@#$%^&*)"
    return True, "Senha válida"

# ==================== CADASTRO ====================

@auth_bp.route("/cadastro", methods=["POST"])
def cadastro():
    """
    Registrar novo usuário
    
    Dados esperados:
    {
        "nome": "João Silva",
        "username": "joaosilva",
        "email": "joao@example.com",
        "senha": "Senha123!",
        "nome_exibicao": "João"
    }
    """
    try:
        dados = request.get_json()
        
        # Validações
        if not dados or not all(k in dados for k in ["nome", "username", "email", "senha"]):
            return jsonify({"erro": "Campos obrigatórios faltando"}), 400
        
        nome = dados["nome"].strip()
        username = dados["username"].strip()
        email = dados["email"].strip().lower()
        senha = dados["senha"]
        nome_exibicao = dados.get("nome_exibicao", nome).strip()
        
        # Validar comprimentos
        if len(username) < 3 or len(username) > 80:
            return jsonify({"erro": "Username deve ter entre 3 e 80 caracteres"}), 400
        
        if len(nome) < 3 or len(nome) > 120:
            return jsonify({"erro": "Nome deve ter entre 3 e 120 caracteres"}), 400
        
        # Validar email
        if not validar_email(email):
            return jsonify({"erro": "Email inválido"}), 400
        
        # Validar senha
        valido, msg = validar_senha(senha)
        if not valido:
            return jsonify({"erro": msg}), 400
        
        # Verificar se username já existe
        if Usuario.query.filter_by(username=username).first():
            return jsonify({"erro": "Username já registrado"}), 409
        
        # Verificar se email já existe
        if Usuario.query.filter_by(email=email).first():
            return jsonify({"erro": "Email já registrado"}), 409
        
        # Criar usuário
        novo_usuario = Usuario(
            nome=nome,
            username=username,
            email=email
        )
        novo_usuario.set_password(senha)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        # Criar perfil de aluno
        novo_aluno = Aluno(
            user_id=novo_usuario.id,
            display_name=nome_exibicao,
            bio="Gamer futurista em evolução!"
        )
        
        db.session.add(novo_aluno)
        db.session.commit()
        
        return jsonify({
            "mensagem": "Cadastro realizado com sucesso!",
            "usuario": novo_usuario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao cadastrar: {str(e)}"}), 500

# ==================== LOGIN ====================

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Fazer login
    
    Dados esperados:
    {
        "username": "joaosilva",
        "senha": "Senha123!"
    }
    """
    try:
        dados = request.get_json()
        
        if not dados or "username" not in dados or "senha" not in dados:
            return jsonify({"erro": "Username e senha são obrigatórios"}), 400
        
        username = dados["username"].strip()
        senha = dados["senha"]
        
        # Buscar usuário
        usuario = Usuario.query.filter_by(username=username).first()
        
        if not usuario or not usuario.check_password(senha):
            return jsonify({"erro": "Username ou senha incorretos"}), 401
        
        # Atualizar último acesso
        usuario.ultimo_acesso = datetime.utcnow()
        db.session.commit()
        
        # Criar sessão
        session["usuario_id"] = usuario.id
        session.permanent = True
        
        return jsonify({
            "mensagem": "Login realizado com sucesso!",
            "usuario": usuario.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao fazer login: {str(e)}"}), 500

# ==================== LOGOUT ====================

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Fazer logout"""
    try:
        session.clear()
        return jsonify({"mensagem": "Logout realizado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao fazer logout: {str(e)}"}), 500

# ==================== VERIFICAR SESSÃO ====================

@auth_bp.route("/sessao", methods=["GET"])
def verificar_sessao():
    """Verificar se há sessão ativa"""
    try:
        if "usuario_id" not in session:
            return jsonify({"autenticado": False}), 401
        
        usuario = Usuario.query.get(session["usuario_id"])
        
        if not usuario:
            session.clear()
            return jsonify({"autenticado": False}), 401
        
        return jsonify({
            "autenticado": True,
            "usuario": usuario.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao verificar sessão: {str(e)}"}), 500

# ==================== PERFIL ====================

@auth_bp.route("/perfil", methods=["GET"])
def obter_perfil():
    """Obter perfil completo do usuário autenticado"""
    try:
        if "usuario_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        
        usuario = Usuario.query.get(session["usuario_id"])
        
        if not usuario:
            session.clear()
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        aluno = usuario.aluno
        
        return jsonify({
            "usuario": usuario.to_dict(),
            "aluno": aluno.profile_data() if aluno else None
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao obter perfil: {str(e)}"}), 500

# ==================== ATUALIZAR PERFIL ====================

@auth_bp.route("/perfil", methods=["PUT"])
def atualizar_perfil():
    """
    Atualizar perfil do usuário
    
    Dados esperados:
    {
        "bio": "Nova bio",
        "nome_exibicao": "Novo nome"
    }
    """
    try:
        if "usuario_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        
        dados = request.get_json()
        
        usuario = Usuario.query.get(session["usuario_id"])
        
        if not usuario:
            session.clear()
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        # Atualizar campos
        if "bio" in dados:
            usuario.bio = dados["bio"][:240]
        
        if "nome_exibicao" in dados and usuario.aluno:
            usuario.aluno.display_name = dados["nome_exibicao"][:90]
        
        db.session.commit()
        
        return jsonify({
            "mensagem": "Perfil atualizado com sucesso!",
            "usuario": usuario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao atualizar perfil: {str(e)}"}), 500

# ==================== ALTERAR SENHA ====================

@auth_bp.route("/alterar-senha", methods=["POST"])
def alterar_senha():
    """
    Alterar senha do usuário
    
    Dados esperados:
    {
        "senha_atual": "SenhaAnterior123!",
        "senha_nova": "SenhaNovaForte456!"
    }
    """
    try:
        if "usuario_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        
        dados = request.get_json()
        
        if not dados or "senha_atual" not in dados or "senha_nova" not in dados:
            return jsonify({"erro": "Senha atual e nova são obrigatórias"}), 400
        
        usuario = Usuario.query.get(session["usuario_id"])
        
        if not usuario:
            session.clear()
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        # Verificar senha atual
        if not usuario.check_password(dados["senha_atual"]):
            return jsonify({"erro": "Senha atual incorreta"}), 401
        
        # Validar nova senha
        valido, msg = validar_senha(dados["senha_nova"])
        if not valido:
            return jsonify({"erro": msg}), 400
        
        # Atualizar senha
        usuario.set_password(dados["senha_nova"])
        db.session.commit()
        
        return jsonify({"mensagem": "Senha alterada com sucesso!"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao alterar senha: {str(e)}"}), 500
