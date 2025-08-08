#!/usr/bin/env python3
"""
Sistema de Gerenciamento de Mensagens e Arquivos WhatsApp
Baseado na estrutura do WPPConnect para receber e organizar dados de clientes
"""

import os
import sqlite3
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import hashlib
import mimetypes

# Importar configurações
from config import Config

class WhatsAppManager:
    def __init__(self, pasta_raiz: Optional[str] = None):
        """
        Inicializa o gerenciador do WhatsApp
        
        Args:
            pasta_raiz: Pasta principal onde serão salvos os arquivos dos clientes
                       Se None, usa Config.PASTA_RAIZ
        """
        # CORREÇÃO: Usar Config.PASTA_RAIZ em vez de parâmetro padrão
        if pasta_raiz is None:
            self.pasta_raiz = Path(Config.PASTA_RAIZ)
        else:
            self.pasta_raiz = Path(pasta_raiz)
            
        # CORREÇÃO: Usar Config.DATABASE_PATH 
        self.db_path = Config.DATABASE_PATH
        
        # Criar pasta raiz se não existir
        self.pasta_raiz.mkdir(parents=True, exist_ok=True)
        
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de contatos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS contatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telefone TEXT UNIQUE NOT NULL,
            nome TEXT,
            pasta_contato TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultimo_contato TIMESTAMP
        )
        ''')
        
        # Tabela de mensagens recebidas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contato_id INTEGER,
            telefone TEXT NOT NULL,
            tipo_mensagem TEXT NOT NULL,
            conteudo_texto TEXT,
            nome_arquivo TEXT,
            caminho_arquivo TEXT,
            tamanho_arquivo INTEGER,
            data_recebimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hash_arquivo TEXT,
            metadados TEXT,
            FOREIGN KEY (contato_id) REFERENCES contatos (id)
        )
        ''')
        
        # Tabela específica para despesas (baseada nas mensagens)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mensagem_id INTEGER,
            contato_id INTEGER,
            tipo_despesa TEXT,
            valor REAL,
            descricao TEXT,
            categoria TEXT,
            data_despesa DATE,
            data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pendente',
            observacoes TEXT,
            FOREIGN KEY (mensagem_id) REFERENCES mensagens (id),
            FOREIGN KEY (contato_id) REFERENCES contatos (id)
        )
        ''')
        
        # Tabela de configurações
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT UNIQUE NOT NULL,
            valor TEXT,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Banco de dados inicializado com sucesso!")
    
    def criar_pasta_contato(self, telefone: str, nome: Optional[str] = None) -> Path:
        """
        Cria pasta para o contato se não existir
        
        Args:
            telefone: Número do telefone
            nome: Nome do contato (opcional)
            
        Returns:
            Path da pasta criada
        """
        # Limpar telefone para nome de pasta
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        
        if nome:
            # Remove caracteres especiais do nome
            nome_limpo = ''.join(c for c in nome if c.isalnum() or c in (' ', '-', '_')).strip()
            nome_pasta = f"{telefone_limpo}_{nome_limpo}"
        else:
            nome_pasta = telefone_limpo
        
        pasta_contato = self.pasta_raiz / nome_pasta
        pasta_contato.mkdir(exist_ok=True)
        
        # Criar subpastas organizacionais
        (pasta_contato / "imagens").mkdir(exist_ok=True)
        (pasta_contato / "documentos").mkdir(exist_ok=True)
        (pasta_contato / "audios").mkdir(exist_ok=True)
        (pasta_contato / "videos").mkdir(exist_ok=True)
        (pasta_contato / "outros").mkdir(exist_ok=True)
        
        return pasta_contato
    
    def registrar_contato(self, telefone: str, nome: Optional[str] = None) -> int:
        """
        Registra ou atualiza um contato no banco
        
        Args:
            telefone: Número do telefone
            nome: Nome do contato
            
        Returns:
            ID do contato
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar se contato já existe
        cursor.execute('SELECT id, pasta_contato FROM contatos WHERE telefone = ?', (telefone,))
        resultado = cursor.fetchone()
        
        if resultado:
            contato_id, pasta_existente = resultado
            # Atualizar último contato
            cursor.execute('''
                UPDATE contatos 
                SET ultimo_contato = CURRENT_TIMESTAMP, nome = COALESCE(?, nome)
                WHERE id = ?
            ''', (nome, contato_id))
        else:
            # Criar pasta do contato
            pasta_contato = self.criar_pasta_contato(telefone, nome)
            
            # Inserir novo contato
            cursor.execute('''
                INSERT INTO contatos (telefone, nome, pasta_contato)
                VALUES (?, ?, ?)
            ''', (telefone, nome, str(pasta_contato)))
            contato_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return contato_id
    
    def calcular_hash_arquivo(self, caminho_arquivo: str) -> str:
        """Calcula hash MD5 do arquivo para evitar duplicatas"""
        hash_md5 = hashlib.md5()
        try:
            with open(caminho_arquivo, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
        except FileNotFoundError:
            return ""
        return hash_md5.hexdigest()
    
    def determinar_tipo_arquivo(self, caminho_arquivo: str) -> str:
        """Determina o tipo do arquivo baseado na extensão"""
        mime_type, _ = mimetypes.guess_type(caminho_arquivo)
        
        if mime_type:
            if mime_type.startswith('image/'):
                return 'imagem'
            elif mime_type.startswith('audio/'):
                return 'audio'
            elif mime_type.startswith('video/'):
                return 'video'
            elif mime_type.startswith('application/pdf'):
                return 'documento'
            elif mime_type.startswith('application/'):
                return 'documento'
            elif mime_type.startswith('text/'):
                return 'documento'
        
        return 'outros'
    
    def salvar_arquivo(self, telefone: str, caminho_origem: str, 
                      nome_personalizado: Optional[str] = None) -> tuple[str, str]:
        """
        Salva arquivo na pasta do contato
        
        Args:
            telefone: Número do contato
            caminho_origem: Caminho do arquivo original
            nome_personalizado: Nome personalizado para o arquivo
            
        Returns:
            Tuple (caminho_destino, tipo_arquivo)
        """
        if not os.path.exists(caminho_origem):
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_origem}")
        
        # Obter pasta do contato
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT pasta_contato FROM contatos WHERE telefone = ?', (telefone,))
        resultado = cursor.fetchone()
        conn.close()
        
        if not resultado:
            raise ValueError(f"Contato não encontrado: {telefone}")
        
        pasta_contato = Path(resultado[0])
        tipo_arquivo = self.determinar_tipo_arquivo(caminho_origem)
        
        # Determinar nome do arquivo
        if nome_personalizado:
            nome_arquivo = nome_personalizado
        else:
            nome_arquivo = Path(caminho_origem).name
        
        # Adicionar timestamp se arquivo já existir
        contador = 1
        nome_base, extensao = os.path.splitext(nome_arquivo)
        pasta_tipo = pasta_contato / f"{tipo_arquivo}s"  # imagens, documentos, etc.
        
        caminho_destino = pasta_tipo / nome_arquivo
        while caminho_destino.exists():
            nome_arquivo = f"{nome_base}_{contador}{extensao}"
            caminho_destino = pasta_tipo / nome_arquivo
            contador += 1
        
        # Copiar arquivo
        shutil.copy2(caminho_origem, caminho_destino)
        print(f"📁 Arquivo salvo: {caminho_destino}")
        
        return str(caminho_destino), tipo_arquivo
    
    def processar_mensagem_texto(self, telefone: str, texto: str, 
                               nome_contato: Optional[str] = None,
                               metadados: Optional[Dict] = None) -> int:
        """
        Processa mensagem de texto recebida
        
        Args:
            telefone: Número do remetente
            texto: Conteúdo da mensagem
            nome_contato: Nome do contato
            metadados: Dados adicionais da mensagem
            
        Returns:
            ID da mensagem registrada
        """
        # Registrar contato
        contato_id = self.registrar_contato(telefone, nome_contato)
        
        # Registrar mensagem
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mensagens (contato_id, telefone, tipo_mensagem, conteudo_texto, metadados)
            VALUES (?, ?, ?, ?, ?)
        ''', (contato_id, telefone, 'texto', texto, json.dumps(metadados or {})))
        
        mensagem_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"💬 Mensagem texto registrada - ID: {mensagem_id}")
        return mensagem_id
    
    def processar_mensagem_arquivo(self, telefone: str, caminho_arquivo: str,
                                 nome_contato: Optional[str] = None,
                                 legenda: Optional[str] = None,
                                 metadados: Optional[Dict] = None) -> int:
        """
        Processa mensagem com arquivo (imagem, documento, áudio, etc.)
        
        Args:
            telefone: Número do remetente
            caminho_arquivo: Caminho do arquivo recebido
            nome_contato: Nome do contato
            legenda: Texto que acompanha o arquivo
            metadados: Dados adicionais
            
        Returns:
            ID da mensagem registrada
        """
        # Registrar contato
        contato_id = self.registrar_contato(telefone, nome_contato)
        
        # Salvar arquivo
        try:
            caminho_destino, tipo_arquivo = self.salvar_arquivo(telefone, caminho_arquivo)
            hash_arquivo = self.calcular_hash_arquivo(caminho_destino)
            tamanho_arquivo = os.path.getsize(caminho_destino)
            nome_arquivo = Path(caminho_destino).name
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            return 0
        
        # Registrar mensagem
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mensagens (
                contato_id, telefone, tipo_mensagem, conteudo_texto,
                nome_arquivo, caminho_arquivo, tamanho_arquivo, hash_arquivo, metadados
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            contato_id, telefone, tipo_arquivo, legenda or '',
            nome_arquivo, caminho_destino, tamanho_arquivo, hash_arquivo,
            json.dumps(metadados or {})
        ))
        
        mensagem_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"📎 Arquivo registrado - ID: {mensagem_id}, Tipo: {tipo_arquivo}")
        return mensagem_id
    
    def registrar_despesa(self, mensagem_id: int, tipo_despesa: str = 'comprovante',
                         valor: Optional[float] = None, descricao: Optional[str] = None,
                         categoria: Optional[str] = None, data_despesa: Optional[str] = None) -> int:
        """
        Registra uma despesa baseada em uma mensagem
        
        Args:
            mensagem_id: ID da mensagem relacionada
            tipo_despesa: Tipo da despesa (comprovante, nota_fiscal, recibo)
            valor: Valor da despesa
            descricao: Descrição da despesa
            categoria: Categoria da despesa
            data_despesa: Data da despesa (formato YYYY-MM-DD)
            
        Returns:
            ID da despesa registrada
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obter contato_id da mensagem
        cursor.execute('SELECT contato_id FROM mensagens WHERE id = ?', (mensagem_id,))
        resultado = cursor.fetchone()
        
        if not resultado:
            conn.close()
            raise ValueError(f"Mensagem não encontrada: {mensagem_id}")
        
        contato_id = resultado[0]
        
        cursor.execute('''
            INSERT INTO despesas (
                mensagem_id, contato_id, tipo_despesa, valor, 
                descricao, categoria, data_despesa
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            mensagem_id, contato_id, tipo_despesa, valor, 
            descricao, categoria, data_despesa
        ))
        
        despesa_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"💰 Despesa registrada - ID: {despesa_id}")
        return despesa_id
    
    def listar_mensagens_contato(self, telefone: str, limite: int = 50) -> List[Dict]:
        """Lista mensagens de um contato específico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.id, m.tipo_mensagem, m.conteudo_texto, m.nome_arquivo,
                   m.caminho_arquivo, m.data_recebimento, c.nome
            FROM mensagens m
            JOIN contatos c ON m.contato_id = c.id
            WHERE m.telefone = ?
            ORDER BY m.data_recebimento DESC
            LIMIT ?
        ''', (telefone, limite))
        
        mensagens = []
        for row in cursor.fetchall():
            mensagens.append({
                'id': row[0],
                'tipo': row[1],
                'texto': row[2],
                'arquivo': row[3],
                'caminho': row[4],
                'data': row[5],
                'nome_contato': row[6]
            })
        
        conn.close()
        return mensagens
    
    def listar_despesas_pendentes(self) -> List[Dict]:
        """Lista despesas com status pendente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.id, d.tipo_despesa, d.valor, d.descricao, d.categoria,
                   d.data_despesa, d.data_registro, c.nome, c.telefone,
                   m.nome_arquivo, m.caminho_arquivo
            FROM despesas d
            JOIN contatos c ON d.contato_id = c.id
            LEFT JOIN mensagens m ON d.mensagem_id = m.id
            WHERE d.status = 'pendente'
            ORDER BY d.data_registro DESC
        ''')
        
        despesas = []
        for row in cursor.fetchall():
            despesas.append({
                'id': row[0],
                'tipo': row[1],
                'valor': row[2],
                'descricao': row[3],
                'categoria': row[4],
                'data_despesa': row[5],
                'data_registro': row[6],
                'nome_contato': row[7],
                'telefone': row[8],
                'arquivo': row[9],
                'caminho_arquivo': row[10]
            })
        
        conn.close()
        return despesas
    
    def atualizar_status_despesa(self, despesa_id: int, status: str, 
                               observacoes: Optional[str] = None) -> bool:
        """Atualiza status de uma despesa"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE despesas 
            SET status = ?, observacoes = ?
            WHERE id = ?
        ''', (status, observacoes, despesa_id))
        
        sucesso = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if sucesso:
            print(f"✅ Status da despesa {despesa_id} atualizado para: {status}")
        
        return sucesso
    
    def obter_estatisticas(self) -> Dict:
        """Obtém estatísticas do sistema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Contadores
        cursor.execute('SELECT COUNT(*) FROM contatos')
        total_contatos = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM mensagens')
        total_mensagens = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM despesas')
        total_despesas = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM despesas WHERE status = "pendente"')
        despesas_pendentes = cursor.fetchone()[0]
        
        # Mensagens por tipo
        cursor.execute('''
            SELECT tipo_mensagem, COUNT(*) 
            FROM mensagens 
            GROUP BY tipo_mensagem
        ''')
        mensagens_por_tipo = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_contatos': total_contatos,
            'total_mensagens': total_mensagens,
            'total_despesas': total_despesas,
            'despesas_pendentes': despesas_pendentes,
            'mensagens_por_tipo': mensagens_por_tipo,
            'pasta_raiz': str(self.pasta_raiz)
        }


def exemplo_uso():
    """Exemplo de como usar o sistema"""
    # Inicializar sistema
    wpp = WhatsAppManager()
    
    # Simular recebimento de mensagem de texto
    print("\n=== TESTE: Mensagem de Texto ===")
    msg_id = wpp.processar_mensagem_texto(
        telefone="5511999887766",
        texto="Olá, preciso enviar meu comprovante de despesa de combustível",
        nome_contato="João Silva"
    )
    
    # Registrar despesa baseada na mensagem
    print("\n=== TESTE: Registrar Despesa ===")
    despesa_id = wpp.registrar_despesa(
        mensagem_id=msg_id,
        tipo_despesa="comprovante",
        valor=85.50,
        descricao="Combustível posto Shell",
        categoria="Transporte",
        data_despesa="2024-08-07"
    )
    
    # Mostrar estatísticas
    print("\n=== ESTATÍSTICAS DO SISTEMA ===")
    stats = wpp.obter_estatisticas()
    for chave, valor in stats.items():
        print(f"{chave}: {valor}")


if __name__ == "__main__":
    exemplo_uso()