"""
Model de Usuário - Sistema de autenticação e perfil
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
import json


class Usuario(db.Model):
    """Modelo de usuário com autenticação segura"""
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Perfil do jogador
    avatar = db.Column(db.String(500), nullable=True)
    bio = db.Column(db.String(240), default="Gamer futurista em evolução!")
    
    # Sistema de XP e Níveis
    experiencia = db.Column(db.Integer, default=0)
    nivel = db.Column(db.Integer, default=1)
    
    # Estatísticas de batalha
    vitoria = db.Column(db.Integer, default=0)
    derrota = db.Column(db.Integer, default=0)
    
    # Moedas e conquistas
    moedas = db.Column(db.Integer, default=100)
    conquistas = db.Column(db.Text, default=json.dumps([]))
    
    # Timestamps
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    aluno = db.relationship("Aluno", back_populates="usuario", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password: str):
        """Criptografar senha com hash seguro"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verificar senha com hash"""
        return check_password_hash(self.password_hash, password)
    
    def adicionar_xp(self, quantidade: int):
        """Adicionar XP e verificar level up"""
        self.experiencia += quantidade
        self._atualizar_nivel()
    
    def _atualizar_nivel(self):
        """Atualizar nível baseado em XP"""
        xp_necessario = 100 + (self.nivel * 50)
        while self.experiencia >= xp_necessario:
            self.experiencia -= xp_necessario
            self.nivel += 1
            self.moedas += 50
            xp_necessario = 100 + (self.nivel * 50)
    
    def adicionar_conquista(self, codigo: str, dados: dict):
        """Adicionar conquista ao perfil"""
        conquistas = json.loads(self.conquistas or "[]")
        if not any(c.get("codigo") == codigo for c in conquistas):
            conquistas.append({
                "codigo": codigo,
                **dados,
                "data_desbloqueio": datetime.utcnow().isoformat()
            })
            self.conquistas = json.dumps(conquistas)
    
    def registrar_vitoria(self):
        """Registrar vitória e adicionar XP"""
        self.vitoria += 1
        self.adicionar_xp(25)
    
    def registrar_derrota(self):
        """Registrar derrota e adicionar XP menor"""
        self.derrota += 1
        self.adicionar_xp(10)

    def to_dict(self):
        """Converter usuário para dicionário"""
        return {
            "id": self.id,
            "nome": self.nome,
            "username": self.username,
            "email": self.email,
            "avatar": self.avatar,
            "bio": self.bio,
            "experiencia": self.experiencia,
            "nivel": self.nivel,
            "vitoria": self.vitoria,
            "derrota": self.derrota,
            "moedas": self.moedas,
            "taxa_vitoria": round((self.vitoria / (self.vitoria + self.derrota) * 100) if (self.vitoria + self.derrota) > 0 else 0, 2),
            "data_criacao": self.data_criacao.isoformat(),
            "ultimo_acesso": self.ultimo_acesso.isoformat(),
        }
