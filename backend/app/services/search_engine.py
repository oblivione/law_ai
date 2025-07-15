from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Dict, Any, Optional
import re
from loguru import logger

from app.models.document import Document, DocumentChunk, SearchResult
from app.services.vector_store import VectorStore
from app.schemas.search import SearchResult as SearchResultSchema, CitationResult

class SearchEngine:
    """Orchestrates document search combining semantic, keyword, and hybrid approaches"""
    
    def __init__(self, db: Session):
        self.db = db
        self.vector_store = VectorStore()
    
    async def semantic_search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResultSchema]:
        """Perform semantic search using vector similarity"""
        try:
            # Get semantic results from vector store
            vector_results = await self.vector_store.semantic_search(
                query=query,
                limit=limit + offset,
                filters=filters
            )
            
            # Convert to SearchResult schema and apply offset
            search_results = []
            for i, result in enumerate(vector_results[offset:offset + limit]):
                # Get document information from database
                document = self.db.query(Document).filter(
                    Document.id == result['document_id']
                ).first()
                
                if document:
                    search_result = SearchResultSchema(
                        document_id=result['document_id'],
                        chunk_id=result.get('chunk_index'),
                        document_title=document.title or document.original_filename,
                        document_type=document.document_type,
                        jurisdiction=document.jurisdiction,
                        chunk_text=result['text'],
                        semantic_score=result['similarity_score'],
                        keyword_score=None,
                        final_score=result['similarity_score'],
                        highlighted_text=self._highlight_text(result['text'], query),
                        legal_concepts=result.get('legal_concepts', []),
                        citations=result.get('citations', []),
                        page_number=result.get('page_number'),
                        section_title=None
                    )
                    search_results.append(search_result)
            
            # Log search for analytics
            await self._log_search(query, search_results, "semantic")
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []
    
    async def keyword_search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResultSchema]:
        """Perform keyword search using database text matching"""
        try:
            # Build database query
            db_query = self.db.query(DocumentChunk).join(Document)
            
            # Add text search conditions
            search_terms = query.split()
            text_conditions = []
            
            for term in search_terms:
                term_condition = or_(
                    DocumentChunk.text.ilike(f'%{term}%'),
                    Document.title.ilike(f'%{term}%'),
                    Document.legal_concepts.contains([term]),
                    Document.citations.contains([term])
                )
                text_conditions.append(term_condition)
            
            if text_conditions:
                db_query = db_query.filter(or_(*text_conditions))
            
            # Apply filters
            if filters:
                if filters.get('document_type'):
                    db_query = db_query.filter(Document.document_type.in_(filters['document_type']))
                if filters.get('jurisdiction'):
                    db_query = db_query.filter(Document.jurisdiction.in_(filters['jurisdiction']))
                if filters.get('date_range'):
                    date_range = filters['date_range']
                    if date_range.get('start'):
                        db_query = db_query.filter(Document.date_published >= date_range['start'])
                    if date_range.get('end'):
                        db_query = db_query.filter(Document.date_published <= date_range['end'])
            
            # Apply pagination and get results
            chunks = db_query.offset(offset).limit(limit).all()
            
            # Convert to SearchResult schema
            search_results = []
            for chunk in chunks:
                # Calculate keyword score
                keyword_score = self._calculate_keyword_score(chunk.text, search_terms)
                
                search_result = SearchResultSchema(
                    document_id=chunk.document_id,
                    chunk_id=chunk.id,
                    document_title=chunk.document.title or chunk.document.original_filename,
                    document_type=chunk.document.document_type,
                    jurisdiction=chunk.document.jurisdiction,
                    chunk_text=chunk.text,
                    semantic_score=None,
                    keyword_score=keyword_score,
                    final_score=keyword_score,
                    highlighted_text=self._highlight_text(chunk.text, query),
                    legal_concepts=chunk.legal_concepts or [],
                    citations=chunk.citations or [],
                    page_number=chunk.page_number,
                    section_title=chunk.section_title
                )
                search_results.append(search_result)
            
            # Sort by keyword score
            search_results.sort(key=lambda x: x.keyword_score or 0, reverse=True)
            
            # Log search for analytics
            await self._log_search(query, search_results, "keyword")
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error in keyword search: {str(e)}")
            return []
    
    async def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[SearchResultSchema]:
        """Perform hybrid search combining semantic and keyword approaches"""
        try:
            # Get results from both approaches
            semantic_results = await self.semantic_search(query, limit * 2, 0, filters)
            keyword_results = await self.keyword_search(query, limit * 2, 0, filters)
            
            # Combine results
            combined_results = {}
            
            # Add semantic results
            for result in semantic_results:
                key = f"{result.document_id}_{result.chunk_id}"
                combined_results[key] = result
                result.final_score = (result.semantic_score or 0) * semantic_weight
            
            # Add or update with keyword results
            for result in keyword_results:
                key = f"{result.document_id}_{result.chunk_id}"
                if key in combined_results:
                    # Update existing result
                    combined_results[key].keyword_score = result.keyword_score
                    combined_results[key].final_score = (
                        (combined_results[key].semantic_score or 0) * semantic_weight +
                        (result.keyword_score or 0) * keyword_weight
                    )
                else:
                    # Add new result
                    combined_results[key] = result
                    result.final_score = (result.keyword_score or 0) * keyword_weight
            
            # Sort by final score and apply pagination
            sorted_results = sorted(
                combined_results.values(),
                key=lambda x: x.final_score,
                reverse=True
            )
            
            paginated_results = sorted_results[offset:offset + limit]
            
            # Log search for analytics
            await self._log_search(query, paginated_results, "hybrid")
            
            return paginated_results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            return []
    
    async def search_citations(
        self,
        citation: str,
        exact_match: bool = False
    ) -> List[CitationResult]:
        """Search for specific legal citations"""
        try:
            citation_results = []
            
            if exact_match:
                # Exact citation matching
                chunks = self.db.query(DocumentChunk).join(Document).filter(
                    or_(
                        DocumentChunk.text.contains(citation),
                        DocumentChunk.citations.contains([citation])
                    )
                ).all()
            else:
                # Fuzzy citation matching
                citation_terms = citation.split()
                conditions = []
                for term in citation_terms:
                    conditions.append(DocumentChunk.text.ilike(f'%{term}%'))
                
                chunks = self.db.query(DocumentChunk).join(Document).filter(
                    and_(*conditions)
                ).all()
            
            for chunk in chunks:
                # Extract citation context
                context = self._extract_citation_context(chunk.text, citation)
                confidence_score = 1.0 if exact_match else self._calculate_citation_confidence(chunk.text, citation)
                
                citation_result = CitationResult(
                    citation=citation,
                    document_id=chunk.document_id,
                    document_title=chunk.document.title or chunk.document.original_filename,
                    context=context,
                    page_number=chunk.page_number,
                    confidence_score=confidence_score
                )
                citation_results.append(citation_result)
            
            # Sort by confidence score
            citation_results.sort(key=lambda x: x.confidence_score, reverse=True)
            
            return citation_results[:20]  # Limit results
            
        except Exception as e:
            logger.error(f"Error in citation search: {str(e)}")
            return []
    
    async def find_similar_documents(
        self,
        document_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find documents similar to a given document"""
        try:
            # Get document chunks
            chunks = self.db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_id
            ).limit(3).all()  # Use first few chunks as representation
            
            if not chunks:
                return []
            
            # Use the first chunk for similarity search
            similar_results = await self.vector_store.find_similar_chunks(
                chunk_id=f"doc_{chunks[0].document_id}_chunk_{chunks[0].chunk_index}",
                limit=limit * 3  # Get more to filter by document
            )
            
            # Group by document and get unique documents
            document_scores = {}
            for result in similar_results:
                doc_id = result['document_id']
                if doc_id != document_id:  # Exclude the original document
                    if doc_id not in document_scores:
                        document_scores[doc_id] = []
                    document_scores[doc_id].append(result['similarity_score'])
            
            # Calculate average similarity per document
            similar_docs = []
            for doc_id, scores in document_scores.items():
                document = self.db.query(Document).filter(Document.id == doc_id).first()
                if document:
                    avg_score = sum(scores) / len(scores)
                    similar_docs.append({
                        'document_id': doc_id,
                        'title': document.title or document.original_filename,
                        'document_type': document.document_type,
                        'similarity_score': avg_score,
                        'legal_concepts': document.legal_concepts or []
                    })
            
            # Sort by similarity score
            similar_docs.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return similar_docs[:limit]
            
        except Exception as e:
            logger.error(f"Error finding similar documents: {str(e)}")
            return []
    
    async def get_search_suggestions(
        self,
        query: str,
        limit: int = 5
    ) -> List[str]:
        """Get search suggestions based on query"""
        try:
            suggestions = []
            
            # Get legal concepts from documents that might be relevant
            legal_concepts = self.db.query(Document.legal_concepts).filter(
                Document.legal_concepts.isnot(None)
            ).all()
            
            # Flatten and filter concepts
            all_concepts = []
            for concepts_list in legal_concepts:
                if concepts_list[0]:  # concepts_list is a tuple
                    all_concepts.extend(concepts_list[0])
            
            # Find matching concepts
            query_lower = query.lower()
            matching_concepts = [
                concept for concept in set(all_concepts)
                if query_lower in concept.lower()
            ]
            
            suggestions.extend(matching_concepts[:limit])
            
            # Add common legal terms if needed
            common_terms = [
                "contract law", "tort law", "criminal law", "constitutional law",
                "property law", "evidence", "procedure", "jurisdiction"
            ]
            
            for term in common_terms:
                if query_lower in term.lower() and term not in suggestions:
                    suggestions.append(term)
                    if len(suggestions) >= limit:
                        break
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {str(e)}")
            return []
    
    async def get_available_filters(self) -> Dict[str, List[str]]:
        """Get available filter options"""
        try:
            # Get unique document types
            doc_types = self.db.query(Document.document_type).distinct().filter(
                Document.document_type.isnot(None)
            ).all()
            
            # Get unique jurisdictions
            jurisdictions = self.db.query(Document.jurisdiction).distinct().filter(
                Document.jurisdiction.isnot(None)
            ).all()
            
            # Get date range
            date_range = self.db.query(
                func.min(Document.date_published),
                func.max(Document.date_published)
            ).first()
            
            return {
                "document_types": [dt[0] for dt in doc_types if dt[0]],
                "jurisdictions": [j[0] for j in jurisdictions if j[0]],
                "date_range": {
                    "min": date_range[0].isoformat() if date_range[0] else None,
                    "max": date_range[1].isoformat() if date_range[1] else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting filters: {str(e)}")
            return {}
    
    async def get_trending_searches(
        self,
        limit: int = 10,
        timeframe: str = "week"
    ) -> List[Dict[str, Any]]:
        """Get trending search queries"""
        try:
            # For now, return mock data
            # In production, this would analyze search logs
            trending = [
                {"query": "contract breach", "count": 45},
                {"query": "constitutional rights", "count": 38},
                {"query": "tort liability", "count": 32},
                {"query": "property law", "count": 28},
                {"query": "criminal procedure", "count": 24}
            ]
            
            return trending[:limit]
            
        except Exception as e:
            logger.error(f"Error getting trending searches: {str(e)}")
            return []
    
    async def get_autocomplete_suggestions(
        self,
        query: str,
        limit: int = 10
    ) -> List[str]:
        """Get autocomplete suggestions"""
        try:
            # Get suggestions from document titles and legal concepts
            suggestions = []
            
            # Search in document titles
            title_matches = self.db.query(Document.title).filter(
                Document.title.ilike(f'%{query}%')
            ).limit(limit // 2).all()
            
            suggestions.extend([title[0] for title in title_matches if title[0]])
            
            # Add legal concepts
            concept_suggestions = await self.get_search_suggestions(query, limit - len(suggestions))
            suggestions.extend(concept_suggestions)
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error getting autocomplete suggestions: {str(e)}")
            return []
    
    async def get_document_content(self, document_id: int) -> Optional[str]:
        """Get full content of a document"""
        try:
            chunks = self.db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_id
            ).order_by(DocumentChunk.chunk_index).all()
            
            if chunks:
                return "\n\n".join([chunk.text for chunk in chunks])
            return None
            
        except Exception as e:
            logger.error(f"Error getting document content: {str(e)}")
            return None
    
    async def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        try:
            return self.db.query(Document).filter(Document.id == document_id).first()
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            return None
    
    async def get_documents_by_ids(self, document_ids: List[int]) -> List[str]:
        """Get document contents by IDs"""
        try:
            documents = []
            for doc_id in document_ids:
                content = await self.get_document_content(doc_id)
                if content:
                    documents.append(content)
            return documents
        except Exception as e:
            logger.error(f"Error getting documents by IDs: {str(e)}")
            return []
    
    def _highlight_text(self, text: str, query: str) -> str:
        """Highlight search terms in text"""
        try:
            highlighted = text
            terms = query.split()
            
            for term in terms:
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                highlighted = pattern.sub(f"<mark>{term}</mark>", highlighted)
            
            return highlighted
        except:
            return text
    
    def _calculate_keyword_score(self, text: str, search_terms: List[str]) -> float:
        """Calculate keyword relevance score"""
        try:
            text_lower = text.lower()
            total_words = len(text_lower.split())
            score = 0.0
            
            for term in search_terms:
                term_lower = term.lower()
                count = text_lower.count(term_lower)
                score += count / total_words
            
            return min(score, 1.0)
        except:
            return 0.0
    
    def _extract_citation_context(self, text: str, citation: str) -> str:
        """Extract context around a citation"""
        try:
            # Find citation in text and extract surrounding context
            citation_pos = text.lower().find(citation.lower())
            if citation_pos == -1:
                return text[:200] + "..." if len(text) > 200 else text
            
            # Extract context (100 chars before and after)
            start = max(0, citation_pos - 100)
            end = min(len(text), citation_pos + len(citation) + 100)
            
            context = text[start:end]
            if start > 0:
                context = "..." + context
            if end < len(text):
                context = context + "..."
            
            return context
        except:
            return text[:200] + "..." if len(text) > 200 else text
    
    def _calculate_citation_confidence(self, text: str, citation: str) -> float:
        """Calculate confidence score for citation match"""
        try:
            citation_terms = citation.split()
            text_lower = text.lower()
            
            matches = 0
            for term in citation_terms:
                if term.lower() in text_lower:
                    matches += 1
            
            return matches / len(citation_terms) if citation_terms else 0.0
        except:
            return 0.0
    
    async def _log_search(
        self,
        query: str,
        results: List[SearchResultSchema],
        search_type: str
    ):
        """Log search for analytics"""
        try:
            # Save search results to database for analytics
            for result in results:
                search_result = SearchResult(
                    query=query,
                    document_id=result.document_id,
                    chunk_id=result.chunk_id,
                    semantic_score=result.semantic_score,
                    keyword_score=result.keyword_score,
                    final_score=result.final_score,
                    search_type=search_type
                )
                self.db.add(search_result)
            
            self.db.commit()
        except Exception as e:
            logger.error(f"Error logging search: {str(e)}")
            # Don't raise error as this is non-critical 