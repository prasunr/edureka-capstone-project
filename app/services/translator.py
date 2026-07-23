"""Text translation via the Google Gemini API."""

from google import genai

from app.core.config import GEMINI_MODEL

PROMPT_TEMPLATE = (
    "You are a professional translator. Translate the text below into "
    "{language}. Preserve the meaning, tone, and formatting of the "
    "original. Return ONLY the translated text, with no explanations, "
    "notes, or quotation marks around it.\n\n"
    "Text to translate:\n{text}"
)


def translate_text(text: str, target_language: str, api_key: str) -> str:
    """Translate `text` into `target_language` using Gemini."""
    client = genai.Client(api_key=api_key)
    prompt = PROMPT_TEMPLATE.format(language=target_language, text=text)
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")
    return response.text.strip()
