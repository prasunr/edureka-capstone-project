"""Extract plain text from uploaded files (TXT, PDF, CSV, Excel)."""

from io import BytesIO, StringIO

import pandas as pd
from pypdf import PdfReader


def extract_text(filename: str, data: bytes) -> str:
    """Return the text content of an uploaded file given its name and bytes.

    Raises ValueError for unsupported or unreadable files.
    """
    name = filename.lower()

    if name.endswith(".txt"):
        return data.decode("utf-8", errors="replace")

    if name.endswith(".pdf"):
        reader = PdfReader(BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
        if not text:
            raise ValueError(
                "No text could be extracted from this PDF. "
                "It may be a scanned/image-only document."
            )
        return text

    if name.endswith(".csv"):
        df = pd.read_csv(StringIO(data.decode("utf-8", errors="replace")))
        return df.to_string(index=False)

    if name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(BytesIO(data))
        return df.to_string(index=False)

    raise ValueError(f"Unsupported file type: {filename}")
