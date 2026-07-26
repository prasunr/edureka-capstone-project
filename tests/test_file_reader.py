"""Offline tests for text extraction across all supported file types."""

from pathlib import Path

import pytest

from app.utils.file_reader import extract_text

FIXTURES = Path(__file__).parent / "fixtures"


def load(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


class TestSupportedTypes:
    def test_txt_with_unicode(self):
        text = extract_text("sample.txt", load("sample.txt"))
        assert "crème brûlée" in text
        assert "你好" in text and "नमस्ते" in text

    def test_pdf(self):
        text = extract_text("sample.pdf", load("sample.pdf"))
        assert "quick brown fox" in text
        assert "$1,234.56" in text

    def test_csv_with_unicode(self):
        text = extract_text("sample.csv", load("sample.csv"))
        assert "Café latte" in text and "绿茶" in text

    def test_xlsx(self):
        text = extract_text("sample.xlsx", load("sample.xlsx"))
        assert "Hyderabad" in text and "São Paulo" in text

    def test_legacy_xls(self):
        text = extract_text("sample.xls", load("sample.xls"))
        assert "Alice" in text and "91" in text

    def test_uppercase_extension(self):
        text = extract_text("SAMPLE.TXT", load("sample.txt"))
        assert "café" in text


class TestErrorPaths:
    def test_empty_file(self):
        with pytest.raises(ValueError, match="empty"):
            extract_text("empty.txt", b"")

    def test_whitespace_only_txt(self):
        with pytest.raises(ValueError, match="no text"):
            extract_text("blank.txt", b"   \n\n  ")

    def test_corrupt_pdf(self):
        with pytest.raises(ValueError, match="corrupted|could not be read"):
            extract_text("broken.pdf", b"not a real pdf")

    def test_unsupported_type(self):
        with pytest.raises(ValueError, match="Unsupported"):
            extract_text("notes.docx", b"abc")

    def test_empty_csv(self):
        with pytest.raises(ValueError, match="no rows"):
            extract_text("empty.csv", b"col_a,col_b\n")
