# Translate & Speak — Project Documentation

Capstone project: a Streamlit web application that translates text into
25 languages using the Google Gemini API, converts the translation to
speech with gTTS, and offers the audio as an MP3 download.

- **Live app:** deployed on Streamlit Community Cloud (auto-redeploys on
  every push to `master`)
- **Repository:** <https://github.com/prasunr/edureka-capstone-project>

---

## 1. Setup

### 1.1 Prerequisites

- Python 3.10 or newer (developed and tested on Python 3.14)
- An internet connection (both Gemini and gTTS are online services)
- A Google Gemini API key (free) — see below

### 1.2 Getting a Gemini API key

1. Visit <https://aistudio.google.com/apikey> and sign in with a Google
   account.
2. Click **Create API key** and copy the generated key (starts with
   `AIza…`).
3. The free tier is sufficient for this app; no billing setup is needed.

### 1.3 Local installation

```bash
git clone https://github.com/prasunr/edureka-capstone-project.git
cd edureka-capstone-project
python3 -m venv venv
source venv/bin/activate          # Windows PowerShell: venv\Scripts\activate
pip install -r requirements.txt
```

### 1.4 Configuring the API key

Two options — pick either:

- **`.env` file (recommended):**

  ```bash
  cp .env.example .env
  # open .env and replace the placeholder with your real key
  ```

- **Sidebar input:** skip the `.env` file and paste the key into the
  "Gemini API key" field in the app's sidebar each time you run it.

The key is never committed to git (`.env` is in `.gitignore`) and never
leaves your machine except in requests to Google's API.

### 1.5 Running

```bash
streamlit run main.py            # opens http://localhost:8501
```

Optional REST API (for non-Python frontends):

```bash
uvicorn app.api.server:app --reload   # docs at http://localhost:8000/docs
```

### 1.6 Running the tests

```bash
pip install -r requirements-dev.txt
python -m pytest tests/
```

### 1.7 Cloud deployment (Streamlit Community Cloud)

1. Sign in at <https://share.streamlit.io> with GitHub.
2. **Create app** → repo `prasunr/edureka-capstone-project`, branch
   `master`, main file `main.py`.
3. **Advanced settings → Secrets** → add
   `GEMINI_API_KEY = "your-key"` (TOML syntax, quotes required).
4. **Deploy.** Later pushes to `master` redeploy automatically, and
   secrets changes are picked up without a reboot (see §4.3).

---

## 2. Using the app

1. **Provide input** — either type/paste text in the **Enter text** tab,
   or switch to **Upload file** and upload a TXT, PDF, CSV, or Excel
   file. Extracted text can be previewed under "Preview extracted text".
2. **Pick a target language** from the dropdown (25 languages, all of
   which support audio).
3. **Click Translate.** The translated text appears below.
4. **Listen or download** — an audio player renders the speech in the
   browser; **Download MP3** saves it as a file.

Guardrails you may encounter:

| Situation | Behaviour |
|---|---|
| No API key | Error asking for the key, with a link to get one |
| Empty input / no language chosen | Clear inline error |
| Input over 50,000 characters | Blocked, with advice to split the text |
| Input over 5,000 characters | Warning that audio generation is slow |
| Invalid/corrupt/scanned-image files | Friendly per-cause error message |
| Gemini rate limit or outage | Plain-language explanation, retry advice |
| gTTS failure | Error shown, but the text translation is preserved |

---

## 3. Considerations and limitations

### 3.1 Design considerations

- **Model choice:** the app uses the `gemini-flash-latest` alias rather
  than a pinned model name, so Google's model retirements don't break
  it. Override with `GEMINI_MODEL` in `.env`/secrets if needed.
- **Language list:** Gemini can translate into far more than 25
  languages, but the dropdown only offers languages gTTS can also
  *speak*, so every translation can produce audio.
- **Prompting:** the translation prompt instructs Gemini to preserve
  numbers, dates, times, currency, and nuances (e.g. a *rescheduled*
  meeting vs a *scheduled* one), translate idioms to natural
  equivalents, and return only the translation — no commentary.
- **Separation of concerns:** UI (`main.py`), services
  (`app/services/`), file parsing (`app/utils/`), configuration
  (`app/core/`), and a REST API (`app/api/`) are separate modules, so a
  future Angular/React frontend can reuse everything except the UI.
- **Security:** the API key lives in `.env` locally or Streamlit
  Secrets in the cloud; both are excluded from version control.

### 3.2 Known limitations

- **Scanned PDFs:** image-only PDFs have no extractable text; OCR is
  not implemented. The app detects this and explains it.
- **gTTS voice quality:** gTTS offers one standard voice per language —
  no voice selection, speed control, or SSML. It also calls an
  unofficial Google endpoint that may throttle heavy use.
- **Free-tier rate limits:** the free Gemini tier allows a limited
  number of requests per minute; bursts of translations can hit 429
  errors (surfaced with a friendly message).
- **Input cap:** 50,000 characters per request, mainly to keep audio
  generation times and API usage reasonable.
- **Tabular files:** CSV/Excel content is translated as a text table;
  the output is translated text, not a translated spreadsheet file.
- **Internet required:** both translation and speech need connectivity;
  nothing works offline.

---

## 4. Challenges faced during development

Real issues encountered and how they were solved:

### 4.1 Dependency pins vs Python 3.14

The initial `requirements.txt` pinned 2023-era versions
(`pandas==2.1.0`, `numpy==1.25.0`). These predate Python 3.14, so pip
had no pre-built wheels and attempted a source build that failed with
hundreds of Cython errors. **Fix:** move to minimum-version constraints
(`pandas>=2.3.3`, …) so pip resolves versions with wheels for the
running interpreter. **Lesson:** exact pins from tutorials age badly;
pin *minimums* (or use a lock file generated on your own machine).

### 4.2 Gemini model retirement (404)

The app initially hardcoded `gemini-2.5-flash`, which Google had
retired for newly created API keys — every translation failed with a
404. **Fix:** query `client.models.list()` to see what the key could
actually access, and switch to the `gemini-flash-latest` alias that
Google keeps pointed at the current model. **Lesson:** never hardcode
model IDs; use provider aliases and verify with the models endpoint.

### 4.3 Streamlit Cloud secrets invisible after deploy

After deployment, the app kept asking for the API key even though the
secret was saved. Cause: the key was read **once at import time**, and
the secret was added *after* the server process had started — a browser
refresh does not restart the process. **Fix:** read configuration
lazily (a `get_gemini_api_key()` function called on each rerun, checking
environment variables first and `st.secrets` second). **Lesson:**
read runtime configuration at call time, not import time.

### 4.4 Legacy `.xls` uploads silently broken

The uploader accepted `.xls` files, but pandas needs the `xlrd` library
for that legacy format, which wasn't installed — every `.xls` failed
with a misleading "file may be corrupted" error. Found while testing
each advertised file type with real fixture files. **Fix:** add
`xlrd>=2.0` to requirements. **Lesson:** test every input type you
advertise, not just the common ones.

### 4.5 Translation nuance loss (Hindi)

A Gemini-based quality audit of six languages flagged that the Hindi
translation of "our meeting **moved to** 3:30 PM" read as "has been
**scheduled**", losing the fact that the time had *changed*. **Fix:**
strengthen the prompt to demand exact preservation of numbers, dates,
times, currency, and "nuances such as changes of plan". Retest passed.
**Lesson:** LLM translation quality needs verification (e.g.
back-translation audits), and prompts benefit from explicit,
example-driven precision requirements.

### 4.6 Raw API errors are hostile to users

Early failures surfaced raw payloads like
`404 NOT_FOUND {'error': {...}}` directly in the UI. **Fix:** map
failures by HTTP status (invalid key, model unavailable, rate limit,
server error, no connectivity) to plain-language messages with a next
step, and keep the translated text visible even when audio generation
fails. **Lesson:** catch errors at the service boundary and translate
them for humans.

---

## 5. Project structure

```
genai-doc-assistant/
├── main.py                    # Streamlit UI (entry point)
├── app/
│   ├── api/server.py          # FastAPI REST endpoints (optional)
│   ├── core/config.py         # env/.env/st.secrets settings (lazy)
│   ├── core/languages.py      # 25 languages + gTTS codes
│   ├── services/translator.py # Gemini translation + friendly errors
│   ├── services/tts.py        # gTTS speech + friendly errors
│   └── utils/file_reader.py   # TXT/PDF/CSV/Excel text extraction
├── tests/                     # pytest suite (13 tests) + fixtures
├── requirements.txt           # runtime dependencies
├── requirements-dev.txt       # test/dev dependencies
├── .env.example               # API key template
└── DOCUMENTATION.md           # this file
```
