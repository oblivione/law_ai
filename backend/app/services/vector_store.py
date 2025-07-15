import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
import json

from app.core.config import settings
from app.models.document import DocumentChunk

class VectorStore:
    """Handles vector database operations and semantic search"""
    
    def __init__(self):
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"description": "Legal document chunks for semantic search"}
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        logger.info(f"VectorStore initialized with collection: {settings.CHROMA_COLLECTION_NAME}")
    
    async def add_document_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """Add document chunks to the vector store"""
        try:
            if not chunks:
                return True
            
            # Prepare data for insertion
            texts = []
            embeddings = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                # Generate embedding
                embedding = await self.generate_embedding(chunk.text)
                
                # Prepare metadata
                metadata = {
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index,
                    "page_number": chunk.page_number or 0,
                    "section_title": chunk.section_title or "",
                    "word_count": chunk.word_count or 0,
                    "char_count": chunk.char_count or 0,
                    "legal_concepts": json.dumps(chunk.legal_concepts or []),
                    "citations": json.dumps(chunk.citations or []),
                    "importance_score": chunk.importance_score or 0.0
                }
                
                # Create unique ID
                chunk_id = f"doc_{chunk.document_id}_chunk_{chunk.chunk_index}"
                
                texts.append(chunk.text)
                embeddings.append(embedding.tolist())
                metadatas.append(metadata)
                ids.append(chunk_id)
            
            # Add to collection
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(chunks)} chunks to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding chunks to vector store: {str(e)}")
            return False
    
    async def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        try:
            # Clean text for embedding
            cleaned_text = text.strip().replace('\n', ' ')
            if not cleaned_text:
                return np.zeros(self.embedding_model.get_sentence_embedding_dimension())
            
            # Generate embedding
            embedding = self.embedding_model.encode(cleaned_text)
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return np.zeros(self.embedding_model.get_sentence_embedding_dimension())
    
    async def semantic_search(
        self, 
        query: str, 
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic search using vector similarity"""
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)
            
            # Prepare where clause for filtering
            where_clause = {}
            if filters:
                if filters.get('document_type'):
                    # This would require storing document_type in chunk metadata
                    pass
                if filters.get('jurisdiction'):
                    # This would require storing jurisdiction in chunk metadata
                    pass
                if filters.get('date_range'):
                    # This would require storing dates in chunk metadata
                    pass
            
            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=limit,
                where=where_clause if where_clause else None,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]
                    
                    # Convert distance to similarity score
                    similarity_score = 1.0 - distance
                    
                    formatted_results.append({
                        'text': doc,
                        'metadata': metadata,
                        'similarity_score': similarity_score,
                        'document_id': metadata.get('document_id'),
                        'chunk_index': metadata.get('chunk_index'),
                        'page_number': metadata.get('page_number'),
                        'legal_concepts': json.loads(metadata.get('legal_concepts', '[]')),
                        'citations': json.loads(metadata.get('citations', '[]'))
                    })
            
            logger.info(f"Semantic search completed: {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []
    
    async def find_similar_chunks(
        self, 
        chunk_id: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find chunks similar to a given chunk"""
        try:
            # Get the chunk by ID
            chunk_result = self.collection.get(
                ids=[chunk_id],
                include=['documents', 'metadatas', 'embeddings']
            )
            
            if not chunk_result['documents']:
                return []
            
            # Use the chunk's embedding to find similar chunks
            chunk_embedding = chunk_result['embeddings'][0]
            
            # Search for similar chunks (excluding the original)
            results = self.collection.query(
                query_embeddings=[chunk_embedding],
                n_results=limit + 1,  # +1 to account for the original chunk
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results and exclude the original chunk
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    result_id = f"doc_{results['metadatas'][0][i]['document_id']}_chunk_{results['metadatas'][0][i]['chunk_index']}"
                    
                    # Skip the original chunk
                    if result_id == chunk_id:
                        continue
                    
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]
                    similarity_score = 1.0 - distance
                    
                    formatted_results.append({
                        'text': doc,
                        'metadata': metadata,
                        'similarity_score': similarity_score,
                        'document_id': metadata.get('document_id'),
                        'chunk_index': metadata.get('chunk_index')
                    })
                    
                    if len(formatted_results) >= limit:
                        break
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error finding similar chunks: {str(e)}")
            return []
    
    async def update_chunk_embedding(self, chunk: DocumentChunk) -> bool:
        """Update embedding for a specific chunk"""
        try:
            chunk_id = f"doc_{chunk.document_id}_chunk_{chunk.chunk_index}"
            
            # Generate new embedding
            embedding = await self.generate_embedding(chunk.text)
            
            # Update metadata
            metadata = {
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number or 0,
                "section_title": chunk.section_title or "",
                "word_count": chunk.word_count or 0,
                "char_count": chunk.char_count or 0,
                "legal_concepts": json.dumps(chunk.legal_concepts or []),
                "citations": json.dumps(chunk.citations or []),
                "importance_score": chunk.importance_score or 0.0
            }
            
            # Delete old entry and add new one
            try:
                self.collection.delete(ids=[chunk_id])
            except:
                pass  # Chunk might not exist
            
            self.collection.add(
                documents=[chunk.text],
                embeddings=[embedding.tolist()],
                metadatas=[metadata],
                ids=[chunk_id]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating chunk embedding: {str(e)}")
            return False
    
    async def delete_document_chunks(self, document_id: int) -> bool:
        """Delete all chunks for a specific document"""
        try:
            # Find all chunks for this document
            results = self.collection.get(
                where={"document_id": document_id},
                include=['metadatas']
            )
            
            if results['metadatas']:
                # Extract chunk IDs
                chunk_ids = []
                for metadata in results['metadatas']:
                    chunk_id = f"doc_{metadata['document_id']}_chunk_{metadata['chunk_index']}"
                    chunk_ids.append(chunk_id)
                
                # Delete chunks
                if chunk_ids:
                    self.collection.delete(ids=chunk_ids)
                    logger.info(f"Deleted {len(chunk_ids)} chunks for document {document_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document chunks: {str(e)}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection"""
        try:
            count = self.collection.count()
            
            return {
                "total_chunks": count,
                "collection_name": settings.CHROMA_COLLECTION_NAME,
                "embedding_model": settings.EMBEDDING_MODEL,
                "embedding_dimension": self.embedding_model.get_sentence_embedding_dimension()
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {}
    
    async def hybrid_search(
        self,
        query: str,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search combining semantic and keyword search"""
        try:
            # Get semantic results
            semantic_results = await self.semantic_search(query, limit * 2, filters)
            
            # Get keyword results (simplified - using text matching)
            keyword_results = await self._keyword_search(query, limit * 2, filters)
            
            # Combine and rank results
            combined_results = {}
            
            # Add semantic results
            for result in semantic_results:
                chunk_id = f"doc_{result['document_id']}_chunk_{result['chunk_index']}"
                combined_results[chunk_id] = {
                    **result,
                    'semantic_score': result['similarity_score'],
                    'keyword_score': 0.0,
                    'final_score': result['similarity_score'] * semantic_weight
                }
            
            # Add keyword results
            for result in keyword_results:
                chunk_id = f"doc_{result['document_id']}_chunk_{result['chunk_index']}"
                if chunk_id in combined_results:
                    # Update existing result
                    combined_results[chunk_id]['keyword_score'] = result['keyword_score']
                    combined_results[chunk_id]['final_score'] = (
                        combined_results[chunk_id]['semantic_score'] * semantic_weight +
                        result['keyword_score'] * keyword_weight
                    )
                else:
                    # Add new result
                    combined_results[chunk_id] = {
                        **result,
                        'semantic_score': 0.0,
                        'keyword_score': result['keyword_score'],
                        'final_score': result['keyword_score'] * keyword_weight
                    }
            
            # Sort by final score and return top results
            sorted_results = sorted(
                combined_results.values(),
                key=lambda x: x['final_score'],
                reverse=True
            )
            
            return sorted_results[:limit]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            return []
    
    async def _keyword_search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Simple keyword search implementation"""
        try:
            # For now, use ChromaDB's built-in text search capabilities
            # In a production system, you'd integrate with Elasticsearch
            
            query_terms = query.lower().split()
            
            # Get all documents and filter based on keyword matching
            all_results = self.collection.get(
                include=['documents', 'metadatas']
            )
            
            keyword_results = []
            if all_results['documents']:
                for i, doc in enumerate(all_results['documents']):
                    doc_lower = doc.lower()
                    
                    # Calculate keyword score based on term frequency
                    score = 0.0
                    for term in query_terms:
                        score += doc_lower.count(term) / len(doc_lower.split())
                    
                    if score > 0:
                        metadata = all_results['metadatas'][i]
                        keyword_results.append({
                            'text': doc,
                            'metadata': metadata,
                            'keyword_score': score,
                            'document_id': metadata.get('document_id'),
                            'chunk_index': metadata.get('chunk_index'),
                            'page_number': metadata.get('page_number'),
                            'legal_concepts': json.loads(metadata.get('legal_concepts', '[]')),
                            'citations': json.loads(metadata.get('citations', '[]'))
                        })
            
            # Sort by keyword score
            keyword_results.sort(key=lambda x: x['keyword_score'], reverse=True)
            
            return keyword_results[:limit]
            
        except Exception as e:
            logger.error(f"Error in keyword search: {str(e)}")
            return [] 