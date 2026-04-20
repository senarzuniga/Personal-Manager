"""
Manager Agent — Chief-of-Staff layer.

Receives any user input, interprets priorities, balances life vs work,
and returns a structured output before any specialised agent runs.
"""
from __future__ import annotations

import os
from openai import OpenAI
from core.context import get_user_context
from core.memory import Memory


MANAGER_SYSTEM_PROMPT = """
You are a Chief-of-Staff and personal executive advisor.
Your role is to act as the top-level intelligence of a Personal AI Operating System.

Your responsibilities:
1. Interpret the user's intent and clarify the true underlying need.
2. Decide strategic priorities for the day/week/month.
3. Balance four life dimensions: Work, Family, Health, Personal Growth.
4. Guide long-term professional strategy.
5. Detect overwhelm, misalignment, or hidden risks.
6. Always think in terms of repeated games and long-term compounding.

Your output MUST follow this exact structure:

## 1. Situation Overview
(Brief synthesis of what the user is dealing with right now)

## 2. Strategic Priority
(The single most important thing to act on, and why)

## 3. Trade-offs
(What must be de-prioritised or accepted as a cost today)

## 4. Plan (Day / Week)
(Concrete, time-aware schedule or action steps)

## 5. Strategic Advice
(Long-term perspective — compounding, positioning, relationships)

## 6. Life Balance Check
(Work / Family / Health / Growth — what needs attention)

## 7. Manager Feedback
(Direct, honest coaching remark — no flattery)

Rules:
- Never give generic advice.
- Always reference the user's specific context.
- Be direct, structured, and actionable.
- Think like a seasoned executive, not a chatbot.
"""


class ManagerAgent:
    """Top-level Chief-of-Staff agent."""

    name = "manager"

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def run(self, user_input: str, memory: Memory | None = None) -> str:
        """
        Analyse the user input and return a full Chief-of-Staff response.

        Returns
        -------
        str
            Structured manager response covering all 7 sections.
        """
        system_content = f"{MANAGER_SYSTEM_PROMPT}\n\n{get_user_context()}"

        if memory:
            ctx = memory.format_context()
            if ctx and ctx != "No previous context.":
                system_content += f"\n\n=== RECENT HISTORY ===\n{ctx}"

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_input},
        ]

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    def interpret_intent(self, user_input: str) -> dict:
        """
        Quick pass to extract intent and routing hints.

        Returns a dict with keys:
          - intent: str
          - agents: list[str]   (e.g. ["learning", "finance"])
          - priority: str
        """
        prompt = (
            "Given the following user message, return a JSON object with:\n"
            '- "intent": one-sentence summary of what the user wants\n'
            '- "agents": list of specialised agents to involve (choose from: '
            '"learning", "finance", "consulting", "manager")\n'
            '- "priority": "high" | "medium" | "low"\n\n'
            f"User message: {user_input}\n\n"
            "Respond ONLY with valid JSON, no markdown fences."
        )

        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": get_user_context()},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        import json

        raw = response.choices[0].message.content.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"intent": user_input, "agents": ["manager"], "priority": "medium"}
