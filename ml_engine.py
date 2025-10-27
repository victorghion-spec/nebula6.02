"""
Motor de Machine Learning para Análise Visual e Geração de Cenários
Nebula Agent v6.0
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import re


# ============================================
# ENUMS E CONSTANTES
# ============================================

class ScreenType(str, Enum):
    """Tipos de telas identificáveis."""
    LOGIN = "login"
    REGISTRATION = "registration"
    CHECKOUT = "checkout"
    DASHBOARD = "dashboard"
    FORM = "form"
    LIST = "list"
    DETAIL = "detail"
    MODAL = "modal"
    ERROR = "error"
    SUCCESS = "success"
    UNKNOWN = "unknown"


class ElementType(str, Enum):
    """Tipos de elementos de UI."""
    INPUT = "input"
    BUTTON = "button"
    LINK = "link"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    SELECT = "select"
    TABLE = "table"
    CARD = "card"
    MODAL = "modal"
    ALERT = "alert"


# ============================================
# CLASSE DE ELEMENTO DE UI
# ============================================

class UIElement:
    """Representa um elemento de UI identificado na tela."""
    
    def __init__(
        self,
        element_type: ElementType,
        label: str,
        name: str = "",
        required: bool = False,
        placeholder: str = ""
    ):
        self.element_type = element_type
        self.label = label
        self.name = name or label.lower().replace(" ", "_")
        self.required = required
        self.placeholder = placeholder
    
    def to_dict(self) -> Dict:
        """Converte o elemento para dicionário."""
        return {
            "type": self.element_type.value,
            "label": self.label,
            "name": self.name,
            "required": self.required,
            "placeholder": self.placeholder
        }
    
    def to_gherkin_step(self) -> str:
        """Converte o elemento para um passo Gherkin."""
        if self.element_type == ElementType.INPUT:
            return f'E eu preencho o campo "{self.label}" com "<valor>"'
        elif self.element_type == ElementType.BUTTON:
            return f'E eu clico no botão "{self.label}"'
        elif self.element_type == ElementType.CHECKBOX:
            return f'E eu marco a caixa de seleção "{self.label}"'
        elif self.element_type == ElementType.DROPDOWN:
            return f'E eu seleciono "<opção>" no dropdown "{self.label}"'
        else:
            return f'E eu interajo com "{self.label}"'


# ============================================
# CLASSE DE ANÁLISE DE TELA
# ============================================

class ScreenAnalysis:
    """Análise de uma tela capturada."""
    
    def __init__(self, screen_description: str):
        self.screen_description = screen_description
        self.screen_type = self._detect_screen_type()
        self.elements = self._extract_elements()
        self.keywords = self._extract_keywords()
        self.confidence = self._calculate_confidence()
    
    def _detect_screen_type(self) -> ScreenType:
        """Detecta o tipo de tela baseado na descrição."""
        desc_lower = self.screen_description.lower()
        
        # Mapeamento de palavras-chave para tipos de tela
        type_keywords = {
            ScreenType.LOGIN: ["login", "logar", "autenticação", "senha", "usuário"],
            ScreenType.REGISTRATION: ["cadastro", "registrar", "criar conta", "inscrição"],
            ScreenType.CHECKOUT: ["checkout", "pagamento", "compra", "carrinho", "pedido"],
            ScreenType.DASHBOARD: ["dashboard", "início", "home", "painel"],
            ScreenType.FORM: ["formulário", "form", "preencher", "enviar"],
            ScreenType.LIST: ["lista", "tabela", "resultado", "busca"],
            ScreenType.DETAIL: ["detalhe", "detalhes", "visualizar", "ver"],
            ScreenType.MODAL: ["modal", "diálogo", "popup", "janela"],
            ScreenType.ERROR: ["erro", "falha", "problema", "aviso"],
            ScreenType.SUCCESS: ["sucesso", "concluído", "realizado", "confirmado"],
        }
        
        for screen_type, keywords in type_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                return screen_type
        
        return ScreenType.UNKNOWN
    
    def _extract_elements(self) -> List[UIElement]:
        """Extrai elementos de UI da descrição da tela."""
        elements = []
        desc_lower = self.screen_description.lower()
        
        # Padrões para identificar elementos
        input_pattern = r"campo[s]?\s+['\"]?([^'\"]+)['\"]?"
        button_pattern = r"botão[s]?\s+['\"]?([^'\"]+)['\"]?"
        link_pattern = r"link[s]?\s+['\"]?([^'\"]+)['\"]?"
        
        # Extrair inputs
        for match in re.finditer(input_pattern, desc_lower):
            label = match.group(1).strip()
            elements.append(UIElement(ElementType.INPUT, label))
        
        # Extrair botões
        for match in re.finditer(button_pattern, desc_lower):
            label = match.group(1).strip()
            elements.append(UIElement(ElementType.BUTTON, label))
        
        # Extrair links
        for match in re.finditer(link_pattern, desc_lower):
            label = match.group(1).strip()
            elements.append(UIElement(ElementType.LINK, label))
        
        # Se não encontrou elementos, criar alguns padrão baseado no tipo de tela
        if not elements:
            elements = self._get_default_elements()
        
        return elements
    
    def _get_default_elements(self) -> List[UIElement]:
        """Retorna elementos padrão baseado no tipo de tela."""
        default_elements = {
            ScreenType.LOGIN: [
                UIElement(ElementType.INPUT, "Usuário", "username"),
                UIElement(ElementType.INPUT, "Senha", "password"),
                UIElement(ElementType.BUTTON, "Entrar"),
                UIElement(ElementType.LINK, "Esqueci a Senha"),
            ],
            ScreenType.REGISTRATION: [
                UIElement(ElementType.INPUT, "Nome", "name"),
                UIElement(ElementType.INPUT, "Email", "email"),
                UIElement(ElementType.INPUT, "Senha", "password"),
                UIElement(ElementType.INPUT, "Confirmar Senha", "confirm_password"),
                UIElement(ElementType.BUTTON, "Criar Conta"),
            ],
            ScreenType.CHECKOUT: [
                UIElement(ElementType.INPUT, "Endereço", "address"),
                UIElement(ElementType.INPUT, "Cidade", "city"),
                UIElement(ElementType.DROPDOWN, "Estado"),
                UIElement(ElementType.INPUT, "CEP", "zip"),
                UIElement(ElementType.DROPDOWN, "Método de Pagamento"),
                UIElement(ElementType.BUTTON, "Finalizar Compra"),
            ],
            ScreenType.FORM: [
                UIElement(ElementType.INPUT, "Campo 1"),
                UIElement(ElementType.INPUT, "Campo 2"),
                UIElement(ElementType.BUTTON, "Enviar"),
            ],
        }
        
        return default_elements.get(self.screen_type, [
            UIElement(ElementType.INPUT, "Campo Genérico"),
            UIElement(ElementType.BUTTON, "Ação"),
        ])
    
    def _extract_keywords(self) -> List[str]:
        """Extrai palavras-chave da descrição da tela."""
        # Remover palavras comuns
        stop_words = {
            "o", "a", "de", "da", "do", "e", "ou", "com", "para", "em",
            "que", "um", "uma", "os", "as", "dos", "das", "é", "são"
        }
        
        words = self.screen_description.lower().split()
        keywords = [word.strip(".,!?;:") for word in words if word.lower() not in stop_words and len(word) > 3]
        
        return list(set(keywords))[:10]  # Retornar top 10 únicos
    
    def _calculate_confidence(self) -> float:
        """Calcula a confiança da análise (0.0 a 1.0)."""
        confidence = 0.5  # Base
        
        # Aumentar confiança se o tipo de tela foi detectado com certeza
        if self.screen_type != ScreenType.UNKNOWN:
            confidence += 0.2
        
        # Aumentar confiança se elementos foram encontrados
        if len(self.elements) > 0:
            confidence += 0.2
        
        # Aumentar confiança se há muitas palavras-chave
        if len(self.keywords) > 5:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def to_dict(self) -> Dict:
        """Converte a análise para dicionário."""
        return {
            "screen_type": self.screen_type.value,
            "confidence": self.confidence,
            "elements": [elem.to_dict() for elem in self.elements],
            "keywords": self.keywords,
            "description": self.screen_description
        }


# ============================================
# CLASSE DE GERADOR DE CENÁRIOS
# ============================================

class ScenarioGenerator:
    """Gera cenários Gherkin baseado na análise de tela."""
    
    def __init__(self, screen_analysis: ScreenAnalysis):
        self.screen_analysis = screen_analysis
    
    def generate_scenario(self, user_intent: str) -> str:
        """Gera um cenário Gherkin completo."""
        feature_name = self._generate_feature_name()
        scenario_name = self._generate_scenario_name(user_intent)
        given_steps = self._generate_given_steps()
        when_steps = self._generate_when_steps()
        then_steps = self._generate_then_steps()
        
        gherkin = f"""Feature: {feature_name}
  Como um usuário
  Quero {user_intent}
  Para validar a funcionalidade

  Scenario: {scenario_name}
{given_steps}
{when_steps}
{then_steps}"""
        
        return gherkin
    
    def _generate_feature_name(self) -> str:
        """Gera o nome da feature."""
        feature_names = {
            ScreenType.LOGIN: "Autenticação de Usuário",
            ScreenType.REGISTRATION: "Registro de Novo Usuário",
            ScreenType.CHECKOUT: "Processo de Checkout",
            ScreenType.DASHBOARD: "Acesso ao Dashboard",
            ScreenType.FORM: "Preenchimento de Formulário",
            ScreenType.LIST: "Visualização de Lista",
        }
        
        return feature_names.get(self.screen_analysis.screen_type, "Funcionalidade da Aplicação")
    
    def _generate_scenario_name(self, user_intent: str) -> str:
        """Gera o nome do cenário."""
        # Limitar a 80 caracteres
        scenario = user_intent[:80]
        if len(user_intent) > 80:
            scenario += "..."
        return scenario
    
    def _generate_given_steps(self) -> str:
        """Gera os passos Given."""
        steps = []
        
        # Passo inicial baseado no tipo de tela
        given_map = {
            ScreenType.LOGIN: "Dado que estou na página de login",
            ScreenType.REGISTRATION: "Dado que estou na página de registro",
            ScreenType.CHECKOUT: "Dado que tenho itens no carrinho",
            ScreenType.DASHBOARD: "Dado que estou autenticado no sistema",
            ScreenType.FORM: "Dado que estou na página com o formulário",
        }
        
        steps.append(f"    {given_map.get(self.screen_analysis.screen_type, 'Dado que estou na aplicação')}")
        
        return "\n".join(steps)
    
    def _generate_when_steps(self) -> str:
        """Gera os passos When."""
        steps = []
        
        # Adicionar passos para cada elemento
        for element in self.screen_analysis.elements[:3]:  # Limitar a 3 elementos
            step = element.to_gherkin_step()
            steps.append(f"    {step}")
        
        return "\n".join(steps) if steps else "    Quando eu realizo uma ação"
    
    def _generate_then_steps(self) -> str:
        """Gera os passos Then."""
        steps = []
        
        # Passo final baseado no tipo de tela
        then_map = {
            ScreenType.LOGIN: "Então devo ser redirecionado para o dashboard",
            ScreenType.REGISTRATION: "Então devo receber uma mensagem de sucesso",
            ScreenType.CHECKOUT: "Então o pedido deve ser confirmado",
            ScreenType.DASHBOARD: "Então devo visualizar meus dados",
            ScreenType.FORM: "Então o formulário deve ser enviado com sucesso",
        }
        
        steps.append(f"    {then_map.get(self.screen_analysis.screen_type, 'Então a ação deve ser bem-sucedida')}")
        
        return "\n".join(steps)


# ============================================
# MOTOR DE ML (SIMULADO)
# ============================================

class MLEngine:
    """Motor de Machine Learning para análise e geração de cenários."""
    
    def analyze_screen(self, screen_description: str) -> ScreenAnalysis:
        """Analisa uma tela capturada."""
        return ScreenAnalysis(screen_description)
    
    def generate_gherkin(self, screen_analysis: ScreenAnalysis, user_intent: str) -> str:
        """Gera um cenário Gherkin."""
        generator = ScenarioGenerator(screen_analysis)
        return generator.generate_scenario(user_intent)
    
    def predict_next_scenarios(self, screen_analysis: ScreenAnalysis) -> List[str]:
        """Prediz possíveis cenários futuros baseado na análise."""
        scenarios = []
        
        # Baseado no tipo de tela, sugerir próximos cenários
        next_scenarios = {
            ScreenType.LOGIN: [
                "Validação de credenciais inválidas",
                "Recuperação de senha",
                "Login com dois fatores"
            ],
            ScreenType.REGISTRATION: [
                "Validação de email duplicado",
                "Validação de senha fraca",
                "Confirmação de email"
            ],
            ScreenType.CHECKOUT: [
                "Validação de endereço",
                "Processamento de pagamento",
                "Confirmação de pedido"
            ],
        }
        
        return next_scenarios.get(self.screen_analysis.screen_type, [])


# ============================================
# INSTÂNCIA GLOBAL
# ============================================

ml_engine = MLEngine()


if __name__ == "__main__":
    # Teste do módulo
    print("=== Teste do Motor de ML ===\n")
    
    # Analisar tela
    screen_desc = "Tela de Login com campos 'Usuário', 'Senha', botão 'Entrar' e link 'Esqueci a Senha'."
    analysis = ml_engine.analyze_screen(screen_desc)
    
    print(f"Análise da Tela:")
    print(f"  Tipo: {analysis.screen_type.value}")
    print(f"  Confiança: {analysis.confidence:.2%}")
    print(f"  Elementos: {len(analysis.elements)}")
    print(f"  Palavras-chave: {analysis.keywords}\n")
    
    # Gerar Gherkin
    gherkin = ml_engine.generate_gherkin(analysis, "fazer login com sucesso")
    print(f"Cenário Gherkin Gerado:\n{gherkin}")

