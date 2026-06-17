"""
Base agent — all specialised agents inherit from this class.
"""
from __future__ import annotations

import os
from openai import OpenAI
from core.context import get_user_context
from core.memory import Memory


class BaseAgent:
    """
    Abstract base for every specialised agent.

    Subclasses must override:
      - SYSTEM_PROMPT  (class-level string)
      - name           (class-level string)
    """

    name: str = "base"
    SYSTEM_PROMPT: str = "You are a helpful assistant."

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self, user_input: str, memory: Memory | None = None) -> str:
        """
        Execute the agent with the given user input.

        Parameters
        ----------
        user_input : str
            The user's message / task.
        memory : Memory, optional
            Shared memory object for conversation history.

        Returns
        -------
        str
            The agent's response.
        """
        messages = self._build_messages(user_input, memory)
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_messages(
        self, user_input: str, memory: Memory | None
    ) -> list[dict]:
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\n{get_user_context()}"
        )
        if memory:
            ctx = memory.format_context()
            if ctx and ctx != "No previous context.":
                system_content += f"\n\n=== RECENT HISTORY ===\n{ctx}"

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_input},
        ]
