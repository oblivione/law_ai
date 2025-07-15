from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class SearchQuery(BaseModel):
    query: str
    search_type: str = "hybrid"  # semantic, keyword, hybrid
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10
    offset: int = 0
    
    @validator('search_type')
    def validate_search_type(cls, v):
        if v not in ['semantic', 'keyword', 'hybrid']:
            raise ValueError('search_type must be one of: semantic, keyword, hybrid')
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if v > 50:
            raise ValueError('limit cannot exceed 50')
        return v

class SearchFilter(BaseModel):
    document_type: Optional[List[str]] = None
    jurisdiction: Optional[List[str]] = None
    date_range: Optional[Dict[str, datetime]] = None
    legal_concepts: Optional[List[str]] = None
    citations: Optional[List[str]] = None

class SearchResult(BaseModel):
    document_id: int
    chunk_id: Optional[int] = None
    document_title: str
    document_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    chunk_text: Optional[str] = None
    semantic_score: Optional[float] = None
    keyword_score: Optional[float] = None
    final_score: float
    highlighted_text: Optional[str] = None
    legal_concepts: Optional[List[str]] = None
    citations: Optional[List[str]] = None
    page_number: Optional[int] = None
    section_title: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: float
    search_type: str
    filters_applied: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None

class LegalAnalysisQuery(BaseModel):
    query: str
    context_documents: Optional[List[int]] = None  # Document IDs for context
    analysis_type: str = "general"  # general, case_law, statute, precedent
    include_citations: bool = True
    include_counterarguments: bool = True

class LegalAnalysisResponse(BaseModel):
    query: str
    analysis: str
    key_points: List[str]
    relevant_citations: List[str]
    precedents: List[str]
    counterarguments: Optional[List[str]] = None
    confidence_score: float
    sources_used: List[int]  # Document IDs used for analysis
    reasoning_chain: List[str]

class CitationSearch(BaseModel):
    citation: str
    exact_match: bool = False

class CitationResult(BaseModel):
    citation: str
    document_id: int
    document_title: str
    context: str
    page_number: Optional[int] = None
    confidence_score: float 