#!/usr/bin/env python3
"""
Sistema de Backup para WhatsApp Manager
"""

import os
import sqlite3
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
import json
from config import Config

class BackupManager:
    def __init__(self):
        self.backup_dir = Path(Config.BACKUP_PATH)
        self.backup_dir.mkdir(exist_ok=True)
    
    def criar_backup_completo(self):
        """Cria backup completo do sistema"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"whatsapp_backup_{timestamp}.zip"
        backup_path = self.backup_dir / backup_name
        
        print(f"📦 Criando backup: {backup_name}")
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Backup do banco de dados
            if os.path.exists(Config.DATABASE_PATH):
                zipf.write(Config.DATABASE_PATH, 'database/whatsapp_dados.db')
                print("✅ Banco de dados incluído no backup")
            
            # Backup dos arquivos de clientes
            pasta_raiz = Path(Config.PASTA_RAIZ)
            if pasta_raiz.exists():
                for root, dirs, files in os.walk(pasta_raiz):
                    for file in files:
                        file_path = Path(root) / file
                        arc_path = file_path.relative_to(pasta_raiz.parent)
                        zipf.write(file_path, arc_path)
                print(f"✅ Arquivos de {pasta_raiz} incluídos no backup")
            
            # Backup das configurações
            if os.path.exists('.env'):
                zipf.write('.env', 'config/.env')
            
            # Metadados do backup
            metadata = {
                'timestamp': timestamp,
                'version': '1.0',
                'files_count': len(zipf.namelist()),
                'created_by': 'WhatsApp Manager Backup System'
            }
            
            zipf.writestr('backup_metadata.json', json.dumps(metadata, indent=2))
        
        print(f"✅ Backup criado com sucesso: {backup_path}")
        print(f"📊 Tamanho do arquivo: {backup_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        return backup_path
    
    def limpar_backups_antigos(self, dias_manter=30):
        """Remove backups mais antigos que X dias"""
        cutoff_date = datetime.now() - timedelta(days=dias_manter)
        
        backups_removidos = 0
        for backup_file in self.backup_dir.glob("whatsapp_backup_*.zip"):
            # Extrair data do nome do arquivo
            try:
                timestamp_str = backup_file.stem.split('_')[-2] + '_' + backup_file.stem.split('_')[-1]
                backup_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                
                if backup_date < cutoff_date:
                    backup_file.unlink()
                    backups_removidos += 1
                    print(f"🗑️ Backup antigo removido: {backup_file.name}")
            
            except (ValueError, IndexError):
                print(f"⚠️ Nome de backup inválido ignorado: {backup_file.name}")
        
        if backups_removidos == 0:
            print("ℹ️ Nenhum backup antigo encontrado para remoção")
        else:
            print(f"✅ {backups_removidos} backup(s) antigo(s) removido(s)")
    
    def listar_backups(self):
        """Lista todos os backups disponíveis"""
        backups = list(self.backup_dir.glob("whatsapp_backup_*.zip"))
        backups.sort(reverse=True)  # Mais recentes primeiro
        
        print(f"📋 Backups disponíveis ({len(backups)}):")
        print("-" * 60)
        
        for backup in backups:
            size_mb = backup.stat().st_size / 1024 / 1024
            mod_time = datetime.fromtimestamp(backup.stat().st_mtime)
            print(f"📦 {backup.name}")
            print(f"   Tamanho: {size_mb:.2f} MB")
            print(f"   Criado: {mod_time.strftime('%d/%m/%Y %H:%M:%S')}")
            print()
    
    def restaurar_backup(self, backup_path):
        """Restaura um backup (USE COM CUIDADO!)"""
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup não encontrado: {backup_path}")
        
        print(f"🔄 Restaurando backup: {backup_file.name}")
     