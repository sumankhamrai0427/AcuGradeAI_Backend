"""Text extraction + chunking for uploaded curriculum documents
(master prompt §11/§29). Supports PDF, DOCX, TXT, CSV."""
import csv
import io

from pypdf import PdfReader
from docx import Document as DocxDocument

from utils.errors import ValidationError

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "csv"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB
CHUNK_SIZE_CHARS = 1200
CHUNK_OVERLAP_CHARS = 150


def validate_upload(filename: str, content_length: int):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"Unsupported file type '.{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}")
    if content_length > MAX_FILE_SIZE_BYTES:
        raise ValidationError("File exceeds the 20MB upload limit")
    return ext


def extract_text(file_bytes: bytes, ext: str) -> str:
    if ext == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if ext == "docx":
        doc = DocxDocument(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)
    if ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")
    if ext == "csv":
        text_stream = io.StringIO(file_bytes.decode("utf-8", errors="ignore"))
        reader = csv.reader(text_stream)
        return "\n".join(", ".join(row) for row in reader)
    raise ValidationError(f"No extractor implemented for '.{ext}'")


def clean_text(raw_text: str) -> str:
    lines = [line.strip() for line in raw_text.splitlines()]
    return "\n".join(line for line in lines if line)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE_CHARS, overlap: int = CHUNK_OVERLAP_CHARS) -> list[str]:
    if not text:
        return []
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        chunks.append(text[start:end])
        if end == length:
            break
        start = end - overlap
    return chunks
