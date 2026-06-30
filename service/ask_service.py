
from sqlalchemy.orm import Session

from schema.ask_schema import (
    AskRequest,
    AskResponse
)

from service.gateway_service import GatewayService


class AskService:

    @staticmethod
    def start_chat(
        db: Session,
        user_id: str,
        request: AskRequest,
        
    ) -> AskResponse:
        """
        Start a new conversation.
        """

        return GatewayService.start_chat(
            db=db,
            user_id=user_id,
            request=request,
            
        )

    @staticmethod
    def continue_chat(
        db: Session,
        user_id: str,
        session_id: str,
        request: AskRequest,
        
    ) -> AskResponse:
        """
        Continue an existing conversation.
        """

        return GatewayService.continue_chat(
            db=db,
            user_id=user_id,
            session_id=session_id,
            request=request,
            
        )