"""The ONLY module allowed to call the Mistral API directly (master prompt §12).
Controllers and helpers must go through this client, never httpx/requests
themselves. Handles retries and reports failure so callers can fall back
cleanly — it never fabricates a response pretending to be from Mistral.
"""
import json
import time

import httpx

from utils.config import config
from utils.logger import logger, log_ai_call

MISTRAL_CHAT_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_EMBED_URL = "https://api.mistral.ai/v1/embeddings"

MAX_RETRIES = 2
TIMEOUT_SECONDS = 30


class MistralUnavailableError(Exception):
    """Raised when Mistral cannot be reached/authenticated after retries.
    Callers (helper/exam_generator.py, helper/diagnostic_engine.py, etc.)
    catch this specifically and switch to their deterministic fallback path —
    never silently pretend the AI produced the content."""


def is_configured() -> bool:
    return bool(config.MISTRAL_API_KEY)


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {config.MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }


def generate_json(system_prompt: str, user_prompt: str, *, temperature: float = 0.4) -> dict:
    """Calls Mistral's chat completion endpoint with JSON-object response
    formatting and returns the parsed dict. Raises MistralUnavailableError
    if the key is missing, the request fails after retries, or the response
    isn't valid JSON — the caller is responsible for falling back."""
    if not is_configured():
        raise MistralUnavailableError("MISTRAL_API_KEY is not configured")

    payload = {
        "model": config.MISTRAL_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }

    last_error = None
    for attempt in range(1, MAX_RETRIES + 2):
        start = time.time()
        try:
            with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
                resp = client.post(MISTRAL_CHAT_URL, headers=_headers(), json=payload)
            duration_ms = (time.time() - start) * 1000

            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                log_ai_call("mistral_generate_json", duration_ms, success=True)
                return parsed

            last_error = f"HTTP {resp.status_code}: {resp.text[:300]}"
            log_ai_call("mistral_generate_json", duration_ms, success=False)

        except (httpx.HTTPError, json.JSONDecodeError, KeyError, IndexError) as exc:
            duration_ms = (time.time() - start) * 1000
            last_error = str(exc)
            log_ai_call("mistral_generate_json", duration_ms, success=False)

        if attempt <= MAX_RETRIES:
            time.sleep(0.5 * attempt)  # simple backoff

    logger.error(f"Mistral generate_json failed after retries: {last_error}")
    raise MistralUnavailableError(last_error or "Unknown Mistral failure")


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Returns one embedding vector per input text via Mistral's embeddings
    endpoint. Used by helper/embedding_engine.py for document ingestion."""
    if not is_configured():
        raise MistralUnavailableError("MISTRAL_API_KEY is not configured")
    if not texts:
        return []

    payload = {"model": config.MISTRAL_EMBED_MODEL, "input": texts}
    start = time.time()
    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            resp = client.post(MISTRAL_EMBED_URL, headers=_headers(), json=payload)
        duration_ms = (time.time() - start) * 1000
        if resp.status_code != 200:
            log_ai_call("mistral_embed", duration_ms, success=False)
            raise MistralUnavailableError(f"HTTP {resp.status_code}: {resp.text[:300]}")
        data = resp.json()["data"]
        log_ai_call("mistral_embed", duration_ms, success=True)
        return [item["embedding"] for item in data]
    except httpx.HTTPError as exc:
        raise MistralUnavailableError(str(exc)) from exc
