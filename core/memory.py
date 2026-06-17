"""
Memory system for the Personal AI OS.
Stores recent interaction history and provides context for agent calls.
"""


class Memory:
    """Stores the last N interaction pairs (input, output) for context."""

    def __init__(self, max_items: int = 10):
        self.history: list[tuple[str, str]] = []
        self.max_items = max_items

    def add(self, input_text: str, output: str) -> None:
        self.history.append((input_text, output))
        if len(self.history) > self.max_items:
            self.history = self.history[-self.max_items :]

    def get_context(self) -> list[tuple[str, str]]:
        """Return the last 5 interaction pairs."""
        return self.history[-5:]

    def format_context(self) -> str:
        """Return a formatted string of the recent conversation history."""
        context = self.get_context()
        if not context:
            return "No previous context."
        lines = []
        for i, (inp, out) in enumerate(context, 1):
            lines.append(f"[Interaction {i}]\nUser: {inp}\nSystem: {out}")
        return "\n\n".join(lines)

    def clear(self) -> None:
        self.history = []
