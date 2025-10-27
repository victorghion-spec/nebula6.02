import os
import re
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Tenta a importação relativa primeiro (para uvicorn)
# Se falhar, tenta a importação direta (para execução local/debug)
try:
    from .agent import process_as_agent, is_llm_available
    from .billing import billing_manager, ActionType, PlanType
    from .scrumban import scrumban_manager, TaskStatus, TaskPriority, create_task_from_message
except ImportError:
    from agent import process_as_agent, is_llm_available
    from billing import billing_manager, ActionType, PlanType
    from scrumban import scrumban_manager, TaskStatus, TaskPriority, create_task_from_message

# ============================================
# NEBULA AGENT v5.0 - Agente de IA com Gherkin
# ============================================

app = FastAPI(title="Nebula Agent v5.0 - Agente de Testes Inteligente")

# ============================================
# CONFIGURAÇÃO INICIAL
# ============================================

# Em produção, troque ["*"] para o seu domínio
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*")
allow_origins = [o.strip() for o in ALLOWED_ORIGINS.split(",")] if ALLOWED_ORIGINS != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Estado Global do Agente
STATE = {"pending_task": None, "conversation_history": [], "user_id": "default_user", "board_id": "default"}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Inicializar usuário padrão
if "default_user" not in billing_manager.users:
    billing_manager.create_user("default_user", PlanType.LITE)

# ============================================
# ROTA PRINCIPAL DO CHAT (AGENTE)
# ============================================

@app.post("/chat")
async def chat_endpoint(request: Request):
    """Endpoint principal para processar mensagens do chat usando o Agente LLM."""
    if not is_llm_available():
        return JSONResponse(
            {"reply": "⚠️ O Agente LLM não está disponível. Verifique a configuração da API Key."},
            status_code=503
        )

    try:
        data = await request.json()
        message = data.get("message", "").strip()
        user_id = data.get("user_id", STATE["user_id"])

        if not message:
            return JSONResponse({"reply": "Por favor, envie uma mensagem válida."})

        # Verificar créditos do usuário
        user = billing_manager.get_user(user_id)
        if not user:
            user = billing_manager.create_user(user_id, PlanType.LITE)
        
        # Tentar realizar a ação (deduza créditos)
        action_result = billing_manager.perform_action(user_id, ActionType.GENERATE_GHERKIN)
        
        if not action_result["success"]:
            return JSONResponse({
                "reply": f"⚠️ {action_result['message']}\n\nCréditos disponíveis: {action_result['credits_remaining']}",
                "credits_remaining": action_result["credits_remaining"]
            })

        # Adiciona ao histórico
        STATE["conversation_history"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        # Processa a mensagem usando o Agente
        reply = process_as_agent(message, STATE)

        # Adiciona resposta ao histórico
        STATE["conversation_history"].append({
            "role": "assistant",
            "content": reply,
            "timestamp": datetime.now().isoformat()
        })
        
        # Criar tarefa no Scrumban
        task_data = create_task_from_message(STATE["board_id"], message)
        
        # Atualizar status da tarefa para "em progresso" e depois "concluído"
        if task_data:
            scrumban_manager.update_task_status(STATE["board_id"], task_data["id"], TaskStatus.IN_PROGRESS)
            scrumban_manager.update_task_status(STATE["board_id"], task_data["id"], TaskStatus.DONE)

        return JSONResponse({
            "reply": reply,
            "credits_remaining": user.credits,
            "task_id": task_data["id"] if task_data else None
        })

    except Exception as e:
        print(f"❌ Erro no chat: {e}")
        return JSONResponse(
            {"reply": f"⚠️ Ocorreu um erro interno ao processar sua mensagem: {e}. Tente novamente."},
            status_code=500
        )

# ============================================
# ROTA DE HISTÓRICO E LIMPEZA
# ============================================

@app.get("/history")
async def get_history():
    """Retorna o histórico da conversa."""
    return JSONResponse(STATE["conversation_history"])

@app.post("/clear-history")
async def clear_history():
    """Limpa o histórico da conversa."""
    STATE["conversation_history"] = []
    return JSONResponse({"message": "Histórico limpo com sucesso!"})

# ============================================
# SERVIR ARQUIVOS ESTÁTICOS E INDEX
# ============================================

# Monta a pasta static
static_path = os.path.join(BASE_DIR, "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/service-worker.js", response_class=HTMLResponse)
async def serve_service_worker():
    """Serve o service-worker.js."""
    sw_path = os.path.join(BASE_DIR, "service-worker.js")
    if os.path.exists(sw_path):
        with open(sw_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read(), media_type="application/javascript")
    return HTMLResponse("/* Service Worker not found */", status_code=404)

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve o index.html principal."""
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>❌ Nebula Agent - index.html não encontrado</h1>", status_code=404)

# ============================================
# ROTAS DE BILLING (CRÉDITOS E PLANOS)
# ============================================

@app.get("/billing/status")
async def get_billing_status(user_id: str = STATE["user_id"]):
    """Retorna o status de créditos e plano do usuário."""
    user = billing_manager.get_user(user_id)
    if not user:
        user = billing_manager.create_user(user_id, PlanType.LITE)
    
    return JSONResponse(user.get_status())

@app.post("/billing/upgrade")
async def upgrade_plan(request: Request):
    """Faz upgrade do plano do usuário."""
    data = await request.json()
    user_id = data.get("user_id", STATE["user_id"])
    new_plan = data.get("plan", "plus")
    
    try:
        plan = PlanType(new_plan)
        result = billing_manager.upgrade_user(user_id, plan)
        return JSONResponse(result)
    except ValueError:
        return JSONResponse({"success": False, "message": f"Plano inválido: {new_plan}"}, status_code=400)

# ============================================
# ROTAS DO SCRUMBAN
# ============================================

@app.get("/scrumban/board")
async def get_scrumban_board(board_id: str = STATE["board_id"]):
    """Retorna os dados completos do board Scrumban."""
    board_data = scrumban_manager.get_board_data(board_id)
    if not board_data:
        scrumban_manager.create_board(board_id)
        board_data = scrumban_manager.get_board_data(board_id)
    
    return JSONResponse(board_data)

@app.get("/scrumban/stats")
async def get_scrumban_stats(board_id: str = STATE["board_id"]):
    """Retorna as estatísticas do board Scrumban."""
    stats = scrumban_manager.get_board_stats(board_id)
    if not stats:
        scrumban_manager.create_board(board_id)
        stats = scrumban_manager.get_board_stats(board_id)
    
    return JSONResponse(stats)

@app.post("/scrumban/task")
async def create_scrumban_task(request: Request):
    """Cria uma nova tarefa no Scrumban."""
    data = await request.json()
    board_id = data.get("board_id", STATE["board_id"])
    title = data.get("title", "")
    description = data.get("description", "")
    priority = data.get("priority", "medium")
    
    try:
        task_priority = TaskPriority(priority)
        task_data = scrumban_manager.create_task(
            board_id=board_id,
            title=title,
            description=description,
            priority=task_priority,
            assignee="Nebula Agent"
        )
        return JSONResponse({"success": True, "task": task_data})
    except ValueError:
        return JSONResponse({"success": False, "message": f"Prioridade inválida: {priority}"}, status_code=400)

@app.post("/scrumban/task/status")
async def update_task_status(request: Request):
    """Atualiza o status de uma tarefa."""
    data = await request.json()
    board_id = data.get("board_id", STATE["board_id"])
    task_id = data.get("task_id", "")
    new_status = data.get("status", "todo")
    
    try:
        status = TaskStatus(new_status)
        success = scrumban_manager.update_task_status(board_id, task_id, status)
        return JSONResponse({
            "success": success,
            "message": "Status atualizado com sucesso" if success else "Tarefa não encontrada"
        })
    except ValueError:
        return JSONResponse({"success": False, "message": f"Status inválido: {new_status}"}, status_code=400)

# ============================================
# ROTA DE SAÚDE (HEALTH CHECK)
# ============================================

@app.get("/health")
async def health_check():
    """Verifica se o servidor está funcionando."""
    user = billing_manager.get_user(STATE["user_id"])
    board = scrumban_manager.get_board(STATE["board_id"])
    
    return JSONResponse({
        "status": "online",
        "version": "6.0",
        "llm_available": is_llm_available(),
        "conversation_messages": len(STATE["conversation_history"]),
        "user_plan": user.plan.value if user else "unknown",
        "user_credits": user.credits if user else 0,
        "scrumban_tasks": len(board.tasks) if board else 0
    })

# ============================================
# LIMPEZA DE ARQUIVOS ANTIGOS
# ============================================

def cleanup_old_files():
    files_to_remove = [
        "knowledge_base.txt", "base.txt", "faq.md", 
        "commands.json", "unrecognized_commands.txt",
        "controller.py", "executor.py", "passenger_wsgi.py",
        "composer.json", "htaccess", "script.js", "chat.js"
    ]
    for filename in files_to_remove:
        filepath = os.path.join(BASE_DIR, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"🗑️ Arquivo antigo removido: {filename}")
            except Exception as e:
                print(f"⚠️ Erro ao remover {filename}: {e}")

# ============================================
# INICIALIZAÇÃO
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    # Executa a limpeza ao iniciar
    cleanup_old_files()
    
    port = int(os.environ.get("PORT", 8000))
    print("=" * 50)
    print("🚀 NEBULA AGENT v5.0 - INICIANDO")
    print("=" * 50)
    print(f"📡 Servidor rodando na porta: {port}")
    print(f"🌐 Acesse: http://localhost:{port}")
    print(f"🧠 LLM Disponível: {is_llm_available()}")
    print("=" * 50)
    uvicorn.run("application:app", host="0.0.0.0", port=port, reload=True)

