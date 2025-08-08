#!/usr/bin/env python3
"""
API Flask para integração com WhatsApp Web
Recebe webhooks e processa mensagens automaticamente
"""

from flask import Flask, request, jsonify
import os
import json
import tempfile
import requests
from datetime import datetime
from whatsapp_manager import WhatsAppManager  # Importar o sistema principal
import re

app = Flask(__name__)

# Inicializar o gerenciador WhatsApp
wpp_manager = WhatsAppManager()

# Configurações
WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN', 'seu_token_webhook_aqui')
PASTA_TEMP = tempfile.mkdtemp()

def validar_webhook(token):
    """Valida token do webhook"""
    return token == WEBHOOK_TOKEN

def extrair_numero_telefone(numero_completo):
    """Extrai número limpo do telefone"""
    # Remove @c.us e outros sufixos, mantém apenas números
    numero = re.sub(r'[^\d]', '', numero_completo)
    
    # Remove código do país se presente (assume Brasil +55)
    if numero.startswith('55') and len(numero) >= 11:
        return numero[2:]  # Remove os primeiros 55
    
    return numero

def baixar_arquivo_temporario(url, nome_arquivo):
    """Baixa arquivo de URL para pasta temporária"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        caminho_temp = os.path.join(PASTA_TEMP, nome_arquivo)
        
        with open(caminho_temp, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return caminho_temp
    except Exception as e:
        print(f"❌ Erro ao baixar arquivo: {e}")
        return None

def processar_texto_despesa(texto):
    """
    Tenta extrair informações de despesa do texto
    Procura por padrões como valores monetários e categorias
    """
    # Padrões para detectar valores monetários
    padrao_valor = r'R?\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)'
    valores = re.findall(padrao_valor, texto.upper())
    
    # Categorias comuns de despesa
    categorias = {
        'combustivel': ['combustivel', 'combustível', 'gasolina', 'alcool', 'álcool', 'diesel', 'posto'],
        'alimentacao': ['almoço', 'almoco', 'jantar', 'lanche', 'restaurante', 'comida', 'alimentação'],
        'transporte': ['uber', 'taxi', 'onibus', 'ônibus', 'metro', 'metrô', 'transporte', 'passagem'],
        'hospedagem': ['hotel', 'pousada', 'hospedagem', 'diaria', 'diária'],
        'material': ['material', 'compra', 'produto', 'equipamento', 'ferramenta'],
        'servico': ['serviço', 'servico', 'consultoria', 'manutencao', 'manutenção', 'reparo']
    }
    
    categoria_detectada = 'outros'
    for categoria, palavras_chave in categorias.items():
        if any(palavra in texto.lower() for palavra in palavras_chave):
            categoria_detectada = categoria
            break
    
    # Converter valor para float se encontrado
    valor_detectado = None
    if valores:
        try:
            # Pega o primeiro valor encontrado e converte
            valor_str = valores[0].replace('.', '').replace(',', '.')
            valor_detectado = float(valor_str)
        except ValueError:
            pass
    
    return {
        'valor': valor_detectado,
        'categoria': categoria_detectada,
        'tem_valor': valor_detectado is not None
    }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    stats = wpp_manager.obter_estatisticas()
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'sistema': 'WhatsApp Manager Python',
        'estatisticas': stats
    })

@app.route('/webhook', methods=['POST'])
def receber_webhook():
    """
    Endpoint principal para receber mensagens do WhatsApp
    Espera payload similar ao WPPConnect
    """
    try:
        # Validar token se configurado
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if WEBHOOK_TOKEN != 'seu_token_webhook_aqui' and not validar_webhook(token):
            return jsonify({'error': 'Token inválido'}), 401
        
        dados = request.get_json()
        if not dados:
            return jsonify({'error': 'Dados inválidos'}), 400
        
        # Log do payload recebido
        print(f"📨 Webhook recebido: {json.dumps(dados, indent=2)}")
        
        # Extrair informações da mensagem
        telefone = extrair_numero_telefone(dados.get('from', ''))
        nome_contato = dados.get('sender', {}).get('name', dados.get('notifyName', ''))
        tipo_mensagem = dados.get('type', 'text')
        timestamp = dados.get('timestamp', datetime.now().isoformat())
        
        if not telefone:
            print("⚠️ Telefone não identificado na mensagem")
            return jsonify({'warning': 'Telefone não identificado'}), 200
        
        mensagem_id = None
        despesa_id = None
        
        # Processar baseado no tipo de mensagem
        if tipo_mensagem == 'text':
            # Mensagem de texto
            texto = dados.get('body', dados.get('content', ''))
            if texto:
                mensagem_id = wpp_manager.processar_mensagem_texto(
                    telefone=telefone,
                    texto=texto,
                    nome_contato=nome_contato,
                    metadados={
                        'timestamp': timestamp,
                        'webhook_data': dados
                    }
                )
                
                # Verificar se é possível extrair dados de despesa do texto
                info_despesa = processar_texto_despesa(texto)
                if info_despesa['tem_valor']:
                    despesa_id = wpp_manager.registrar_despesa(
                        mensagem_id=mensagem_id,
                        tipo_despesa='texto_com_valor',
                        valor=info_despesa['valor'],
                        categoria=info_despesa['categoria'],
                        descricao=texto[:200],  # Limite de 200 caracteres
                        data_despesa=datetime.now().strftime('%Y-%m-%d')
                    )
        
        elif tipo_mensagem in ['image', 'document', 'audio', 'video', 'ptt']:
            # Mensagens com arquivos
            legenda = dados.get('caption', dados.get('body', ''))
            
            # Informações do arquivo
            arquivo_info = dados.get('mediaData', dados.get('media', {}))
            nome_arquivo = arquivo_info.get('filename', f'arquivo_{timestamp}.bin')
            url_arquivo = arquivo_info.get('url', '')
            
            if url_arquivo:
                # Baixar arquivo
                caminho_temp = baixar_arquivo_temporario(url_arquivo, nome_arquivo)
                
                if caminho_temp:
                    mensagem_id = wpp_manager.processar_mensagem_arquivo(
                        telefone=telefone,
                        caminho_arquivo=caminho_temp,
                        nome_contato=nome_contato,
                        legenda=legenda,
                        metadados={
                            'timestamp': timestamp,
                            'tipo_original': tipo_mensagem,
                            'webhook_data': dados
                        }
                    )
                    
                    # Para imagens e documentos, assumir que pode ser comprovante de despesa
                    if tipo_mensagem in ['image', 'document'] and mensagem_id:
                        # Tentar extrair valor da legenda se houver
                        info_despesa = processar_texto_despesa(legenda) if legenda else {'valor': None, 'categoria': 'documento'}
                        
                        despesa_id = wpp_manager.registrar_despesa(
                            mensagem_id=mensagem_id,
                            tipo_despesa='comprovante',
                            valor=info_despesa.get('valor'),
                            categoria=info_despesa.get('categoria', 'documento'),
                            descricao=legenda[:200] if legenda else 'Arquivo enviado sem descrição',
                            data_despesa=datetime.now().strftime('%Y-%m-%d')
                        )
                    
                    # Limpar arquivo temporário
                    try:
                        os.unlink(caminho_temp)
                    except:
                        pass
                else:
                    print(f"❌ Falha ao baixar arquivo de: {telefone}")
            else:
                print(f"⚠️ URL do arquivo não fornecida para mensagem de: {telefone}")
        
        # Resposta de sucesso
        resposta = {
            'success': True,
            'telefone': telefone,
            'tipo_mensagem': tipo_mensagem,
            'mensagem_id': mensagem_id,
            'timestamp': datetime.now().isoformat()
        }
        
        if despesa_id:
            resposta['despesa_id'] = despesa_id
            resposta['despesa_registrada'] = True
        
        return jsonify(resposta)
    
    except Exception as e:
        print(f"❌ Erro no webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/mensagens/<telefone>', methods=['GET'])
def listar_mensagens(telefone):
    """Lista mensagens de um contato"""
    try:
        limite = request.args.get('limite', 50, type=int)
        mensagens = wpp_manager.listar_mensagens_contato(telefone, limite)
        
        return jsonify({
            'telefone': telefone,
            'total': len(mensagens),
            'mensagens': mensagens
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/despesas', methods=['GET'])
def listar_despesas():
    """Lista despesas pendentes ou todas"""
    try:
        status = request.args.get('status', 'pendente')
        
        if status == 'pendente':
            despesas = wpp_manager.listar_despesas_pendentes()
        else:
            # Implementar listagem com filtros se necessário
            despesas = wpp_manager.listar_despesas_pendentes()
        
        return jsonify({
            'total': len(despesas),
            'despesas': despesas
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/despesas/<int:despesa_id>', methods=['PUT'])
def atualizar_despesa(despesa_id):
    """Atualiza status de uma despesa"""
    try:
        dados = request.get_json()
        status = dados.get('status', 'pendente')
        observacoes = dados.get('observacoes', '')
        
        sucesso = wpp_manager.atualizar_status_despesa(despesa_id, status, observacoes)
        
        if sucesso:
            return jsonify({'success': True, 'despesa_id': despesa_id, 'status': status})
        else:
            return jsonify({'error': 'Despesa não encontrada'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/despesas', methods=['POST'])
def criar_despesa_manual():
    """Cria despesa manualmente"""
    try:
        dados = request.get_json()
        
        # Dados obrigatórios
        telefone = dados.get('telefone')
        valor = dados.get('valor')
        descricao = dados.get('descricao', '')
        
        if not telefone or valor is None:
            return jsonify({'error': 'Telefone e valor são obrigatórios'}), 400
        
        # Criar mensagem de texto primeiro (para ter referência)
        mensagem_id = wpp_manager.processar_mensagem_texto(
            telefone=telefone,
            texto=f"Despesa manual: {descricao}",
            nome_contato=dados.get('nome_contato')
        )
        
        # Criar despesa
        despesa_id = wpp_manager.registrar_despesa(
            mensagem_id=mensagem_id,
            tipo_despesa=dados.get('tipo_despesa', 'manual'),
            valor=valor,
            descricao=descricao,
            categoria=dados.get('categoria', 'outros'),
            data_despesa=dados.get('data_despesa', datetime.now().strftime('%Y-%m-%d'))
        )
        
        return jsonify({
            'success': True,
            'despesa_id': despesa_id,
            'mensagem_id': mensagem_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/contatos', methods=['GET'])
def listar_contatos():
    """Lista todos os contatos"""
    try:
        import sqlite3
        
        conn = sqlite3.connect(wpp_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.telefone, c.nome, c.pasta_contato, c.data_criacao, c.ultimo_contato,
                   COUNT(m.id) as total_mensagens,
                   COUNT(d.id) as total_despesas
            FROM contatos c
            LEFT JOIN mensagens m ON c.id = m.contato_id
            LEFT JOIN despesas d ON c.id = d.contato_id
            GROUP BY c.id
            ORDER BY c.ultimo_contato DESC
        ''')
        
        contatos = []
        for row in cursor.fetchall():
            contatos.append({
                'id': row[0],
                'telefone': row[1],
                'nome': row[2],
                'pasta_contato': row[3],
                'data_criacao': row[4],
                'ultimo_contato': row[5],
                'total_mensagens': row[6],
                'total_despesas': row[7]
            })
        
        conn.close()
        
        return jsonify({
            'total': len(contatos),
            'contatos': contatos
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/estatisticas', methods=['GET'])
def obter_estatisticas():
    """Retorna estatísticas do sistema"""
    try:
        stats = wpp_manager.obter_estatisticas()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/processar-arquivo', methods=['POST'])
def processar_arquivo_manual():
    """Endpoint para processar arquivo enviado manualmente"""
    try:
        dados = request.get_json()
        telefone = dados.get('telefone')
        caminho_arquivo = dados.get('caminho_arquivo')
        nome_contato = dados.get('nome_contato')
        legenda = dados.get('legenda', '')
        
        if not telefone or not caminho_arquivo:
            return jsonify({'error': 'Telefone e caminho do arquivo são obrigatórios'}), 400
        
        if not os.path.exists(caminho_arquivo):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        # Processar arquivo
        mensagem_id = wpp_manager.processar_mensagem_arquivo(
            telefone=telefone,
            caminho_arquivo=caminho_arquivo,
            nome_contato=nome_contato,
            legenda=legenda,
            metadados={'origem': 'upload_manual'}
        )
        
        # Criar despesa se for imagem/documento
        despesa_id = None
        tipo_arquivo = wpp_manager.determinar_tipo_arquivo(caminho_arquivo)
        
        if tipo_arquivo in ['imagem', 'documento']:
            info_despesa = processar_texto_despesa(legenda) if legenda else {'valor': None, 'categoria': 'documento'}
            
            despesa_id = wpp_manager.registrar_despesa(
                mensagem_id=mensagem_id,
                tipo_despesa='comprovante',
                valor=info_despesa.get('valor'),
                categoria=info_despesa.get('categoria', 'documento'),
                descricao=legenda[:200] if legenda else 'Arquivo processado manualmente',
                data_despesa=datetime.now().strftime('%Y-%m-%d')
            )
        
        resposta = {
            'success': True,
            'mensagem_id': mensagem_id,
            'tipo_arquivo': tipo_arquivo
        }
        
        if despesa_id:
            resposta['despesa_id'] = despesa_id
        
        return jsonify(resposta)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Middleware para log de requests
@app.before_request
def log_request():
    print(f"📡 {request.method} {request.path} - {request.remote_addr}")

if __name__ == '__main__':
    print("🚀 Iniciando API WhatsApp Manager...")
    print(f"📊 Health check: http://localhost:5000/health")
    print(f"📨 Webhook: http://localhost:5000/webhook")
    print(f"📋 Despesas: http://localhost:5000/despesas")
    print(f"👥 Contatos: http://localhost:5000/contatos")
    print(f"📊 Estatísticas: http://localhost:5000/estatisticas")
    
    # Criar pasta temporária se não existir
    os.makedirs(PASTA_TEMP, exist_ok=True)
    
    # Rodar servidor
    app.run(host='0.0.0.0', port=5000, debug=True)