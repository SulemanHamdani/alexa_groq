"""Groq chat client wrapper using the OpenAI-compatible SDK.

Encapsulates client configuration and inbound/outbound shaping.
"""

from __future__ import annotations

from typing import Optional

from httpx import Timeout, HTTPError
from openai import OpenAI

from app_config import Config


class GroqChatClient:
    """Thin wrapper around OpenAI SDK pointed to Groq.

    Keeps exception handling and defaults consistent for Alexa UX.
    """

    def __init__(self, config: Config) -> None:
        self._config = config

        # client is created lazily on first use to keep cold start small
        self._client: Optional[OpenAI] = None

    def _ensure_client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                api_key=self._config.api_key,
                base_url=self._config.base_url,
                timeout=Timeout(self._config.timeout_seconds),
            )
        return self._client

    def answer(self, question: str) -> str:
        if not self._config.api_key:
            return (
                "Groq key is not set. Please add GROQ_API_KEY in Lambda environment variables."
            )

        client = self._ensure_client()

        try:
            resp = client.chat.completions.create(
                model=self._config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Answer briefly and clearly for a voice assistant.",
                    },
                    {"role": "user", "content": question},
                ],
                temperature=0.3,
                max_tokens=self._config.max_tokens,
            )
            text = (resp.choices[0].message.content or "").strip()
            return text[:600] if text else "I couldn't get an answer."
        except HTTPError as e:
            msg = str(e)
            # Basic categorization; TTS friendly
            if "401" in msg:
                return "Groq rejected the key (unauthorized). Check GROQ_API_KEY."
            if "403" in msg:
                return (
                    "Groq says forbidden for this model or key. Try a different model or check access."
                )
            if "Timeout" in msg:
                return "Groq timed out. Please try again."
            return "Groq request failed."
        except Exception:
            return "Unexpected error talking to Groq."
