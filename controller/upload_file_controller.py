from flask import request, g

from database.dbConnection import get_session
from helper.rag_ingestion import ingest_document
from middleware.authMiddleware import token_required
from middleware.roleMiddleware import roles_required
from model.models import Document
from utils.errors import ValidationError
from utils.response import success


@token_required
@roles_required("ADMIN", "SUPER_ADMIN")
def upload_file():
    if "file" not in request.files:
        raise ValidationError("No file part in the request")
    file = request.files["file"]
    if not file.filename:
        raise ValidationError("No file selected")

    file_bytes = file.read()

    with get_session() as session:
        document = ingest_document(
            session,
            filename=file.filename,
            file_bytes=file_bytes,
            content_type=file.mimetype or "application/octet-stream",
            board=request.form.get("board"),
            class_grade=request.form.get("classGrade"),
            subject=request.form.get("subject"),
            runbook_id=request.form.get("runbookId"),
            uploaded_by=g.current_user_id,
        )
        return success({
            "id": document.id, "filename": document.filename, "status": document.status,
        }, 201)


@token_required
@roles_required("ADMIN", "SUPER_ADMIN")
def get_document_status(document_id):
    with get_session() as session:
        document = session.get(Document, document_id)
        if not document:
            raise ValidationError("Document not found")
        return success({
            "id": document.id, "filename": document.filename, "status": document.status,
            "board": document.board, "classGrade": document.class_grade, "subject": document.subject,
        })

