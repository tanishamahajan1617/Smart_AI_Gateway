from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from core.exceptions import (
    ConversationNotFoundError,
    NoUsableAPIKeysError,
    RouterException
)
from core.exceptions import ProviderException
from service.history_window import HistoryWindow
from models.message_model import Message
from models.session_model import Session as ChatSession
from models.gatewayLog import Conversation
from schema.ask_schema import AskResponse,Usage,AskRequest
from schema.message_schema import MessageResponse
from schema.routing_schema import (
    RankedKey,
    RoutingRequirements
)


from models.api_key import APIKey
from core.title_generator import generate_title

from schema.provider_schema import (
    ProviderResponse
)

from providers.base_provider import (
    BaseProvider
)


from providers.provider_factory import (
    ProviderFactory
)

from core.exceptions import (
    ProviderError,ProviderException
)

from service.key_selector import KeySelector
from service.routing_service import RoutingService
from service.key_service import KeyService
from service.summary_service import SummaryService
class GatewayService:

    


    @classmethod
    def _create_session(
        cls,
        db: Session,
        user_id: str,
        title: str = "New Chat"
    ) -> str:
            """
            Create a new chat session and return its ID.
            """

            session = ChatSession(

                user_id=user_id,

                title=title

            )

            db.add(session)

            db.flush()

            db.refresh(session)

            return session.session_id

    @classmethod
    def _validate_session(
        cls,
        db: Session,
        user_id: str,
        session_id: str
    ) -> ChatSession:
        """
        Validate that the requested session exists
        and belongs to the authenticated user.
        """

        statement = (
            select(ChatSession)
            .where(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id
            )
        )

        session = db.scalar(statement)

        if session is None:
            raise ConversationNotFoundError(
                f"Session '{session_id}' was not found."
            )

        return session

    # ======================================================
    # HISTORY
    # ======================================================
    @classmethod
    def _load_history(
        cls,
        db: Session,
        session_id: str
    ) -> list[dict[str, str]]:
        statement = (
            select(Message)
            .where(
                Message.session_id == session_id
            )
            .order_by(
                asc(Message.created_at)
            )
        )

        messages = db.scalars(statement).all()

        return [
            cls._to_provider_message(message)
            for message in messages
        ]

    # ======================================================
    # HELPERS
    # ======================================================

    @staticmethod
    def _to_provider_message(
        message: Message
    ) -> dict[str, str]:
        """
        Convert a Message model into the
        provider-compatible format.
        """

        return {
            "role": message.role,
            "content": message.content
        }

    
    # ======================================================
    # ROUTING
    # ======================================================
    @classmethod
    def _route(
    cls,
    request: AskRequest
    ) -> RoutingRequirements:
            """
            Build routing requirements from the
            incoming user prompt.
            """

            try:

                return RoutingService.analyze(
                    request.message
                )

            except Exception as exc:

                raise RouterException(
                    "Failed to classify request."
                ) from exc

    # ======================================================
    # KEY SELECTION
    # ======================================================

    @classmethod
    def _select_keys(
        cls,
        db: Session,
        user_id: str,
        requirements: RoutingRequirements
    ) -> list[RankedKey]:
        """
        Return all ranked API keys.
        """

        ranked_keys = KeySelector.select_keys(
            db=db,
            user_id=user_id,
            requirements=requirements
        )

        if not ranked_keys:
            raise NoUsableAPIKeysError()

        return ranked_keys
    # ======================================================
# GENERATE
# ======================================================

    @classmethod
    def _generate(
        cls,
        ranked_key: RankedKey,
        request: AskRequest,
        history: list[dict[str, str]]
    ) -> ProviderResponse:

        try:

            provider = cls._build_provider(
                ranked_key
            )

            return provider.generate(
                request=request,
                history=history
            )

        except ProviderError:
            raise

        except Exception as exc:

            raise ProviderError(
                f"{ranked_key.key.provider}: {str(exc)}"
            ) from exc
        

    @staticmethod
    def _build_provider(
        ranked_key: RankedKey
    ):

        return ProviderFactory.create(
            api_key=ranked_key.key,
            model=ranked_key.model
        )
    
    @classmethod
    def _try_generate(
        cls,
        db: Session,
        session_id: str,
        ranked_keys: list[RankedKey],
        request: AskRequest,
        history: list[dict[str, str]]
    ) -> tuple[
        RankedKey,
        BaseProvider,
        ProviderResponse
    ]:
            """
            Try providers/models in ranked order until one succeeds.
            """

            last_exception = None

            summary = SummaryService.get_summary(
                db=db,
                session_id=session_id
            )

            for candidate in ranked_keys:

                print("=" * 80)
                print(f"Trying Provider : {candidate.key.provider}")
                print(f"Trying Model    : {candidate.model.model}")
                print("=" * 80)

                try:

                    trimmed_history = HistoryWindow.build(
                        history=history,
                        summary=summary,
                        context_window=candidate.model.context_window,
                        reserved_tokens=request.max_tokens or 2048
                    )

                    provider = cls._build_provider(
                        candidate
                    )

                    response = provider.generate(
                        request=request,
                        history=trimmed_history
                    )

                    print("SUCCESS")
                    print("=" * 80)

                    return (
                        candidate,
                        provider,
                        response
                    )

                except Exception as exc:

                    print(f"FAILED : {exc}")

                    last_exception = exc

                    continue

            raise ProviderException(
                "All providers failed."
            ) from last_exception

    # ======================================================
    # SAVE USER MESSAGE
    # ======================================================
    @classmethod
    def _save_user_message(
        cls,
        db: Session,
        session_id: str,
        request: AskRequest
    ) -> Message:
        """
        Persist the user's message.
        """

        message = Message(
            session_id=session_id,
            role="user",
            content=request.message
        )

        db.add(message)
        db.flush()

        return message

    # ======================================================
    # SAVE ASSISTANT MESSAGE
    # ======================================================
    @classmethod
    def _save_assistant_message(
        cls,
        db: Session,
        session_id: str,
        response: ProviderResponse
    ) -> Message:
        """
        Persist the assistant response.
        """

        message = Message(
            session_id=session_id,
            role="assistant",
            content=response.content
        )

        db.add(message)
        db.flush()

        return message

    # ======================================================
    # UPDATE API KEY USAGE
    # ======================================================
    @classmethod
    def _update_key_usage(
        cls,
        ranked_key: RankedKey,
        response: ProviderResponse
    ) -> None:
        """
        Update API key and model usage statistics.
        """

        KeyService.update_usage(
            key=ranked_key.key,
            model=ranked_key.model,
            tokens_used=response.usage.total_tokens
        )

    # ======================================================
    # ANALYTICS
    # ======================================================
    @classmethod
    def _save_analytics(
        cls,
        db: Session,
        user_id: str,
        session_id: str,
        request: AskRequest,
        ranked_key: RankedKey,
        response: ProviderResponse,
        requirements: RoutingRequirements,
        *,
        selected_by: str = "ml_router",
        selected_rank: int = 1,
        attempt_count: int = 1,
        retry_count: int = 0,
        success: bool = True,
        failure_reason: str | None = None
    ) -> None:
        """
        Persist gateway analytics for the completed request.
        """

        log = Conversation(

            # ==================================================
            # User
            # ==================================================

            user_id=user_id,

            session_id=session_id,

            key_id=ranked_key.key.key_id,

            model_id=ranked_key.model.model_id,

            # ==================================================
            # Prompt
            # ==================================================

            query=request.message,

            response=response.content,

            source="llm",

            # ==================================================
            # Model
            # ==================================================

            provider=response.provider,

            model=response.model,

            # ==================================================
            # Token Usage
            # ==================================================

            input_tokens=response.usage.prompt_tokens,

            output_tokens=response.usage.completion_tokens,

            tokens_used=response.usage.total_tokens,

            total_cost_usd=response.usage.total_cost_usd,

            # ==================================================
            # Prompt Analytics
            # ==================================================

            query_length=len(request.message),

            prompt_category=(
                "reasoning" if requirements.reasoning
                else "code_generation" if requirements.code_generation
                else "long_context" if requirements.long_context
                else "fast_response" if requirements.fast_response
                else "low_cost" if requirements.low_cost
                else "general"
            ),

            routing_hint=str(
                requirements.model_dump()
            ),

            # ==================================================
            # Gateway Analytics
            # ==================================================

            selected_by=selected_by,

            selected_rank=selected_rank,

            attempt_count=attempt_count,

            retry_count=retry_count,

            success=success,

            failure_reason=failure_reason,

            latency_ms=response.latency_ms
        )

        db.add(log)

    # ======================================================
    # RESPONSE
    # ======================================================
    @classmethod
    def _build_response(
    cls,
    session_id: str,
    assistant_message: Message,
    title:str,
    provider_response: ProviderResponse
    ) -> AskResponse:
            """
            Build API response.
            """

            return AskResponse(

                session_id=session_id,
                title=title,
                message=MessageResponse(

                    id=assistant_message.id,

                    session_id=assistant_message.session_id,

                    role=assistant_message.role,

                    content=assistant_message.content,

                    created_at=assistant_message.created_at
                ),

                provider=provider_response.provider,

                model=provider_response.model,

                latency_ms=provider_response.latency_ms,

                usage=Usage(

                    prompt_tokens=provider_response.usage.prompt_tokens,

                    completion_tokens=provider_response.usage.completion_tokens,

                    total_tokens=provider_response.usage.total_tokens,

                    total_cost_usd=provider_response.usage.total_cost_usd
                )
            )

    @classmethod
    def continue_chat(
        cls,
        db: Session,
        user_id: str,
        session_id: str,
        request: AskRequest,
        
    ) -> AskResponse:
        cls._validate_session(
            db=db,
            user_id=user_id,
            session_id=session_id
        )

        return cls._process_chat(
            db=db,
            user_id=user_id,
            session_id=session_id,
            request=request,
        
        )

    @classmethod
    def _process_chat(
    cls,
    db: Session,
    user_id: str,
    session_id: str,
    request: AskRequest,
    
    ) -> AskResponse:
        """
        Shared chat pipeline used by both:
        - start_chat()
        - continue_chat()
        """

        try:

            # ==================================================
            # Save User Message
            # ==================================================

            cls._save_user_message(
                db=db,
                session_id=session_id,
                request=request
            )

            # ==================================================
            # Route Prompt
            # ==================================================

            requirements = cls._route(
                request
            )

            # ==================================================
            # Select API Keys
            # ==================================================

            ranked_keys = cls._select_keys(
                db=db,
                user_id=user_id,
                requirements=requirements
            )

            # ==================================================
            # Load Full Conversation History
            # ==================================================

            history = cls._load_history(
                db=db,
                session_id=session_id
            )

            # ==================================================
            # Generate Response (with fallback)
            # ==================================================

            selected_candidate, provider, provider_response = cls._try_generate(
                    db=db,
                    session_id=session_id,
                    ranked_keys=ranked_keys,
                    request=request,
                    history=history
                     )

            # ==================================================
            # Analytics Metadata
            # ==================================================

            selected_rank = (
                ranked_keys.index(selected_candidate) + 1
            )

            attempt_count = selected_rank

            selected_by = (
                "ml_router"
                if selected_rank == 1
                else "fallback"
            )

            # ==================================================
            # Save Assistant Message
            # ==================================================
            assistant_message = cls._save_assistant_message(
                        db=db,
                        session_id=session_id,
                        response=provider_response
                    )

                # ==========================================
                # Update Conversation Summary
                # ==========================================

            
            SummaryService.update_summary(
            db=db,
            session_id=session_id,
            provider=provider,
                )
            # ==================================================
            # Update Usage
            # ==================================================

            cls._update_key_usage(
                ranked_key=selected_candidate,
                response=provider_response
            )

            # ==================================================
            # Save Analytics
            # ==================================================

            cls._save_analytics(
                db=db,
                user_id=user_id,
                session_id=session_id,
                request=request,
                ranked_key=selected_candidate,
                response=provider_response,
                requirements=requirements,
                selected_by=selected_by,
                selected_rank=selected_rank,
                attempt_count=attempt_count,
                retry_count=0,
                success=True,
                failure_reason=None
            )

            # ==================================================
            # Update Session Title
            # ==================================================

            cls._update_session_title(
                db=db,
                session_id=session_id,
                message=request.message
            )

            # ==================================================
            # Commit
            # ==================================================

            db.commit()

            db.refresh(
                assistant_message
            )

            session = (
                db.query(ChatSession)
                .filter(
                    ChatSession.session_id == session_id
                )
                .first()
            )

            # ==================================================
            # Response
            # ==================================================

            return cls._build_response(
                session_id=session_id,
                title=session.title,
                assistant_message=assistant_message,
                provider_response=provider_response,
                
            )

        except Exception:

            db.rollback()

            raise


    @classmethod
    def start_chat(
        cls,
        db: Session,
        user_id: str,
        request: AskRequest,
        
    ) -> AskResponse:
        """
        Start a new chat session.
        """

        session_id = cls._create_session(
            db=db,
            user_id=user_id
        )

        return cls._process_chat(
            db=db,
            user_id=user_id,
            session_id=session_id,
            request=request,
           
        )
    

    @classmethod
    def _update_session_title(
    cls,
    db: Session,
    session_id: str,
    message: str
    ) -> None:
            """
            Set the session title using the first user message.
            """

            session = (
                db.query(ChatSession)
                .filter(
                    ChatSession.session_id == session_id
                )
                .first()
            )

            if session is None:
                return

            # Only update if title is still default
            if session.title == "New Chat":

                session.title = (
                    message[:50] + "..."
                    if len(message) > 50
                    else message
                )