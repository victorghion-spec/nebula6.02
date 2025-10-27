# 🚀 Nebula Agent v5.0 - Agente de Testes Inteligente

Parabéns! Seu **Nebula Agent** foi aprimorado para a versão **5.0**, com uma interface moderna e profissional (inspirada no Manus) e com a nova funcionalidade de **Geração Automática de Cenários Gherkin** usando Machine Learning (simulado) e Large Language Models (LLM).

## ✨ Novidades da Versão 5.0

1.  **Interface Moderna (Inspirada no Manus):** Design mais limpo, profissional e responsivo, mantendo a identidade visual verde/ciano.
2.  **Agente de Testes (LLM-Powered):** A lógica de chat foi substituída por um agente inteligente focado em BDD (Behavior-Driven Development).
3.  **Geração Automática de Gherkin:** O agente gera cenários de teste completos em Gherkin (`Feature`, `Scenario`, `Given`, `When`, `Then`) com base na sua solicitação e na **análise visual da tela**.
4.  **Arquitetura Preparada para ML:** A função de **Análise Visual de Tela** está simulada (`simulate_screen_analysis` em `agent.py`), permitindo uma integração futura com um modelo de Visão Computacional real.

## 🛠️ Como Executar o Projeto

O projeto é construído em **Python** com **FastAPI** para o backend e **HTML/CSS/JavaScript** para o frontend.

### Pré-requisitos

*   Python 3.8+
*   Acesso à internet para o LLM (OpenAI)

### 1. Instalação de Dependências

Certifique-se de estar no diretório raiz do projeto (`nebula-agent`) e instale as dependências:

```bash
pip install -r requirements.txt
```

### 2. Configuração do LLM

O projeto utiliza um Large Language Model (LLM) para a geração do Gherkin. Ele usa a biblioteca `openai` e espera que as credenciais sejam configuradas via variáveis de ambiente.

**Recomendado:** O sistema está configurado para usar um endpoint compatível com OpenAI. Você pode configurar a chave de API da seguinte forma:

```bash
# Substitua pela sua chave de API
export OPENAI_API_KEY="SUA_CHAVE_AQUI" 
```

### 3. Inicialização do Servidor

Inicie o servidor usando `uvicorn`:

```bash
uvicorn application:app --reload
```

O servidor será iniciado em `http://127.0.0.1:8000`.

## 💡 Como Usar o Novo Agente

O agente foi treinado para responder a comandos de geração de Gherkin.

1.  **Acesse:** Abra seu navegador em `http://127.0.0.1:8000`.
2.  **Comande:** Peça ao agente para gerar um cenário.

**Exemplos de Comandos:**

*   `Gerar um cenário Gherkin para o fluxo de login com sucesso`
*   `Criar um teste para o checkout de um produto`
*   `Quero o Gherkin para o cadastro de um novo usuário`

O agente irá:
1.  Interpretar sua intenção.
2.  Simular a análise visual da tela (ex: "Tela de Login com campos 'Usuário', 'Senha', botão 'Entrar'").
3.  Gerar o cenário Gherkin completo, formatado em um bloco de código Markdown.

## Próximos Passos (Integração ML Real)

Para implementar a **análise visual de tela real**, você precisará:

1.  **Desenvolver/Integrar um Modelo de Visão Computacional:** Um modelo que receba uma imagem (screenshot) e retorne uma descrição estruturada dos elementos da tela (campos, botões, labels).
2.  **Atualizar `agent.py`:** Substituir a função `simulate_screen_analysis` por uma chamada de API para o seu novo modelo de ML.

```python
# Exemplo de como ficaria a função atualizada em agent.py (futuro)
def get_real_screen_analysis(screenshot_path: str) -> str:
    # 1. Enviar a imagem para o seu serviço de ML
    # 2. Receber a descrição estruturada
    # return "Descrição detalhada da tela gerada pelo ML"
    pass
```

O restante da arquitetura (LLM e Gherkin Generator) já está pronto para consumir essa nova entrada!

