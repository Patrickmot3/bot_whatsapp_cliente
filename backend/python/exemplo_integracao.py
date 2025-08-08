#!/usr/bin/env python3
"""
Exemplo de Integração Completa do Sistema WhatsApp Manager
Demonstra como usar todas as funcionalidades juntas
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Importar componentes do sistema
from whatsapp_manager import WhatsAppManager
from config import Config

def exemplo_completo():
    """Exemplo completo de uso do sistema"""
    
    print("🚀 === EXEMPLO COMPLETO DO WHATSAPP MANAGER ===")
    print()
    
    # 1. Inicializar o sistema
    print("1️⃣ Inicializando sistema...")
    wpp = WhatsAppManager(pasta_raiz="arquivos_clientes")
    print("✅ Sistema inicializado!")
    print()
    
    # 2. Simular recebimento de mensagens de texto
    print("2️⃣ Simulando mensagens de texto...")
    
    # Mensagem com valor monetário
    msg1_id = wpp.processar_mensagem_texto(
        telefone="11999887766",
        texto="Oi! Paguei R$ 85,50 de combustível no posto Shell da marginal",
        nome_contato="João Silva",
        metadados={'tipo': 'despesa', 'urgente': False}
    )
    
    # Mensagem simples
    msg2_id = wpp.processar_mensagem_texto(
        telefone="11888776655",
        texto="Boa tarde! Preciso enviar o comprovante do almoço de hoje",
        nome_contato="Maria Santos"
    )
    
    print(f"✅ Mensagens processadas - IDs: {msg1_id}, {msg2_id}")
    print()
    
    # 3. Registrar despesas baseadas nas mensagens
    print("3️⃣ Registrando despesas...")
    
    despesa1_id = wpp.registrar_despesa(
        mensagem_id=msg1_id,
        tipo_despesa="combustivel",
        valor=85.50,
        descricao="Abastecimento no Posto Shell",
        categoria="transporte",
        data_despesa="2024-08-07"
    )
    
    despesa2_id = wpp.registrar_despesa(
        mensagem_id=msg2_id,
        tipo_despesa="refeicao",
        valor=35.00,
        descricao="Almoço executivo",
        categoria="alimentacao",
        data_despesa="2024-08-07"
    )
    
    print(f"✅ Despesas registradas - IDs: {despesa1_id}, {despesa2_id}")
    print()
    
    # 4. Simular processamento de arquivos (se você tiver arquivos de exemplo)
    print("4️⃣ Simulando processamento de arquivos...")
    
    # Criar arquivo de exemplo para demonstração
    exemplo_dir = Path("arquivos_exemplo")
    exemplo_dir.mkdir(exist_ok=True)
    
    # Criar um arquivo de texto simples como exemplo
    arquivo_exemplo = exemplo_dir / "comprovante_exemplo.txt"
    with open(arquivo_exemplo, 'w', encoding='utf-8') as f:
        f.write("COMPROVANTE DE PAGAMENTO\n")
        f.write("========================\n")
        f.write("Data: 07/08/2024\n")
        f.write("Valor: R$ 125,00\n")
        f.write("Estabelecimento: Restaurante ABC\n")
        f.write("Tipo: Alimentação\n")
    
    try:
        msg3_id = wpp.processar_mensagem_arquivo(
            telefone="11777665544",
            caminho_arquivo=str(arquivo_exemplo),
            nome_contato="Carlos Oliveira",
            legenda="Comprovante do jantar com cliente - R$ 125,00",
            metadados={'tipo': 'comprovante', 'cliente': 'Empresa XYZ'}
        )
        
        # Registrar despesa do arquivo
        despesa3_id = wpp.registrar_despesa(
            mensagem_id=msg3_id,
            tipo_despesa="comprovante",
            valor=125.00,
            descricao="Jantar com cliente",
            categoria="alimentacao",
            data_despesa="2024-08-07"
        )
        
        print(f"✅ Arquivo processado - Mensagem ID: {msg3_id}, Despesa ID: {despesa3_id}")
    except Exception as e:
        print(f"⚠️ Não foi possível processar arquivo: {e}")
    
    print()
    
    # 5. Listar mensagens e despesas
    print("5️⃣ Listando dados do sistema...")
    print()
    
    # Listar mensagens de um contato
    print("📱 Mensagens do João Silva:")
    mensagens_joao = wpp.listar_mensagens_contato("11999887766", limite=10)
    for msg in mensagens_joao:
        print(f"  - {msg['tipo']}: {msg['texto'][:50]}... ({msg['data']})")
    print()
    
    # Listar despesas pendentes
    print("💰 Despesas pendentes:")
    despesas_pendentes = wpp.listar_despesas_pendentes()
    for despesa in despesas_pendentes:
        print(f"  - ID {despesa['id']}: R$ {despesa['valor']} - {despesa['descricao']}")
        print(f"    Contato: {despesa['nome_contato']} ({despesa['telefone']})")
        print(f"    Categoria: {despesa['categoria']}")
    print()
    
    # 6. Atualizar status de despesas
    print("6️⃣ Atualizando status de despesas...")
    
    # Aprovar primeira despesa
    sucesso1 = wpp.atualizar_status_despesa(
        despesa1_id, 
        "aprovado", 
        "Comprovante válido, valor aprovado"
    )
    
    # Rejeitar segunda despesa (exemplo)
    sucesso2 = wpp.atualizar_status_despesa(
        despesa2_id, 
        "rejeitado", 
        "Falta comprovante físico"
    )
    
    print(f"✅ Status atualizados - Despesa {despesa1_id}: {sucesso1}, Despesa {despesa2_id}: {sucesso2}")
    print()
    
    # 7. Mostrar estatísticas finais
    print("7️⃣ Estatísticas do sistema:")
    stats = wpp.obter_estatisticas()
    
    print(f"📊 Total de contatos: {stats['total_contatos']}")
    print(f"📊 Total de mensagens: {stats['total_mensagens']}")
    print(f"📊 Total de despesas: {stats['total_despesas']}")
    print(f"📊 Despesas pendentes: {stats['despesas_pendentes']}")
    print(f"📊 Pasta raiz: {stats['pasta_raiz']}")
    
    print("\n📈 Mensagens por tipo:")
    for tipo, quantidade in stats['mensagens_por_tipo'].items():
        print(f"  - {tipo}: {quantidade}")
    
    print()
    
    # 8. Demonstrar funcionalidades avançadas
    print("8️⃣ Funcionalidades avançadas...")
    
    # Simular processamento de múltiplos contatos
    contatos_exemplo = [
        {"telefone": "11666555444", "nome": "Ana Costa", "mensagem": "Taxi para aeroporto R$ 45,00"},
        {"telefone": "11555444333", "nome": "Pedro Lima", "mensagem": "Hotel 2 diárias R$ 320,00"},
        {"telefone": "11444333222", "nome": "Lucia Ferreira", "mensagem": "Material escritório R$ 89,90"}
    ]
    
    print("📱 Processando múltiplos contatos:")
    for contato in contatos_exemplo:
        msg_id = wpp.processar_mensagem_texto(
            telefone=contato["telefone"],
            texto=contato["mensagem"],
            nome_contato=contato["nome"]
        )
        print(f"  ✅ {contato['nome']}: Mensagem {msg_id}")
    
    print()
    
    # 9. Demonstrar relatório de atividades
    print("9️⃣ Relatório de atividades recentes:")
    
    import sqlite3
    conn = sqlite3.connect(wpp.db_path)
    cursor = conn.cursor()
    
    # Atividades das últimas 24 horas
    cursor.execute('''
        SELECT 'mensagem' as tipo, telefone, data_recebimento as data, conteudo_texto as descricao
        FROM mensagens 
        WHERE datetime(data_recebimento) > datetime('now', '-1 day')
        
        UNION ALL
        
        SELECT 'despesa' as tipo, 
               (SELECT telefone FROM contatos WHERE id = d.contato_id) as telefone,
               data_registro as data,
               descricao
        FROM despesas d
        WHERE datetime(data_registro) > datetime('now', '-1 day')
        
        ORDER BY data DESC
        LIMIT 10
    ''')
    
    atividades = cursor.fetchall()
    conn.close()
    
    for atividade in atividades:
        tipo, telefone, data, descricao = atividade
        print(f"  📝 {tipo.upper()}: {telefone} - {descricao[:40]}... ({data})")
    
    print()
    
    # 10. Limpeza de exemplo
    print("🔟 Exemplo concluído!")
    print()
    print("🧹 Para limpar os dados de exemplo, você pode:")
    print(f"  - Remover pasta: {wpp.pasta_raiz}")
    print(f"  - Remover banco: {wpp.db_path}")
    print(f"  - Remover arquivos exemplo: {exemplo_dir}")
    print()
    print("🎉 Sistema WhatsApp Manager funcionando perfeitamente!")

def exemplo_integracao_api():
    """Exemplo de como integrar com a API Flask"""
    
    print("\n🌐 === EXEMPLO DE INTEGRAÇÃO COM API ===")
    print()
    
    # Simular dados que viriam do webhook
    webhook_data_texto = {
        "from": "5511999887766@c.us",
        "sender": {"name": "João Silva"},
        "type": "text",
        "body": "Despesa de combustível R$ 85,50",
        "timestamp": datetime.now().isoformat()
    }
    
    webhook_data_arquivo = {
        "from": "5511888776655@c.us", 
        "sender": {"name": "Maria Santos"},
        "type": "image",
        "caption": "Comprovante almoço R$ 35,00",
        "mediaData": {
            "filename": "comprovante.jpg",
            "url": "https://exemplo.com/arquivo.jpg"
        },
        "timestamp": datetime.now().isoformat()
    }
    
    print("📡 Dados de exemplo que viriam do webhook:")
    print(f"🔸 Mensagem texto: {json.dumps(webhook_data_texto, indent=2, ensure_ascii=False)}")
    print()
    print(f"🔸 Mensagem arquivo: {json.dumps(webhook_data_arquivo, indent=2, ensure_ascii=False)}")
    print()
    
    print("🔧 Para testar a API:")
    print("1. Execute: python whatsapp_api_integration.py")
    print("2. Teste o health check: curl http://localhost:5000/health")
    print("3. Envie webhook: curl -X POST http://localhost:5000/webhook -H 'Content-Type: application/json' -d '{...}'")
    print("4. Veja despesas: curl http://localhost:5000/despesas")
    print()

def exemplo_backup_monitor():
    """Exemplo de sistema de backup e monitoramento"""
    
    print("\n💾 === EXEMPLO DE BACKUP E MONITORAMENTO ===")
    print()
    
    try:
        from backup_sistema import BackupManager
        
        backup_manager = BackupManager()
        
        print("🔧 Funcionalidades disponíveis:")
        print("1. Criar backup completo:")
        print("   python backup_sistema.py criar")
        print()
        print("2. Listar backups:")
        print("   python backup_sistema.py listar")
        print()
        print("3. Monitorar sistema:")
        print("   python monitor_sistema.py")
        print()
        
        # Exemplo de verificação básica
        backup_dir = Path("backups")
        if backup_dir.exists():
            backups = list(backup_dir.glob("whatsapp_backup_*.zip"))
            print(f"📦 Backups encontrados: {len(backups)}")
        else:
            print("📁 Pasta de backup será criada automaticamente")
            
    except ImportError:
        print("⚠️ Execute o setup.sh primeiro para criar os scripts de backup")

def main():
    """Função principal - executa todos os exemplos"""
    
    print("🎯 SISTEMA WHATSAPP MANAGER - DEMONSTRAÇÃO COMPLETA")
    print("=" * 60)
    print()
    
    # Exemplo básico
    exemplo_completo()
    
    # Exemplo de API
    exemplo_integracao_api()
    
    # Exemplo de backup
    exemplo_backup_monitor()
    
    print("\n" + "=" * 60)
    print("✨ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print()
    print("📋 RESUMO DO QUE FOI CRIADO:")
    print("• Sistema de gerenciamento de mensagens e arquivos")
    print("• Banco de dados SQLite com tabelas estruturadas")
    print("• Organização automática de arquivos por contato")
    print("• Sistema de despesas integrado")
    print("• API Flask para webhooks")
    print("• Sistema de backup automatizado")
    print("• Monitor de sistema")
    print("• Scripts de configuração")
    print()
    print("🚀 PRÓXIMOS PASSOS:")
    print("1. Execute: chmod +x setup.sh && ./setup.sh")
    print("2. Configure seu .env com tokens reais")
    print("3. Instale dependências: pip install -r requirements.txt")
    print("4. Execute o sistema principal")
    print()
    print("📚 DOCUMENTAÇÃO:")
    print("• Todos os scripts têm comentários detalhados")
    print("• Exemplos de uso em cada arquivo")
    print("• Sistema modular e extensível")
    print()
    print("🎉 Seu sistema WhatsApp Manager está pronto para uso!")

if __name__ == "__main__":
    main()