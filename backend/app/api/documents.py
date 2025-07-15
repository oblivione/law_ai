from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import uuid
from pathlib import Path
from loguru import logger

from app.core.database import get_db
from app.core.config import settings
from app.models.document import Document, DocumentChunk
from app.schemas.document import (
    Document as DocumentSchema, 
    DocumentCreate, 
    DocumentUpdate,
    DocumentList,
    DocumentUploadResponse,
    DocumentProcessingStatus
)
from app.services.document_processor import DocumentProcessor
from app.services.ai_analyzer import AIAnalyzer

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    jurisdiction: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a new legal document for processing"""
    
    # Validate file type
    if not file.filename.lower().endswith(tuple(settings.ALLOWED_EXTENSIONS)):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Supported types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Validate file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )
    
    try:
        # Create upload directory if it doesn't exist
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create document record
        document = Document(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file.size or 0,
            file_type=file_extension.lower(),
            title=title or file.filename,
            document_type=document_type,
            jurisdiction=jurisdiction,
            source=source,
            processing_status="pending"
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Start background processing
        # TODO: Implement Celery task for async processing
        logger.info(f"Document uploaded successfully: {document.id}")
        
        return DocumentUploadResponse(
            message="Document uploaded successfully",
            document_id=document.id,
            filename=file.filename,
            processing_status="pending"
        )
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail="Error uploading document")

@router.get("/", response_model=DocumentList)
async def list_documents(
    page: int = 1,
    per_page: int = 20,
    document_type: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    processing_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all documents with optional filtering"""
    
    query = db.query(Document)
    
    # Apply filters
    if document_type:
        query = query.filter(Document.document_type == document_type)
    if jurisdiction:
        query = query.filter(Document.jurisdiction == jurisdiction)
    if processing_status:
        query = query.filter(Document.processing_status == processing_status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    documents = query.offset(offset).limit(per_page).all()
    
    return DocumentList(
        documents=documents,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/{document_id}", response_model=DocumentSchema)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a specific document by ID"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.put("/{document_id}", response_model=DocumentSchema)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """Update document metadata"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update fields
    for field, value in document_update.dict(exclude_unset=True).items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    
    return document

@router.delete("/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document and its associated data"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Delete file from filesystem
        file_path = Path(document.file_path)
        if file_path.exists():
            file_path.unlink()
        
        # Delete database record (cascades to chunks)
        db.delete(document)
        db.commit()
        
        logger.info(f"Document deleted successfully: {document_id}")
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting document")

@router.post("/{document_id}/process")
async def process_document(document_id: int, db: Session = Depends(get_db)):
    """Manually trigger document processing"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.processing_status == "completed":
        raise HTTPException(status_code=400, detail="Document already processed")
    
    try:
        # Update status to processing
        document.processing_status = "processing"
        db.commit()
        
        # TODO: Trigger async processing task
        logger.info(f"Document processing started: {document_id}")
        
        return {"message": "Document processing started", "document_id": document_id}
        
    except Exception as e:
        logger.error(f"Error starting document processing: {str(e)}")
        raise HTTPException(status_code=500, detail="Error starting document processing")

@router.get("/{document_id}/status", response_model=DocumentProcessingStatus)
async def get_processing_status(document_id: int, db: Session = Depends(get_db)):
    """Get document processing status"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Calculate progress percentage
    progress = 0.0
    if document.text_extracted:
        progress += 33.3
    if document.embeddings_generated:
        progress += 33.3
    if document.ai_analysis_completed:
        progress += 33.4
    
    return DocumentProcessingStatus(
        document_id=document.id,
        processing_status=document.processing_status,
        text_extracted=document.text_extracted,
        embeddings_generated=document.embeddings_generated,
        ai_analysis_completed=document.ai_analysis_completed,
        progress_percentage=progress
    )

@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: int,
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db)
):
    """Get chunks for a specific document"""
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    query = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id)
    total = query.count()
    
    offset = (page - 1) * per_page
    chunks = query.offset(offset).limit(per_page).all()
    
    return {
        "document_id": document_id,
        "chunks": chunks,
        "total": total,
        "page": page,
        "per_page": per_page
    } 