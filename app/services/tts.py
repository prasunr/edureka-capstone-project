"""Text-to-speech conversion using gTTS."""

from io import BytesIO

from gtts import gTTS


def text_to_speech(text: str, lang_code: str) -> bytes:
    """Convert text to spoken audio and return MP3 bytes."""
    tts = gTTS(text=text, lang=lang_code)
    buffer = BytesIO()
    tts.write_to_fp(buffer)
    return buffer.getvalue()
