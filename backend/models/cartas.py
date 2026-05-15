from datetime import datetime
from database import db


class Carta(db.Model):
    __tablename__ = "cartas"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("alunos.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    rarity = db.Column(db.String(32), default="Raro")
    power = db.Column(db.Integer, default=10)
    evolution_stage = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    image_filename = db.Column(db.String(260), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship("Aluno", back_populates="cards")

    def xp_needed(self):
        return 80 + self.evolution_stage * 60

    def evolve(self):
        if self.xp < self.xp_needed():
            return False
        self.xp -= self.xp_needed()
        self.evolution_stage += 1
        self.power += 15
        if self.evolution_stage % 2 == 0:
            self.power += 5
        return True

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "rarity": self.rarity,
            "power": self.power,
            "evolution_stage": self.evolution_stage,
            "xp": self.xp,
            "xp_needed": self.xp_needed(),
            "image_url": f"/api/mochila/image/{self.image_filename}" if self.image_filename else None,
            "created_at": self.created_at.isoformat(),
        }
