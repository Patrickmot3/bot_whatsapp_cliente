#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const wppconnect = require('@wppconnect-team/wppconnect');
const express = require('express');

const app = express();
app.use(express.json());

let wppClient;
let ultimoStatusLogado = false;
let contadorStatusLogado = 0;

// ===== CONFIGURAÇÃO DE CAMINHOS =====
const PATHS = {
  root: path.join(__dirname, '..', '..'),
  data: path.join(__dirname, '..', '..', 'data'),
  storage: path.join(__dirname, '..', '..', 'storage'),
  static: path.join(__dirname, '..', '..', 'data', 'static'),
  puppeteer: path.join(__dirname, '..', '..', 'puppeteer'),
  python: path.join(__dirname, '..', 'python')
};

// Criar diretórios se não existirem
Object.values(PATHS).forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// ===== INTEGRAÇÃO PYTHON =====
const pythonWebhookUrl = 'http://localhost:5000/webhook';
const pythonToken = 'desenvolvimento';

// Função para verificar se é mensagem válida (não status)
function isValidMessage(message) {
  // Filtrar mensagens de status
  if (message.from === 'status@broadcast') return false;
  
  // Filtrar outros tipos irrelevantes
  if (message.isGroupMsg && !message.mentionedJidList?.length) return false;
  
  // Só processar mensagens diretas ou menções em grupos
  return true;
}

async function enviarParaPython(messageData) {
  try {
    const fetch = (await import('node-fetch')).default;
    
    const response = await fetch(pythonWebhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${pythonToken}`
      },
      body: JSON.stringify(messageData)
    });

    if (response.ok) {
      const result = await response.json();
      console.log(`🐍 Python: ${result.success ? 'Processado' : 'Erro'}`, 
                  result.despesa_registrada ? '💰 Despesa criada' : '');
      return result;
    } else {
      console.log('⚠️ Python erro:', response.status);
    }
  } catch (error) {
    console.error('❌ Python integração:', error.message);
  }
}

async function testarIntegracaoPython() {
  console.log('🧪 Testando integração Python...');
  
  try {
    const fetch = (await import('node-fetch')).default;
    const healthCheck = await fetch('http://localhost:5000/health');
    
    if (healthCheck.ok) {
      console.log('✅ Sistema Python está online!');
      
      const testMessage = {
        from: '5511999887766@c.us',
        sender: { name: 'Teste Integração' },
        type: 'text',
        body: 'Teste de integração Node.js + Python - R$ 50,00',
        timestamp: new Date().toISOString(),
        metadata: { source: 'teste_nodejs' }
      };
      
      const resultado = await enviarParaPython(testMessage);
      if (resultado?.success) {
        console.log('🎉 Integração Python funcionando perfeitamente!');
      }
    } else {
      console.log('⚠️ Sistema Python não está acessível');
    }
  } catch (error) {
    console.log('⚠️ Python não conectado ainda:', error.message);
  }
}

// ===== CONFIGURAÇÕES WHATSAPP =====
const chromePath = path.join(PATHS.puppeteer, 'chrome', 'win64-131.0.6778.204', 'chrome-win64', 'chrome.exe');

function salvarStatus(logado, mensagem = '') {
  try {
    if (logado !== ultimoStatusLogado || contadorStatusLogado < 3) {
      
      if (logado === ultimoStatusLogado) {
        contadorStatusLogado++;
      } else {
        contadorStatusLogado = 1;
        ultimoStatusLogado = logado;
      }
      
      if (contadorStatusLogado >= 2 || !logado) {
        const statusInfo = {
          logado,
          data: new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' }),
          confirmacoes: contadorStatusLogado,
          mensagem: mensagem || (logado ? 'Conectado e verificado' : 'Aguardando conexão'),
          timestamp: Date.now()
        };
        
        const statusPath = path.join(PATHS.static, 'status.json');
        fs.writeFileSync(statusPath, JSON.stringify(statusInfo, null, 2));
        
        console.log(`📊 Status salvo: ${logado ? 'LOGADO' : 'DESCONECTADO'} (${contadorStatusLogado}x confirmações)`);
      }
    }
  } catch (error) {
    console.error('Erro ao salvar status:', error);
  }
}

// ===== CLIENTE WPPCONNECT =====
wppconnect
  .create({
    session: 'sessionName32',
    browserPath: fs.existsSync(chromePath) ? chromePath : undefined,
    catchQR: (base64Qr, asciiQR) => {
      console.log('📱 QR Code gerado - aguardando leitura...');
      console.log(asciiQR);

      const matches = base64Qr.match(/^data:([A-Za-z-+/]+);base64,(.+)$/);
      if (!matches || matches.length !== 3) return;

      const buffer = Buffer.from(matches[2], 'base64');
      fs.writeFileSync(path.join(PATHS.static, 'out.png'), buffer, 'binary');

      salvarStatus(false, 'QR Code gerado - aguardando leitura');
    },
    
    statusFind: (statusSession) => {
      console.log('🔄 Status recebido:', statusSession);
      
      const statusLogado = ['isLogged', 'qrReadSuccess', 'chatsAvailable'];
      const statusDesconectado = ['notLogged', 'browserClose', 'qrReadFail'];
      
      let logado = false;
      let mensagem = statusSession;
      
      if (statusLogado.includes(statusSession)) {
        logado = true;
        mensagem = 'WhatsApp conectado com sucesso';
      } else if (statusDesconectado.includes(statusSession)) {
        logado = false;
        mensagem = 'WhatsApp desconectado';
      } else {
        console.log(`⚠️ Status intermediário: ${statusSession} - mantendo estado anterior`);
        return;
      }
      
      salvarStatus(logado, mensagem);
    },
    
    logQR: false,
  })
  .then(async (client) => {
    wppClient = client;
    console.log('✅ Cliente WPPConnect iniciado com sucesso!');
    
    // ===== LISTENERS DE MENSAGENS COM FILTROS =====
    client.onMessage(async (message) => {
      try {
        // ===== FILTRO: Ignorar mensagens de status =====
        if (!isValidMessage(message)) {
          // Não processar mensagens de status
          return;
        }

        console.log('📨 Mensagem VÁLIDA recebida de:', message.from);
        console.log('📝 Conteúdo:', message.body?.substring(0, 50) + '...');

        let tipoMensagem = 'text';
        if (message.type === 'image') tipoMensagem = 'image';
        else if (message.type === 'document') tipoMensagem = 'document';
        else if (message.type === 'audio' || message.type === 'ptt') tipoMensagem = 'audio';
        else if (message.type === 'video') tipoMensagem = 'video';

        let nomeContato = message.sender?.name || message.notifyName || message.contact?.name || 'Contato WhatsApp';

        const dadosPython = {
          from: message.from,
          sender: { name: nomeContato },
          type: tipoMensagem,
          body: message.body || message.content || message.caption || '',
          timestamp: new Date().toISOString(),
          notifyName: message.notifyName || '',
          
          ...(message.mediaData && {
            mediaData: {
              filename: message.mediaData.filename || `arquivo_${Date.now()}.bin`,
              mimetype: message.mediaData.mimetype || 'application/octet-stream',
              url: message.mediaData.url || '',
              size: message.mediaData.size || 0
            }
          }),

          metadata: {
            source: 'wppconnect_nodejs',
            messageId: message.id,
            isGroup: message.isGroupMsg || false,
            chatId: message.chatId || message.from,
            timestamp_node: Date.now(),
            messageType: message.type
          }
        };

        // ===== ENVIAR PARA PYTHON =====
        enviarParaPython(dadosPython);

      } catch (error) {
        console.error('❌ Erro ao processar mensagem para Python:', error);
      }
    });

    // Listener para mídia (também com filtro)
    client.onAnyMessage(async (message) => {
      try {
        // ===== FILTRO: Ignorar mensagens de status =====
        if (!isValidMessage(message)) {
          return;
        }

        if (['image', 'document', 'audio', 'video', 'sticker'].includes(message.type)) {
          console.log(`📎 Mídia VÁLIDA recebida: ${message.type} de ${message.from}`);
          console.log(`   Arquivo: ${message.mediaData?.filename || 'sem_nome'}`);
        }
      } catch (error) {
        console.error('❌ Erro ao processar mídia:', error);
      }
    });
    
    setTimeout(() => {
      salvarStatus(true, 'Cliente inicializado - verificando conexão...');
      testarIntegracaoPython();
    }, 5000);
  })
  .catch((error) => {
    console.log('❌ Erro ao iniciar cliente:', error);
    salvarStatus(false, 'Erro ao inicializar cliente');
  });

// ===== ENDPOINTS API =====
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'ok', 
    timestamp: new Date(),
    clientReady: !!wppClient,
    ultimoStatus: ultimoStatusLogado,
    paths: PATHS,
    pythonIntegration: {
      webhookUrl: pythonWebhookUrl,
      configured: true
    },
    server: 'WhatsApp Server - Filtros Aplicados'
  });
});

app.get('/status', (req, res) => {
  try {
    const statusPath = path.join(PATHS.static, 'status.json');
    if (fs.existsSync(statusPath)) {
      const statusData = JSON.parse(fs.readFileSync(statusPath, 'utf8'));
      res.json(statusData);
    } else {
      res.json({ 
        logado: false, 
        data: new Date().toISOString(), 
        mensagem: 'Status não encontrado' 
      });
    }
  } catch (error) {
    res.status(500).json({ error: 'Erro ao ler status', logado: false });
  }
});

app.post('/python-callback', (req, res) => {
  try {
    const { evento, dados } = req.body;
    console.log(`🐍➡️📱 Python callback: ${evento}`);
    
    switch (evento) {
      case 'despesa_criada':
        console.log(`💰 Nova despesa Python: R$ ${dados.valor} - ${dados.categoria}`);
        break;
      case 'arquivo_salvo':
        console.log(`📁 Arquivo salvo Python: ${dados.nome_arquivo}`);
        break;
      case 'erro_processamento':
        console.log(`❌ Erro Python: ${dados.erro}`);
        break;
      default:
        console.log(`📋 Evento Python: ${evento}`, dados);
    }
    
    res.json({ status: 'recebido', timestamp: new Date().toISOString() });
  } catch (error) {
    console.error('❌ Erro callback Python:', error);
    res.status(500).json({ error: error.message });
  }
});

app.post('/testar-python', async (req, res) => {
  try {
    const testMessage = {
      from: '5511999887766@c.us',
      sender: { name: 'Teste Manual' },
      type: 'text',
      body: req.body.mensagem || 'Teste manual de integração - R$ 100,00',
      timestamp: new Date().toISOString(),
      metadata: { source: 'teste_manual_nodejs' }
    };
    
    const resultado = await enviarParaPython(testMessage);
    
    if (resultado?.success) {
      res.json({ 
        success: true, 
        mensagem: 'Teste enviado com sucesso',
        resultado: resultado 
      });
    } else {
      res.status(500).json({ 
        success: false, 
        erro: 'Falha ao enviar para Python' 
      });
    }
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      erro: error.message 
    });
  }
});

app.post('/enviar-mensagem', async (req, res) => {
  try {
    if (!wppClient) {
      return res.status(500).json({ error: 'Cliente WhatsApp não está pronto.' });
    }

    const { telefone, mensagem, tipo = 'text' } = req.body;

    if (!telefone || !mensagem) {
      return res.status(400).json({ error: 'Telefone e mensagem são obrigatórios.' });
    }

    const telefoneFormatado = telefone.includes('@c.us') ? 
      telefone : 
      `55${telefone.replace(/\D/g, '')}@c.us`;

    console.log(`📤 Enviando mensagem para: ${telefoneFormatado}`);

    await wppClient.sendText(telefoneFormatado, mensagem);
    
    res.json({ 
      success: true, 
      telefone: telefoneFormatado, 
      mensagem: 'Mensagem enviada com sucesso!',
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Erro ao enviar mensagem:', error);
    res.status(500).json({ 
      error: 'Erro ao enviar mensagem', 
      details: error.message 
    });
  }
});

app.get('/contatos', async (req, res) => {
  try {
    if (!wppClient) {
      return res.status(500).json({ error: 'Cliente WhatsApp não está pronto.' });
    }

    const contacts = await wppClient.getAllContacts();
    
    const contatosFormatados = contacts
      .filter(contact => contact.name && !contact.isGroup)
      .map(contact => ({
        id: contact.id,
        name: contact.name,
        number: contact.number,
        isMyContact: contact.isMyContact,
        profilePicThumbObj: contact.profilePicThumbObj
      }))
      .slice(0, 100);

    res.json({
      success: true,
      total: contatosFormatados.length,
      contatos: contatosFormatados
    });

  } catch (error) {
    console.error('❌ Erro ao obter contatos:', error);
    res.status(500).json({ 
      error: 'Erro ao obter contatos', 
      details: error.message 
    });
  }
});

app.get('/chats', async (req, res) => {
  try {
    if (!wppClient) {
      return res.status(500).json({ error: 'Cliente WhatsApp não está pronto.' });
    }

    const chats = await wppClient.getAllChats();
    
    const chatsFormatados = chats
      .filter(chat => !chat.isGroup)
      .map(chat => ({
        id: chat.id,
        name: chat.name,
        lastMessage: chat.lastMessage?.body || '',
        lastMessageTime: chat.lastMessage?.timestamp,
        unreadCount: chat.unreadCount,
        contact: chat.contact
      }))
      .slice(0, 50);

    res.json({
      success: true,
      total: chatsFormatados.length,
      chats: chatsFormatados
    });

  } catch (error) {
    console.error('❌ Erro ao obter chats:', error);
    res.status(500).json({ 
      error: 'Erro ao obter chats', 
      details: error.message 
    });
  }
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`🚀 Servidor WhatsApp rodando na porta ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`📊 Status check: http://localhost:${PORT}/status`);
  console.log('🔗 Integração Python configurada!');
  console.log(`📡 Webhook Python: ${pythonWebhookUrl}`);
  console.log('');
  console.log('⚠️  IMPORTANTE: Inicie o Python PRIMEIRO!');
  console.log('   cd backend/python && python whatsapp_api_integration.py');
  console.log('');
  console.log('🔧 Filtros aplicados:');
  console.log('   ❌ Mensagens de status ignoradas');
  console.log('   ✅ Apenas mensagens diretas processadas');
  console.log('');
  console.log('📋 Endpoints disponíveis:');
  console.log('  GET  /health           - Status do servidor');
  console.log('  GET  /status           - Status do WhatsApp');
  console.log('  GET  /contatos         - Lista contatos');
  console.log('  GET  /chats            - Lista chats recentes');
  console.log('  POST /enviar-mensagem  - Enviar mensagem direta');
  console.log('  POST /testar-python    - Testar integração Python');
  console.log('');
  console.log('🎯 Sistema otimizado e filtrado!');
});