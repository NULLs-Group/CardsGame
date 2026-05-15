"""
Model de Batalha - Sistema de combate PvP e PvE
"""

from datetime import datetime
from database import db
import json
import random


class Batalha(db.Model):
    """Modelo de batalha entre jogadores"""
    __tablename__ = "batalhas"

    id = db.Column(db.Integer, primary_key=True)
    
    # Participantes
    atacante_id = db.Column(db.Integer, db.ForeignKey("alunos.id"), nullable=False)
    defensor_id = db.Column(db.Integer, db.ForeignKey("alunos.id"), nullable=False)
    
    # Status
    status = db.Column(db.String(20), default="em_progresso")  # em_progresso, vitoria_atacante, vitoria_defensor
    vencedor_id = db.Column(db.Integer, db.ForeignKey("alunos.id"), nullable=True)
    
    # Cartas usadas
    cartas_atacante = db.Column(db.Text, default=json.dumps([]))
    cartas_defensor = db.Column(db.Text, default=json.dumps([]))
    
    # Recompensas
    xp_ganho = db.Column(db.Integer, default=0)
    moedas_ganhas = db.Column(db.Integer, default=0)
    
    # Timestamps
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    atacante = db.relationship("Aluno", foreign_keys=[atacante_id])
    defensor = db.relationship("Aluno", foreign_keys=[defensor_id])
    rodadas = db.relationship("BatalhaRodada", back_populates="batalha", cascade="all, delete-orphan")
    
    def adicionar_rodada(self, poder_atacante: int, poder_defensor: int):
        """Adicionar rodada de combate"""
        rodada = BatalhaRodada(
            batalha_id=self.id,
            poder_atacante=poder_atacante,
            poder_defensor=poder_defensor,
            numero_rodada=len(self.rodadas) + 1
        )
        db.session.add(rodada)
        return rodada
    
    def calcular_vencedor(self):
        """Calcular vencedor baseado em poder total"""
        poder_total_atacante = sum(r.poder_atacante for r in self.rodadas)
        poder_total_defensor = sum(r.poder_defensor for r in self.rodadas)
        
        if poder_total_atacante > poder_total_defensor:
            self.vencedor_id = self.atacante_id
            self.status = "vitoria_atacante"
            self.xp_ganho = 50
            self.moedas_ganhas = 30
        elif poder_total_defensor > poder_total_atacante:
            self.vencedor_id = self.defensor_id
            self.status = "vitoria_defensor"
            self.xp_ganho = 30
            self.moedas_ganhas = 20
        else:
            self.status = "empate"
            self.xp_ganho = 20
            self.moedas_ganhas = 10
        
        self.data_fim = datetime.utcnow()
    
    def to_dict(self):
        """Converter batalha para dicionário"""
        return {
            "id": self.id,
            "atacante": {
                "id": self.atacante.id,
                "nome": self.atacante.display_name
            },
            "defensor": {
                "id": self.defensor.id,
                "nome": self.defensor.display_name
            },
            "status": self.status,
            "vencedor_id": self.vencedor_id,
            "xp_ganho": self.xp_ganho,
            "moedas_ganhas": self.moedas_ganhas,
            "rodadas": [r.to_dict() for r in self.rodadas],
            "data_inicio": self.data_inicio.isoformat(),
            "data_fim": self.data_fim.isoformat() if self.data_fim else None,
        }


class BatalhaRodada(db.Model):
    """Modelo de rodada de batalha"""
    __tablename__ = "batalha_rodadas"

    id = db.Column(db.Integer, primary_key=True)
    batalha_id = db.Column(db.Integer, db.ForeignKey("batalhas.id"), nullable=False)
    
    numero_rodada = db.Column(db.Integer, nullable=False)
    poder_atacante = db.Column(db.Integer, nullable=False)
    poder_defensor = db.Column(db.Integer, nullable=False)
    
    # Relacionamento
    batalha = db.relationship("Batalha", back_populates="rodadas")
    
    def to_dict(self):
        """Converter rodada para dicionário"""
        vencedor = "atacante" if self.poder_atacante > self.poder_defensor else "defensor" if self.poder_defensor > self.poder_atacante else "empate"
        return {
            "numero": self.numero_rodada,
            "poder_atacante": self.poder_atacante,
            "poder_defensor": self.poder_defensor,
            "vencedor": vencedor
        }
