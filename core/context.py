"""
Context module — holds static user profile and strategic context
that is injected into every agent call.
"""

USER_PROFILE = {
    "work_setup": "Works from home",
    "family": "Married, 3 children (ages 12, 12, 15)",
    "pets": "Has a dog",
    "health_goal": "Daily sport / physical activity",
    "professional_goal": "Building a consulting business",
}

PROFESSIONAL_STRATEGY = {
    "approach": "Repeated games — focus on long-term clients to maximise lifetime value",
    "switching_costs": "Increase switching costs so clients depend on the system, not just the person",
    "differentiation": "Become hard to compare: own language, proprietary frameworks, unique positioning",
    "target_market": "Industrial companies with €50M–€500M revenue",
    "flagship_offer": "Industrial Revenue Architecture Program",
}


def get_user_context() -> str:
    """Return a formatted string of the user profile for prompt injection."""
    profile_lines = "\n".join(f"- {k}: {v}" for k, v in USER_PROFILE.items())
    strategy_lines = "\n".join(
        f"- {k}: {v}" for k, v in PROFESSIONAL_STRATEGY.items()
    )
    return (
        "=== USER PROFILE ===\n"
        f"{profile_lines}\n\n"
        "=== PROFESSIONAL STRATEGY ===\n"
        f"{strategy_lines}"
    )
