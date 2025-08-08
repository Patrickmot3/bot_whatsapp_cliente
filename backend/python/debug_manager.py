#!/usr/bin/env python3
"""
Debug do WhatsAppManager para ver onde está o problema
"""

import sys
import os
from pathlib import Path

# Garantir que estamos na pasta correta
if Path.cwd().name == "python":
    os.chdir(Path.cwd().parent.parent)

sys.path.insert(0, str(Path.cwd() / "backend" / "python"))

try:
    from whatsapp_manager import WhatsAppManager
    from config import Config
    
    print("🔍 Debug WhatsAppManager")
    print("=" * 40)
    
    # Verificar config
    print(f"📁 Config.PASTA_RAIZ: {Config.PASTA_RAIZ}")
    
    # Inicializar manager
    wpp = WhatsAppManager()
    print(f"📁 Manager.pasta_raiz: {wpp.pasta_raiz}")
    print(f"📍 Caminho absoluto: {wpp.pasta_raiz.absolute()}")
    print(f"✅ Pasta existe: {wpp.pasta_raiz.exists()}")
    
    # Simular registro de contato
    print(f"\n🧪 Simulando registro de contato:")
    telefone = "6281483040"
    nome = "Meu Contato Pessoal"
    
    print(f"  📱 Telefone: {telefone}")
    print(f"  👤 Nome: {nome}")
    
    # Chamar registrar_contato
    contato_id = wpp.registrar_contato(telefone, nome)
    print(f"  ✅ Contato ID: {contato_id}")
    
    # Verificar se pasta foi criada
    telefone_limpo = ''.join(filter(str.isdigit, telefone))
    nome_limpo = ''.join(c for c in nome if c.isalnum() or c in (' ', '-', '_')).strip()
    nome_pasta = f"{telefone_limpo}_{nome_limpo}"
    
    pasta_esperada = wpp.pasta_raiz / nome_pasta
    print(f"  📁 Pasta esperada: {pasta_esperada}")
    print(f"  ✅ Pasta existe: {pasta_esperada.exists()}")
    
    if pasta_esperada.exists():
        print(f"  📂 Conteúdo:")
        for item in pasta_esperada.iterdir():
            tipo = "📁" if item.is_dir() else "📄"
            print(f"    {tipo} {item.name}")
    else:
        print(f"  ❌ Pasta não foi criada!")
        
        # Tentar criar manualmente
        print(f"\n🔧 Tentando criar manualmente...")
        pasta_criada = wpp.criar_pasta_contato(telefone, nome)
        print(f"  📁 Pasta criada: {pasta_criada}")
        print(f"  ✅ Existe agora: {pasta_criada.exists()}")
    
    # Listar todas as pastas na pasta raiz
    print(f"\n📋 Todas as pastas em {wpp.pasta_raiz}:")
    if wpp.pasta_raiz.exists():
        for item in wpp.pasta_raiz.iterdir():
            if item.is_dir():
                print(f"  📁 {item.name}")
    else:
        print(f"  ❌ Pasta raiz não existe!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
