# reorganizar.ps1 - Script para reorganizar arquivos existentes
Write-Host "🔄 Reorganizando estrutura do projeto..." -ForegroundColor Green

# Criar estrutura de pastas
Write-Host "📁 Criando estrutura..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "backend\python" -Force | Out-Null
New-Item -ItemType Directory -Path "backend\nodejs" -Force | Out-Null
New-Item -ItemType Directory -Path "data\static" -Force | Out-Null
New-Item -ItemType Directory -Path "storage\arquivos_clientes" -Force | Out-Null
New-Item -ItemType Directory -Path "storage\backups" -Force | Out-Null
New-Item -ItemType Directory -Path "storage\logs" -Force | Out-Null
New-Item -ItemType Directory -Path "storage\temp" -Force | Out-Null

# Mover arquivos Python
Write-Host "🐍 Organizando arquivos Python..." -ForegroundColor Blue
$pythonFiles = @(
    "whatsapp_manager.py",
    "whatsapp_api_integration.py", 
    "config.py",
    "backup_sistema.py",
    "monitor_sistema.py",
    "exemplo_integracao.py",
    "requirements.txt",
    ".env",
    ".env.example"
)

foreach ($file in $pythonFiles) {
    if (Test-Path $file) {
        Move-Item $file "backend\python\" -Force
        Write-Host "  ✅ Movido: $file" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ Não encontrado: $file" -ForegroundColor Yellow
    }
}

# Mover arquivos Node.js
Write-Host "📦 Organizando arquivos Node.js..." -ForegroundColor Blue
$nodejsFiles = @(
    "whatsapp_server.js",
    "package.json",
    "package-lock.json"
)

foreach ($file in $nodejsFiles) {
    if (Test-Path $file) {
        Move-Item $file "backend\nodejs\" -Force
        Write-Host "  ✅ Movido: $file" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ Não encontrado: $file" -ForegroundColor Yellow
    }
}

# Mover pasta node_modules se existir
if (Test-Path "node_modules") {
    Move-Item "node_modules" "backend\nodejs\" -Force
    Write-Host "  ✅ Movido: node_modules" -ForegroundColor Green
}

# Mover bancos de dados
Write-Host "💾 Organizando bancos de dados..." -ForegroundColor Blue
$dbFiles = @("*.db", "*.sqlite", "*.sqlite3")
foreach ($pattern in $dbFiles) {
    Get-ChildItem -Path . -Name $pattern | ForEach-Object {
        Move-Item $_ "data\" -Force
        Write-Host "  ✅ Movido: $_" -ForegroundColor Green
    }
}

# Mover pasta static se existir
if (Test-Path "static") {
    Move-Item "static\*" "data\static\" -Force -ErrorAction SilentlyContinue
    Remove-Item "static" -Force -ErrorAction SilentlyContinue
    Write-Host "  ✅ Movido: static/" -ForegroundColor Green
}

# Mover pasta puppeteer se existir
if (Test-Path "puppeteer") {
    Move-Item "puppeteer" "." -Force
    Write-Host "  ✅ Mantido: puppeteer/" -ForegroundColor Green
}

# Atualizar config.py com novos caminhos
Write-Host "⚙️ Atualizando configurações..." -ForegroundColor Blue
$configContent = @"
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    # Caminhos baseados na nova estrutura
    BASE_DIR = Path(__file__).parent.parent.parent  # Volta para raiz
    PASTA_RAIZ = os.getenv('PASTA_RAIZ', str(BASE_DIR / 'storage' / 'arquivos_clientes'))
    DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'data' / 'whatsapp_dados.db'))
    BACKUP_PATH = os.getenv('BACKUP_PATH', str(BASE_DIR / 'storage' / 'backups'))
    
    # API
    WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN', 'desenvolvimento')
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave-desenvolvimento')
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Limites
    MAX_FILE_SIZE = os.getenv('MAX_FILE_SIZE', '50MB')
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'jpg,jpeg,png,pdf,doc,docx,mp3,mp4,wav').split(','))
    
    # Backup
    BACKUP_INTERVAL = os.getenv('BACKUP_INTERVAL', '24h')
    AUTO_BACKUP = os.getenv('AUTO_BACKUP', 'True').lower() == 'true'
    
    @staticmethod
    def parse_file_size(size_str):
        size_str = size_str.upper()
        if size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        return int(size_str)

config = {'default': Config}
"@

$configContent | Out-File -FilePath "backend\python\config.py" -Encoding UTF8
Write-Host "  ✅ config.py atualizado" -ForegroundColor Green

# Criar scripts de execução
Write-Host "📝 Criando scripts de execução..." -ForegroundColor Blue

# Script Python
@"
@echo off
echo 🐍 Iniciando sistema Python...
cd backend\python
call ..\..\venv\Scripts\activate.bat
python whatsapp_api_integration.py
pause
"@ | Out-File -FilePath "start_python.bat" -Encoding ASCII

# Script Node.js
@"
@echo off
echo 📦 Iniciando sistema Node.js...
cd backend\nodejs
npm start
pause
"@ | Out-File -FilePath "start_nodejs.bat" -Encoding ASCII

# Script ambos
@"
@echo off
echo 🚀 Iniciando sistemas integrados...
echo 🐍 Iniciando Python...
start "Python WhatsApp" cmd /k "cd backend\python && call ..\..\venv\Scripts\activate.bat && python whatsapp_api_integration.py"
timeout /t 5 /nobreak > nul
echo 📦 Iniciando Node.js...
start "Node.js WhatsApp" cmd /k "cd backend\nodejs && npm start"
echo ✅ Sistemas iniciados em janelas separadas!
echo 🐍 Python API: http://localhost:5000/health
echo 📦 Node.js API: http://localhost:3000/health
pause
"@ | Out-File -FilePath "start_all.bat" -Encoding ASCII

Write-Host "  ✅ Scripts criados" -ForegroundColor Green

Write-Host ""
Write-Host "✅ Reorganização concluída!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Nova estrutura:" -ForegroundColor White
Write-Host "├── backend\python\     (Sistema Python)" -ForegroundColor Cyan
Write-Host "├── backend\nodejs\     (Sistema Node.js)" -ForegroundColor Cyan  
Write-Host "├── data\              (Bancos de dados)" -ForegroundColor Cyan
Write-Host "├── storage\           (Arquivos e backups)" -ForegroundColor Cyan
Write-Host "└── scripts .bat       (Scripts de execução)" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Para iniciar:" -ForegroundColor Yellow
Write-Host "start_all.bat          (Ambos sistemas)" -ForegroundColor White
Write-Host "start_python.bat       (Só Python)" -ForegroundColor White
Write-Host "start_nodejs.bat       (Só Node.js)" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. cd backend\nodejs && npm install" -ForegroundColor White
Write-Host "2. .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "3. cd backend\python && pip install -r requirements.txt" -ForegroundColor White
Write-Host "4. .\start_all.bat" -ForegroundColor White