import providers.plugins

from models.api_key import APIKey
from models.api_key_models import APIKeyModel

from providers.base_provider import BaseProvider
from providers.provider_registry import (
    get_provider_class,
)


class ProviderFactory:

    @staticmethod
    def create(
        api_key: APIKey,
        model: APIKeyModel
    ) -> BaseProvider:

        provider_class = get_provider_class(
            api_key.provider
        )

        if provider_class is None:

            raise ValueError(
                f"Provider '{api_key.provider}' is not registered."
            )

        return provider_class(
            api_key=api_key,
            model=model
        )