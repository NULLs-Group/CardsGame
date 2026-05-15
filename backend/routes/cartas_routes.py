"""
Rotas de Cartas - Sistema de cartas e loja
"""

from flask import Blueprint, request, jsonify, session
from database import db
from models.usuario import Usuario
from models.aluno import Aluno
from models.cartas import Carta
import random

cartas_bp = Blueprint("cartas", __name__)

# ==================== OBTER TODAS AS CARTAS BASE ====================

@cartas_bp.route("/", methods=["GET"])
def listar_cartas_base():
    """Listar todas as cartas base disponíveis"""
    try:
        cartas_base = [
            {"id": 1, "nome": "Guerreiro Neon", "tipo": "guerreiro", "poder": 8, "raridade": "comum"},
            {"id": 2, "nome": "Mago Cósmico", "tipo": "mago", "poder": 10, "raridade": "comum"},
            {"id": 3, "nome": "Ninja Sombra", "tipo": "assassino", "poder": 9, "raridade": "raro"},
            {"id": 4, "nome": "Dragão Futurista", "tipo": "lendario", "poder": 12, "raridade": "lendario"},
            {"id": 5, "nome": "Protetor Robótico", "tipo": "defensor", "poder": 5, "raridade": "comum"},
            {"id": 6, "nome": "Espreita Digital", "tipo": "assassino", "poder": 11, "raridade": "raro"},
        ]
        
        return jsonify(cartas_base), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao listar cartas: {str(e)}"}), 500

# ==================== COMPRAR CARTA ====================

@cartas_bp.route("/comprar", methods=["POST"])
def comprar_carta():
    """
    Comprar uma carta aleatória
    
    Dados esperados:
    {
        "rarity": "comum"  // comum, raro, epico, lendario
    }
    """
    try:
        if "usuario_id" not in session:
            return jsonify({"erro": "Não autenticado"}), 401
        
        dados = request.get_json()
        raridade = dados.get("raridade", "comum")
        
        usuario = Usuario.query.get(session["usuario_id"])
        
        if not usuario or not usuario.aluno:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        # Preço por raridade
        precos = {
            "comum": 50,
            "raro": 150,
            "epico": 400,
            "lendario": 1000
        }
        
        preco = precos.get(raridade, 50)
        
        # Verificar moedas
        if usuario.moedas < preco:
            return jsonify({"erro": "Moedas insuficientes"}), 400
        
        # Cartas disponíveis
        cartas_disponiveis = {
            "comum": [
                {"nome": "Guerreiro Neon", "poder": 8},
                {"nome": "Mago Cósmico", "poder": 10},
                {"nome": "Protetor Robótico", "poder": 5},
            ],
            "raro": [
                {"nome": "Ninja Sombra", "poder": 9},
                {"nome": "Espreita Digital", "poder": 11},
            ],
            "epico": [
                {"nome": "Golem Neon", "poder": 13},
                {"nome": "Fênix Cósmica", "poder": 14},
            ],
            "lendario": [
                {"nome": "Dragão Futurista", "poder": 12},
                {"nome": "Titã Dimensional", "poder": 15},
            ]
        }
        
        cartas_lista = cartas_disponiveis.get(raridade, cartas_disponiveis["comum"])
        carta_info = random.choice(cartas_lista)
        
        # Criar carta
        nova_carta = Carta(
            owner_id=usuario.aluno.id,
            name=carta_info["nome"],
            rarity=raridade,
            power=carta_info["poder"]
        )
        
        # Debitar moedas
        usuario.moedas -= preco
        
        db.session.add(nova_carta)
        db.session.commit()
        
        usuario.adicionar_conquista("compra_carta", {
            "titulo": "Coletor",
            "descricao": f"Comprou sua primeira carta {raridade}"
        })
        
        db.session.commit()
        
        return jsonify({
            "mensagem": f"Carta {raridade} comprada!",
            "carta": nova_carta.to_dict(),
            "moedas_restantes": usuario.moedas
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro ao comprar carta: {str(e)}"}), 500

# ==================== LOJA ====================

@cartas_bp.route("/loja", methods=["GET"])
def loja():
    """Obter informações da loja"""
    try:
        loja_info = {
            "nome": "Loja Futurista",
            "pacotes": [
                {
                    "id": 1,
                    "nome": "Pacote Iniciante",
                    "raridade": "comum",
                    "preco": 50,
                    "garantidos": 1,
                    "descricao": "Perfeito para começar sua jornada"
                },
                {
                    "id": 2,
                    "nome": "Pacote Aventureiro",
                    "raridade": "raro",
                    "preco": 150,
                    "garantidos": 1,
                    "descricao": "Cartas mais raras e poderosas"
                },
                {
                    "id": 3,
                    "nome": "Pacote Épico",
                    "raridade": "epico",
                    "preco": 400,
                    "garantidos": 2,
                    "descricao": "Cartas épicas garantidas"
                },
                {
                    "id": 4,
                    "nome": "Pacote Lendário",
                    "raridade": "lendario",
                    "preco": 1000,
                    "garantidos": 3,
                    "descricao": "O topo das cartas"
                }
            ]
        }
        
        return jsonify(loja_info), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao obter loja: {str(e)}"}), 500

# ==================== COLEÇÃO DE CARTAS ====================

@cartas_bp.route("/colecao", methods=["GET"])
def colecao_global():
    """Obter todas as cartas do sistema com estatísticas"""
    try:
        cartas_base = [
            {"id": 1, "nome": "Guerreiro Neon", "tipo": "guerreiro", "poder": 8, "raridade": "comum"},
            {"id": 2, "nome": "Mago Cósmico", "tipo": "mago", "poder": 10, "raridade": "comum"},
            {"id": 3, "nome": "Ninja Sombra", "tipo": "assassino", "poder": 9, "raridade": "raro"},
            {"id": 4, "nome": "Dragão Futurista", "tipo": "lendario", "poder": 12, "raridade": "lendario"},
            {"id": 5, "nome": "Protetor Robótico", "tipo": "defensor", "poder": 5, "raridade": "comum"},
            {"id": 6, "nome": "Espreita Digital", "tipo": "assassino", "poder": 11, "raridade": "raro"},
            {"id": 7, "nome": "Golem Neon", "tipo": "defensor", "poder": 13, "raridade": "epico"},
            {"id": 8, "nome": "Fênix Cósmica", "tipo": "lendario", "poder": 14, "raridade": "epico"},
            {"id": 9, "nome": "Titã Dimensional", "tipo": "lendario", "poder": 15, "raridade": "lendario"},
        ]
        
        # Adicionar contagem de posse
        for carta in cartas_base:
            count = Carta.query.filter_by(name=carta["nome"]).count()
            carta["detentores"] = count
        
        return jsonify(cartas_base), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao obter coleção: {str(e)}"}), 500
