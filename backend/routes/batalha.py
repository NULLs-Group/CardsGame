"""
Rotas de Batalha - Sistema de combate PvP
Iniciar, continuar e finalizar batalhas
"""

from flask import Blueprint, request, jsonify, session
from database import db
from models.usuario import Usuario
from models.aluno import Aluno
from models.batalha import Batalha, BatalhaRodada
from models.cartas import Carta
import random

batalha_bp = Blueprint("batalha", __name__)

# ==================== INICIAR BATALHA ====================

@batalha_bp.route("/iniciar", methods=["POST"])
def iniciar_batalha():
    """
    Iniciar nova batalha
    
    Dados esperados:
    {
        "defensor_id": 2,
        "cartas_selecionadas": [1, 2, 3]  # IDs das cartas
    }
    """
    try:
        if "usuario_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        
        dados = request.get_json()
        
        usuario_atacante = Usuario.query.get(session["usuario_id"])
        
        if not usuario_atacante or not usuario_atacante.aluno:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        # Verificar defensor
        defensor_id = dados.get("defensor_id")
        aluno_defensor = Aluno.query.get(defensor_id)
        
        if not aluno_defensor:
            return jsonify({"erro": "Defensor não encontrado"}), 404
        
        if aluno_defensor.id == usuario_atacante.aluno.id:
            return jsonify({"erro": "Não pode atacar a si mesmo"}), 400
        
        # Verificar cartas selecionadas
        cartas_ids = dados.get("cartas_selecionadas", [])
        
        if not cartas_ids or len(cartas_ids) > 3:
            return jsonify({"erro": "Selecione entre 1 e 3 cartas"}), 400
        
        cartas = Carta.query.filter(
            Carta.id.in_(cartas_ids),
            Carta.owner_id == usuario_atacante.aluno.id
        ).all()
        
        if len(cartas) != len(cartas_ids):
            return jsonify({"erro": "Uma ou mais cartas não encontradas"}), 404
        
        # Criar batalha
        batalha = Batalha(
            atacante_id=usuario_atacante.aluno.id,
            defensor_id=aluno_defensor.id,
            cartas_atacante=",".join(str(c.id) for c in cartas)
        )
        
        db.session.add(batalha)
        db.session.commit()
        
        return jsonify({
            "mensagem": "Batalha iniciada!",
            "batalha_id": batalha.id,
            "batalha": batalha.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao iniciar batalha: {str(e)}"}), 500

# ==================== EXECUTAR RODADA ====================

@batalha_bp.route("/<int:batalha_id>/rodada", methods=["POST"])
def executar_rodada(batalha_id: int):
    """
    Executar rodada de batalha
    
    Dados esperados:
    {
        "carta_selecionada": 1  # ID da carta a usar
    }
    """
    try:
        if "usuario_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        
        dados = request.get_json()
        usuario = Usuario.query.get(session["usuario_id"])
        
        if not usuario or not usuario.aluno:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        batalha = Batalha.query.get(batalha_id)
        
        if not batalha:
            return jsonify({"erro": "Batalha não encontrada"}), 404
        
        # Verificar se é a vez do jogador
        if batalha.atacante_id != usuario.aluno.id and batalha.defensor_id != usuario.aluno.id:
            return jsonify({"erro": "Você não está nesta batalha"}), 403
        
        if batalha.status != "em_progresso":
            return jsonify({"erro": "Batalha já terminou"}), 400
        
        # Obter carta
        carta_id = dados.get("carta_selecionada")
        carta = Carta.query.get(carta_id)
        
        if not carta:
            return jsonify({"erro": "Carta não encontrada"}), 404
        
        # Calcular poder
        poder = carta.power + random.randint(-5, 10)
        
        # Determinar se é atacante ou defensor
        if batalha.atacante_id == usuario.aluno.id:
            poder_atacante = poder
            # Defensor usa carta aleatória
            cartas_defensor = Carta.query.filter_by(
                owner_id=batalha.defensor_id
            ).all()
            
            if not cartas_defensor:
                poder_defensor = random.randint(5, 15)
            else:
                carta_def = random.choice(cartas_defensor)
                poder_defensor = carta_def.power + random.randint(-5, 10)
        else:
            poder_defensor = poder
            # Atacante usa carta aleatória
            cartas_atacante = Carta.query.filter(
                Carta.id.in_(batalha.cartas_atacante.split(","))
            ).all()
            
            if not cartas_atacante:
                poder_atacante = random.randint(5, 15)
            else:
                carta_ataque = random.choice(cartas_atacante)
                poder_atacante = carta_ataque.power + random.randint(-5, 10)
        
        # Criar rodada
        rodada = batalha.adicionar_rodada(poder_atacante, poder_defensor)
        
        # Verificar se batalha terminou
        if len(batalha.rodadas) >= 3:
            batalha.calcular_vencedor()
            
            # Adicionar recompensas
            if batalha.vencedor_id:
                vencedor = Aluno.query.get(batalha.vencedor_id)
                vencedor_usuario = Usuario.query.get(vencedor.user_id)
                
                vencedor_usuario.adicionar_xp(batalha.xp_ganho)
                vencedor_usuario.moedas += batalha.moedas_ganhas
                vencedor_usuario.registrar_vitoria()
                
                # Perdedor também ganha XP menor
                perdedor_id = batalha.atacante_id if batalha.vencedor_id != batalha.atacante_id else batalha.defensor_id
                perdedor = Aluno.query.get(perdedor_id)
                perdedor_usuario = Usuario.query.get(perdedor.user_id)
                perdedor_usuario.adicionar_xp(10)
                perdedor_usuario.registrar_derrota()
        
        db.session.commit()
        
        return jsonify({
            "mensagem": "Rodada executada!",
            "rodada": rodada.to_dict(),
            "batalha": batalha.to_dict(),
            "encerrada": batalha.status != "em_progresso"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao executar rodada: {str(e)}"}), 500

# ==================== OBTER BATALHA ====================

@batalha_bp.route("/<int:batalha_id>", methods=["GET"])
def obter_batalha(batalha_id: int):
    """Obter detalhes de uma batalha"""
    try:
        batalha = Batalha.query.get(batalha_id)
        
        if not batalha:
            return jsonify({"erro": "Batalha não encontrada"}), 404
        
        return jsonify(batalha.to_dict()), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao obter batalha: {str(e)}"}), 500

# ==================== LISTAR BATALHAS DO JOGADOR ====================

@batalha_bp.route("/historico", methods=["GET"])
def listar_batalhas():
    """Listar histórico de batalhas do jogador"""
    try:
        if "usuario_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        
        usuario = Usuario.query.get(session["usuario_id"])
        
        if not usuario or not usuario.aluno:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        # Buscar batalhas do jogador
        batalhas = Batalha.query.filter(
            (Batalha.atacante_id == usuario.aluno.id) | 
            (Batalha.defensor_id == usuario.aluno.id)
        ).order_by(Batalha.data_inicio.desc()).limit(50).all()
        
        return jsonify({
            "total": len(batalhas),
            "batalhas": [b.to_dict() for b in batalhas]
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao listar batalhas: {str(e)}"}), 500

# ==================== RANKING DE BATALHAS ====================

@batalha_bp.route("/ranking", methods=["GET"])
def ranking_batalhas():
    """Obter ranking de jogadores por vitórias"""
    try:
        usuarios = Usuario.query.order_by(
            Usuario.vitoria.desc(),
            Usuario.nivel.desc()
        ).limit(100).all()
        
        ranking = []
        for idx, u in enumerate(usuarios, 1):
            ranking.append({
                "posicao": idx,
                "nome": u.nome,
                "level": u.nivel,
                "vitorias": u.vitoria,
                "derrotas": u.derrota,
                "taxa_vitoria": round((u.vitoria / (u.vitoria + u.derrota) * 100) if (u.vitoria + u.derrota) > 0 else 0, 2)
            })
        
        return jsonify(ranking), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao obter ranking: {str(e)}"}), 500
