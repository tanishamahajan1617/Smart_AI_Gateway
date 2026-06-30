from typing import Dict, List, Optional, Type

from providers.base_provider import BaseProvider


# ==========================================================
# GLOBAL PROVIDER REGISTRY
# ==========================================================

PROVIDER_REGISTRY: Dict[str, Type[BaseProvider]] = {}


# ==========================================================
# REGISTER PROVIDER
# ==========================================================

def register_provider(name: str):
    """
    Decorator used to register provider plugins.

    Example
    -------
    @register_provider("openai")
    class OpenAICompatibleProvider(BaseProvider):
        ...
    """

    def decorator(provider_class: Type[BaseProvider]):

        provider_name = name.strip().lower()

        if provider_name in PROVIDER_REGISTRY:

            raise ValueError(
                f"Provider '{provider_name}' is already registered."
            )

        PROVIDER_REGISTRY[provider_name] = provider_class

        return provider_class

    return decorator


# ==========================================================
# GET PROVIDER
# ==========================================================

def get_provider_class(
    name: str
) -> Optional[Type[BaseProvider]]:
    """
    Returns the registered provider class.

    Returns None if the provider
    has not been registered.
    """

    return PROVIDER_REGISTRY.get(
        name.strip().lower()
    )


# ==========================================================
# LIST REGISTERED PROVIDERS
# ==========================================================

def list_registered_providers() -> List[str]:
    """
    Returns all registered provider names.
    """

    return sorted(
        PROVIDER_REGISTRY.keys()
    )


# ==========================================================
# CHECK REGISTRATION
# ==========================================================

def is_provider_registered(
    name: str
) -> bool:
    """
    Returns True if the provider
    is registered.
    """

    return (
        name.strip().lower()
        in PROVIDER_REGISTRY
    )