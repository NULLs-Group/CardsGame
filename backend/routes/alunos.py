"""
Rotas de Alunos - Perfis e dados dos jogadores
Ranking, perfil público, listagem
"""

from flask import Blueprint, request, jsonify, session
from database import db
from models.usuario import Usuario
from models.aluno import Aluno
from models.cartas import Carta

alunos_bp = Blueprint("alunos", __name__)

# ==================== LISTAR ALUNOS ====================

@alunos_bp.route("/", methods=["GET"])
def listar_alunos():
    """Listar todos os alunos (públicos)"""
    try:
        # Paginação
        pagina = request.args.get("pagina", 1, type=int)
        limite = request.args.get("limite", 20, type=int)
        
        if limite > 100:
            limite = 100
        
        # Query
        alunos = Aluno.query.paginate(page=pagina, per_page=limite)
        
        dados_alunos = [{
            "id": a.id,
            "nome": a.display_name,
            "bio": a.bio,
            "level": a.level,
            "xp": a.xp,
            "total_cartas": len(a.cards),
            "avatar": a.avatar
        } for a in alunos.items]
        
        return jsonify({
            "pagina": pagina,
            "limite": limite,
            "total": alunos.total,
            "total_paginas": alunos.pages,
            "alunos": dados_alunos
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao listar alunos: {str(e)}"}), 500

# ==================== OBTER PERFIL PÚBLICO ====================

@alunos_bp.route("/<int:aluno_id>", methods=["GET"])
def obter_perfil_publico(aluno_id: int):
    """Obter perfil público de um aluno"""
    try:
        aluno = Aluno.query.get(aluno_id)
        
        if not aluno:
            return jsonify({"erro": "Aluno não encontrado"}), 404
        
        usuario = Usuario.query.get(aluno.user_id)
        
        # Contar estatísticas
        total_cartas = len(aluno.cards)
        carta_mais_forte = max(aluno.cards, key=lambda c: c.power) if aluno.cards else None
        
        return jsonify({
            "id": aluno.id,
            "nome": aluno.display_name,
            "bio": aluno.bio,
            "avatar": aluno.avatar,
            "level": aluno.level,
            "xp": aluno.xp,
            "moedas": aluno.coins,
            "total_cartas": total_cartas,
            "vitorias": usuario.vitoria,
            "derrotas": usuario.derrota,
            "taxa_vitoria": round((usuario.vitoria / (usuario.vitoria + usuario.derrota) * 100) if (usuario.vitoria + usuario.derrota) > 0 else 0, 2),
            "carta_mais_forte": {
                "nome": carta_mais_forte.name,
                "poder": carta_mais_forte.power,
                "evolucao": carta_mais_forte.evolution_stage
            } if carta_mais_forte else None,
            "criado_em": aluno.created_at.isoformat(),
            "ultimo_acesso": usuario.ultimo_acesso.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao obter perfil: {str(e)}"}), 500

# ==================== RANKING GERAL ====================

@alunos_bp.route("/ranking/geral", methods=["GET"])
def ranking_geral():
    """Obter ranking geral de alunos"""
    try:
        # Paginação
        pagina = request.args.get("pagina", 1, type=int)
        limite = request.args.get("limite", 50, type=int)
        
        if limite > 100:
            limite = 100
        
        # Buscar usuarios ordenados
        usuarios = Usuario.query.order_by(
            Usuario.nivel.desc(),
            Usuario.experiencia.desc()
        ).paginate(page=pagina, per_page=limite)
        
        ranking = []
        for idx, (u, aluno) in enumerate([
            (u, u.aluno) for u in usuarios.items
        ], (pagina - 1) * limite + 1):
            if aluno:
                ranking.append({
                    "posicao": idx,
                    "nome": aluno.display_name,
                    "nivel": u.nivel,
                    "experiencia": u.experiencia,
                    "vitorias": u.vitoria,
                    "derrotas": u.derrota,
                    "taxa_vitoria": round((u.vitoria / (u.vitoria + u.derrota) * 100) if (u.vitoria + u.derrota) > 0 else 0, 2),
                    "aluno_id": aluno.id
                })
        
        return jsonify({
            "pagina": pagina,
            "limite": limite,
            "total": usuarios.total,
            "total_paginas": usuarios.pages,
            "ranking": ranking
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao obter ranking: {str(e)}"}), 500

# ==================== RANKING POR XP ====================

@alunos_bp.route("/ranking/xp", methods=["GET"])
def ranking_xp():
    """Obter ranking por XP total"""
    try:
        alunos = Aluno.query.order_by(Aluno.xp.desc()).limit(100).all()
        
        ranking = [{
            "posicao": idx,
            "nome": a.display_name,
            "xp": a.xp,
            "level": a.level,
            "cartas": len(a.cards),
            "aluno_id": a.id
        } for idx, a in enumerate(alunos, 1)]
        
        return jsonify(ranking), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao obter ranking XP: {str(e)}"}), 500

# ==================== RANKING POR CARTAS ====================

@alunos_bp.route("/ranking/cartas", methods=["GET"])
def ranking_cartas():
    """Obter ranking por quantidade de cartas"""
    try:
        from sqlalchemy import func
        
        # Query complexa para contar cartas por aluno
        resultado = db.session.query(
            Aluno.id,
            Aluno.display_name,
            func.count(Carta.id).label("total_cartas"),
            func.max(Carta.power).label("poder_maximo")
        ).outerjoin(Carta).group_by(Aluno.id).order_by(
            func.count(Carta.id).desc()
        ).limit(100).all()
        
        ranking = [{
            "posicao": idx,
            "nome": r[1],
            "total_cartas": r[2] or 0,
            "poder_maximo": r[3] or 0,
            "aluno_id": r[0]
        } for idx, r in enumerate(resultado, 1)]
        
        return jsonify(ranking), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao obter ranking cartas: {str(e)}"}), 500

# ==================== BUSCAR ALUNO ====================

@alunos_bp.route("/buscar", methods=["GET"])
def buscar_aluno():
    """Buscar aluno por nome"""
    try:
        termo = request.args.get("q", "", type=str).strip()
        
        if len(termo) < 2:
            return jsonify({"erro": "Termo de busca muito curto"}), 400
        
        alunos = Aluno.query.filter(
            Aluno.display_name.ilike(f"%{termo}%")
        ).limit(20).all()
        
        resultados = [{
            "id": a.id,
            "nome": a.display_name,
            "level": a.level,
            "cartas": len(a.cards)
        } for a in alunos]
        
        return jsonify(resultados), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar aluno: {str(e)}"}), 500

# ==================== CARTAS DO ALUNO ====================

@alunos_bp.route("/<int:aluno_id>/cartas", methods=["GET"])
def cartas_aluno(aluno_id: int):
    """Listar cartas públicas de um aluno"""
    try:
        aluno = Aluno.query.get(aluno_id)
        
        if not aluno:
            return jsonify({"erro": "Aluno não encontrado"}), 404
        
        cartas = Carta.query.filter_by(owner_id=aluno_id).all()
        
        # Agrupar por raridade
        por_raridade = {}
        for carta in cartas:
            if carta.rarity not in por_raridade:
                por_raridade[carta.rarity] = []
            por_raridade[carta.rarity].append({
                "id": carta.id,
                "nome": carta.name,
                "poder": carta.power,
                "evolucao": carta.evolution_stage
            })
        
        return jsonify({
            "aluno_id": aluno_id,
            "total_cartas": len(cartas),
            "por_raridade": por_raridade
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao listar cartas: {str(e)}"}), 500

# ==================== ESTATÍSTICAS ====================

@alunos_bp.route("/estatisticas", methods=["GET"])
def estatisticas_globais():
    """Obter estatísticas globais do sistema"""
    try:
        total_usuarios = Usuario.query.count()
        total_alunos = Aluno.query.count()
        total_cartas = Carta.query.count()
        media_level = db.session.query(db.func.avg(Usuario.nivel)).scalar() or 0
        
        # Usuário mais ativo
        usuario_top = Usuario.query.order_by(
            Usuario.vitoria.desc()
        ).first()
        
        return jsonify({
            "total_usuarios": total_usuarios,
            "total_alunos": total_alunos,
            "total_cartas": total_cartas,
            "media_level": round(media_level, 2),
            "usuario_top": {
                "nome": usuario_top.nome if usuario_top else None,
                "vitorias": usuario_top.vitoria if usuario_top else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao obter estatísticas: {str(e)}"}), 500
