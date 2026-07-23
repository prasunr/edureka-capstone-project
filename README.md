# 🌍 GenAI Doc Assistant — Translate & Speak

Capstone project: a Streamlit web app that translates text into 25
languages using the **Google Gemini API**, converts the translation to
speech with **gTTS**, and lets you play or download the audio as MP3.
The same translation/TTS logic is also exposed as a **FastAPI** REST API
for a future Angular/React frontend.

## Features

- Type text directly **or** upload a file: TXT, PDF, CSV, or Excel
- Choose a target language from a dropdown (25 languages)
- Context-aware translation via Gemini (`gemini-2.5-flash`)
- Listen to the translation in the browser
- Download the audio as an MP3 file

## Project structure

```
genai-doc-assistant/
├── main.py                    # Streamlit UI (entry point)
├── app/
│   ├── api/server.py          # FastAPI REST endpoints
│   ├── core/config.py         # .env loading, model settings
│   ├── core/languages.py      # Supported languages + gTTS codes
│   ├── services/translator.py # Gemini API translation
│   ├── services/tts.py        # gTTS text-to-speech
│   ├── agents/                # (reserved for future agent logic)
│   └── utils/file_reader.py   # Text extraction from TXT/PDF/CSV/Excel
├── data/                      # Input files (not committed)
├── requirements.txt
└── .env.example
```

## Setup

1. **Create and activate the virtual environment, install dependencies**

   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Add your Gemini API key**

   Get a free key at <https://aistudio.google.com/apikey>, then:

   ```bash
   cp .env.example .env
   # edit .env and paste your key
   ```

   (Alternatively, paste the key into the sidebar while the app is running.)

3. **Run the Streamlit app**

   ```bash
   streamlit run main.py
   ```

   The app opens at <http://localhost:8501>.

4. **(Optional) Run the REST API** — for a non-Python frontend:

   ```bash
   uvicorn app.api.server:app --reload
   ```

   Interactive docs at <http://localhost:8000/docs>. Endpoints:
   `GET /languages`, `POST /translate`, `POST /tts`, `POST /extract-text`.

## Notes

- Both Gemini and gTTS require an internet connection.
- The language list is limited to languages gTTS can speak; Gemini can
  translate into many more.
- Scanned/image-only PDFs are not supported (no OCR).
