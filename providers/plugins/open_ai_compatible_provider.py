import time
from typing import Any, Dict, List

from openai import (
    OpenAI,
    AuthenticationError,
    RateLimitError,
    APITimeoutError,
    APIConnectionError,
    APIStatusError,
)

from core.encrypt import decrypt_key
from core.providers_endpoint import OPENAI_COMPATIBLE_ENDPOINTS

from models.api_key import APIKey
from models.api_key_models import APIKeyModel

from providers.base_provider import BaseProvider
from providers.provider_registry import register_provider

from schema.ask_schema import AskRequest
from schema.provider_schema import (
    ProviderResponse,
    Usage,
)


@register_provider("openai")
@register_provider("deepseek")
@register_provider("groq")
@register_provider("together")
@register_provider("openrouter")
@register_provider("fireworks")
@register_provider("cerebras")
@register_provider("sambanova")
class OpenAICompatibleProvider(BaseProvider):
    """
    Provider plugin for all OpenAI-compatible APIs.
    Responsible only for text generation.
    """

    def __init__(
        self,
        api_key: APIKey,
        model: APIKeyModel | None = None,
    ):

        super().__init__(
            api_key,
            model,
        )

        self.provider = api_key.provider.lower()

        self.model_name = (
                model.model
                if model is not None
                else None
            )

        self.base_url = OPENAI_COMPATIBLE_ENDPOINTS.get(
            self.provider
        )

        if self.base_url is None:
            raise ValueError(
                f"No endpoint configured for provider '{self.provider}'."
            )

        self.client = self._build_client()

    def _build_client(self) -> OpenAI:

        decrypted_key = decrypt_key(
            self.api_key.api_key
        )

        if not decrypted_key:
            raise ValueError(
                "Failed to decrypt API key."
            )

        return OpenAI(
            api_key=decrypted_key,
            base_url=self.base_url,
        )

    def _build_messages(
        self,
        request: AskRequest,
        history: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:

        messages: List[Dict[str, str]] = []

        for message in history:

            role = message.get("role")
            content = message.get("content")

            if role and content:

                messages.append(
                    {
                        "role": role,
                        "content": content,
                    }
                )

        messages.append(
            {
                "role": "user",
                "content": request.message,
            }
        )

        return messages

    def _call_llm(
    self,
    messages: List[Dict[str, str]],
    request: AskRequest,
    ) -> ProviderResponse:

            start_time = time.perf_counter()

            try:

                if self.model_name is None:
                    raise RuntimeError(
                        "No model selected for generation."
                    )

                response = self.client.chat.completions.create(

                    model=self.model_name,

                    messages=messages,

                    temperature=request.temperature,

                    max_tokens=request.max_tokens,

                    stream=request.stream,
                )

            except AuthenticationError as e:

                raise RuntimeError(
                    f"{self.provider}: Invalid API key."
                ) from e

            except RateLimitError as e:

                raise RuntimeError(
                    f"{self.provider}: Rate limit exceeded."
                ) from e

            except APITimeoutError as e:

                raise RuntimeError(
                    f"{self.provider}: Request timed out."
                ) from e

            except APIConnectionError as e:

                raise RuntimeError(
                    f"{self.provider}: Unable to connect."
                ) from e

            except APIStatusError as e:

                raise RuntimeError(
                    f"{self.provider}: HTTP {e.status_code}."
                ) from e

            except Exception as e:

                raise RuntimeError(
                    f"{self.provider}: {str(e)}"
                ) from e

            latency_ms = (
                time.perf_counter() - start_time
            ) * 1000

            usage = Usage(

                prompt_tokens=response.usage.prompt_tokens
                if response.usage
                else 0,

                completion_tokens=response.usage.completion_tokens
                if response.usage
                else 0,

                total_tokens=response.usage.total_tokens
                if response.usage
                else 0,
            )

            content = ""

            if response.choices:

                content = (
                    response.choices[0]
                    .message
                    .content
                    or ""
                )

            metadata = {

                "finish_reason": (
                    response.choices[0].finish_reason
                    if response.choices
                    else None
                )

            }

            return ProviderResponse(

                content=content,

                provider=self.provider,

                model=self.model_name,

                latency_ms=latency_ms,

                usage=usage,

                metadata=metadata,
            )

    def generate(
        self,
        request: AskRequest,
        history: List[Dict[str, Any]],
    ) -> ProviderResponse:

        self._validate_request(request)

        request = self._preprocess_request(request)

        messages = self._build_messages(
            request=request,
            history=history,
        )

        response = self._call_llm(
            messages=messages,
            request=request,
        )

        response = self._postprocess_response(
            response
        )

        return response

    def _validate_request(
        self,
        request: AskRequest,
    ) -> None:

        if not request.message.strip():
            raise ValueError(
                "Message cannot be empty."
            )

    def _preprocess_request(
        self,
        request: AskRequest,
    ) -> AskRequest:

        return request

    def _postprocess_response(
        self,
        response: ProviderResponse,
    ) -> ProviderResponse:

        return response