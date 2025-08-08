import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configurações do sistema"""
    
    # Definir pasta base do projeto corretamente
    BASE_DIR = Path(__file__).parent.parent.parent  # backend/python -> backend -> bot_whatsapp_cliente
    
    # Usar caminhos relativos ao BASE_DIR
    PASTA_RAIZ = str(BASE_DIR / 'storage' / 'arquivos_clientes')
    DATABASE_PATH = str(BASE_DIR / 'data' / 'whatsapp_dados.db')
    BACKUP_PATH = str(BASE_DIR / 'storage' / 'backups')
    
    # Permitir override via .env se necessário
    if os.getenv('PASTA_RAIZ'):
        custom_pasta = os.getenv('PASTA_RAIZ')
        if not os.path.isabs(custom_pasta):
            PASTA_RAIZ = str(BASE_DIR / custom_pasta)
        else:
            PASTA_RAIZ = custom_pasta
    
    if os.getenv('DATABASE_PATH'):
        custom_db = os.getenv('DATABASE_PATH')
        if not os.path.isabs(custom_db):
            DATABASE_PATH = str(BASE_DIR / custom_db)
        else:
            DATABASE_PATH = custom_db
    
    if os.getenv('BACKUP_PATH'):
        custom_backup = os.getenv('BACKUP_PATH')
        if not os.path.isabs(custom_backup):
            BACKUP_PATH = str(BASE_DIR / custom_backup)
        else:
            BACKUP_PATH = custom_backup
    
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

# Configurações específicas por ambiente
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Debug para verificar caminhos
if __name__ == "__main__":
    print("🔧 Configurações carregadas:")
    print(f"  BASE_DIR: {Config.BASE_DIR}")
    print(f"  PASTA_RAIZ: {Config.PASTA_RAIZ}")
    print(f"  DATABASE_PATH: {Config.DATABASE_PATH}")
    print(f"  BACKUP_PATH: {Config.BACKUP_PATH}")