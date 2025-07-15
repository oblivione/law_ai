from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import time
from loguru import logger

from app.core.database import get_db
from app.schemas.search import (
    LegalAnalysisQuery,
    LegalAnalysisResponse
)
from app.services.ai_analyzer import AIAnalyzer
from app.services.search_engine import SearchEngine

router = APIRouter()

@router.post("/legal-reasoning", response_model=LegalAnalysisResponse)
async def perform_legal_analysis(
    analysis_query: LegalAnalysisQuery,
    db: Session = Depends(get_db)
):
    """Perform comprehensive legal analysis using AI reasoning"""
    
    try:
        # Initialize AI analyzer
        ai_analyzer = AIAnalyzer()
        search_engine = SearchEngine(db)
        
        # Get relevant context from documents
        if analysis_query.context_documents:
            # Use specified documents as context
            context_docs = await search_engine.get_documents_by_ids(
                analysis_query.context_documents
            )
        else:
            # Search for relevant documents based on query
            search_results = await search_engine.hybrid_search(
                query=analysis_query.query,
                limit=10
            )
            context_docs = [result.chunk_text for result in search_results if result.chunk_text]
        
        # Perform AI analysis
        analysis_result = await ai_analyzer.perform_legal_reasoning(
            query=analysis_query.query,
            context=context_docs,
            analysis_type=analysis_query.analysis_type,
            include_citations=analysis_query.include_citations,
            include_counterarguments=analysis_query.include_counterarguments
        )
        
        logger.info(f"Legal analysis completed for query: {analysis_query.query[:50]}...")
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Legal analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Legal analysis failed")

@router.post("/document-summary/{document_id}")
async def generate_document_summary(
    document_id: int,
    summary_type: str = "comprehensive",  # comprehensive, executive, key_points
    max_length: int = 1000,
    db: Session = Depends(get_db)
):
    """Generate AI-powered summary of a specific document"""
    
    try:
        ai_analyzer = AIAnalyzer()
        
        # Get document content
        search_engine = SearchEngine(db)
        document_content = await search_engine.get_document_content(document_id)
        
        if not document_content:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Generate summary
        summary = await ai_analyzer.generate_document_summary(
            content=document_content,
            summary_type=summary_type,
            max_length=max_length
        )
        
        return {
            "document_id": document_id,
            "summary_type": summary_type,
            "summary": summary,
            "generated_at": time.time()
        }
        
    except Exception as e:
        logger.error(f"Document summary error: {str(e)}")
        raise HTTPException(status_code=500, detail="Document summary generation failed")

@router.post("/extract-entities/{document_id}")
async def extract_legal_entities(
    document_id: int,
    entity_types: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """Extract legal entities from a document"""
    
    try:
        ai_analyzer = AIAnalyzer()
        search_engine = SearchEngine(db)
        
        # Get document content
        document_content = await search_engine.get_document_content(document_id)
        
        if not document_content:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Extract entities
        entities = await ai_analyzer.extract_legal_entities(
            content=document_content,
            entity_types=entity_types
        )
        
        return {
            "document_id": document_id,
            "entities": entities,
            "extracted_at": time.time()
        }
        
    except Exception as e:
        logger.error(f"Entity extraction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Entity extraction failed")

@router.post("/compare-documents")
async def compare_documents(
    document_ids: List[int],
    comparison_type: str = "similarity",  # similarity, differences, legal_alignment
    db: Session = Depends(get_db)
):
    """Compare multiple legal documents using AI analysis"""
    
    if len(document_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 documents required for comparison")
    
    if len(document_ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 documents allowed for comparison")
    
    try:
        ai_analyzer = AIAnalyzer()
        search_engine = SearchEngine(db)
        
        # Get document contents
        documents = []
        for doc_id in document_ids:
            content = await search_engine.get_document_content(doc_id)
            if content:
                documents.append({"id": doc_id, "content": content})
        
        if len(documents) < 2:
            raise HTTPException(status_code=404, detail="Some documents not found")
        
        # Perform comparison
        comparison_result = await ai_analyzer.compare_documents(
            documents=documents,
            comparison_type=comparison_type
        )
        
        return {
            "document_ids": document_ids,
            "comparison_type": comparison_type,
            "comparison_result": comparison_result,
            "compared_at": time.time()
        }
        
    except Exception as e:
        logger.error(f"Document comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail="Document comparison failed")

@router.post("/generate-brief")
async def generate_legal_brief(
    topic: str,
    document_ids: Optional[List[int]] = None,
    jurisdiction: Optional[str] = None,
    brief_type: str = "research",  # research, argument, motion
    max_length: int = 2000,
    db: Session = Depends(get_db)
):
    """Generate a legal brief on a specific topic"""
    
    try:
        ai_analyzer = AIAnalyzer()
        search_engine = SearchEngine(db)
        
        # Get relevant documents
        if document_ids:
            relevant_docs = []
            for doc_id in document_ids:
                content = await search_engine.get_document_content(doc_id)
                if content:
                    relevant_docs.append(content)
        else:
            # Search for relevant documents
            search_results = await search_engine.hybrid_search(
                query=topic,
                limit=15,
                filters={"jurisdiction": [jurisdiction]} if jurisdiction else None
            )
            relevant_docs = [result.chunk_text for result in search_results if result.chunk_text]
        
        # Generate brief
        brief = await ai_analyzer.generate_legal_brief(
            topic=topic,
            relevant_documents=relevant_docs,
            brief_type=brief_type,
            jurisdiction=jurisdiction,
            max_length=max_length
        )
        
        return {
            "topic": topic,
            "brief_type": brief_type,
            "jurisdiction": jurisdiction,
            "brief": brief,
            "sources_count": len(relevant_docs),
            "generated_at": time.time()
        }
        
    except Exception as e:
        logger.error(f"Brief generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Legal brief generation failed")

@router.get("/analytics/document/{document_id}")
async def get_document_analytics(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get analytics and insights for a specific document"""
    
    try:
        ai_analyzer = AIAnalyzer()
        search_engine = SearchEngine(db)
        
        # Get document and its metadata
        document = await search_engine.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Generate analytics
        analytics = await ai_analyzer.generate_document_analytics(document)
        
        return analytics
        
    except Exception as e:
        logger.error(f"Document analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Document analytics generation failed") 