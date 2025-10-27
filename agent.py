import os
from openai import OpenAI
from typing import List, Dict, Any

# Tenta a importação relativa primeiro (para uvicorn)
try:
    from .ml_engine import ml_engine, ScreenAnalysis
except ImportError:
    from ml_engine import ml_engine, ScreenAnalysis

# Inicializa o cliente OpenAI
# As variáveis de ambiente OPENAI_API_KEY e BASE_URL são configuradas automaticamente
try:
    client = OpenAI()
except Exception as e:
    print(f"⚠️ Erro ao inicializar o cliente OpenAI: {e}")
    client = None

# Modelo a ser utilizado
MODEL_NAME = os.environ.get("LLM_MODEL", "gpt-4.1-mini")

# ============================================
# FUNÇÕES DE GERAÇÃO DE CENÁRIO GHERKIN
# ============================================

def generate_gherkin_scenario(
    screen_analysis: ScreenAnalysis, 
    user_intent: str, 
    conversation_history: List[Dict[str, str]]
) -> str:
    """
    Gera um cenário Gherkin completo usando um LLM ou o motor de ML,
    baseado na análise de tela, intenção do usuário e histórico da conversa.
    """
    
    # Se o cliente LLM não está disponível, usar o motor de ML
    if not client:
        return ml_engine.generate_gherkin(screen_analysis, user_intent)

    # 1. Construir o histórico de mensagens para o LLM
    messages = [
        {"role": "system", "content": f"""Você é o NEBULA AGENT 6.0, um especialista em BDD (Behavior-Driven Development) e automação de testes.
Sua única função é analisar o contexto fornecido (análise de tela, elementos identificados e histórico da conversa) 
e gerar um **CENÁRIO GHERKIN** completo e otimizado para o teste de software.

O Gherkin deve ser focado na **intenção do usuário** e na **funcionalidade principal** da tela.
A saída DEVE ser formatada em um bloco de código Markdown Gherkin, começando com a tag `Feature:`.

**Instruções:**
1.  **Feature:** Deve ser um título conciso sobre a funcionalidade principal.
2.  **Scenario:** Deve descrever o caso de uso principal.
3.  **Given:** O contexto inicial (ex: "Dado que o usuário está na tela de login").
4.  **When:** A ação do usuário (ex: "Quando ele preenche os campos 'Usuário' e 'Senha'").
5.  **Then:** O resultado esperado (ex: "Então ele deve ser redirecionado para a página inicial").

**Contexto da Análise:**
- **Tipo de Tela:** {screen_analysis.screen_type.value}
- **Confiança:** {screen_analysis.confidence:.0%}
- **Elementos:** {', '.join([elem.label for elem in screen_analysis.elements])}
- **Intenção do Usuário:** {user_intent}
"""}
    ]

    # Adicionar o histórico da conversa (limitando para evitar tokens excessivos)
    for item in conversation_history[-5:]:
        role = "user" if item["role"] == "user" else "assistant"
        messages.append({"role": role, "content": item["content"]})

    # Adicionar a última intenção do usuário como a mensagem final
    messages.append({"role": "user", "content": f"Minha intenção é: {user_intent}. Gere o cenário Gherkin."})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.2,
            max_tokens=1024
        )
        
        # Extrair e limpar o texto gerado
        gherkin_text = response.choices[0].message.content.strip()
        
        # Tentar extrair apenas o bloco de código Gherkin
        if "```gherkin" in gherkin_text:
            start = gherkin_text.find("```gherkin") + len("```gherkin")
            end = gherkin_text.find("```", start)
            return gherkin_text[start:end].strip()
        elif "```" in gherkin_text:
            start = gherkin_text.find("```") + len("```")
            end = gherkin_text.find("```", start)
            return gherkin_text[start:end].strip()
        
        return gherkin_text

    except Exception as e:
        print(f"❌ Erro na chamada do LLM: {e}")
        # Fallback para o motor de ML
        return ml_engine.generate_gherkin(screen_analysis, user_intent)


# ============================================
# FUNÇÃO DE ANÁLISE DE TELA
# ============================================

def simulate_screen_analysis(message: str) -> ScreenAnalysis:
    """
    Simula a análise visual de uma tela usando o motor de ML.
    Retorna um objeto ScreenAnalysis com informações detalhadas.
    """
    msg_lower = message.lower()
    
    # Mapear intenção do usuário para descrição de tela
    screen_descriptions = {
        "login": "Tela de Login com campos 'Usuário', 'Senha', botão 'Entrar' e link 'Esqueci a Senha'.",
        "logar": "Tela de Login com campos 'Usuário', 'Senha', botão 'Entrar' e link 'Esqueci a Senha'.",
        "cadastro": "Tela de Cadastro de Novo Usuário com campos 'Nome', 'Email', 'CPF', 'Senha', 'Confirmar Senha' e botão 'Criar Conta'.",
        "registrar": "Tela de Cadastro de Novo Usuário com campos 'Nome', 'Email', 'CPF', 'Senha', 'Confirmar Senha' e botão 'Criar Conta'.",
        "checkout": "Tela de Checkout com formulário de endereço, seleção de método de pagamento (Cartão, Pix) e botão 'Finalizar Compra'.",
        "pagamento": "Tela de Checkout com formulário de endereço, seleção de método de pagamento (Cartão, Pix) e botão 'Finalizar Compra'.",
    }
    
    # Encontrar a descrição mais apropriada
    screen_desc = "Tela Genérica com formulário e botão de ação."
    for keyword, desc in screen_descriptions.items():
        if keyword in msg_lower:
            screen_desc = desc
            break
    
    # Usar o motor de ML para analisar a tela
    return ml_engine.analyze_screen(screen_desc)


# ============================================
# FUNÇÃO DE AGENTE (PROCESSAMENTO PRINCIPAL)
# ============================================

def process_as_agent(message: str, state: Dict[str, Any]) -> str:
    """
    Função principal do agente que decide a ação a ser tomada.
    Integra análise de tela com ML e geração de Gherkin.
    """
    
    msg_lower = message.lower()
    
    # Se o usuário pedir para gerar Gherkin, cenário ou teste
    if any(keyword in msg_lower for keyword in ["gherkin", "cenário", "teste", "automatizar", "validar"]):
        
        # 1. Analisar a tela usando o motor de ML
        screen_analysis = simulate_screen_analysis(message)
        
        # 2. Gerar o cenário Gherkin
        gherkin = generate_gherkin_scenario(screen_analysis, message, state["conversation_history"])
        
        # 3. Montar a resposta com informações detalhadas
        response = f"""✅ **Cenário Gherkin Gerado com Sucesso!**

**Análise da Tela:**
- Tipo: {screen_analysis.screen_type.value}
- Confiança: {screen_analysis.confidence:.0%}
- Elementos Identificados: {len(screen_analysis.elements)}

**Cenário Gherkin:**
```gherkin
{gherkin}
```

**Próximos Passos:**
1. Executar o teste automatizado
2. Validar os resultados
3. Corrigir falhas se necessário
4. Atualizar o cenário conforme necessário"""
        
        return response
    
    # Se o usuário pedir para analisar uma tela
    elif any(keyword in msg_lower for keyword in ["analisar", "análise", "tela", "screen"]):
        
        screen_analysis = simulate_screen_analysis(message)
        
        elements_str = "\n".join([f"- {elem.label} ({elem.element_type.value})" for elem in screen_analysis.elements])
        
        response = f"""📊 **Análise da Tela Concluída**

**Tipo de Tela:** {screen_analysis.screen_type.value}
**Confiança:** {screen_analysis.confidence:.0%}

**Elementos Identificados:**
{elements_str}

**Palavras-chave:** {', '.join(screen_analysis.keywords)}

Deseja que eu gere um cenário Gherkin para esta tela?"""
        
        return response

    # Resposta padrão
    return f"""🤖 **Entendido!** Sua solicitação foi: '{message}'.

Sou especializada em:
- 📝 **Gerar cenários Gherkin** para testes automatizados
- 🔍 **Analisar telas** e identificar elementos
- 🤖 **Automatizar testes** de aplicações
- 📊 **Validar funcionalidades** com BDD

Tente me pedir para:
- "Gerar um cenário Gherkin para uma tela de login"
- "Analisar a tela de checkout"
- "Criar um teste para validar o cadastro\""""


# ============================================
# FUNÇÃO DE SAÚDE
# ============================================

def is_llm_available() -> bool:
    """Verifica se o cliente LLM está pronto para uso."""
    return client is not None


if __name__ == "__main__":
    # Exemplo de uso (apenas para teste local)
    print("--- Teste de Geração Gherkin ---")
    mock_state = {"conversation_history": []}
    mock_message = "Gerar um cenário Gherkin para o fluxo de login com sucesso"
    
    result = process_as_agent(mock_message, mock_state)
    print(result)

