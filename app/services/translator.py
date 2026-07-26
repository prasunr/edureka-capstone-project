"""Text translation via the Google Gemini API."""

from google import genai
from google.genai import errors as genai_errors

from app.core.config import GEMINI_MODEL

PROMPT_TEMPLATE = (
    "You are a professional translator. Translate the text below into "
    "{language}. Preserve the meaning, tone, and formatting of the "
    "original exactly — including numbers, dates, times, currency, and "
    "nuances such as changes of plan or degree. Translate idioms to "
    "natural equivalents in the target language. Return ONLY the "
    "translated text, with no explanations, notes, or quotation marks "
    "around it.\n\n"
    "Text to translate:\n{text}"
)


class TranslationError(Exception):
    """Raised with a user-friendly message when translation fails."""


def _friendly_message(exc: genai_errors.APIError) -> str:
    code = exc.code
    if code in (400, 401, 403):
        return (
            "The Gemini API rejected your API key. Double-check the key in "
            "the sidebar or your .env file (no extra spaces), or create a "
            "new one at https://aistudio.google.com/apikey."
        )
    if code == 404:
        return (
            f"The model '{GEMINI_MODEL}' is not available to your API key. "
            "Set GEMINI_MODEL in your .env file to a model you have access to."
        )
    if code == 429:
        return (
            "You've hit the Gemini API rate limit. Wait a minute and try "
            "again — free-tier keys allow a limited number of requests."
        )
    if code and code >= 500:
        return "Google's servers had a hiccup. Please try again in a moment."
    return f"The Gemini API returned an error: {exc.message or exc}"


def translate_text(text: str, target_language: str, api_key: str) -> str:
    """Translate `text` into `target_language` using Gemini.

    Raises TranslationError with a user-friendly message on failure.
    """
    client = genai.Client(api_key=api_key)
    prompt = PROMPT_TEMPLATE.format(language=target_language, text=text)
    try:
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    except genai_errors.APIError as exc:
        raise TranslationError(_friendly_message(exc)) from exc
    except Exception as exc:
        raise TranslationError(
            "Could not reach the Gemini API. Check your internet connection "
            "and try again."
        ) from exc
    if not response.text:
        raise TranslationError(
            "Gemini returned an empty response. Try again, or rephrase the text."
        )
    return response.text.strip()
