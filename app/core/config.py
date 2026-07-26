"""App configuration: loads settings from the environment / .env file.

Locally, values come from a .env file. On Streamlit Community Cloud,
they come from the app's Secrets (st.secrets). Settings are read via
functions, not import-time constants, so a secret added or changed
after startup is picked up on the next rerun.
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


def get_gemini_api_key() -> str:
    return _get_setting("GEMINI_API_KEY")


def get_gemini_model() -> str:
    return _get_setting("GEMINI_MODEL", "gemini-flash-latest")
