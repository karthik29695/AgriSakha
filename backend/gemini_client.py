import os
import itertools
import logging
import google.generativeai as genai

log = logging.getLogger("agrisakha-gemini")

GEMINI_API_KEYS = [
    k.strip() for k in os.getenv("GEMINI_API_KEYS", "").split(",") if k.strip()
]

if not GEMINI_API_KEYS:
    raise RuntimeError(
        "No Gemini API keys provided. "
        "Set the GEMINI_API_KEYS environment variable (comma-separated for rotation)."
    )

key_cycle = itertools.cycle(GEMINI_API_KEYS)
_current_key = next(key_cycle)


def configure_gemini(key: str):
    genai.configure(api_key=key)


configure_gemini(_current_key)
log.info("Gemini API key rotation initialized.")


async def call_gemini_with_rotation(
    prompt_or_inputs,
    model_name="gemini-2.5-flash"
):
    global _current_key

    last_error = None
    for _ in range(len(GEMINI_API_KEYS)):
        try:
            model = genai.GenerativeModel(model_name)
            return await model.generate_content_async(prompt_or_inputs)
        except Exception as e:
            last_error = e
            log.warning(f"Gemini error, rotating key: {e}")
            _current_key = next(key_cycle)
            configure_gemini(_current_key)

    raise RuntimeError(
        f"All Gemini API keys failed. Last error: {last_error}"
    )
