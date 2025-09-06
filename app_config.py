"""Configuration utilities for the Alexa Groq Lambda.

Provides a small, typed configuration layer sourced from environment
variables with sensible defaults suitable for Alexa Lambda execution.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Immutable configuration for the Groq-backed Alexa Lambda."""

    # Groq / OpenAI-compatible settings
    api_key: str | None
    model: str
    base_url: str
    timeout_seconds: float
    max_tokens: int

    # Voice UX strings (keep concise for TTS)
    launch_prompt: str = (
        "Hello Chat is ready. Just say what you want to ask."
    )
    launch_reprompt: str = "Say anything, for example: explain quantum computing."
    help_text: str = (
        "After opening Hello Chat, just say anything you want me to answer."
    )
    fallback_text: str = (
        "I didn’t catch that. Just say what you want to ask."
    )
    goodbye_text: str = "Goodbye!"


def _env(key: str, default: str | None = None) -> str | None:
    value = os.getenv(key)
    return value if value is not None else default


def load_config() -> Config:
    """Load configuration from environment variables.

    Defaults keep responses short and timeout conservative to fit within
    Alexa's overall 8s limit.
    """

    return Config(
        api_key=_env("GROQ_API_KEY"),
        model=_env("GROQ_MODEL", "openai/gpt-oss-120b"),
        base_url=_env("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        timeout_seconds=float(_env("GROQ_TIMEOUT_S", "5.0")),
        max_tokens=int(_env("GROQ_MAX_TOKENS", "220")),
    )
