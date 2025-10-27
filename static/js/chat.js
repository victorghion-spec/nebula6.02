// ===============================
// Nebula Chat Frontend v6.0
// Agente Inteligente com Scrumban e Planos
// ===============================

// Função auxiliar para construir URLs de API
function getApiUrl(endpoint) {
  // Se estamos em produção (HTTPS), usar o mesmo domínio
  // Se estamos em desenvolvimento (HTTP), usar o mesmo domínio
  return window.location.origin + endpoint;
}

document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chatBox");
  const userInput = document.getElementById("userInput");
  const sendBtn = document.getElementById("sendBtn");
  const clearHistoryBtn = document.getElementById("clearHistoryBtn");
  
  // Elementos de Navegação
  const navChat = document.getElementById("navChat");
  const navSearch = document.getElementById("navSearch");
  const navLibrary = document.getElementById("navLibrary");
  
  const chatView = document.getElementById("chatView");
  const searchView = document.getElementById("searchView");
  const libraryView = document.getElementById("libraryView");
  
  // Elementos de Plano (Sidebar)
  const planDropdown = document.querySelector(".plan-dropdown");
  const planMenu = document.getElementById("planMenu");
  const planOptions = document.querySelectorAll(".plan-option");
  const planName = document.getElementById("planName");
  
  // Elementos de Versao (Header)
  const versionDropdown = document.getElementById("versionDropdown");
  const versionMenu = document.getElementById("versionMenu");
  const versionOptions = document.querySelectorAll(".version-option");
  const versionLabel = document.getElementById("versionLabel");
  
  // Elementos de Scrumban
  const scrumbanRefresh = document.getElementById("scrumbanRefresh");
  const scrumbanBoard = document.getElementById("scrumbanBoard");
  
  // Elementos de Sidebar
  const historyList = document.getElementById("historyList");
  const historyToggle = document.getElementById("historyToggle");
  const shareBtn = document.getElementById("shareBtn");
  
  // Estado Global
  let currentView = "chat";
  let currentPlan = "lite";
  let currentVersion = "lite";
  let taskHistory = [];
  let scrumbanTasks = {
    todo: [],
    blocked: [],
    inprogress: [],
    done: []
  };

  // ===============================
  // Função para adicionar mensagens
  // ===============================
  function addMessage(sender, text, isMarkdown = false) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender === "user" ? "user-msg" : "bot-msg");
    
    const bubble = document.createElement("div");
    bubble.classList.add("bubble");
    
    if (isMarkdown) {
      bubble.innerHTML = parseMarkdown(text);
    } else {
      bubble.innerHTML = text.replace(/\n/g, "<br>");
    }
    
    msgDiv.appendChild(bubble);
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    return bubble;
  }

  // ===============================
  // Parser Markdown Simples
  // ===============================
  function parseMarkdown(text) {
    let html = text;
    
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__([^_]+)__/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    html = html.replace(/_([^_]+)_/g, '<em>$1</em>');
    html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    html = html.replace(/\n/g, "<br>");
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color: #69ffdb; text-decoration: underline;">$1</a>');
    
    return html;
  }

  // ===============================
  // Indicador de Digitação
  // ===============================
  function createTypingIndicator() {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", "bot-msg");
    
    const bubble = document.createElement("div");
    bubble.classList.add("bubble");
    bubble.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
    
    msgDiv.appendChild(bubble);
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    return msgDiv;
  }

  // ===============================
  // Enviar Mensagem ao Backend
  // ===============================
  async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    userInput.disabled = true;
    sendBtn.disabled = true;

    addMessage("user", message, false);
    userInput.value = "";
    userInput.focus();

    const typingDiv = createTypingIndicator();

    try {
      // Usar caminho relativo que funciona em localhost e em produção
      const response = await fetch(getApiUrl("/chat"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`);
      }

      const data = await response.json();
      const reply = data.reply || data.response || "Sem resposta no momento.";

      typingDiv.remove();

      addMessage("bot", reply, true);

      // Adicionar à história
      const taskTitle = message.substring(0, 50) + (message.length > 50 ? "..." : "");
      addTaskToHistory(taskTitle);
      
      // Simular adição ao Scrumban
      addTaskToScrumban(taskTitle, "done");

      console.log("✅ Resposta recebida:", reply);
    } catch (error) {
      typingDiv.remove();

      addMessage("bot", 
        "⚠️ <strong>Erro de Conexão</strong><br>" +
        "Não consegui conectar ao servidor. Verifique se o backend está rodando em " + getApiUrl("/"), 
        true
      );
      console.error("❌ Erro:", error);
    } finally {
      userInput.disabled = false;
      sendBtn.disabled = false;
      userInput.focus();
    }
  }

  // ===============================
  // Limpar Histórico
  // ===============================
  async function clearHistory() {
    if (!confirm("Tem certeza que deseja limpar o histórico de conversa?")) {
      return;
    }

    try {
      const response = await fetch(getApiUrl("/clear-history"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (response.ok) {
        chatBox.innerHTML = '';
        taskHistory = [];
        updateHistoryList();
        
        addMessage("bot", 
          "🌌 <strong>Histórico limpo!</strong><br>" +
          "Iniciamos uma nova conversa. Como posso ajudar?", 
          true
        );
        
        console.log("✅ Histórico limpo com sucesso");
      }
    } catch (error) {
      console.error("❌ Erro ao limpar histórico:", error);
      alert("Erro ao limpar o histórico. Tente novamente.");
    }
  }

  // ===============================
  // Navegação entre Views
  // ===============================
  function switchView(viewName) {
    // Esconder todas as views
    chatView.style.display = "none";
    searchView.style.display = "none";
    libraryView.style.display = "none";
    
    // Remover classe active de todos os botões
    navChat.classList.remove("active");
    navSearch.classList.remove("active");
    navLibrary.classList.remove("active");
    
    // Mostrar a view selecionada
    switch(viewName) {
      case "chat":
        chatView.style.display = "flex";
        navChat.classList.add("active");
        userInput.focus();
        break;
      case "search":
        searchView.style.display = "flex";
        navSearch.classList.add("active");
        document.getElementById("searchInput").focus();
        break;
      case "library":
        libraryView.style.display = "flex";
        navLibrary.classList.add("active");
        loadLibrary();
        break;
    }
    
    currentView = viewName;
  }

  // ===============================
  // Gerenciamento de Planos
  // ===============================
  function togglePlanMenu() {
    const isVisible = planMenu.style.display === "flex";
    planMenu.style.display = isVisible ? "none" : "flex";
    planDropdown.classList.toggle("active");
  }

  function selectPlan(plan) {
    currentPlan = plan;
    const planLabels = {
      lite: "Nebula Lite",
      plus: "Nebula Plus",
      pro: "Nebula Pro",
      ultra: "Nebula Ultra"
    };
    
    planName.textContent = planLabels[plan];
    planMenu.style.display = "none";
    planDropdown.classList.remove("active");
    
    console.log(`✅ Plano alterado para: ${planLabels[plan]}`);
  }
  
  // ===============================
  // Gerenciamento de Versao (Header)
  // ===============================
  function toggleVersionMenu() {
    const isVisible = versionMenu.style.display === "flex";
    versionMenu.style.display = isVisible ? "none" : "flex";
    versionDropdown.classList.toggle("active");
  }
  
  function selectVersion(version) {
    currentVersion = version;
    const versionLabels = {
      lite: "Lite",
      plus: "Plus",
      pro: "Pro",
      ultra: "Ultra"
    };
    
    versionLabel.textContent = versionLabels[version];
    versionMenu.style.display = "none";
    versionDropdown.classList.remove("active");
    
    console.log(`✅ Versao alterada para: ${versionLabels[version]}`);
  }

  // ===============================
  // Gerenciamento do Scrumban
  // ===============================
  function addTaskToScrumban(title, status = "todo") {
    const task = {
      id: Date.now(),
      title: title,
      status: status,
      timestamp: new Date().toLocaleTimeString()
    };
    
    scrumbanTasks[status].push(task);
    renderScrumban();
  }

  function renderScrumban() {
    const statusMap = {
      todo: "todoCards",
      blocked: "blockedCards",
      inprogress: "inprogressCards",
      done: "doneCards"
    };
    
    Object.keys(statusMap).forEach(status => {
      const container = document.getElementById(statusMap[status]);
      container.innerHTML = "";
      
      scrumbanTasks[status].forEach(task => {
        const card = document.createElement("div");
        card.classList.add("scrumban-card");
        card.draggable = true;
        card.innerHTML = `
          <div class="card-title">${task.title}</div>
          <div class="card-status">${task.timestamp}</div>
        `;
        
        card.addEventListener("dragstart", (e) => {
          e.dataTransfer.effectAllowed = "move";
          e.dataTransfer.setData("taskId", task.id);
          e.dataTransfer.setData("fromStatus", status);
          card.classList.add("dragging");
        });
        
        card.addEventListener("dragend", () => {
          card.classList.remove("dragging");
        });
        
        container.appendChild(card);
      });
    });
    
    // Adicionar listeners de drop
    document.querySelectorAll(".column-cards").forEach(column => {
      column.addEventListener("dragover", (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = "move";
        column.style.backgroundColor = "rgba(46, 222, 168, 0.15)";
      });
      
      column.addEventListener("dragleave", () => {
        column.style.backgroundColor = "";
      });
      
      column.addEventListener("drop", (e) => {
        e.preventDefault();
        column.style.backgroundColor = "";
        
        const taskId = parseInt(e.dataTransfer.getData("taskId"));
        const fromStatus = e.dataTransfer.getData("fromStatus");
        const toStatus = column.getAttribute("data-status");
        
        // Encontrar e mover a tarefa
        const taskIndex = scrumbanTasks[fromStatus].findIndex(t => t.id === taskId);
        if (taskIndex !== -1) {
          const task = scrumbanTasks[fromStatus].splice(taskIndex, 1)[0];
          task.status = toStatus;
          scrumbanTasks[toStatus].push(task);
          renderScrumban();
        }
      });
    });
  }

  // ===============================
  // Gerenciamento do Histórico
  // ===============================
  function addTaskToHistory(title) {
    taskHistory.unshift({
      title: title,
      timestamp: new Date().toLocaleTimeString()
    });
    
    if (taskHistory.length > 10) {
      taskHistory.pop();
    }
    
    updateHistoryList();
  }

  function updateHistoryList() {
    historyList.innerHTML = "";
    taskHistory.forEach((task, index) => {
      const li = document.createElement("li");
      li.innerHTML = `
        <span class="task-title">${task.title}</span>
        <span class="task-time">${task.timestamp}</span>
      `;
      li.addEventListener("click", () => {
        userInput.value = task.title.replace("...", "");
        userInput.focus();
      });
      historyList.appendChild(li);
    });
  }

  // ===============================
  // Carregar Library
  // ===============================
  function loadLibrary() {
    const libraryContent = document.getElementById("libraryContent");
    libraryContent.innerHTML = `
      <div class="library-item">
        <h3>📚 Biblioteca de Cenários</h3>
        <p>Aqui você pode encontrar cenários Gherkin salvos e reutilizáveis.</p>
      </div>
      <div class="library-item">
        <h3>🔍 Buscar Cenários</h3>
        <input type="text" id="librarySearch" placeholder="Buscar cenário..." style="width: 100%; padding: 8px; margin-top: 8px;">
      </div>
    `;
  }

  // ===============================
  // Event Listeners
  // ===============================
  
  // Chat
  sendBtn.addEventListener("click", sendMessage);
  userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  
  clearHistoryBtn.addEventListener("click", clearHistory);
  
  // Navegação
  navChat.addEventListener("click", () => switchView("chat"));
  navSearch.addEventListener("click", () => switchView("search"));
  navLibrary.addEventListener("click", () => switchView("library"));
  
  // Planos (Sidebar)
  planDropdown.addEventListener("click", togglePlanMenu);
  planOptions.forEach(option => {
    option.addEventListener("click", () => {
      const plan = option.getAttribute("data-plan");
      selectPlan(plan);
    });
  });
  
  // Versao (Header)
  versionDropdown.addEventListener("click", toggleVersionMenu);
  versionOptions.forEach(option => {
    option.addEventListener("click", () => {
      const version = option.getAttribute("data-version");
      selectVersion(version);
    });
  });
  
  // Scrumban
  if (scrumbanRefresh) {
    scrumbanRefresh.addEventListener("click", renderScrumban);
  }
  
  // Histórico
  if (historyToggle) {
    historyToggle.addEventListener("click", () => {
      historyList.style.display = historyList.style.display === "none" ? "block" : "none";
    });
  }
  
  // Share
  if (shareBtn) {
    shareBtn.addEventListener("click", () => {
      alert("Compartilhamento em desenvolvimento!");
    });
  }
  
  // Inicializar
  switchView("chat");
  addMessage("bot", 
    "👋 <strong>Olá! Sou a Nebula Agent v6.0</strong><br>" +
    "Sou uma assistente inteligente especializada em automação de testes e geração de cenários Gherkin.<br>" +
    "Como posso ajudar você hoje?", 
    true
  );
});



// Funcao global para selecionar plano e fechar a view
function selectPlanAndClose(plan) {
  const planLabels = {
    lite: "Nebula Lite",
    plus: "Nebula Plus",
    pro: "Nebula Pro",
    ultra: "Nebula Ultra"
  };
  
  alert("Plano " + planLabels[plan] + " selecionado!");
  console.log("Plano selecionado: " + plan);
  
  // Voltar para a view de chat
  const chatView = document.getElementById("chatView");
  const plansView = document.getElementById("plansView");
  
  if (chatView && plansView) {
    plansView.style.display = "none";
    chatView.style.display = "flex";
  }
}

