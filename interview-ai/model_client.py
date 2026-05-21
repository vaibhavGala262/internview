# model_client.py
import os
import time

import anthropic
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
GEMINI_MODEL = "gemini-2.0-flash-lite"
GEMINI_FALLBACK_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
]


def _load_local_env() -> None:
    """Load simple KEY=VALUE lines from a local .env file if present."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8-sig") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip().lstrip("\ufeff"), value.strip().strip('"').strip("'"))


def call_model(system_prompt: str, user_message: str) -> str:
    """
    Call the configured AI model provider and return the raw text response.

    Environment:
        MODEL_PROVIDER: "anthropic" or "gemini" (defaults to "anthropic")
        ANTHROPIC_API_KEY: required when MODEL_PROVIDER=anthropic
        GEMINI_API_KEY: required when MODEL_PROVIDER=gemini
    """
    _load_local_env()
    provider = os.getenv("MODEL_PROVIDER", "anthropic").strip().lower()

    if provider == "anthropic":
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required when MODEL_PROVIDER=gemini")

        genai.configure(api_key=api_key)
        full_prompt = system_prompt + "\n\n" + user_message
        configured_models = [
            model.strip()
            for model in os.getenv("GEMINI_FALLBACK_MODELS", "").split(",")
            if model.strip()
        ]
        model_names = [os.getenv("GEMINI_MODEL", GEMINI_MODEL).strip()]
        model_names.extend(configured_models or GEMINI_FALLBACK_MODELS)

        seen = set()
        last_error = None
        for model_name in model_names:
            if model_name in seen:
                continue
            seen.add(model_name)
            model = genai.GenerativeModel(model_name)
            for attempt in range(3):
                try:
                    response = model.generate_content(full_prompt)
                    return response.text
                except google_exceptions.ResourceExhausted as exc:
                    last_error = exc
                    error_text = str(exc)
                    if "PerDay" in error_text or "limit: 0" in error_text:
                        break
                    if attempt == 2:
                        break
                    time.sleep(35)

        if last_error:
            raise last_error
        raise RuntimeError("No Gemini model candidates were configured.")

    raise ValueError(
        f"Unsupported MODEL_PROVIDER: {provider}. "
        "Use 'anthropic' or 'gemini'."
    )
