"""
Módulo de Billing e Gerenciamento de Créditos
Nebula Agent v6.0
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

# ============================================
# ENUMS E CONSTANTES
# ============================================

class PlanType(str, Enum):
    """Tipos de planos disponíveis."""
    LITE = "lite"
    PLUS = "plus"
    PRO = "pro"
    ULTRA = "ultra"


class ActionType(str, Enum):
    """Tipos de ações que consomem créditos."""
    GENERATE_GHERKIN = "generate_gherkin"
    RUN_TEST = "run_test"
    ANALYZE_SCREEN = "analyze_screen"
    CREATE_SCENARIO = "create_scenario"
    EXPORT_REPORT = "export_report"


# Configuração de Planos
PLAN_CONFIG = {
    PlanType.LITE: {
        "name": "Nebula Lite",
        "credits": 100,
        "monthly_limit": 100,
        "features": {
            "gherkin_generation": True,
            "screen_analysis": True,
            "scrumban_board": True,
            "export_report": False,
            "api_access": False,
        },
        "price": 0.0,  # Gratuito
    },
    PlanType.PLUS: {
        "name": "Nebula Plus",
        "credits": 500,
        "monthly_limit": 500,
        "features": {
            "gherkin_generation": True,
            "screen_analysis": True,
            "scrumban_board": True,
            "export_report": True,
            "api_access": False,
        },
        "price": 29.99,
    },
    PlanType.PRO: {
        "name": "Nebula Pro",
        "credits": 2000,
        "monthly_limit": 2000,
        "features": {
            "gherkin_generation": True,
            "screen_analysis": True,
            "scrumban_board": True,
            "export_report": True,
            "api_access": True,
        },
        "price": 99.99,
    },
    PlanType.ULTRA: {
        "name": "Nebula Ultra",
        "credits": float("inf"),
        "monthly_limit": float("inf"),
        "features": {
            "gherkin_generation": True,
            "screen_analysis": True,
            "scrumban_board": True,
            "export_report": True,
            "api_access": True,
        },
        "price": 299.99,
    },
}

# Custo de Ações em Créditos
ACTION_COSTS = {
    ActionType.GENERATE_GHERKIN: 5,
    ActionType.RUN_TEST: 10,
    ActionType.ANALYZE_SCREEN: 3,
    ActionType.CREATE_SCENARIO: 8,
    ActionType.EXPORT_REPORT: 15,
}


# ============================================
# CLASSE DE USUÁRIO COM CRÉDITOS
# ============================================

class User:
    """Representa um usuário com gerenciamento de créditos e plano."""
    
    def __init__(
        self,
        user_id: str,
        plan: PlanType = PlanType.LITE,
        initial_credits: Optional[int] = None
    ):
        self.user_id = user_id
        self.plan = plan
        self.credits = initial_credits or PLAN_CONFIG[plan]["credits"]
        self.max_credits = PLAN_CONFIG[plan]["credits"]
        self.created_at = datetime.now()
        self.last_reset = datetime.now()
        self.usage_history: List[Dict] = []
    
    def has_feature(self, feature: str) -> bool:
        """Verifica se o usuário tem acesso a uma feature."""
        return PLAN_CONFIG[self.plan]["features"].get(feature, False)
    
    def can_perform_action(self, action: ActionType) -> bool:
        """Verifica se o usuário pode realizar uma ação (tem créditos suficientes)."""
        cost = ACTION_COSTS.get(action, 0)
        return self.credits >= cost
    
    def perform_action(self, action: ActionType) -> bool:
        """
        Realiza uma ação e deduz os créditos necessários.
        Retorna True se bem-sucedido, False caso contrário.
        """
        if not self.can_perform_action(action):
            return False
        
        cost = ACTION_COSTS.get(action, 0)
        self.credits -= cost
        
        # Registrar no histórico
        self.usage_history.append({
            "action": action.value,
            "cost": cost,
            "timestamp": datetime.now().isoformat(),
            "remaining_credits": self.credits
        })
        
        return True
    
    def add_credits(self, amount: int) -> None:
        """Adiciona créditos ao usuário (até o limite do plano)."""
        self.credits = min(self.credits + amount, self.max_credits)
    
    def upgrade_plan(self, new_plan: PlanType) -> None:
        """Faz upgrade para um novo plano."""
        old_plan = self.plan
        self.plan = new_plan
        self.max_credits = PLAN_CONFIG[new_plan]["credits"]
        
        # Se o novo plano tem mais créditos, adicionar a diferença
        if self.max_credits > self.credits:
            self.credits = self.max_credits
        
        print(f"✅ Usuário {self.user_id} fez upgrade de {old_plan.value} para {new_plan.value}")
    
    def reset_monthly_credits(self) -> None:
        """Reseta os créditos mensais (simulação de renovação mensal)."""
        self.credits = self.max_credits
        self.last_reset = datetime.now()
        print(f"✅ Créditos mensais resetados para {self.user_id}")
    
    def get_status(self) -> Dict:
        """Retorna o status atual do usuário."""
        return {
            "user_id": self.user_id,
            "plan": self.plan.value,
            "plan_name": PLAN_CONFIG[self.plan]["name"],
            "credits": self.credits,
            "max_credits": self.max_credits,
            "usage_count": len(self.usage_history),
            "created_at": self.created_at.isoformat(),
            "features": PLAN_CONFIG[self.plan]["features"],
        }


# ============================================
# GERENCIADOR DE USUÁRIOS (SIMULADO)
# ============================================

class BillingManager:
    """Gerencia usuários e seus créditos."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
    
    def create_user(
        self,
        user_id: str,
        plan: PlanType = PlanType.LITE
    ) -> User:
        """Cria um novo usuário."""
        if user_id in self.users:
            return self.users[user_id]
        
        user = User(user_id, plan)
        self.users[user_id] = user
        print(f"✅ Usuário criado: {user_id} (Plano: {plan.value})")
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Obtém um usuário existente."""
        return self.users.get(user_id)
    
    def perform_action(self, user_id: str, action: ActionType) -> Dict:
        """
        Realiza uma ação para um usuário.
        Retorna um dicionário com o resultado.
        """
        user = self.get_user(user_id)
        if not user:
            return {
                "success": False,
                "message": "Usuário não encontrado",
                "credits_remaining": 0
            }
        
        # Verificar se o usuário tem a feature
        feature_map = {
            ActionType.GENERATE_GHERKIN: "gherkin_generation",
            ActionType.ANALYZE_SCREEN: "screen_analysis",
            ActionType.EXPORT_REPORT: "export_report",
        }
        
        feature = feature_map.get(action)
        if feature and not user.has_feature(feature):
            return {
                "success": False,
                "message": f"Feature '{feature}' não disponível no plano {user.plan.value}",
                "credits_remaining": user.credits
            }
        
        # Realizar a ação
        success = user.perform_action(action)
        
        if success:
            return {
                "success": True,
                "message": f"Ação '{action.value}' realizada com sucesso",
                "credits_remaining": user.credits,
                "cost": ACTION_COSTS.get(action, 0)
            }
        else:
            cost = ACTION_COSTS.get(action, 0)
            return {
                "success": False,
                "message": f"Créditos insuficientes. Necessário: {cost}, Disponível: {user.credits}",
                "credits_remaining": user.credits,
                "cost": cost
            }
    
    def get_user_status(self, user_id: str) -> Optional[Dict]:
        """Obtém o status de um usuário."""
        user = self.get_user(user_id)
        if not user:
            return None
        return user.get_status()
    
    def upgrade_user(self, user_id: str, new_plan: PlanType) -> Dict:
        """Faz upgrade de um usuário."""
        user = self.get_user(user_id)
        if not user:
            return {"success": False, "message": "Usuário não encontrado"}
        
        user.upgrade_plan(new_plan)
        return {
            "success": True,
            "message": f"Upgrade realizado para {new_plan.value}",
            "user_status": user.get_status()
        }


# ============================================
# INSTÂNCIA GLOBAL (SIMULADA)
# ============================================

# Em produção, isso seria um banco de dados real
billing_manager = BillingManager()

# Criar um usuário padrão para testes
DEFAULT_USER_ID = "default_user"
billing_manager.create_user(DEFAULT_USER_ID, PlanType.LITE)


# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def get_plan_info(plan: PlanType) -> Dict:
    """Retorna informações sobre um plano."""
    return PLAN_CONFIG[plan]


def get_all_plans() -> Dict[str, Dict]:
    """Retorna informações sobre todos os planos."""
    return {
        plan.value: PLAN_CONFIG[plan]
        for plan in PlanType
    }


if __name__ == "__main__":
    # Teste do módulo
    print("=== Teste do Módulo Billing ===\n")
    
    # Criar usuário
    user = billing_manager.create_user("test_user", PlanType.LITE)
    print(f"Status inicial: {user.get_status()}\n")
    
    # Realizar ações
    result = billing_manager.perform_action("test_user", ActionType.GENERATE_GHERKIN)
    print(f"Resultado: {result}\n")
    
    # Fazer upgrade
    upgrade_result = billing_manager.upgrade_user("test_user", PlanType.PLUS)
    print(f"Upgrade: {upgrade_result}\n")
    
    # Status final
    print(f"Status final: {billing_manager.get_user_status('test_user')}")

