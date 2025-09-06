from __future__ import annotations

# Entrypoint kept minimal: wires config + handlers + client.

from app_config import load_config
from groq_client import GroqChatClient
from handlers import handle


# Initialize once per runtime for perf; config reads env each cold start
_CONFIG = load_config()
_CLIENT = GroqChatClient(_CONFIG)


def lambda_handler(event, context):
    return handle(event, context, _CONFIG, _CLIENT)
