from core.token_counter import TokenCounter


class HistoryWindow:

    @classmethod
    def build(
        cls,
        history: list[dict],
        context_window: int,
        reserved_tokens: int,
        summary: str | None = None
    ) -> list[dict]:

        # Reserve space for response generation
        history_budget = max(
            context_window - reserved_tokens - 500,
            1000
        )

        selected = []

        used_tokens = 0

        # Reserve tokens for summary if present
        if summary:

            summary_tokens = TokenCounter.estimate(summary)

            history_budget -= summary_tokens

            history_budget = max(history_budget, 500)

        # Keep newest messages first
        for message in reversed(history):

            tokens = TokenCounter.estimate(
                message.get("content", "")
            )

            if used_tokens + tokens > history_budget:
                break

            selected.append(message)

            used_tokens += tokens

        selected.reverse()

        # Add summary as the first system message
        if summary:

            selected.insert(
                0,
                {
                    "role": "system",
                    "content": (
                        "Conversation Summary:\n\n"
                        f"{summary}\n\n"
                        "Use this summary as long-term context. "
                        "If the detailed history conflicts with the summary, "
                        "prefer the detailed history."
                    )
                }
            )

        return selected