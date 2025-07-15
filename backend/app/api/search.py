from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import time
from loguru import logger

from app.core.database import get_db
from app.schemas.search import (
    SearchQuery,
    SearchResponse,
    SearchResult,
    CitationSearch,
    CitationResult
)
from app.services.search_engine import SearchEngine
from app.services.vector_store import VectorStore

router = APIRouter()

@router.post("/", response_model=SearchResponse)
async def search_documents(
    search_query: SearchQuery,
    db: Session = Depends(get_db)
):
    """Perform document search using semantic, keyword, or hybrid approach"""
    
    start_time = time.time()
    
    try:
        # Initialize search engine
        search_engine = SearchEngine(db)
        
        # Perform search based on type
        if search_query.search_type == "semantic":
            results = await search_engine.semantic_search(
                query=search_query.query,
                limit=search_query.limit,
                offset=search_query.offset,
                filters=search_query.filters
            )
        elif search_query.search_type == "keyword":
            results = await search_engine.keyword_search(
                query=search_query.query,
                limit=search_query.limit,
                offset=search_query.offset,
                filters=search_query.filters
            )
        else:  # hybrid
            results = await search_engine.hybrid_search(
                query=search_query.query,
                limit=search_query.limit,
                offset=search_query.offset,
                filters=search_query.filters
            )
        
        search_time_ms = (time.time() - start_time) * 1000
        
        # Generate search suggestions
        suggestions = await search_engine.get_search_suggestions(search_query.query)
        
        logger.info(f"Search completed: {len(results)} results in {search_time_ms:.2f}ms")
        
        return SearchResponse(
            query=search_query.query,
            results=results,
            total_results=len(results),
            search_time_ms=search_time_ms,
            search_type=search_query.search_type,
            filters_applied=search_query.filters,
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")

@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=2),
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """Get search suggestions based on partial query"""
    
    try:
        search_engine = SearchEngine(db)
        suggestions = await search_engine.get_search_suggestions(query, limit)
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get suggestions")

@router.post("/citations", response_model=List[CitationResult])
async def search_citations(
    citation_search: CitationSearch,
    db: Session = Depends(get_db)
):
    """Search for specific legal citations in documents"""
    
    try:
        search_engine = SearchEngine(db)
        results = await search_engine.search_citations(
            citation=citation_search.citation,
            exact_match=citation_search.exact_match
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Citation search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Citation search failed")

@router.get("/filters")
async def get_available_filters(db: Session = Depends(get_db)):
    """Get available filter options for search"""
    
    try:
        search_engine = SearchEngine(db)
        filters = await search_engine.get_available_filters()
        
        return filters
        
    except Exception as e:
        logger.error(f"Error getting filters: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get filters")

@router.get("/similar/{document_id}")
async def find_similar_documents(
    document_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Find documents similar to a given document"""
    
    try:
        search_engine = SearchEngine(db)
        similar_docs = await search_engine.find_similar_documents(
            document_id=document_id,
            limit=limit
        )
        
        return {"similar_documents": similar_docs}
        
    except Exception as e:
        logger.error(f"Similar documents search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Similar documents search failed")

@router.get("/trending")
async def get_trending_searches(
    limit: int = Query(10, ge=1, le=20),
    timeframe: str = Query("week", regex="^(day|week|month)$"),
    db: Session = Depends(get_db)
):
    """Get trending search queries"""
    
    try:
        search_engine = SearchEngine(db)
        trending = await search_engine.get_trending_searches(limit, timeframe)
        
        return {"trending_searches": trending}
        
    except Exception as e:
        logger.error(f"Error getting trending searches: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get trending searches")

@router.get("/autocomplete")
async def autocomplete_search(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get autocomplete suggestions for search queries"""
    
    try:
        search_engine = SearchEngine(db)
        suggestions = await search_engine.get_autocomplete_suggestions(query, limit)
        
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Autocomplete error: {str(e)}")
        raise HTTPException(status_code=500, detail="Autocomplete failed") 