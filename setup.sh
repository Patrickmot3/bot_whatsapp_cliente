#!/bin/bash
# setup_organizado.sh - Configuração da estrutura completa organizada

echo "🏗️ Configurando Estrutura Completa WhatsApp Manager"
echo "=================================================="

# Criar estrutura de diretórios
echo "📁 Criando estrutura de pastas..."

mkdir -p backend/python
mkdir -p backend/nodejs
mkdir -p data/static
mkdir -p storage/arquivos_clientes
mkdir -p storage/backups
mkdir -p storage/logs
mkdir -p storage/temp

echo "✅ Estrutura de pastas criada!"

# Configurar backend Python
echo "🐍 Configurando backend Python..."
cd backend/python

# Criar ambiente virtual se não existir
if [ ! -d "../../.venv" ]; then
    echo "📦 Criando ambiente virtual Python..."
    python -m venv ../../.venv
fi

# Ativar ambiente virtual
source ../../.venv/bin/activate

# Copiar arquivos Python para pasta correta
echo "📄 Movendo arquivos Python..."
mv ../../whatsapp_manager.py . 2>/dev/null || echo "Arquivo whatsapp_manager.py não encontrado na raiz"
mv ../../whatsapp_api_integration.py . 2>/dev/null || echo "Arquivo whatsapp_api_integration.py não encontrado na raiz"
mv ../../config.py . 2>/dev/null || echo "Arquivo config.py não encontrado na raiz"
mv ../../backup_sistema.py . 2>/dev/null || echo "Arquivo backup_sistema.py não encontrado na raiz"
mv ../../monitor_sistema.py . 2>/dev/null || echo "Arquivo monitor_sistema.py não encontrado na raiz"
mv ../../exemplo_integracao.py . 2>/dev/null || echo "Arquivo exemplo_integracao.py não encontrado na raiz"
mv ../../requirements.txt . 2>/dev/null || echo "Arquivo requirements.txt não encontrado na raiz"
mv ../../.env . 2>/dev/null || echo "Arquivo .env não encontrado na raiz"

# Atualizar caminhos no config.py
echo "⚙️ Atualizando configurações Python..."
cat > config.py << 'EOF'
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configurações do sistema"""
    
    # Caminhos baseados na nova estrutura
    BASE_DIR = Path(__file__).parent.parent.parent  # Volta para raiz
    PASTA_RAIZ = os.getenv('PASTA_RAIZ', str(BASE_DIR / 'storage' / 'arquivos_clientes'))
    DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'data' / 'whatsapp_dados.db'))
    BACKUP_PATH = os.getenv('BACKUP_PATH', str(BASE_DIR / 'storage' / 'backups'))
    
    # API
    WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN', 'desenvolvimento')
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave-desenvolvimento-nao-usar-em-producao')
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Limites de arquivo
    MAX_FILE_SIZE = os.getenv('MAX_FILE_SIZE', '50MB')
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'jpg,jpeg,png,pdf,doc,docx,mp3,mp4,wav').split(','))
    
    # Backup
    BACKUP_INTERVAL = os.getenv('BACKUP_INTERVAL', '24h')
    AUTO_BACKUP = os.getenv('AUTO_BACKUP', 'True').lower() == 'true'
    
    @staticmethod
    def init_app(app):
        """Inicializa configurações no Flask"""
        app.config['SECRET_KEY'] = Config.SECRET_KEY
        app.config['MAX_CONTENT_LENGTH'] = Config.parse_file_size(Config.MAX_FILE_SIZE)
    
    @staticmethod
    def parse_file_size(size_str):
        """Converte string de tamanho para bytes"""
        size_str = size_str.upper()
        if size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        return int(size_str)

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
EOF

# Criar .env se não existir
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env..."
    cat > .env << 'EOF'
# Configurações do WhatsApp Manager
WEBHOOK_TOKEN=desenvolvimento
PASTA_RAIZ=storage/arquivos_clientes
DATABASE_PATH=data/whatsapp_dados.db
BACKUP_PATH=storage/backups

# Configurações da API
API_HOST=0.0.0.0
API_PORT=5000
DEBUG=True

# Configurações de segurança
SECRET_KEY=sua_chave_secreta_aqui
MAX_FILE_SIZE=50MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf,doc,docx,mp3,mp4,wav

# Configurações de backup
BACKUP_INTERVAL=24h
AUTO_BACKUP=True
EOF
fi

# Instalar dependências Python
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

cd ../../  # Voltar para raiz

# Configurar backend Node.js
echo "📦 Configurando backend Node.js..."
cd backend/nodejs

# Inicializar package.json se não existir
if [ ! -f "package.json" ]; then
    echo "📝 Criando package.json..."
    npm init -y
    
    # Atualizar package.json com configurações
    cat > package.json << 'EOF'
{
  "name": "whatsapp-nodejs-backend",
  "version": "1.0.0",
  "description": "Backend Node.js para integração WhatsApp com sistema Python",
  "main": "whatsapp_server.js",
  "scripts": {
    "start": "node whatsapp_server.js",
    "dev": "nodemon whatsapp_server.js"
  },
  "dependencies": {
    "@wppconnect-team/wppconnect": "^1.32.0",
    "express": "^4.18.2",
    "sqlite3": "^5.1.6",
    "node-fetch": "^3.3.2"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  },
  "keywords": ["whatsapp", "wppconnect", "nodejs", "integration"],
  "author": "Seu Nome",
  "license": "MIT"
}
EOF
fi

# Instalar dependências Node.js
echo "📦 Instalando dependências Node.js..."
npm install

# Mover whatsapp_server.js se existir na raiz
if [ -f "../../whatsapp_server.js" ]; then
    echo "📄 Movendo whatsapp_server.js..."
    mv ../../whatsapp_server.js .
fi

cd ../../  # Voltar para raiz

# Criar scripts de execução
echo "📝 Criando scripts de execução..."

# Script para iniciar Python
cat > start_python.sh << 'EOF'
#!/bin/bash
echo "🐍 Iniciando sistema Python..."
cd backend/python
source ../../.venv/bin/activate
python whatsapp_api_integration.py
EOF

# Script para iniciar Node.js
cat > start_nodejs.sh << 'EOF'
#!/bin/bash
echo "📦 Iniciando sistema Node.js..."
cd backend/nodejs
npm start
EOF

# Script para iniciar ambos
cat > start_all.sh << 'EOF'
#!/bin/bash
echo "🚀 Iniciando sistemas integrados..."

# Iniciar Python em background
echo "🐍 Iniciando Python..."
cd backend/python
source ../../.venv/bin/activate
python whatsapp_api_integration.py &
PYTHON_PID=$!

# Voltar para raiz
cd ../../

# Aguardar um pouco
sleep 3

# Iniciar Node.js
echo "📦 Iniciando Node.js..."
cd backend/nodejs
npm start &
NODEJS_PID=$!

# Voltar para raiz
cd ../../

echo "✅ Sistemas iniciados!"
echo "🐍 Python PID: $PYTHON_PID"
echo "📦 Node.js PID: $NODEJS_PID"
echo ""
echo "URLs disponíveis:"
echo "🐍 Python API: http://localhost:5000/health"
echo "📦 Node.js API: http://localhost:3000/health"
echo ""
echo "Para parar os sistemas:"
echo "kill $PYTHON_PID $NODEJS_PID"

# Manter script rodando
wait
EOF

# Dar permissões de execução
chmod +x start_python.sh
chmod +x start_nodejs.sh
chmod +x start_all.sh

#