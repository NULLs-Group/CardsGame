"""
🎮 CARDS GAME - Backend Flask Professional
Sistema completo de jogo de cartas com autenticação, batalhas, ranking e XP
Estilo: Futurista | Neon | Gamer | Glassmorphism
"""

import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from datetime import timedelta
from dotenv import load_dotenv

from database import db
from routes.auth import auth_bp
from routes.alunos import alunos_bp
from routes.mochila import mochila_bp
from routes.batalha import batalha_bp

# ==================== CONFIGURAÇÃO INICIAL ====================
load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "cartas")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Criar diretórios necessários
os.makedirs(os.path.join(BASE_DIR, "uploads", "perfis"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "uploads", "cartas"), exist_ok=True)

# ==================== INICIALIZAR FLASK ====================
app = Flask(__name__, static_folder="../frontend", static_url_path="")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cards-game-super-secret-2024")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # True em produção
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

# ==================== CORS ====================
CORS(app, resources={
    r"/api/*": {"origins": "*"},
}, supports_credentials=True)

# ==================== INICIALIZAR BD ====================
db.init_app(app)

# ==================== REGISTRAR BLUEPRINTS ====================
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(alunos_bp, url_prefix="/api/alunos")
app.register_blueprint(mochila_bp, url_prefix="/api/mochila")
app.register_blueprint(batalha_bp, url_prefix="/api/batalha")

# ==================== ROTAS PÚBLICAS ====================

@app.route("/")
def index():
    """Servir index.html"""
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check do servidor"""
    try:
        db.session.execute("SELECT 1")
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/<path:path>")
def serve_static(path):
    """Servir arquivos estáticos"""
    full_path = os.path.join(app.static_folder, path)
    if os.path.isfile(full_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

# ==================== ERROR HANDLERS ====================

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Requisição inválida"}), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"error": "Não autorizado"}), 401

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error": "Acesso proibido"}), 403

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Recurso não encontrado"}), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return jsonify({"error": "Erro interno do servidor"}), 500

# ==================== INICIALIZAR BD ====================
with app.app_context():
    db.create_all()
    print("✅ Banco de dados inicializado!")

# ==================== MAIN ====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
