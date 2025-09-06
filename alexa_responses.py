"""Alexa response builders.

Keeps JSON shapes consistent and easy to test. Only PlainText output
is used for simplicity and broad device support.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


def speak(text: str, *, end: bool = False, reprompt: Optional[str] = None) -> Dict[str, Any]:
    """Build a simple Alexa response with optional reprompt.

    Parameters
    - text: main TTS text
    - end: whether to end the session
    - reprompt: optional reprompt text when session remains open
    """
    response: Dict[str, Any] = {
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": text},
            "shouldEndSession": end,
        },
    }
    if not end and reprompt:
        response["response"]["reprompt"] = {
            "outputSpeech": {"type": "PlainText", "text": reprompt}
        }
    return response


def end_session() -> Dict[str, Any]:
    return {"version": "1.0", "response": {"shouldEndSession": True}}

