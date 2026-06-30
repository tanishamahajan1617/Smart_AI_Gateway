from sqlalchemy.orm import Session

from models.conversation_summary import ConversationSummary
from models.message_model import Message

from schema.ask_schema import AskRequest


class SummaryService:
    """
    Handles conversation summarization.

    Responsibilities:
    - Fetch existing summary
    - Decide when to regenerate
    - Generate summary using the current provider
    - Save / update summary
    """

    SUMMARY_AFTER_MESSAGES = 50
    SUMMARY_UPDATE_INTERVAL = 25

    # ======================================================
    # PUBLIC
    # ======================================================

    @classmethod
    def get_summary(
        cls,
        db: Session,
        session_id: str
    ) -> str | None:
        """
        Return stored summary if available.
        """

        record = (
            db.query(ConversationSummary)
            .filter(
                ConversationSummary.session_id == session_id
            )
            .first()
        )

        if record is None:
            return None

        return record.summary

    @classmethod
    def update_summary(
        cls,
        db: Session,
        session_id: str,
        provider
    ) -> None:
        """
        Generate a new summary if required.
        """

        if not cls._should_update(
            db=db,
            session_id=session_id
        ):
            return

        messages = cls._load_messages(
            db=db,
            session_id=session_id
        )

        summary = cls._generate_summary(
            provider=provider,
            messages=messages
        )

        cls._save_summary(
            db=db,
            session_id=session_id,
            summary=summary,
            message_count=len(messages)
        )

    # ======================================================
    # PRIVATE
    # ======================================================

    @classmethod
    def _should_update(
        cls,
        db: Session,
        session_id: str
    ) -> bool:
        """
        Decide whether summary should be regenerated.
        """

        message_count = (
            db.query(Message)
            .filter(
                Message.session_id == session_id
            )
            .count()
        )

        record = (
            db.query(ConversationSummary)
            .filter(
                ConversationSummary.session_id == session_id
            )
            .first()
        )

        # Never summarized before
        if record is None:

            return (
                message_count >=
                cls.SUMMARY_AFTER_MESSAGES
            )

        # Update every N new messages
        return (
            message_count -
            record.message_count
            >=
            cls.SUMMARY_UPDATE_INTERVAL
        )

    @staticmethod
    def _load_messages(
        db: Session,
        session_id: str
    ) -> list[Message]:
        """
        Load the complete conversation.
        """

        return (
            db.query(Message)
            .filter(
                Message.session_id == session_id
            )
            .order_by(
                Message.created_at.asc()
            )
            .all()
        )

    @staticmethod
    def _build_prompt() -> str:
        """
        Prompt used to summarize conversations.
        """

        return """
You are an AI conversation summarizer.

Summarize the following conversation while preserving:

- User preferences
- Personal information shared by the user
- Important facts
- Important decisions
- Pending tasks
- Long-term context

Ignore greetings and small talk.

Maximum length: 300 words.
"""

    @classmethod
    def _generate_summary(
        cls,
        provider,
        messages: list[Message]
    ) -> str:
        """
        Generate conversation summary using
        the currently selected provider.
        """

        history = []

        for message in messages:

            history.append(
                {
                    "role": message.role,
                    "content": message.content
                }
            )

        request = AskRequest(
            message=cls._build_prompt(),
            temperature=0.2,
            max_tokens=300
        )

        response = provider.generate(
            request=request,
            history=history
        )

        return response.content

    @staticmethod
    def _save_summary(
        db: Session,
        session_id: str,
        summary: str,
        message_count: int
    ) -> None:
        """
        Insert or update conversation summary.
        """

        record = (
            db.query(ConversationSummary)
            .filter(
                ConversationSummary.session_id == session_id
            )
            .first()
        )

        if record is None:

            record = ConversationSummary(
                session_id=session_id,
                summary=summary,
                message_count=message_count
            )

            db.add(record)

        else:

            record.summary = summary
            record.message_count = message_count