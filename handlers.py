"""Alexa request routing and intent handlers."""

from __future__ import annotations

import json
from typing import Any, Dict

from alexa_responses import speak, end_session
from app_config import Config
from groq_client import GroqChatClient
from utils import get_slot, get_remaining_ms


def handle_launch(cfg: Config) -> Dict[str, Any]:
    # Keep session open so next utterance hits FreeFormIntent
    return speak(cfg.launch_prompt, end=False, reprompt=cfg.launch_reprompt)


def handle_intent(event: Dict[str, Any], cfg: Config, client: GroqChatClient, remaining_ms: int) -> Dict[str, Any]:
    name = event.get("request", {}).get("intent", {}).get("name")

    if name == "FreeFormIntent":
        utterance = get_slot(event, "utterance")
        if not utterance:
            return speak(
                "I'm listening. What should I ask?",
                end=False,
                reprompt="Try: explain quantum computing.",
            )
        if remaining_ms < 2500:
            return speak("I’m running out of time. Please try again.", end=True)
        answer = client.answer(utterance)
        return speak(answer or "I couldn't get an answer.", end=True)

    if name == "AMAZON.HelpIntent":
        return speak(cfg.help_text, end=False, reprompt=cfg.launch_reprompt)

    if name in ("AMAZON.CancelIntent", "AMAZON.StopIntent"):
        return speak(cfg.goodbye_text, end=True)

    if name == "AMAZON.FallbackIntent":
        return speak(cfg.fallback_text, end=False, reprompt=cfg.launch_reprompt)

    return speak(
        "Sorry, I only handle hello and groq questions right now.",
        end=False,
        reprompt="Say: hello. Or: ask groq what is quantum computing.",
    )


def handle(event: Dict[str, Any], context: Any, cfg: Config, client: GroqChatClient) -> Dict[str, Any]:
    # Lightweight logging for observability
    try:
        print("EVENT:", json.dumps(event))
    except Exception:
        pass

    req = event.get("request", {})
    rtype = req.get("type")

    if rtype == "LaunchRequest":
        return handle_launch(cfg)
    if rtype == "IntentRequest":
        remaining_ms = get_remaining_ms(context)
        return handle_intent(event, cfg, client, remaining_ms)
    if rtype == "SessionEndedRequest":
        try:
            req = event.get("request", {})
            print("SessionEndedRequest:", req.get("reason"), req.get("error"))
        except Exception:
            pass
        return end_session()

    print("UNEXPECTED_REQUEST_TYPE:", rtype)
    return speak("Something went wrong.", end=True)
