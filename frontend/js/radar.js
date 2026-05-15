/**
 * 🎮 CARDS GAME - Radar.js
 * Módulo de radar em tempo real (visualização 2D de jogadores)
 */

class RadarManager {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.particulas = [];
        this.jogadores = [];
    }

    inicializar() {
        const container = document.getElementById('radarContainer');
        if (!container) return;

        this.canvas = document.createElement('canvas');
        this.canvas.width = 400;
        this.canvas.height = 400;
        this.canvas.id = 'radarCanvas';
        this.canvas.style.cssText = `
            border: 2px solid var(--cor-azul-neon);
            border-radius: 12px;
            background: rgba(0, 0, 0, 0.3);
            margin-top: 20px;
        `;

        container.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');

        this.desenhar();
    }

    adicionarJogador(x, y, nome, nivel) {
        this.jogadores.push({ x, y, nome, nivel, angulo: 0 });
    }

    desenhar() {
        const w = this.canvas.width;
        const h = this.canvas.height;
        const cx = w / 2;
        const cy = h / 2;

        // Limpar
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        this.ctx.fillRect(0, 0, w, h);

        // Grid
        this.ctx.strokeStyle = 'rgba(0, 212, 255, 0.1)';
        this.ctx.lineWidth = 1;
        for (let i = 0; i < 5; i++) {
            const r = (w / 2) * (i / 4);
            this.ctx.beginPath();
            this.ctx.arc(cx, cy, r, 0, Math.PI * 2);
            this.ctx.stroke();
        }

        // Centro
        this.ctx.fillStyle = 'var(--cor-azul-neon)';
        this.ctx.beginPath();
        this.ctx.arc(cx, cy, 5, 0, Math.PI * 2);
        this.ctx.fill();

        // Jogadores
        this.jogadores.forEach((jogador) => {
            const angle = (jogador.angulo * Math.PI) / 180;
            const distancia = 80;
            const x = cx + Math.cos(angle) * distancia;
            const y = cy + Math.sin(angle) * distancia;

            this.ctx.fillStyle = 'var(--cor-rosa-neon)';
            this.ctx.beginPath();
            this.ctx.arc(x, y, 8, 0, Math.PI * 2);
            this.ctx.fill();

            jogador.angulo = (jogador.angulo + 2) % 360;
        });

        requestAnimationFrame(() => this.desenhar());
    }
}

// Inicializar
const radarManager = new RadarManager();
console.log('✅ Radar module loaded');
