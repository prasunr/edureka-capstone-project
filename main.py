"""Translate & Speak — Streamlit app (capstone project).

Translates text (typed or uploaded as TXT/PDF/CSV/Excel) into a chosen
language with the Gemini API, speaks it with gTTS, and offers the audio
as an MP3 download. Run with:

    streamlit run main.py
"""

import streamlit as st

from app.core.config import GEMINI_API_KEY
from app.core.languages import LANGUAGES
from app.services.translator import TranslationError, translate_text
from app.services.tts import SpeechError, text_to_speech
from app.utils.file_reader import extract_text

# Above this size, translation is still fine but audio generation gets slow.
SLOW_AUDIO_CHARS = 5_000
# Hard cap to keep requests reasonable for the free Gemini tier.
MAX_INPUT_CHARS = 50_000

st.set_page_config(page_title="Translate & Speak", page_icon="🌍", layout="centered")

st.title("🌍 Translate & Speak")
st.caption(
    "Translate text into another language with Google Gemini, "
    "listen to it with gTTS, and download the audio as MP3."
)

# --- Sidebar: API key + instructions ---
with st.sidebar:
    st.header("Settings")
    api_key = GEMINI_API_KEY
    if api_key:
        st.success("Gemini API key loaded from .env")
    else:
        api_key = st.text_input(
            "Gemini API key",
            type="password",
            help="Get a free key at https://aistudio.google.com/apikey, "
            "or put it in a .env file as GEMINI_API_KEY.",
        )
        if not api_key:
            st.info(
                "You need a (free) Gemini API key to translate. "
                "Create one at [aistudio.google.com/apikey]"
                "(https://aistudio.google.com/apikey) and paste it above."
            )
    st.markdown("---")
    st.markdown(
        "**How to use**\n\n"
        "1. Enter text *or* upload a file\n"
        "2. Pick a target language\n"
        "3. Click **Translate**\n"
        "4. Play or download the audio"
    )

# --- Input: typed text or uploaded file ---
tab_text, tab_file = st.tabs(["✏️ Enter text", "📄 Upload file"])

source_text = ""

with tab_text:
    typed = st.text_area(
        "Text to translate",
        height=200,
        key="typed_text",
        placeholder="Type or paste the text you want to translate…",
        help="Any language is fine as input — Gemini detects it automatically.",
    )
    if typed.strip():
        source_text = typed.strip()
        st.caption(f"{len(source_text):,} characters")

with tab_file:
    uploaded = st.file_uploader(
        "Upload a TXT, PDF, CSV, or Excel file",
        type=["txt", "pdf", "csv", "xlsx", "xls"],
        help="The file's text is extracted and translated. "
        "Scanned/image-only PDFs are not supported.",
    )
    if uploaded is not None:
        try:
            source_text = extract_text(uploaded.name, uploaded.getvalue())
            st.success(
                f"Extracted {len(source_text):,} characters from {uploaded.name}"
            )
            with st.expander("Preview extracted text"):
                st.text(source_text[:3000] + ("…" if len(source_text) > 3000 else ""))
        except ValueError as exc:
            st.error(f"⚠️ {exc}")

# --- Language selection and translation ---
target_language = st.selectbox(
    "Translate into",
    list(LANGUAGES.keys()),
    index=None,
    placeholder="Choose a language",
    help="Languages are limited to those gTTS can also speak aloud.",
)

if source_text and len(source_text) > SLOW_AUDIO_CHARS:
    st.warning(
        f"⏳ Your text is {len(source_text):,} characters — translation will "
        "work, but generating the audio may take a while."
    )

if st.button("Translate", type="primary", use_container_width=True):
    if not api_key:
        st.error(
            "🔑 No API key yet. Paste your Gemini API key in the sidebar "
            "(get a free one at https://aistudio.google.com/apikey)."
        )
    elif not source_text:
        st.error(
            "✏️ Nothing to translate yet. Type some text in the "
            "**Enter text** tab or upload a file in the **Upload file** tab."
        )
    elif not target_language:
        st.error("🌐 Please choose a target language from the dropdown above.")
    elif len(source_text) > MAX_INPUT_CHARS:
        st.error(
            f"📏 Your text is {len(source_text):,} characters; the limit is "
            f"{MAX_INPUT_CHARS:,}. Please split it into smaller parts."
        )
    else:
        try:
            with st.spinner(f"Translating into {target_language}…"):
                st.session_state.translation = translate_text(
                    source_text, target_language, api_key
                )
                st.session_state.translation_language = target_language
        except TranslationError as exc:
            st.error(f"⚠️ {exc}")
        except Exception:
            st.error(
                "⚠️ Something unexpected went wrong during translation. "
                "Please try again."
            )

# --- Results: translated text + audio ---
if "translation" in st.session_state:
    lang = st.session_state.translation_language
    st.subheader(f"Translation ({lang})")
    st.text_area("Translated text", st.session_state.translation, height=200)

    try:
        with st.spinner("Generating speech…"):
            audio_bytes = text_to_speech(st.session_state.translation, LANGUAGES[lang])
        st.audio(audio_bytes, format="audio/mp3")
        st.download_button(
            "⬇️ Download MP3",
            data=audio_bytes,
            file_name=f"translation_{LANGUAGES[lang]}.mp3",
            mime="audio/mpeg",
            use_container_width=True,
        )
    except SpeechError as exc:
        st.error(f"🔇 {exc} (Your translation above is still available.)")

# --- Help & troubleshooting ---
with st.expander("❓ Help & troubleshooting"):
    st.markdown(
        "**Supported input**: typed text, or TXT / PDF / CSV / Excel files "
        f"(up to {MAX_INPUT_CHARS:,} characters).\n\n"
        "**Common issues**\n"
        "- *API key rejected* — re-copy the key from "
        "[aistudio.google.com/apikey](https://aistudio.google.com/apikey); "
        "watch for extra spaces.\n"
        "- *Rate limit reached* — free keys allow limited requests per "
        "minute; wait a bit and retry.\n"
        "- *No text extracted from PDF* — scanned/image PDFs need OCR, "
        "which this app doesn't do.\n"
        "- *No audio* — gTTS needs an internet connection; the translated "
        "text still appears and can be copied.\n\n"
        "Both translation and speech require an internet connection."
    )
