#!/usr/bin/env python3
"""
Script para diagnosticar problema de criação de pastas
"""

import os
import sys
from pathlib import Path

# Adicionar o caminho do backend/python ao sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'python'))

def verificar_estrutura():
    """Verifica a estrutura atual e configurações"""
    
    print("🔍 Diagnóstico do Sistema de Pastas")
    print("=" * 50)
    
    # 1. Verificar diretório atual
    current_dir = Path.cwd()
    print(f"📍 Diretório atual: {current_dir}")
    
    # 2. Verificar se estamos na pasta correta
    expected_structure = [
        "backend/python",
        "backend/nodejs", 
        "storage",
        "data"
    ]
    
    print("\n📁 Verificando estrutura esperada:")
    for item in expected_structure:
        path = current_dir / item
        status = "✅" if path.exists() else "❌"
        print(f"  {status} {item}")
    
    # 3. Tentar importar config
    try:
        sys.path.insert(0, str(current_dir / "backend" / "python"))
        from config import Config
        
        print(f"\n⚙️ Configurações carregadas:")
        print(f"  📁 PASTA_RAIZ: {Config.PASTA_RAIZ}")
        print(f"  💾 DATABASE_PATH: {Config.DATABASE_PATH}")
        print(f"  📦 BACKUP_PATH: {Config.BACKUP_PATH}")
        
        # Verificar se os caminhos são absolutos ou relativos
        pasta_raiz_path = Path(Config.PASTA_RAIZ)
        if pasta_raiz_path.is_absolute():
            print(f"  🔗 Caminho absoluto: {pasta_raiz_path}")
        else:
            print(f"  🔗 Caminho relativo: {current_dir / pasta_raiz_path}")
            
    except ImportError as e:
        print(f"\n❌ Erro ao importar config: {e}")
        return False
    
    # 4. Testar criação de pasta manualmente
    try:
        from whatsapp_manager import WhatsAppManager
        
        print(f"\n🧪 Testando WhatsAppManager...")
        wpp = WhatsAppManager()
        
        print(f"  📁 Pasta raiz configurada: {wpp.pasta_raiz}")
        print(f"  📍 Pasta raiz absoluta: {wpp.pasta_raiz.absolute()}")
        print(f"  ✅ Pasta existe: {wpp.pasta_raiz.exists()}")
        
        # Testar criação de pasta de contato
        print(f"\n🔧 Testando criação de pasta de contato...")
        telefone_teste = "6281483040"
        nome_teste = "Teste Pasta"
        
        pasta_criada = wpp.criar_pasta_contato(telefone_teste, nome_teste)
        print(f"  📁 Pasta criada: {pasta_criada}")
        print(f"  📍 Caminho absoluto: {pasta_criada.absolute()}")
        print(f"  ✅ Existe: {pasta_criada.exists()}")
        
        # Verificar subpastas
        subpastas = ["imagens", "documentos", "audios", "videos", "outros"]
        print(f"\n📂 Subpastas criadas:")
        for subpasta in subpastas:
            sub_path = pasta_criada / subpasta
            status = "✅" if sub_path.exists() else "❌"
            print(f"  {status} {subpasta}/")
            
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao testar WhatsAppManager: {e}")
        import traceback
        traceback.print_exc()
        return False

def corrigir_paths():
    """Corrige os caminhos se necessário"""
    
    print(f"\n🔧 Tentando corrigir configurações...")
    
    # Verificar se estamos na pasta raiz do projeto
    current_dir = Path.cwd()
    
    # Se estivermos em backend/python, voltar para raiz
    if current_dir.name == "python" and current_dir.parent.name == "backend":
        os.chdir(current_dir.parent.parent)
        print(f"📍 Mudando para diretório raiz: {Path.cwd()}")
    
    # Criar pastas necessárias
    pastas_necessarias = [
        "storage/arquivos_clientes",
        "storage/backups", 
        "storage/logs",
        "storage/temp",
        "data"
    ]
    
    print(f"\n📁 Criando estrutura necessária:")
    for pasta in pastas_necessarias:
        path = Path(pasta)
        path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {pasta}")

def main():
    """Função principal"""
    
    if not verificar_estrutura():
        print(f"\n🔧 Tentando corrigir problemas...")
        corrigir_paths()
        
        print(f"\n🔄 Verificando novamente...")
        verificar_estrutura()
    
    print(f"\n✅ Diagnóstico concluído!")
    print(f"\n💡 Se ainda houver problemas:")
    print(f"   1. Execute este script na pasta raiz do projeto")
    print(f"   2. Verifique se o .env está correto")
    print(f"   3. Reinstale o sistema se necessário")

if __name__ == "__main__":
    main()
