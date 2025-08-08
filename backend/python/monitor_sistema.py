#!/usr/bin/env python3
"""
Monitor do sistema WhatsApp Manager
"""

import time
import schedule
import psutil
import sqlite3
from datetime import datetime
from pathlib import Path
from config import Config
from backup_sistema import BackupManager

class SystemMonitor:
    def __init__(self):
        self.backup_manager = BackupManager()
    
    def verificar_saude_sistema(self):
        """Verifica a saúde do sistema"""
        print(f"🩺 Verificação de saúde - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        # Verificar banco de dados
        try:
            conn = sqlite3.connect(Config.DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contatos")
            total_contatos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM mensagens")
            total_mensagens = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM despesas WHERE status = 'pendente'")
            despesas_pendentes = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"✅ Banco de dados: OK")
            print(f"   - {total_contatos} contatos")
            print(f"   - {total_mensagens} mensagens")
            print(f"   - {despesas_pendentes} despesas pendentes")
        
        except Exception as e:
            print(f"❌ Banco de dados: ERRO - {e}")
        
        # Verificar espaço em disco
        pasta_raiz = Path(Config.PASTA_RAIZ)
        if pasta_raiz.exists():
            disk_usage = psutil.disk_usage(pasta_raiz)
            used_gb = disk_usage.used / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            total_gb = disk_usage.total / (1024**3)
            percent_used = (disk_usage.used / disk_usage.total) * 100
            
            print(f"💾 Espaço em disco: {percent_used:.1f}% usado")
            print(f"   - Usado: {used_gb:.