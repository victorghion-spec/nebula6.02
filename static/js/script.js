/* === Nebula Chat - script.js ===
   Ajuste apenas as duas constantes abaixo:
   - API_BASE (HTTPs REST) ou WS_URL (WebSocket)
*/

const USE_WEBSOCKET = false; // true se seu backend usa WebSocket, false para REST
const API_BASE = "/chat"; // Ajustado para o endpoint do backend
const WS_URL = "wss://performanceoptimizer.com.br/ws"; // <-- ajuste se usar websocket

// util: seletores do layout (ajuste se usarem outros IDs/classes)
const inputEl = document.querySelector('input[type="text"], textarea, #userInput'); // Ajustado para #userInput
const sendBtn = document.querySelector('#sendBtn'); // Ajustado para #sendBtn
const chatContainer = document.querySelector('#chatBox'); // Ajustado para #chatBox

// botão "explore" (exemplo da sua primeira linha)
const exploreBtn = document.getElementById("explore-btn");
if (exploreBtn) {
  exploreBtn.addEventListener("click", () => {
    alert("Explorando o universo Nebula");
  });
}

// Conexão WebSocket (opcional)
let socket = null;
function connectWebSocket() {
  if (!WS_URL) return;
  try {
    socket = new WebSocket(WS_URL);
    socket.addEventListener('open', () => {
      console.log('WebSocket aberto');
      appendSystemMessage('Conexão WebSocket estabelecida.');
    });
    socket.addEventListener('message', (ev) => {
      console.log('WS message', ev.data);
      appendBotMessage(ev.data);
    });
    socket.addEventListener('close', () => {
      console.log('WebSocket fechado');
      appendSystemMessage('Conexão WebSocket fechada.');
    });
    socket.addEventListener('error', (err) => {
      console.error('WebSocket erro', err);
      appendSystemMessage('Erro de conexão com o servidor (WebSocket).');
    });
  } catch (e) {
    console.error('Falha ao conectar WebSocket', e);
  }
}

// Enviar via REST
async function sendViaREST(text) {
  try {
    const resp = await fetch(API_BASE, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: text })
    });
    if (!resp.ok) {
      console.error('Resposta não OK', resp.status, await resp.text());
      appendSystemMessage('Erro de conexão com o servidor. Código: ' + resp.status);
      return;
    }
    const data = await resp.json();
    // ajuste aqui se sua API retorna { reply: "..." }
    appendBotMessage(data.reply ?? JSON.stringify(data));
  } catch (err) {
    console.error('Erro fetch', err);
    appendSystemMessage('Erro de conexão com o servidor (fetch). Veja console.');
  }
}

// envio principal
function sendMessage(text) {
  if (!text || !text.trim()) return;
  appendUserMessage(text);
  if (USE_WEBSOCKET && socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ message: text }));
  } else if (USE_WEBSOCKET) {
    appendSystemMessage('WebSocket não está conectado. Tentando reconectar...');
    connectWebSocket();
    // fallback para REST:
    sendViaREST(text);
  } else {
    sendViaREST(text);
  }
  if (inputEl) inputEl.value = '';
}

// helpers UI (substitua por suas funções reais)
function appendUserMessage(text) {
  if (!chatContainer) return;
  const el = document.createElement('div');
  el.className = 'message user-msg'; // Ajustado para a classe CSS correta
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;
  el.appendChild(bubble);
  chatContainer.appendChild(el);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}
function appendBotMessage(text) {
  if (!chatContainer) return;
  const el = document.createElement('div');
  el.className = 'message bot-msg'; // Ajustado para a classe CSS correta
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;
  el.appendChild(bubble);
  chatContainer.appendChild(el);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}
function appendSystemMessage(text) {
  if (!chatContainer) return;
  const el = document.createElement('div');
  el.className = 'message bot-msg system-msg'; // Classe extra para sistema
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;
  el.appendChild(bubble);
  chatContainer.appendChild(el);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// eventos
if (sendBtn) {
  sendBtn.addEventListener('click', () => {
    const value = inputEl ? inputEl.value : '';
    sendMessage(value);
  });
}
if (inputEl) {
  inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputEl.value);
    }
  });
}

// iniciar WS se necessário
if (USE_WEBSOCKET) {
  connectWebSocket();
}
