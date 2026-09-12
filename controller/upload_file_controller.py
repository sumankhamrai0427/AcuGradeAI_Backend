import os
from uuid import uuid4

from flask import request, g
from werkzeug.utils import secure_filename

from database.dbConnection import get_session
from helper.rag_ingestion import ingest_document
from middleware.authMiddleware import token_required
from middleware.roleMiddleware import roles_required
from model.models import Document
from utils.errors import ValidationError
from utils.response import success
from utils.config import config


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@token_required
@roles_required("ADMIN", "SUPER_ADMIN", "AUTHOR")
def upload_blog_image():
    if "file" not in request.files:
        raise ValidationError("No image file supplied")
    image = request.files["file"]
    if not image.filename or image.mimetype not in ALLOWED_IMAGE_TYPES:
        raise ValidationError("Only JPG, PNG, WEBP, and GIF images are supported")

    filename = f"{uuid4().hex}_{secure_filename(image.filename)}"
    upload_dir = os.path.join(config.UPLOAD_DIR, "blogs")
    os.makedirs(upload_dir, exist_ok=True)
    image.save(os.path.join(upload_dir, filename))
    return success({"url": f"/uploads/blogs/{filename}", "filename": filename}, 201)


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


@token_required
@roles_required("ADMIN", "SUPER_ADMIN")
def get_rag_status():
    """Returns overview of ChromaDB vector store and indexed curriculum documents."""
    from sqlalchemy import text
    from database import vector_db

    with get_session() as session:
        total_docs = session.execute(text("SELECT COUNT(*) FROM documents")).scalar() or 0
        total_chunks = session.execute(text("SELECT COUNT(*) FROM document_chunks")).scalar() or 0
        total_runbooks = session.execute(text("SELECT COUNT(*) FROM runbooks WHERE status = 'PUBLISHED'")).scalar() or 0

        # Query all documents with chunk count
        docs_sql = text("""
            SELECT 
                d.id, d.filename, d.content_type, d.board, d.class_grade, d.subject,
                d.status, d.created_at,
                COUNT(dc.id) AS chunk_count
            FROM documents d
            LEFT JOIN document_chunks dc ON dc.document_id = d.id
            GROUP BY d.id, d.filename, d.content_type, d.board, d.class_grade, d.subject, d.status, d.created_at
            ORDER BY d.created_at DESC
        """)
        rows = session.execute(docs_sql).mappings().fetchall()

        docs_list = []
        for r in rows:
            docs_list.append({
                "id": r["id"],
                "filename": r["filename"],
                "content_type": r["content_type"],
                "board": r["board"],
                "classGrade": r["class_grade"],
                "subject": r["subject"],
                "status": r["status"],
                "chunk_count": r["chunk_count"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None
            })

        return success({
            "vector_store_enabled": vector_db.is_enabled(),
            "total_documents": total_docs,
            "total_chunks": total_chunks,
            "total_runbooks": total_runbooks,
            "documents": docs_list
        })


@token_required
@roles_required("ADMIN", "SUPER_ADMIN")
def delete_rag_document(document_id):
    """Deletes a document, its chunks from MySQL and vectors from ChromaDB."""
    from sqlalchemy import text
    from model.models import Document, DocumentChunk
    from database import vector_db

    with get_session() as session:
        document = session.get(Document, document_id)
        if not document:
            raise ValidationError("Document not found")

        # Fetch chunk vector ids to clean up ChromaDB
        chunks = session.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
        vector_ids = [c.vector_id for c in chunks if c.vector_id]

        if vector_ids and vector_db.is_enabled():
            try:
                # Remove from ChromaDB if client supports delete
                collection = vector_db.get_collection()
                collection.delete(ids=vector_ids)
            except Exception:
                pass

        session.delete(document)
        session.commit()

        return success({"deleted": True, "id": document_id})

