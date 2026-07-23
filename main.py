"""Translate & Speak — Streamlit app (capstone project).

Translates text (typed or uploaded as TXT/PDF/CSV/Excel) into a chosen
language with the Gemini API, speaks it with gTTS, and offers the audio
as an MP3 download. Run with:

    streamlit run main.py
"""

import streamlit as st

from app.core.config import GEMINI_API_KEY
from app.core.languages import LANGUAGES
from app.services.translator import translate_text
from app.services.tts import text_to_speech
from app.utils.file_reader import extract_text

st.set_page_config(page_title="Translate & Speak", page_icon="🌍", layout="centered")

st.title("🌍 Translate & Speak")
st.caption(
    "Translate text into another language with Google Gemini, "
    "listen to it with gTTS, and download the audio as MP3."
)

# --- Sidebar: API key ---
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
    st.markdown("---")
    st.markdown(
        "**How to use**\n\n"
        "1. Enter text or upload a file\n"
        "2. Pick a target language\n"
        "3. Click **Translate**\n"
        "4. Play or download the audio"
    )

# --- Input: typed text or uploaded file ---
tab_text, tab_file = st.tabs(["✏️ Enter text", "📄 Upload file"])

source_text = ""

with tab_text:
    typed = st.text_area("Text to translate", height=200, key="typed_text")
    if typed.strip():
        source_text = typed.strip()

with tab_file:
    uploaded = st.file_uploader(
        "Upload a TXT, PDF, CSV, or Excel file",
        type=["txt", "pdf", "csv", "xlsx", "xls"],
    )
    if uploaded is not None:
        try:
            source_text = extract_text(uploaded.name, uploaded.getvalue())
            st.success(f"Extracted {len(source_text):,} characters from {uploaded.name}")
            with st.expander("Preview extracted text"):
                st.text(source_text[:3000] + ("…" if len(source_text) > 3000 else ""))
        except ValueError as exc:
            st.error(str(exc))

# --- Language selection and translation ---
target_language = st.selectbox(
    "Translate into",
    list(LANGUAGES.keys()),
    index=None,
    placeholder="Choose a language",
)

if st.button("Translate", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please provide your Gemini API key in the sidebar.")
    elif not source_text:
        st.error("Please enter some text or upload a file first.")
    elif not target_language:
        st.error("Please choose a target language.")
    else:
        try:
            with st.spinner(f"Translating into {target_language}…"):
                st.session_state.translation = translate_text(
                    source_text, target_language, api_key
                )
                st.session_state.translation_language = target_language
        except Exception as exc:
            st.error(f"Translation failed: {exc}")

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
    except Exception as exc:
        st.error(f"Text-to-speech failed: {exc}")
