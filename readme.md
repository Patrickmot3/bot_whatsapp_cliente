# WhatsApp Manager Python 📱

Sistema completo de gerenciamento de mensagens e arquivos do WhatsApp com integração para despesas empresariais.

## 🎯 Funcionalidades

- ✅ **Recebimento automático** de mensagens e arquivos via webhook
- 📁 **Organização automática** de arquivos por contato em pastas individuais
- 💰 **Sistema de despesas** integrado com categorização automática
- 🗃️ **Banco SQLite** estruturado para armazenamento
- 🔄 **APIs RESTful** para integração e consultas
- 💾 **Sistema de backup** automatizado
- 🔍 **Monitoramento** de sistema em tempo real
- 🛡️ **Segurança** com validação de tokens e arquivos

## 📂 Estrutura do Projeto

```
whatsapp-manager/
├── whatsapp_manager.py          # Sistema principal
├── whatsapp_api_integration.py  # API Flask com webhooks
├── config.py                    # Configurações centralizadas
├── backup_sistema.py            # Sistema de backup
├── monitor_sistema.py           # Monitor do sistema
├── exemplo_integracao.py        # Exemplos de uso
├── requirements.txt             # Dependências
├── .env.example                 # Exemplo de configuração
├── setup.sh                     # Script de instalação
└── README.md                    # Este arquivo
```

## 🚀 Instalação Rápida

### 1. Clone e Configure
```bash
# No VSCode, crie a pasta principal do projeto
mkdir bot_whatsapp_cliente
cd bot_whatsapp_cliente

# Copie todos os arquivos Python para esta pasta

# Torne o script executável
chmod +x setup.sh

# Execute a configuração
./setup.sh
```

### 2. Configure suas Variáveis
```bash
# Copie e edite o arquivo de configuração
cp .env.example .env
nano .env
```

### 3. Execute o Sistema
```bash
# Teste o sistema com exemplos
python exemplo_integracao.py

# Inicie a API
python whatsapp_api_integration.py
```

## ⚙️ Configuração (.env)

```env
# Tokens e segurança
WEBHOOK_TOKEN=seu_token_webhook_seguro_aqui
SECRET_KEY=sua_chave_secreta_aqui

# Caminhos
PASTA_RAIZ=arquivos_clientes
DATABASE_PATH=whatsapp_dados.db
BACKUP_PATH=backups/

# API
API_HOST=0.0.0.0
API_PORT=5000
DEBUG=True

# Limites
MAX_FILE_SIZE=50MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf,doc,docx,mp3,mp4,wav

# Backup automático
AUTO_BACKUP=True
BACKUP_INTERVAL=24h
```

## 💻 Uso no VSCode

### 1. Abrir o Projeto
```bash
code whatsapp-manager
```

### 2. Configurar Python Interpreter
- `Ctrl+Shift+P` → "Python: Select Interpreter"
- Escolha o ambiente virtual se criado

### 3. Executar Arquivos
- `F5` para debug
- `Ctrl+F5` para execução
- Terminal integrado: `Ctrl+`` `

## 📊 APIs Disponíveis

### Health Check
```bash
GET http://localhost:5000/health
```

### Webhook (Principal)
```bash
POST http://localhost:5000/webhook
Content-Type: application/json
Authorization: Bearer SEU_TOKEN

{
  "from": "5511999887766@c.us",
  "sender": {"name": "João Silva"},
  "type": "text",
  "body": "Despesa de combustível R$ 85,50"
}
```

### Listar Despesas
```bash
GET http://localhost:5000/despesas?status=pendente
```

### Atualizar Despesa
```bash
PUT http://localhost:5000/despesas/1
Content-Type: application/json

{
  "status": "aprovado",
  "observacoes": "Comprovante válido"
}
```

### Listar Contatos
```bash
GET http://localhost:5000/contatos
```

### Estatísticas
```bash
GET http://localhost:5000/estatisticas
```

## 🗄️ Estrutura do Banco

### Tabela: contatos
```sql
- id (INTEGER PRIMARY KEY)
- telefone (TEXT UNIQUE)
- nome (TEXT)
- pasta_contato (TEXT)
- data_criacao (TIMESTAMP)
- ultimo_contato (TIMESTAMP)
```

### Tabela: mensagens
```sql
- id (INTEGER PRIMARY KEY)
- contato_id (INTEGER FK)
- telefone (TEXT)
- tipo_mensagem (TEXT) -- texto, imagem, audio, documento
- conteudo_texto (TEXT)
- nome_arquivo (TEXT)
- caminho_arquivo (TEXT)
- tamanho_arquivo (INTEGER)
- hash_arquivo (TEXT)
- data_recebimento (TIMESTAMP)
- metadados (TEXT JSON)
```

### Tabela: despesas
```sql
- id (INTEGER PRIMARY KEY)
- mensagem_id (INTEGER FK)
- contato_id (INTEGER FK)
- tipo_despesa (TEXT)
- valor (REAL)
- descricao (TEXT)
- categoria (TEXT)
- data_despesa (DATE)
- status (TEXT) -- pendente, aprovado, rejeitado
- observacoes (TEXT)
```

## 📁 Organização de Arquivos

```
bot_whatsapp_cliente/                    ← Pasta principal do projeto
├── arquivos_clientes/                   ← Arquivos dos clientes organizados
│   ├── 5511999887766_João_Silva/
│   │   ├── imagens/
│   │   │   ├── comprovante_001.jpg
│   │   │   └── nota_fiscal_002.png
│   │   ├── documentos/
│   │   │   ├── contrato_001.pdf
│   │   │   └── planilha_002.xlsx
│   │   ├── audios/
│   │   ├── videos/
│   │   └── outros/
│   └── 5511888776655_Maria_Santos/
│       └── ...
├── backups/                             ← Backups automáticos
├── logs/                                ← Logs do sistema  
├── whatsapp_dados.db                    ← Banco SQLite
└── [arquivos python...]                 ← Scripts do sistema
```

## 🔧 Comandos Úteis

### Sistema Principal
```bash
# Processar mensagem
python -c "
from whatsapp_manager import WhatsAppManager
wpp = WhatsAppManager()
wpp.processar_mensagem_texto('11999887766', 'Teste', 'João')
"
```

### Backup
```bash
# Criar backup
python backup_sistema.py criar

# Listar backups
python backup_sistema.py listar

# Limpar backups antigos
python backup_sistema.py limpar
```

### Monitoramento
```bash
# Iniciar monitor
python monitor_sistema.py
```

## 🧪 Testando o Sistema

### 1. Teste Básico
```python
from whatsapp_manager import WhatsAppManager

# Inicializar
wpp = WhatsAppManager()

# Processar mensagem
msg_id = wpp.processar_mensagem_texto(
    telefone="11999887766",
    texto="Paguei R$ 85,50 de combustível",
    nome_contato="João Silva"
)

# Registrar despesa
despesa_id = wpp.registrar_despesa(
    mensagem_id=msg_id,
    valor=85.50,
    categoria="transporte"
)

print(f"Mensagem: {msg_id}, Despesa: {despesa_id}")
```

### 2. Teste com Arquivo
```python
# Processar arquivo
msg_id = wpp.processar_mensagem_arquivo(
    telefone="11999887766",
    caminho_arquivo="comprovante.jpg",
    nome_contato="João Silva",
    legenda="Comprovante combustível R$ 85,50"
)
```

### 3. Teste da API
```bash
# Com curl
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "from": "5511999887766@c.us",
    "type": "text",
    "body": "Teste de despesa R$ 50,00"
  }'
```

## 🔒 Segurança

### Validação de Tokens
```python
# No .env
WEBHOOK_TOKEN=token_super_secreto_123

# Validação automática em todos os endpoints
Authorization: Bearer token_super_secreto_123
```

### Validação de Arquivos
- Verificação de extensões permitidas
- Limite de tamanho configurável
- Hash MD5 para evitar duplicatas
- Sanitização de nomes de arquivos

### Logs de Auditoria
- Todas as operações são logadas
- Timestamps precisos
- Rastreamento de origem das mensagens

## 🐛 Troubleshooting

### Erro: Módulo não encontrado
```bash
# Instalar dependências
pip install -r requirements.txt

# Verificar imports
python -c "import flask; print('Flask OK')"
```

### Erro: Banco de dados bloqueado
```bash
# Verificar processos
ps aux | grep python

# Matar processos se necessário
pkill -f whatsapp
```

### Erro: Porta em uso
```bash
# Verificar porta
lsof -i :5000

# Matar processo
kill -9 PID
```

### Webhook não recebe dados
1. Verificar token no .env
2. Verificar formato do payload
3. Testar com curl primeiro
4. Verificar logs da aplicação

## 📈 Monitoramento

### Métricas Disponíveis
- Total de contatos
- Total de mensagens por tipo
- Despesas pendentes/aprovadas/rejeitadas
- Uso de disco
- Uso de memória
- Uptime do sistema

### Alertas Automáticos
- Espaço em disco baixo (>90%)
- Memória alta (>85%)
- Falhas no banco de dados
- Backup com falhas

## 🔄 Integração com WPPConnect

Para integrar com seu sistema Node.js existente:

### 1. Webhook Bridge
```javascript
// No seu código Node.js
const pythonWebhook = 'http://localhost:5000/webhook';

// Ao receber mensagem
wppClient.onMessage(async (message) => {
  // Enviar para Python
  await fetch(pythonWebhook, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.WEBHOOK_TOKEN}`
    },
    body: JSON.stringify(message)
  });
});
```

### 2. Sincronização de Status
```python
# No Python, notificar Node.js
import requests

def notificar_nodejs(evento, dados):
    requests.post('http://localhost:3000/python-event', {
        'evento': evento,
        'dados': dados,
        'timestamp': datetime.now().isoformat()
    })
```

## 🚀 Deploy em Produção

### 1. Configuração de Produção
```bash
# .env para produção
DEBUG=False
WEBHOOK_TOKEN=token_producao_super_seguro
API_HOST=0.0.0.0
API_PORT=5000
```

### 2. Usando Gunicorn
```bash
# Instalar
pip install gunicorn

# Executar
gunicorn -w 4 -b 0.0.0.0:5000 whatsapp_api_integration:app
```

### 3. Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Supervisor para Auto-restart
```ini
[program:whatsapp_manager]
command=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 whatsapp_api_integration:app
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
```

### 5. Systemd Service
```ini
[Unit]
Description=WhatsApp Manager
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/whatsapp-manager
Environment=PATH=/home/ubuntu/whatsapp-manager/venv/bin
ExecStart=/home/ubuntu/whatsapp-manager/venv/bin/python whatsapp_api_integration.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📚 Extensões e Customizações

### 1. Adicionar Novos Tipos de Despesa
```python
# Em whatsapp_manager.py
TIPOS_DESPESA = {
    'combustivel': ['combustivel', 'gasolina', 'posto'],
    'alimentacao': ['almoço', 'jantar', 'restaurante'],
    'hospedagem': ['hotel', 'pousada'],
    'transporte': ['uber', 'taxi', 'onibus'],
    'material': ['material', 'equipamento'],
    'servico': ['consultor', 'manutencao'],
    'viagem': ['passagem', 'aviao'],  # NOVO
    'comunicacao': ['telefone', 'internet']  # NOVO
}
```

### 2. Webhooks Personalizados
```python
@app.route('/webhook-custom', methods=['POST'])
def webhook_customizado():
    dados = request.get_json()
    
    # Sua lógica personalizada
    if dados.get('tipo') == 'aprovacao_gerente':
        processar_aprovacao(dados)
    
    return jsonify({'status': 'processado'})
```

### 3. Relatórios Customizados
```python
def gerar_relatorio_mensal(mes, ano):
    conn = sqlite3.connect(wpp_manager.db_path)
    
    query = """
    SELECT categoria, SUM(valor), COUNT(*)
    FROM despesas 
    WHERE strftime('%m', data_despesa) = ? 
    AND strftime('%Y', data_despesa) = ?
    GROUP BY categoria
    """
    
    result = conn.execute(query, (mes, ano)).fetchall()
    conn.close()
    
    return result
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 🆘 Suporte

### Documentação
- README.md (este arquivo)
- Comentários detalhados no código
- Exemplos práticos em `exemplo_integracao.py`

### Issues Comuns
1. **Import Error**: Verificar se todas as dependências estão instaladas
2. **Database Lock**: Verificar se não há múltiplas instâncias rodando
3. **Permission Denied**: Verificar permissões das pastas
4. **Port Already in Use**: Mudar porta no .env ou matar processo

### Contato
- 📧 Email: seu-email@exemplo.com
- 💬 WhatsApp: (11) 99999-9999
- 🐛 Issues: GitHub Issues

---

## 🎉 Conclusão

Este sistema oferece uma solução completa para gerenciamento de mensagens WhatsApp com foco em despesas empresariais. É modular, extensível e production-ready.

### Principais Vantagens:
- ✅ **Organização automática** de arquivos
- ✅ **Detecção inteligente** de despesas
- ✅ **APIs robustas** para integração
- ✅ **Sistema de backup** confiável
- ✅ **Monitoramento** em tempo real
- ✅ **Segurança** empresarial
- ✅ **Fácil manutenção** e extensão

**Desenvolvido com ❤️ para otimizar a gestão de despesas via WhatsApp!**