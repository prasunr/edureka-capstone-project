"""Extract plain text from uploaded files (TXT, PDF, CSV, Excel)."""

from io import BytesIO, StringIO

import pandas as pd
from pypdf import PdfReader
from pypdf.errors import PyPdfError


def extract_text(filename: str, data: bytes) -> str:
    """Return the text content of an uploaded file given its name and bytes.

    Raises ValueError with a user-friendly message for unsupported or
    unreadable files.
    """
    name = filename.lower()

    if not data:
        raise ValueError(f"'{filename}' is empty — there is nothing to translate.")

    if name.endswith(".txt"):
        text = data.decode("utf-8", errors="replace").strip()
        if not text:
            raise ValueError(f"'{filename}' contains no text.")
        return text

    if name.endswith(".pdf"):
        try:
            reader = PdfReader(BytesIO(data))
            pages = [page.extract_text() or "" for page in reader.pages]
        except PyPdfError as exc:
            raise ValueError(
                f"'{filename}' could not be read — it may be corrupted or "
                "password-protected."
            ) from exc
        text = "\n".join(pages).strip()
        if not text:
            raise ValueError(
                f"No text could be extracted from '{filename}'. It may be a "
                "scanned/image-only PDF, which isn't supported."
            )
        return text

    if name.endswith(".csv"):
        try:
            df = pd.read_csv(StringIO(data.decode("utf-8", errors="replace")))
        except Exception as exc:
            raise ValueError(
                f"'{filename}' could not be parsed as CSV — check that it is "
                "a valid comma-separated file."
            ) from exc
        if df.empty:
            raise ValueError(f"'{filename}' has no rows to translate.")
        return df.to_string(index=False)

    if name.endswith((".xlsx", ".xls")):
        try:
            df = pd.read_excel(BytesIO(data))
        except Exception as exc:
            raise ValueError(
                f"'{filename}' could not be opened as an Excel file — it may "
                "be corrupted or in an unsupported format."
            ) from exc
        if df.empty:
            raise ValueError(f"'{filename}' has no rows to translate.")
        return df.to_string(index=False)

    raise ValueError(
        f"Unsupported file type: '{filename}'. "
        "Please upload a TXT, PDF, CSV, or Excel file."
    )
