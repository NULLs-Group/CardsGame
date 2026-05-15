/**
 * 🎮 CARDS GAME - Main.js
 * Lógica principal da aplicação
 */

const API_BASE = '/api';
let usuarioAtual = null;
let temaAtual = 'escuro';

// ==================== CLASSE DE API ====================

class CardsGameAPI {
    static async fetch(endpoint, opcoes = {}) {
        try {
            const url = `${API_BASE}${endpoint}`;
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...opcoes.headers,
                },
                credentials: 'include',
                ...opcoes,
            });

            if (!response.ok) {
                const erro = await response.json();
                throw new Error(erro.erro || 'Erro na requisição');
            }

            return await response.json();
        } catch (erro) {
            console.error('API Error:', erro);
            throw erro;
        }
    }

    // ==================== AUTH ====================

    static async cadastro(nome, username, email, senha) {
        return this.fetch('/auth/cadastro', {
            method: 'POST',
            body: JSON.stringify({ nome, username, email, senha }),
        });
    }

    static async login(username, senha) {
        return this.fetch('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, senha }),
        });
    }

    static async logout() {
        return this.fetch('/auth/logout', { method: 'POST' });
    }

    static async verificarSessao() {
        return this.fetch('/auth/sessao');
    }

    // ==================== CARTAS ====================

    static async comprarCarta(raridade = 'comum') {
        return this.fetch('/cartas/comprar', {
            method: 'POST',
            body: JSON.stringify({ raridade }),
        });
    }

    static async listarCartas() {
        return this.fetch('/mochila/cartas');
    }

    // ==================== BATALHA ====================

    static async iniciarBatalha(defensorId, cartasSelecionadas) {
        return this.fetch('/batalha/iniciar', {
            method: 'POST',
            body: JSON.stringify({
                defensor_id: defensorId,
                cartas_selecionadas: cartasSelecionadas,
            }),
        });
    }

    static async executarRodada(batalhaId, cartaSelecionada) {
        return this.fetch(`/batalha/${batalhaId}/rodada`, {
            method: 'POST',
            body: JSON.stringify({ carta_selecionada: cartaSelecionada }),
        });
    }

    static async obterRanking() {
        return this.fetch('/ranking');
    }

    // ==================== ALUNOS ====================

    static async listarAlunos(pagina = 1) {
        return this.fetch(`/alunos?pagina=${pagina}&limite=20`);
    }

    static async obterPerfilPublico(alunoId) {
        return this.fetch(`/alunos/${alunoId}`);
    }

    static async rankingGeral() {
        return this.fetch('/alunos/ranking/geral');
    }
}

// ==================== GERENCIADOR DE NOTIFICAÇÕES ====================

class NotificacaoManager {
    static mostrar(mensagem, tipo = 'info', duracao = 3000) {
        const container = document.getElementById('notificacoes');
        const notificacao = document.createElement('div');
        notificacao.className = `notificacao ${tipo}`;
        notificacao.textContent = mensagem;

        container.appendChild(notificacao);

        setTimeout(() => {
            notificacao.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => notificacao.remove(), 300);
        }, duracao);
    }

    static sucesso(mensagem) {
        this.mostrar(`✅ ${mensagem}`, 'sucesso');
    }

    static erro(mensagem) {
        this.mostrar(`❌ ${mensagem}`, 'erro', 5000);
    }

    static info(mensagem) {
        this.mostrar(`ℹ️ ${mensagem}`, 'info');
    }
}

// ==================== GERENCIADOR DE PARTICULAS ====================

class ParticleManager {
    static criar() {
        const container = document.getElementById('particles');
        const numParticles = window.innerWidth > 768 ? 50 : 20;

        for (let i = 0; i < numParticles; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';

            const x = Math.random() * window.innerWidth;
            const y = Math.random() * window.innerHeight;
            const duration = 15 + Math.random() * 20;

            particle.style.setProperty('--duration', `${duration}s`);
            particle.style.left = x + 'px';
            particle.style.top = y + 'px';

            container.appendChild(particle);

            setTimeout(() => {
                particle.remove();
                this.criar();
            }, duration * 1000);
        }
    }
}

// ==================== RENDERIZAÇÃO DE INTERFACE ====================

class UIRenderer {
    static renderarLogin() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="auth-container">
                <div class="auth-box">
                    <div class="auth-header">
                        <h1><span class="logo">🎮</span> CARDS GAME</h1>
                        <p class="auth-subtitle">Sistema Futurista de Cartas</p>
                    </div>
                    <form id="loginForm">
                        <div class="form-group">
                            <label for="username">Username</label>
                            <input type="text" id="username" placeholder="Seu username" required>
                        </div>
                        <div class="form-group">
                            <label for="senha">Senha</label>
                            <input type="password" id="senha" placeholder="Sua senha segura" required>
                        </div>
                        <button type="submit" class="btn-auth">🚀 Entrar</button>
                    </form>
                    <div class="toggle-auth">
                        Não tem conta? <a onclick="mudarParaCadastro()">Criar agora</a>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('loginForm').addEventListener('submit', executarLogin);
    }

    static renderarCadastro() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="auth-container">
                <div class="auth-box">
                    <div class="auth-header">
                        <h1><span class="logo">🎮</span> CARDS GAME</h1>
                        <p class="auth-subtitle">Crie sua Conta</p>
                    </div>
                    <form id="cadastroForm">
                        <div class="form-group">
                            <label for="nome">Nome Completo</label>
                            <input type="text" id="nome" placeholder="Seu nome" required>
                        </div>
                        <div class="form-group">
                            <label for="username">Username</label>
                            <input type="text" id="username" placeholder="username único" required>
                        </div>
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" id="email" placeholder="seu@email.com" required>
                        </div>
                        <div class="form-group">
                            <label for="senha">Senha</label>
                            <input type="password" id="senha" placeholder="Mínimo 8 caracteres" required>
                            <div class="password-strength" id="passwordStrength">
                                <div class="strength-bar">
                                    <div class="strength-fill" id="strengthFill"></div>
                                </div>
                                <div class="strength-text" id="strengthText">Fraca</div>
                            </div>
                        </div>
                        <button type="submit" class="btn-auth">✨ Cadastrar</button>
                    </form>
                    <div class="toggle-auth">
                        Já tem conta? <a onclick="mudarParaLogin()">Faça login</a>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('cadastroForm').addEventListener('submit', executarCadastro);
        document.getElementById('senha').addEventListener('input', verificarForcaSenha);
    }

    static renderarDashboard() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="menu-header">
                <div class="menu-header-content">
                    <div class="menu-logo">🎮 CARDS GAME</div>
                    <div class="menu-nav">
                        <button class="nav-btn active" onclick="mostrarDashboard()">📊 Dashboard</button>
                        <button class="nav-btn" onclick="mostrarMochila()">🎴 Mochila</button>
                        <button class="nav-btn" onclick="mostrarBatalha()">⚔️ Batalha</button>
                        <button class="nav-btn" onclick="mostrarRanking()">🏆 Ranking</button>
                    </div>
                    <div class="user-info">
                        <div class="user-avatar">${usuarioAtual.nome.charAt(0).toUpperCase()}</div>
                        <div>
                            <div class="user-name">${usuarioAtual.nome}</div>
                            <small style="opacity: 0.7">Level ${usuarioAtual.nivel}</small>
                        </div>
                        <button class="nav-btn" onclick="executarLogout()" style="margin-left: 12px;">🚪 Sair</button>
                    </div>
                </div>
            </div>
            <div id="conteudoPrincipal"></div>
        `;

        mostrarDashboard();
        ocultarLoadingScreen();
    }

    static renderarDashboard() {
        const conteudo = document.getElementById('conteudoPrincipal');
        conteudo.innerHTML = `
            <div class="dashboard">
                <h2>Bem-vindo, ${usuarioAtual.nome}! 🎮</h2>
                <div class="stats-bar">
                    <div class="stat-card">
                        <div class="stat-icon">⭐</div>
                        <div class="stat-label">Nível</div>
                        <div class="stat-value">${usuarioAtual.nivel}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">✨</div>
                        <div class="stat-label">XP</div>
                        <div class="stat-value">${usuarioAtual.experiencia}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🏆</div>
                        <div class="stat-label">Vitórias</div>
                        <div class="stat-value">${usuarioAtual.vitoria}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">💰</div>
                        <div class="stat-label">Moedas</div>
                        <div class="stat-value">${usuarioAtual.moedas}</div>
                    </div>
                </div>

                <h3 style="margin: 24px 0 16px;">Quick Actions</h3>
                <div class="flex" style="flex-wrap: wrap;">
                    <button class="btn btn-primary" onclick="mostrarLoja()">🛍️ Comprar Cartas</button>
                    <button class="btn btn-secondary" onclick="mostrarBatalha()">⚔️ Iniciar Batalha</button>
                    <button class="btn btn-secondary" onclick="mostrarMochila()">🎴 Minha Mochila</button>
                    <button class="btn btn-secondary" onclick="mostrarRanking()">🏆 Ranking</button>
                </div>
            </div>
        `;
    }
}

// ==================== FUNÇÕES DE TELA ====================

function mostrarDashboard() {
    UIRenderer.renderarDashboard();
}

function mostrarMochila() {
    const conteudo = document.getElementById('conteudoPrincipal');
    conteudo.innerHTML = `<div class="container"><h2>🎴 Minha Mochila</h2><p>Carregando...</p></div>`;

    CardsGameAPI.listarCartas()
        .then((dados) => {
            let html = `
                <div class="container">
                    <h2>🎴 Minha Mochila (${dados.total} cartas)</h2>
                    <div class="cartas-grid">
            `;

            dados.cartas.forEach((carta) => {
                html += `
                    <div class="card card-carta">
                        <div class="carta-imagem">🎴</div>
                        <div class="carta-nome">${carta.name}</div>
                        <div class="carta-raridade ${carta.rarity.toLowerCase()}">${carta.rarity}</div>
                        <div class="carta-stats">
                            <div class="stat-poder">⚡ ${carta.power}</div>
                            <div class="stat-evolucao">🌟 ${carta.evolution_stage}</div>
                        </div>
                    </div>
                `;
            });

            html += `</div></div>`;
            conteudo.innerHTML = html;
        })
        .catch((erro) => {
            NotificacaoManager.erro('Erro ao carregar mochila');
        });
}

function mostrarBatalha() {
    const conteudo = document.getElementById('conteudoPrincipal');
    conteudo.innerHTML = `
        <div class="container">
            <h2>⚔️ Iniciar Batalha</h2>
            <p style="text-align: center; padding: 40px;">
                Sistema de batalha em desenvolvimento...
                <br><br>
                Selecione um oponente e comece a lutar!
            </p>
        </div>
    `;
}

function mostrarRanking() {
    const conteudo = document.getElementById('conteudoPrincipal');
    conteudo.innerHTML = `<div class="container"><h2>🏆 Ranking Global</h2><p>Carregando...</p></div>`;

    CardsGameAPI.rankingGeral()
        .then((dados) => {
            let html = `
                <div class="container">
                    <h2>🏆 Ranking Global</h2>
                    <table class="ranking-table">
                        <thead>
                            <tr>
                                <th>Posição</th>
                                <th>Nome</th>
                                <th>Nível</th>
                                <th>Vitórias</th>
                                <th>Taxa de Vitória</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            dados.ranking.forEach((jogador) => {
                const posicaoClass = jogador.posicao <= 3 ? `top${jogador.posicao}` : '';
                html += `
                    <tr>
                        <td class="ranking-posicao ${posicaoClass}">
                            ${jogador.posicao <= 3 ? ['🥇', '🥈', '🥉'][jogador.posicao - 1] : jogador.posicao}
                        </td>
                        <td class="ranking-nome">${jogador.nome}</td>
                        <td class="ranking-valor">⭐ ${jogador.nivel}</td>
                        <td class="ranking-valor">🏆 ${jogador.vitorias}</td>
                        <td class="ranking-valor">${jogador.taxa_vitoria}%</td>
                    </tr>
                `;
            });

            html += `</tbody></table></div>`;
            conteudo.innerHTML = html;
        })
        .catch((erro) => {
            NotificacaoManager.erro('Erro ao carregar ranking');
        });
}

function mostrarLoja() {
    const conteudo = document.getElementById('conteudoPrincipal');
    conteudo.innerHTML = `
        <div class="container">
            <h2>🛍️ Loja de Cartas</h2>
            <div class="grid grid-2" style="margin-top: 24px;">
                <div class="card">
                    <h3>📦 Pacote Comum</h3>
                    <p style="font-size: 2rem; color: var(--cor-azul-neon); margin: 12px 0;">50 moedas</p>
                    <button class="btn btn-primary" onclick="comprarCarta('comum')">Comprar</button>
                </div>
                <div class="card">
                    <h3>💎 Pacote Raro</h3>
                    <p style="font-size: 2rem; color: var(--cor-roxo); margin: 12px 0;">150 moedas</p>
                    <button class="btn btn-primary" onclick="comprarCarta('raro')">Comprar</button>
                </div>
            </div>
        </div>
    `;
}

function comprarCarta(raridade) {
    CardsGameAPI.comprarCarta(raridade)
        .then((dados) => {
            NotificacaoManager.sucesso(`Carta ${dados.carta.rarity} adquirida: ${dados.carta.name}!`);
            usuarioAtual.moedas = dados.moedas_restantes;
            mostrarLoja();
        })
        .catch((erro) => {
            NotificacaoManager.erro(erro.message);
        });
}

// ==================== AUTENTICAÇÃO ====================

async function executarLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const senha = document.getElementById('senha').value;

    try {
        mostrarLoadingScreen();
        const dados = await CardsGameAPI.login(username, senha);
        usuarioAtual = dados.usuario;
        UIRenderer.renderarDashboard();
        NotificacaoManager.sucesso('Login realizado com sucesso!');
    } catch (erro) {
        ocultarLoadingScreen();
        NotificacaoManager.erro(erro.message || 'Erro ao fazer login');
    }
}

async function executarCadastro(e) {
    e.preventDefault();
    const nome = document.getElementById('nome').value;
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;

    try {
        mostrarLoadingScreen();
        const dados = await CardsGameAPI.cadastro(nome, username, email, senha);
        NotificacaoManager.sucesso('Cadastro realizado! Faça login para continuar');
        mudarParaLogin();
        ocultarLoadingScreen();
    } catch (erro) {
        ocultarLoadingScreen();
        NotificacaoManager.erro(erro.message || 'Erro ao cadastrar');
    }
}

async function executarLogout() {
    try {
        await CardsGameAPI.logout();
        usuarioAtual = null;
        UIRenderer.renderarLogin();
        NotificacaoManager.info('Logout realizado');
    } catch (erro) {
        NotificacaoManager.erro('Erro ao fazer logout');
    }
}

function mudarParaLogin() {
    UIRenderer.renderarLogin();
}

function mudarParaCadastro() {
    UIRenderer.renderarCadastro();
}

function verificarForcaSenha(e) {
    const senha = e.target.value;
    const strengthFill = document.getElementById('strengthFill');
    const strengthText = document.getElementById('strengthText');

    let forca = 0;
    if (senha.length >= 8) forca += 25;
    if (/[A-Z]/.test(senha)) forca += 25;
    if (/[0-9]/.test(senha)) forca += 25;
    if (/[!@#$%^&*]/.test(senha)) forca += 25;

    strengthFill.style.width = forca + '%';
    strengthFill.className = 'strength-fill';

    if (forca < 50) {
        strengthFill.classList.add('fraca');
        strengthText.textContent = 'Fraca';
        strengthText.className = 'strength-text fraca';
    } else if (forca < 75) {
        strengthFill.classList.add('media');
        strengthText.textContent = 'Média';
        strengthText.className = 'strength-text media';
    } else {
        strengthFill.classList.add('forte');
        strengthText.textContent = 'Forte';
        strengthText.className = 'strength-text forte';
    }
}

// ==================== TELAS DE CARREGAMENTO ====================

function mostrarLoadingScreen() {
    document.getElementById('loadingScreen').classList.remove('hidden');
}

function ocultarLoadingScreen() {
    document.getElementById('loadingScreen').classList.add('hidden');
}

// ==================== INICIALIZAR ====================

async function inicializar() {
    ParticleManager.criar();

    try {
        const dados = await CardsGameAPI.verificarSessao();
        usuarioAtual = dados.usuario;
        UIRenderer.renderarDashboard();
    } catch (erro) {
        UIRenderer.renderarLogin();
    }
}

// Inicializar ao carregar
document.addEventListener('DOMContentLoaded', inicializar);
