from abc import ABC, abstractmethod
from typing import Any, Dict, List

from models.api_key import APIKey
from models.api_key_models import APIKeyModel

from schema.ask_schema import AskRequest
from schema.provider_schema import ProviderResponse


class BaseProvider(ABC):
    """
    Base class for all provider plugins.

    Providers are responsible only for
    generating responses.
    """

    def __init__(
        self,
        api_key: APIKey,
        model: APIKeyModel
    ):

        self.api_key = api_key

        self.model = model

    @abstractmethod
    def generate(
        self,
        request: AskRequest,
        history: List[Dict[str, Any]]
    ) -> ProviderResponse:
        """
        Generate a response from the provider.

        Parameters
        ----------
        request : AskRequest
            Incoming user request.

        history : List[Dict[str, Any]]
            Previous conversation in provider format.

        Returns
        -------
        ProviderResponse
        """
        pass