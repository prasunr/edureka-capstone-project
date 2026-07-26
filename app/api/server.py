"""REST API exposing translation, text-to-speech, and file extraction.

Intended for a future non-Python frontend (Angular/React). Run with:

    uvicorn app.api.server:app --reload
"""

from io import BytesIO

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.config import get_gemini_api_key
from app.core.languages import LANGUAGES
from app.services.translator import translate_text
from app.services.tts import text_to_speech
from app.utils.file_reader import extract_text

app = FastAPI(title="GenAI Doc Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TranslateRequest(BaseModel):
    text: str
    target_language: str


class TranslateResponse(BaseModel):
    translated_text: str
    target_language: str
    tts_lang_code: str


@app.get("/languages")
def list_languages() -> dict[str, str]:
    """Supported target languages mapped to their gTTS codes."""
    return LANGUAGES


@app.post("/translate", response_model=TranslateResponse)
def translate(req: TranslateRequest) -> TranslateResponse:
    if req.target_language not in LANGUAGES:
        raise HTTPException(400, f"Unsupported language: {req.target_language}")
    if not req.text.strip():
        raise HTTPException(400, "Text must not be empty.")
    api_key = get_gemini_api_key()
    if not api_key:
        raise HTTPException(500, "GEMINI_API_KEY is not configured on the server.")
    try:
        translated = translate_text(req.text, req.target_language, api_key)
    except Exception as exc:
        raise HTTPException(502, f"Translation failed: {exc}") from exc
    return TranslateResponse(
        translated_text=translated,
        target_language=req.target_language,
        tts_lang_code=LANGUAGES[req.target_language],
    )


@app.post("/tts")
def tts(req: TranslateRequest) -> StreamingResponse:
    """Convert text to speech; target_language selects the voice."""
    if req.target_language not in LANGUAGES:
        raise HTTPException(400, f"Unsupported language: {req.target_language}")
    try:
        audio = text_to_speech(req.text, LANGUAGES[req.target_language])
    except Exception as exc:
        raise HTTPException(502, f"Text-to-speech failed: {exc}") from exc
    return StreamingResponse(
        BytesIO(audio),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=translation.mp3"},
    )


@app.post("/extract-text")
async def extract(file: UploadFile) -> dict[str, str]:
    """Extract plain text from an uploaded TXT/PDF/CSV/Excel file."""
    data = await file.read()
    try:
        text = extract_text(file.filename or "", data)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"filename": file.filename or "", "text": text}
