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


import re

BOARD_PATTERNS = {
    "CBSE": [r"\bcbse\b", r"central\s+board\s+of\s+secondary\s+education"],
    "ICSE": [r"\bicse\b", r"indian\s+certificate\s+of\s+secondary\s+education"],
    "ISC": [r"\bisc\b", r"indian\s+school\s+certificate\b"],
    "WBBSE": [r"\bwbbse\b", r"west\s+bengal\s+board\s+of\s+secondary", r"\bmadhyamik\b"],
    "WBCHSE": [r"\bwbchse\b", r"west\s+bengal\s+council\s+of\s+higher\s+secondary"],
    "UK-Cambridge": [r"\bcambridge\b", r"\bigcse\b", r"\bcie\b", r"\bcaie\b"],
    "NCERT": [r"\bncert\b", r"national\s+council\s+of\s+educational\s+research"],
    "NEET": [r"\bneet\b", r"national\s+eligibility\s+cum\s+entrance"],
    "IIT": [r"\biit\b", r"\bjee\b", r"joint\s+entrance\s+examination"],
}

CLASS_PATTERNS = {
    "Class 12": [r"\bclass\s*(?:12|xii)\b", r"\bgrade\s*(?:12|xii)\b", r"\bstd\s*(?:12|xii)\b", r"\bclass_12\b", r"\bclass-12\b"],
    "Class 11": [r"\bclass\s*(?:11|xi)\b", r"\bgrade\s*(?:11|xi)\b", r"\bstd\s*(?:11|xi)\b", r"\bclass_11\b", r"\bclass-11\b"],
    "Class 10": [r"\bclass\s*(?:10|x)\b", r"\bgrade\s*(?:10|x)\b", r"\bstd\s*(?:10|x)\b", r"\bclass_10\b", r"\bclass-10\b", r"\bmatric\b"],
    "Class 9": [r"\bclass\s*(?:9|ix)\b", r"\bgrade\s*(?:9|ix)\b", r"\bstd\s*(?:9|ix)\b", r"\bclass_9\b", r"\bclass-9\b"],
    "Class 8": [r"\bclass\s*(?:8|viii)\b", r"\bgrade\s*(?:8|viii)\b", r"\bstd\s*(?:8|viii)\b", r"\bclass_8\b", r"\bclass-8\b"],
    "Class 7": [r"\bclass\s*(?:7|vii)\b", r"\bgrade\s*(?:7|vii)\b", r"\bstd\s*(?:7|vii)\b", r"\bclass_7\b", r"\bclass-7\b"],
    "Class 6": [r"\bclass\s*(?:6|vi)\b", r"\bgrade\s*(?:6|vi)\b", r"\bstd\s*(?:6|vi)\b", r"\bclass_6\b", r"\bclass-6\b"],
    "Class 5": [r"\bclass\s*(?:5|v)\b", r"\bgrade\s*(?:5|v)\b", r"\bstd\s*(?:5|v)\b", r"\bclass_5\b", r"\bclass-5\b"],
    "Class 4": [r"\bclass\s*(?:4|iv)\b", r"\bgrade\s*(?:4|iv)\b", r"\bstd\s*(?:4|iv)\b", r"\bclass_4\b", r"\bclass-4\b"],
    "Class 3": [r"\bclass\s*(?:3|iii)\b", r"\bgrade\s*(?:3|iii)\b", r"\bstd\s*(?:3|iii)\b", r"\bclass_3\b", r"\bclass-3\b"],
    "Class 2": [r"\bclass\s*(?:2|ii)\b", r"\bgrade\s*(?:2|ii)\b", r"\bstd\s*(?:2|ii)\b", r"\bclass_2\b", r"\bclass-2\b"],
    "Class 1": [r"\bclass\s*(?:1|i)\b", r"\bgrade\s*(?:1|i)\b", r"\bstd\s*(?:1|i)\b", r"\bclass_1\b", r"\bclass-1\b"],
}

SUBJECT_PATTERNS = {
    "Mathematics": [r"\bmathematics\b", r"\bmaths\b", r"\bmath\b", r"\balgebra\b", r"\bcalculus\b", r"\bgeometry\b", r"\btrigonometry\b"],
    "Physics": [r"\bphysics\b", r"\bkinematics\b", r"\belectrodynamics\b", r"\bthermodynamics\b", r"\boptics\b"],
    "Chemistry": [r"\bchemistry\b", r"\borganic\s+chemistry\b", r"\binorganic\s+chemistry\b", r"\bchemical\s+bonding\b"],
    "Biology": [r"\bbiology\b", r"\bzoology\b", r"\bbotany\b", r"\bgenetics\b", r"\bhuman\s+anatomy\b"],
    "Computer Science": [r"\bcomputer\s+science\b", r"\binformatics\b", r"\bpython\b", r"\bdata\s+structure\b", r"\bcoding\b"],
    "English": [r"\benglish\b", r"\bgrammar\b", r"\bliterature\b", r"\bprose\b", r"\bpoetry\b"],
    "Social Studies": [r"\bsocial\s+science\b", r"\bsocial\s+studies\b", r"\bhistory\b", r"\bgeography\b", r"\bcivics\b", r"\beconomics\b"],
}


def detect_curriculum_metadata(filename: str, sample_text: str = "") -> dict:
    """Detects Board, ClassGrade, and Subject from filename and header text."""
    combined = f"{filename} {sample_text}"
    # Replace underscores, hyphens, and dots with spaces so word boundary regex matches correctly
    normalized = re.sub(r"[-_.]", " ", combined).lower()
    
    detected_board = None
    for board_name, patterns in BOARD_PATTERNS.items():
        if any(re.search(p, normalized, re.IGNORECASE) for p in patterns):
            detected_board = board_name
            break

    detected_class = None
    for class_name, patterns in CLASS_PATTERNS.items():
        if any(re.search(p, normalized, re.IGNORECASE) for p in patterns):
            detected_class = class_name
            break

    detected_subject = None
    for subject_name, patterns in SUBJECT_PATTERNS.items():
        if any(re.search(p, normalized, re.IGNORECASE) for p in patterns):
            detected_subject = subject_name
            break

    return {
        "board": detected_board,
        "classGrade": detected_class,
        "subject": detected_subject,
    }


def validate_curriculum_metadata(
    filename: str,
    raw_text: str,
    target_board: str | None,
    target_class: str | None,
    target_subject: str | None,
):
    """Validates that target dropdown values match detected content in file/text."""
    sample = raw_text[:10000] if raw_text else ""
    detected = detect_curriculum_metadata(filename, sample)

    # 1. Board mismatch check (NCERT and CBSE share curriculum books, so tolerate CBSE <-> NCERT)
    if target_board and detected["board"]:
        t_board = target_board.upper().strip()
        d_board = detected["board"].upper().strip()
        is_ncert_cbse_compatible = (t_board in ["CBSE", "NCERT"] and d_board in ["CBSE", "NCERT"])
        if t_board != d_board and not is_ncert_cbse_compatible:
            raise ValidationError(
                f"Board Mismatch: Document content/filename indicates '{detected['board']}', "
                f"but '{target_board}' was selected in the dropdown. Please select the matching Board."
            )

    # 2. Class mismatch check
    if target_class and detected["classGrade"]:
        t_class = target_class.lower().replace(" ", "").strip()
        d_class = detected["classGrade"].lower().replace(" ", "").strip()
        if t_class != d_class:
            raise ValidationError(
                f"Class Mismatch: Document content/filename indicates '{detected['classGrade']}', "
                f"but '{target_class}' was selected in the dropdown. Please select '{detected['classGrade']}'."
            )

    # 3. Subject mismatch check
    if target_subject and detected["subject"]:
        t_sub = target_subject.lower().strip()
        d_sub = detected["subject"].lower().strip()
        is_science_compatible = (t_sub == "science" and d_sub in ["physics", "chemistry", "biology", "science"])
        if t_sub != d_sub and not is_science_compatible:
            raise ValidationError(
                f"Subject Mismatch: Document content indicates '{detected['subject']}', "
                f"but '{target_subject}' was selected in the dropdown. Please select '{detected['subject']}'."
            )
