from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    
    # Document metadata
    title = Column(String(500))
    document_type = Column(String(100))  # court_decision, statute, regulation, etc.
    jurisdiction = Column(String(100))
    date_published = Column(DateTime)
    source = Column(String(200))
    
    # Processing status
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    text_extracted = Column(Boolean, default=False)
    embeddings_generated = Column(Boolean, default=False)
    ai_analysis_completed = Column(Boolean, default=False)
    
    # AI-generated metadata
    legal_concepts = Column(JSON)  # List of extracted legal concepts
    citations = Column(JSON)  # List of legal citations found
    summary = Column(Text)  # AI-generated summary
    key_points = Column(JSON)  # List of key legal points
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    search_results = relationship("SearchResult", back_populates="document")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # Chunk content
    text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order within document
    page_number = Column(Integer)
    section_title = Column(String(200))
    
    # Chunk metadata
    word_count = Column(Integer)
    char_count = Column(Integer)
    
    # Vector embeddings (stored as JSON for simplicity)
    embedding = Column(JSON)  # Vector embedding
    embedding_model = Column(String(100))  # Model used for embedding
    
    # AI analysis
    legal_concepts = Column(JSON)  # Legal concepts in this chunk
    citations = Column(JSON)  # Citations found in this chunk
    importance_score = Column(Float)  # AI-assigned importance score
    chunk_summary = Column(Text)  # AI-generated chunk summary
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chunks")

class SearchResult(Base):
    __tablename__ = "search_results"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_id = Column(Integer, ForeignKey("document_chunks.id"))
    
    # Search scores
    semantic_score = Column(Float)  # Semantic similarity score
    keyword_score = Column(Float)  # Keyword matching score
    final_score = Column(Float)  # Combined final score
    
    # Search metadata
    search_type = Column(String(50))  # semantic, keyword, hybrid
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="search_results")
    chunk = relationship("DocumentChunk") 