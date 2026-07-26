"""App configuration: loads settings from the environment / .env file.

Locally, values come from a .env file. On Streamlit Community Cloud,
they come from the app's Secrets (exposed as environment variables and
via st.secrets).
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _get_setting(name: str, default: str = "") -> str:
    value = os.getenv(name, "")
    if value:
        return value
    try:
        import streamlit as st

        return str(st.secrets.get(name, default))
    except Exception:
        return default


GEMINI_API_KEY = _get_setting("GEMINI_API_KEY")
GEMINI_MODEL = _get_setting("GEMINI_MODEL", "gemini-flash-latest")
