import json
from datetime import datetime
from database import db


class Aluno(db.Model):
    __tablename__ = "alunos"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    display_name = db.Column(db.String(90), nullable=False)
    avatar = db.Column(db.String(250), nullable=True)
    bio = db.Column(db.String(240), default="Gamer futurista em evolução.")
    xp = db.Column(db.Integer, default=120)
    level = db.Column(db.Integer, default=1)
    coins = db.Column(db.Integer, default=80)
    achievements = db.Column(db.Text, default=json.dumps([]))
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship("Usuario", back_populates="aluno")
    cards = db.relationship("Carta", back_populates="owner", cascade="all, delete-orphan")
    battles = db.relationship("Batalha", back_populates="attacker", foreign_keys="Batalha.attacker_id")

    def level_threshold(self) -> int:
        return 100 + self.level * 120

    def update_level(self):
        while self.xp >= self.level_threshold():
            self.xp -= self.level_threshold()
            self.level += 1
            self.coins += 15
            self.add_achievement("level_up", {
                "title": f"Nível {self.level}",
                "description": "Sua jornada gamer avançou mais um nível."
            })

    def add_xp(self, amount: int):
        self.xp += amount
        self.update_level()

    def add_achievement(self, code: str, award: dict):
        achievements = json.loads(self.achievements or "[]")
        if any(item.get("code") == code for item in achievements):
            return
        achievements.append({"code": code, **award, "unlocked_at": datetime.utcnow().isoformat()})
        self.achievements = json.dumps(achievements)

    def profile_data(self):
        achievements = json.loads(self.achievements or "[]")
        return {
            "id": self.id,
            "display_name": self.display_name,
            "avatar": self.avatar,
            "bio": self.bio,
            "xp": self.xp,
            "level": self.level,
            "coins": self.coins,
            "achievements": achievements,
            "cards": [card.to_dict() for card in self.cards],
            "last_login": self.last_login.isoformat(),
            "created_at": self.created_at.isoformat(),
        }
