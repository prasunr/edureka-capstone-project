"""Every language offered in the UI must be speakable by gTTS."""

from gtts.lang import tts_langs

from app.core.languages import LANGUAGES


def test_all_language_codes_supported_by_gtts():
    supported = tts_langs()
    unsupported = {n: c for n, c in LANGUAGES.items() if c not in supported}
    assert not unsupported, f"gTTS cannot speak: {unsupported}"


def test_no_duplicate_codes():
    codes = list(LANGUAGES.values())
    assert len(codes) == len(set(codes))
