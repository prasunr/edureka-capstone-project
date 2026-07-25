"""Text-to-speech conversion using gTTS."""

from io import BytesIO

from gtts import gTTS
from gtts.tts import gTTSError


class SpeechError(Exception):
    """Raised with a user-friendly message when audio generation fails."""


def text_to_speech(text: str, lang_code: str) -> bytes:
    """Convert text to spoken audio and return MP3 bytes.

    Raises SpeechError with a user-friendly message on failure.
    """
    if not text.strip():
        raise SpeechError("There is no text to convert to speech.")
    try:
        tts = gTTS(text=text, lang=lang_code)
        buffer = BytesIO()
        tts.write_to_fp(buffer)
    except gTTSError as exc:
        raise SpeechError(
            "Could not generate audio. gTTS needs an internet connection and "
            "may throttle repeated requests — wait a moment and try again."
        ) from exc
    except ValueError as exc:
        raise SpeechError(
            f"This language isn't supported for speech (code '{lang_code}')."
        ) from exc
    audio = buffer.getvalue()
    if not audio:
        raise SpeechError("Audio generation produced no output. Please try again.")
    return audio
