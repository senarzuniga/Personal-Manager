"""
Finance Agent — personal + business finance, forecasting, risk.
"""
from __future__ import annotations

import os
from openai import OpenAI
from core.context import get_user_context
from core.memory import Memory


PERSONAL_FINANCE_PROMPT = """
You are a Personal Finance Advisor specialising in entrepreneurs who work from home
and are building a consulting business.

Focus areas:
- Monthly cash-flow analysis
- Expense tracking and categorisation
- Emergency fund management
- Family budget optimisation
- Tax optimisation for freelancers / consultants

Rules:
- If the user lacks data, ask targeted questions (one at a time) to collect it
- Work with partial information — always provide a partial answer + clarification request
- Be specific and numerical when possible
- Suggest concrete, ranked action steps
"""

BUSINESS_FINANCE_PROMPT = """
You are a Business Finance Advisor for a solo consultant building a firm.

Focus areas:
- Revenue forecasting
- Pricing and offer structuring
- Business cash-flow and runway
- Investment in growth (time, tools, marketing)
- Risk management for a one-person consulting firm

Rules:
- Think in quarters and years, not just months
- Connect financial decisions to strategic positioning
- Flag dependencies and concentration risks (e.g. single client)
- Always provide a next action and a decision framework
"""

FORECASTING_PROMPT = """
You are a Financial Forecasting specialist.

Capabilities:
- Build simple 3-6 month cash-flow models from partial data
- Identify break-even points
- Scenario analysis: base / optimistic / pessimistic
- Highlight key levers and sensitivities

Output format:
- Scenario table (if data allows)
- Key assumptions stated explicitly
- Recommended actions to improve the forecast
"""

RISK_PROMPT = """
You are a Risk Management advisor for a solo entrepreneur.

Focus:
- Income concentration risk
- Family financial exposure
- Opportunity cost analysis
- Mitigation strategies (diversification, contracts, retainers)

Always:
- Quantify risk where possible
- Prioritise by impact × probability
- Suggest pragmatic hedges, not theoretical ones
"""


class FinanceAgent:
    """
    Finance agent that routes to the appropriate sub-agent based on context.

    Sub-agents:
      personal   — personal household finance
      business   — consulting business finance
      forecast   — cash-flow forecasting
      risk       — risk management
    """

    name = "finance"

    _SUB_PROMPTS = {
        "personal": PERSONAL_FINANCE_PROMPT,
        "business": BUSINESS_FINANCE_PROMPT,
        "forecast": FORECASTING_PROMPT,
        "risk": RISK_PROMPT,
    }

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # ------------------------------------------------------------------

    def run(self, user_input: str, memory: Memory | None = None) -> str:
        """
        Route the request to the most relevant finance sub-agent and
        consolidate outputs.
        """
        sub_agent = self._route(user_input)
        system_prompt = self._SUB_PROMPTS[sub_agent]

        system_content = f"{system_prompt}\n\n{get_user_context()}"
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
            temperature=0.5,
        )
        result = response.choices[0].message.content.strip()
        return f"**[Finance / {sub_agent.capitalize()} Advisor]**\n\n{result}"

    # ------------------------------------------------------------------

    def _route(self, user_input: str) -> str:
        """Determine which sub-agent to use based on keywords."""
        text = user_input.lower()
        if any(w in text for w in ["forecast", "predict", "project", "scenario", "runway"]):
            return "forecast"
        if any(w in text for w in ["risk", "danger", "exposure", "dependent", "concentration"]):
            return "risk"
        if any(w in text for w in ["business", "revenue", "invoice", "client", "pricing", "offer"]):
            return "business"
        return "personal"
