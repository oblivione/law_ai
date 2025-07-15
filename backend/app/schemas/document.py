from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentBase(BaseModel):
    title: Optional[str] = None
    document_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    date_published: Optional[datetime] = None
    source: Optional[str] = None

class DocumentCreate(DocumentBase):
    filename: str
    file_size: int
    file_type: str

class DocumentUpdate(DocumentBase):
    processing_status: Optional[str] = None
    legal_concepts: Optional[List[str]] = None
    citations: Optional[List[str]] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None

class DocumentChunk(BaseModel):
    id: int
    chunk_index: int
    text: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    word_count: Optional[int] = None
    char_count: Optional[int] = None
    legal_concepts: Optional[List[str]] = None
    citations: Optional[List[str]] = None
    importance_score: Optional[float] = None
    chunk_summary: Optional[str] = None
    
    class Config:
        from_attributes = True

class Document(DocumentBase):
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    file_type: str
    processing_status: str
    text_extracted: bool
    embeddings_generated: bool
    ai_analysis_completed: bool
    legal_concepts: Optional[List[str]] = None
    citations: Optional[List[str]] = None
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    chunks: Optional[List[DocumentChunk]] = None
    
    class Config:
        from_attributes = True

class DocumentList(BaseModel):
    documents: List[Document]
    total: int
    page: int
    per_page: int

class DocumentUploadResponse(BaseModel):
    message: str
    document_id: int
    filename: str
    processing_status: str

class DocumentProcessingStatus(BaseModel):
    document_id: int
    processing_status: str
    text_extracted: bool
    embeddings_generated: bool
    ai_analysis_completed: bool
    progress_percentage: float
    estimated_completion: Optional[datetime] = None 