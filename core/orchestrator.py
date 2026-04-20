"""
Orchestrator — COO execution layer.

Flow:
  1. Receive user input + mode
  2. Ask the Manager Agent for intent interpretation
  3. Route to specialised agents
  4. Combine outputs into a final response
"""
from __future__ import annotations

from core.memory import Memory
from manager.manager_agent import ManagerAgent
from agents.learning.learning_agent import LearningAgent
from agents.finance.finance_agent import FinanceAgent
from agents.consulting.consulting_agent import ConsultingAgent


class Orchestrator:
    """
    Central execution router.

    Parameters
    ----------
    manager : ManagerAgent
        The Chief-of-Staff agent.
    agents : dict[str, object]
        Registry of specialised agents keyed by name.
    memory : Memory
        Shared conversation memory.
    """

    def __init__(
        self,
        manager: ManagerAgent,
        agents: dict,
        memory: Memory,
    ):
        self.manager = manager
        self.agents = agents
        self.memory = memory

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def execute(self, user_input: str, mode: str) -> str:
        """
        Process a user message end-to-end.

        Parameters
        ----------
        user_input : str
            The user's message.
        mode : str
            One of: "manager", "learning", "finance", "consulting".

        Returns
        -------
        str
            Final combined response.
        """
        # Step 1: Manager always evaluates first
        manager_response = self.manager.run(user_input, self.memory)

        # Step 2: Determine which agents to involve
        if mode == "manager":
            # Manager-only mode: return manager output directly
            self.memory.add(user_input, manager_response)
            return manager_response

        # Step 3: Route to the selected specialised agent
        agent_response = self._route(user_input, mode)

        # Step 4: Combine outputs
        combined = self._combine(manager_response, agent_response, mode)

        # Step 5: Store in memory
        self.memory.add(user_input, combined)

        return combined

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _route(self, user_input: str, mode: str) -> str:
        """Delegate to the appropriate specialised agent."""
        agent = self.agents.get(mode)
        if agent is None:
            return f"[No agent registered for mode '{mode}']"
        return agent.run(user_input, self.memory)

    def _combine(
        self, manager_response: str, agent_response: str, mode: str
    ) -> str:
        """Merge manager and specialised agent outputs."""
        separator = "\n\n" + "─" * 60 + "\n\n"
        return (
            f"## 🧠 Chief-of-Staff Assessment\n\n{manager_response}"
            f"{separator}"
            f"## 🔧 {mode.capitalize()} Specialist\n\n{agent_response}"
        )


# ------------------------------------------------------------------
# Factory helper
# ------------------------------------------------------------------

def build_orchestrator() -> Orchestrator:
    """
    Instantiate the full system with all agents and shared memory.

    Returns
    -------
    Orchestrator
        Ready-to-use orchestrator.
    """
    memory = Memory()
    manager = ManagerAgent()

    agents = {
        "learning": LearningAgent(),
        "finance": FinanceAgent(),
        "consulting": ConsultingAgent(),
    }

    return Orchestrator(manager=manager, agents=agents, memory=memory)
