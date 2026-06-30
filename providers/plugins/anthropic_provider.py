import time
from typing import Any, Dict, List

from anthropic import (
    Anthropic,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APIStatusError,
)

from core.encrypt import decrypt_key

from providers.base_provider import BaseProvider
from providers.provider_registry import register_provider

from models.api_key import APIKey
from models.api_key_models import APIKeyModel

from schema.ask_schema import AskRequest
from schema.provider_schema import (
    ProviderResponse,
    Usage,
)


@register_provider("anthropic")
class AnthropicProvider(BaseProvider):
    """
    Provider plugin for Anthropic Claude models.
    """

    def __init__(
        self,
        api_key: APIKey,
        model: APIKeyModel,
    ):

        super().__init__(
            api_key,
            model,
        )

        self.provider = "anthropic"

        self.model_name = model.model

        self.client = self._build_client()

    def _build_client(self) -> Anthropic:

        decrypted_key = decrypt_key(
            self.api_key.api_key
        )

        if not decrypted_key:

            raise ValueError(
                "Failed to decrypt API key."
            )

        return Anthropic(
            api_key=decrypted_key
        )

    def _build_messages(
        self,
        request: AskRequest,
        history: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        messages: List[Dict[str, Any]] = []

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
        messages: List[Dict[str, Any]],
        request: AskRequest,
    ) -> ProviderResponse:

        start_time = time.perf_counter()

        try:

            response = self.client.messages.create(

                model=self.model_name,

                messages=messages,

                temperature=request.temperature,

                max_tokens=request.max_tokens,
            )

        except AuthenticationError as e:

            raise RuntimeError(
                "anthropic: Invalid API key."
            ) from e

        except RateLimitError as e:

            raise RuntimeError(
                "anthropic: Rate limit exceeded."
            ) from e

        except APIConnectionError as e:

            raise RuntimeError(
                "anthropic: Unable to connect."
            ) from e

        except APIStatusError as e:

            raise RuntimeError(
                f"anthropic: HTTP {e.status_code}."
            ) from e

        except Exception as e:

            raise RuntimeError(
                f"anthropic: {str(e)}"
            ) from e

        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        usage = Usage(

            prompt_tokens=response.usage.input_tokens,

            completion_tokens=response.usage.output_tokens,

            total_tokens=(
                response.usage.input_tokens
                + response.usage.output_tokens
            ),
        )

        content = ""

        if response.content:

            content = "".join(

                block.text

                for block in response.content

                if getattr(block, "type", None) == "text"

            )

        metadata = {

            "finish_reason": response.stop_reason,

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