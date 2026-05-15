"""
Rotas de Mochila - Gerenciar cartas do jogador
Evolução, venda, equipe de batalha
"""

from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from database import db
from models.usuario import Usuario
from models.aluno import Aluno
from models.cartas import Carta

mochila_bp = Blueprint("mochila", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def arquivo_permitido(nome_arquivo: str) -> bool:
    """Verificar se extensão de arquivo é permitida"""
    return "." in nome_arquivo and nome_arquivo.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== LISTAR CARTAS ====================

@mochila_bp.route("/cartas", methods=["GET"])
def listar_cartas():
    """Listar todas as cartas do jogador"""
    try:
        if "usuario_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        
        usuario = Usuario.query.get(session["usuario_id"])
        
        if not usuario or not usuario.aluno:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        cartas = Carta.query.filter_by(owner_id=usuario.aluno.id).all()
        
        return jsonify({
            "total": len(cartas),
            "cartas": [carta.to_dict() for carta in cartas]
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao listar cartas: {str(e)}"}), 500

# ==================== OBTER CARTA ====================

@mochila_bp.route("/cartas/<int:carta_id>", methods=["GET"])
def obter_carta(carta_id: int):
    """Obter detalhes de uma carta específica"""
    try:
        carta = Carta.query.get(carta_id)
        
        if not carta:
            return jsonify({"erro": "Carta não encontrada"}), 404
        
        # Verificar permissão
        if "usuario_id" in session:
            usuario = Usuario.query.get(session["usuario_id"])
            if usuario.aluno and usuario.aluno.id == carta.owner_id:
                return jsonify(carta.to_dict()), 200
        
        # Retornar dados públicos
        return jsonify({
            "id": carta.id,
            "name": carta.name,
            "rarity": carta.rarity,
            "power": carta.power,
            "evolution_stage": carta.evolution_stage,
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao obter carta: {str(e)}"}), 500

# ==================== EVOLUIR CARTA ====================

@mochila_bp.route("/cartas/<int:carta_id>/evoluir", methods=["POST"])
def evoluir_carta(carta_id: int):
    """Evoluir uma carta do jogador"""
    try:
        if "usuario_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        
        usuario = Usuario.query.get(session["usuario_id"])
        
        if not usuario or not usuario.aluno:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        carta = Carta.query.get(carta_id)
        
        if not carta or carta.owner_id != usuario.aluno.id:
            return jsonify({"erro": "Carta não encontrada"}), 404
        
        # Verificar XP necessário
        xp_necessario = carta.xp_needed()
        if carta.xp < xp_necessario:
            return jsonify({
                "erro": f"XP insuficiente. Necessário: {xp_necessario}, Possui: {carta.xp}"
            }), 400
        
        # Evoluir
        sucesso = carta.evolve()
        
        if not sucesso:
            return jsonify({"erro": "Falha ao evoluir carta"}), 400
        
        db.session.commit()
        
        usuario.adicionar_conquista("evolucao_carta", {
            "titulo": f"{carta.name} Evoluído",
            "descricao": f"Evoluiu {carta.name} para o estágio {carta.evolution_stage}"
        })
        
        db.session.commit()
        
        return jsonify({
            "mensagem": "Carta evoluída com sucesso!",
            "carta": carta.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao evoluir carta: {str(e)}"}), 500

# ==================== VENDER CARTA ====================

@mochila_bp.route("/cartas/<int:carta_id>/vender", methods=["POST"])
def vender_carta(carta_id: int):
    """Vender uma carta e receber moedas"""
    try:
        if "usuario_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        
        usuario = Usuario.query.get(session["usuario_id"])
        
        if not usuario or not usuario.aluno:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        carta = Carta.query.get(carta_id)
        
        if not carta or carta.owner_id != usuario.aluno.id:
            return jsonify({"erro": "Carta não encontrada"}), 404
        
        # Calcular preço baseado em raridade e evolução
        preco_base = {
            "Comum": 50,
            "Raro": 150,
            "Épico": 400,
            "Lendário": 1000
        }
        preco = preco_base.get(carta.rarity, 50) * (1 + carta.evolution_stage * 0.2)
        preco = int(preco)
        
        # Adicionar moedas
        usuario.moedas += preco
        
        # Remover carta
        db.session.delete(carta)
        db.session.commit()
        
        return jsonify({
            "mensagem": f"Carta vendida por {preco} moedas!",
            "moedas_ganhas": preco,
            "moedas_total": usuario.moedas
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao vender carta: {str(e)}"}), 500

# ==================== UPLOAD DE IMAGEM ====================

@mochila_bp.route("/upload-imagem/<int:carta_id>", methods=["POST"])
def upload_imagem(carta_id: int):
    """Fazer upload de imagem para uma carta"""
    try:
        if "usuario_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        
        usuario = Usuario.query.get(session["usuario_id"])
        
        if not usuario or not usuario.aluno:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        carta = Carta.query.get(carta_id)
        
        if not carta or carta.owner_id != usuario.aluno.id:
            return jsonify({"erro": "Carta não encontrada"}), 404
        
        # Verificar arquivo
        if "arquivo" not in request.files:
            return jsonify({"erro": "Nenhum arquivo enviado"}), 400
        
        arquivo = request.files["arquivo"]
        
        if arquivo.filename == "":
            return jsonify({"erro": "Nenhum arquivo selecionado"}), 400
        
        if not arquivo_permitido(arquivo.filename):
            return jsonify({"erro": "Tipo de arquivo não permitido"}), 400
        
        # Salvar arquivo
        nome_arquivo = f"carta_{carta_id}_{datetime.utcnow().timestamp()}.{arquivo.filename.rsplit('.', 1)[1].lower()}"
        nome_arquivo_seguro = secure_filename(nome_arquivo)
        
        caminho = os.path.join(current_app.config["UPLOAD_FOLDER"], nome_arquivo_seguro)
        arquivo.save(caminho)
        
        # Atualizar carta
        carta.image_filename = nome_arquivo_seguro
        db.session.commit()
        
        return jsonify({
            "mensagem": "Imagem enviada com sucesso!",
            "carta": carta.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao enviar imagem: {str(e)}"}), 500

# ==================== IMAGEM ====================

@mochila_bp.route("/image/<nome_arquivo>", methods=["GET"])
def obter_imagem(nome_arquivo: str):
    """Obter imagem de carta"""
    try:
        caminho = os.path.join(current_app.config["UPLOAD_FOLDER"], secure_filename(nome_arquivo))
        
        if not os.path.isfile(caminho):
            return jsonify({"erro": "Imagem não encontrada"}), 404
        
        from flask import send_file
        return send_file(caminho)
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao obter imagem: {str(e)}"}), 500

# ==================== ADICIONAR MOEDAS (DEBUG) ====================

@mochila_bp.route("/debug/moedas", methods=["POST"])
def debug_adicionar_moedas():
    """DEBUG: Adicionar moedas ao jogador"""
    if not current_app.debug:
        return jsonify({"erro": "Não disponível em produção"}), 403
    
    try:
        if "usuario_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        
        dados = request.get_json()
        quantidade = dados.get("quantidade", 100)
        
        usuario = Usuario.query.get(session["usuario_id"])
        usuario.moedas += quantidade
        db.session.commit()
        
        return jsonify({"moedas": usuario.moedas}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500
