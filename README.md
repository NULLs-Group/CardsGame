# 🎮 CARDS GAME - Sistema Futurista de Cartas

Um jogo de cartas multiplayer neon futurista com design glassmorphism, desenvolvido com Flask (backend) e HTML/CSS/JavaScript (frontend).

## 🎨 Características

### Visual
- ✨ Design **Neon Futurista** com glassmorphism
- 🎯 Paleta: Preto | Azul Neon | Roxo | Rosa Neon
- 🌈 Animações suaves e efeitos de partículas
- 💫 Hover animado com brilho neon
- 🔆 Sombras e efeitos de profundidade

### Responsividade
- 📱 100% responsivo (celular, tablet, desktop)
- ⚡ Performance otimizada
- 🎯 Touch-friendly

### Funcionalidades
- 🔐 Sistema de autenticação seguro com criptografia
- 🎴 Sistema de cartas com raridade e evolução
- ⚔️ Sistema de batalhas PvP em tempo real
- 📊 Dashboard com estatísticas
- 🏆 Ranking global com leaderboard
- 💰 Sistema de moedas e loja
- ✨ Sistema de XP, níveis e conquistas
- 🛡️ Validação de upload de arquivos
- 📧 Validação de email robusta
- 🔒 Proteção de rotas com sessão segura

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.8+
- pip

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/NULLs-Group/CardsGame.git
cd CardsGame
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure o arquivo .env**
```bash
cp .env.example .env
```

5. **Inicie o servidor**
```bash
cd backend
python app.py
```

O servidor estará em **http://localhost:5000** 🚀

## 📁 Estrutura do Projeto

```
CardsGame/
├── backend/
│   ├── app.py                 # Aplicação Flask principal
│   ├── database.py            # Banco de dados
│   ├── models/                # Modelos SQLAlchemy
│   ├── routes/                # Endpoints da API
│   └── uploads/               # Armazenamento de arquivos
├── frontend/
│   ├── index.html             # Página principal
│   ├── css/                   # Estilos (neon + glassmorphism)
│   └── js/                    # Lógica JavaScript
├── requirements.txt           # Dependências Python
├── .env.example              # Configuração exemplo
└── README.md                 # Este arquivo
```

## 🔌 API Endpoints Principais

### Autenticação
- `POST /api/auth/cadastro` - Registrar
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/sessao` - Verificar sessão

### Sistema de Cartas
- `GET /api/cartas/` - Listar cartas
- `POST /api/cartas/comprar` - Comprar carta
- `GET /api/mochila/cartas` - Minhas cartas

### Batalhas
- `POST /api/batalha/iniciar` - Iniciar batalha
- `POST /api/batalha/<id>/rodada` - Executar rodada
- `GET /api/batalha/ranking` - Ranking

### Alunos
- `GET /api/alunos/` - Listar jogadores
- `GET /api/alunos/<id>` - Perfil público
- `GET /api/alunos/ranking/geral` - Ranking geral

## 🔐 Segurança

✅ Senhas criptografadas com bcrypt  
✅ Validação de email robusta  
✅ Requisitos de senha forte  
✅ Sessão segura com HttpOnly cookies  
✅ CORS configurado  
✅ Proteção contra upload malicioso  
✅ Validação em todas as rotas  

## 🎮 Como Jogar

1. **Cadastre-se** com email e senha forte
2. **Compre cartas** na loja (diferentes raridades)
3. **Duele com outros jogadores** em batalhas de 3 rodadas
4. **Suba de nível** acumulando XP
5. **Evolua suas cartas** para ficarem mais fortes
6. **Compita** no ranking global

## 🐛 Troubleshooting

```bash
# Erro de dependências?
pip install -r requirements.txt

# Porta 5000 em uso?
# Edite backend/app.py e mude a porta

# Banco de dados corrompido?
rm backend/database.db
# Reinicie o servidor
```

## 📈 Roadmap

- [ ] Chat em tempo real
- [ ] Sistema de amigos
- [ ] Clãs/Guildas
- [ ] Mercado de cartas
- [ ] Mobile app
- [ ] Websocket para tempo real

## 📝 Licença

MIT - Veja LICENSE para detalhes

## 👥 Contribuindo

Contribuições são bem-vindas! Faça um Fork, crie uma branch e abra um Pull Request.

---

**Desenvolvido com ❤️ e neon futurista** 🎮✨
