"""
Módulo de Gerenciamento do Board Scrumban
Nebula Agent v6.0
"""

from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import uuid


# ============================================
# ENUMS E CONSTANTES
# ============================================

class TaskStatus(str, Enum):
    """Status possíveis de uma tarefa no Scrumban."""
    TODO = "todo"
    BLOCKED = "blocked"
    IN_PROGRESS = "inprogress"
    DONE = "done"


class TaskPriority(str, Enum):
    """Prioridades de tarefas."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================
# CLASSE DE TAREFA
# ============================================

class Task:
    """Representa uma tarefa no board Scrumban."""
    
    def __init__(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        status: TaskStatus = TaskStatus.TODO,
        assignee: str = ""
    ):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.assignee = assignee
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.comments: List[Dict] = []
        self.tags: List[str] = []
    
    def update_status(self, new_status: TaskStatus) -> None:
        """Atualiza o status da tarefa."""
        self.status = new_status
        self.updated_at = datetime.now()
        
        if new_status == TaskStatus.DONE:
            self.completed_at = datetime.now()
    
    def add_comment(self, author: str, text: str) -> None:
        """Adiciona um comentário à tarefa."""
        self.comments.append({
            "author": author,
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()
    
    def add_tag(self, tag: str) -> None:
        """Adiciona uma tag à tarefa."""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def to_dict(self) -> Dict:
        """Converte a tarefa para um dicionário."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "assignee": self.assignee,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "comments": self.comments,
            "tags": self.tags
        }


# ============================================
# CLASSE DO BOARD SCRUMBAN
# ============================================

class ScrumbanBoard:
    """Representa o board Scrumban com gerenciamento de tarefas."""
    
    def __init__(self, board_id: str = "default"):
        self.board_id = board_id
        self.tasks: Dict[str, Task] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def create_task(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        assignee: str = ""
    ) -> Task:
        """Cria uma nova tarefa no board."""
        task = Task(
            title=title,
            description=description,
            priority=priority,
            status=TaskStatus.TODO,
            assignee=assignee
        )
        self.tasks[task.id] = task
        self.updated_at = datetime.now()
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Obtém uma tarefa pelo ID."""
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, new_status: TaskStatus) -> bool:
        """Atualiza o status de uma tarefa."""
        task = self.get_task(task_id)
        if task:
            task.update_status(new_status)
            self.updated_at = datetime.now()
            return True
        return False
    
    def delete_task(self, task_id: str) -> bool:
        """Deleta uma tarefa do board."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.updated_at = datetime.now()
            return True
        return False
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Retorna todas as tarefas com um status específico."""
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        """Retorna todas as tarefas com uma prioridade específica."""
        return [task for task in self.tasks.values() if task.priority == priority]
    
    def get_tasks_by_assignee(self, assignee: str) -> List[Task]:
        """Retorna todas as tarefas atribuídas a um usuário."""
        return [task for task in self.tasks.values() if task.assignee == assignee]
    
    def get_board_stats(self) -> Dict:
        """Retorna estatísticas do board."""
        total_tasks = len(self.tasks)
        completed_tasks = len(self.get_tasks_by_status(TaskStatus.DONE))
        in_progress = len(self.get_tasks_by_status(TaskStatus.IN_PROGRESS))
        blocked = len(self.get_tasks_by_status(TaskStatus.BLOCKED))
        todo = len(self.get_tasks_by_status(TaskStatus.TODO))
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress": in_progress,
            "blocked": blocked,
            "todo": todo,
            "completion_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }
    
    def get_board_data(self) -> Dict:
        """Retorna os dados completos do board organizados por status."""
        return {
            "board_id": self.board_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "stats": self.get_board_stats(),
            "columns": {
                TaskStatus.TODO.value: [task.to_dict() for task in self.get_tasks_by_status(TaskStatus.TODO)],
                TaskStatus.BLOCKED.value: [task.to_dict() for task in self.get_tasks_by_status(TaskStatus.BLOCKED)],
                TaskStatus.IN_PROGRESS.value: [task.to_dict() for task in self.get_tasks_by_status(TaskStatus.IN_PROGRESS)],
                TaskStatus.DONE.value: [task.to_dict() for task in self.get_tasks_by_status(TaskStatus.DONE)],
            }
        }


# ============================================
# GERENCIADOR DE BOARDS (SIMULADO)
# ============================================

class ScrumbanManager:
    """Gerencia múltiplos boards Scrumban."""
    
    def __init__(self):
        self.boards: Dict[str, ScrumbanBoard] = {}
    
    def create_board(self, board_id: str) -> ScrumbanBoard:
        """Cria um novo board."""
        if board_id in self.boards:
            return self.boards[board_id]
        
        board = ScrumbanBoard(board_id)
        self.boards[board_id] = board
        print(f"✅ Board criado: {board_id}")
        return board
    
    def get_board(self, board_id: str) -> Optional[ScrumbanBoard]:
        """Obtém um board existente."""
        return self.boards.get(board_id)
    
    def create_task(
        self,
        board_id: str,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        assignee: str = ""
    ) -> Optional[Dict]:
        """Cria uma nova tarefa em um board."""
        board = self.get_board(board_id)
        if not board:
            board = self.create_board(board_id)
        
        task = board.create_task(title, description, priority, assignee)
        return task.to_dict()
    
    def update_task_status(self, board_id: str, task_id: str, new_status: TaskStatus) -> bool:
        """Atualiza o status de uma tarefa."""
        board = self.get_board(board_id)
        if board:
            return board.update_task_status(task_id, new_status)
        return False
    
    def get_board_data(self, board_id: str) -> Optional[Dict]:
        """Obtém os dados completos de um board."""
        board = self.get_board(board_id)
        if board:
            return board.get_board_data()
        return None
    
    def get_board_stats(self, board_id: str) -> Optional[Dict]:
        """Obtém as estatísticas de um board."""
        board = self.get_board(board_id)
        if board:
            return board.get_board_stats()
        return None


# ============================================
# INSTÂNCIA GLOBAL (SIMULADA)
# ============================================

# Em produção, isso seria um banco de dados real
scrumban_manager = ScrumbanManager()

# Criar um board padrão para testes
DEFAULT_BOARD_ID = "default"
scrumban_manager.create_board(DEFAULT_BOARD_ID)


# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def create_task_from_message(board_id: str, message: str) -> Optional[Dict]:
    """
    Cria uma tarefa a partir de uma mensagem do usuário.
    Útil para integração com o agente de chat.
    """
    # Extrair informações da mensagem (simples)
    title = message[:100]  # Primeiros 100 caracteres
    description = message
    priority = TaskPriority.MEDIUM
    
    # Detectar prioridade a partir de palavras-chave
    if any(word in message.lower() for word in ["urgente", "crítico", "importante"]):
        priority = TaskPriority.HIGH
    elif any(word in message.lower() for word in ["baixa", "depois"]):
        priority = TaskPriority.LOW
    
    return scrumban_manager.create_task(
        board_id=board_id,
        title=title,
        description=description,
        priority=priority,
        assignee="Nebula Agent"
    )


if __name__ == "__main__":
    # Teste do módulo
    print("=== Teste do Módulo Scrumban ===\n")
    
    # Criar board
    board = scrumban_manager.create_board("test_board")
    
    # Criar tarefas
    task1 = board.create_task(
        "Gerar cenário Gherkin para login",
        "Análise de tela de login",
        TaskPriority.HIGH,
        "Nebula Agent"
    )
    
    task2 = board.create_task(
        "Testar fluxo de checkout",
        "Validação do checkout",
        TaskPriority.MEDIUM,
        "Nebula Agent"
    )
    
    print(f"Tarefa 1 criada: {task1.title}\n")
    print(f"Tarefa 2 criada: {task2.title}\n")
    
    # Atualizar status
    board.update_task_status(task1.id, TaskStatus.IN_PROGRESS)
    print(f"Status da tarefa 1 atualizado para: {TaskStatus.IN_PROGRESS.value}\n")
    
    # Estatísticas
    stats = board.get_board_stats()
    print(f"Estatísticas do board: {stats}\n")
    
    # Dados completos
    board_data = board.get_board_data()
    print(f"Dados do board: {board_data}")

