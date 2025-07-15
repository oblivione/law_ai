import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image
import re
import io
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from loguru import logger
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.models.document import Document, DocumentChunk

class DocumentProcessor:
    """Handles document processing including text extraction, cleaning, and chunking"""
    
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except:
            pass
        
        # Initialize sentence transformer for semantic chunking
        self.sentence_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    
    async def process_document(self, document: Document) -> bool:
        """Main document processing pipeline"""
        try:
            logger.info(f"Starting document processing for: {document.filename}")
            
            # Step 1: Extract text from document
            text_content = await self.extract_text(document.file_path, document.file_type)
            if not text_content:
                logger.error(f"No text extracted from document: {document.filename}")
                return False
            
            # Step 2: Clean and preprocess text
            cleaned_text = await self.clean_text(text_content)
            
            # Step 3: Extract metadata
            metadata = await self.extract_metadata(cleaned_text, document.file_type)
            
            # Step 4: Create intelligent chunks
            chunks = await self.create_chunks(cleaned_text, document.id)
            
            # Step 5: Save chunks to database (this would be handled by the calling service)
            document.text_extracted = True
            
            logger.info(f"Document processing completed: {len(chunks)} chunks created")
            return True
            
        except Exception as e:
            logger.error(f"Error processing document {document.filename}: {str(e)}")
            return False
    
    async def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from various document types"""
        
        try:
            if file_type.lower() == ".pdf":
                return await self._extract_pdf_text(file_path)
            elif file_type.lower() == ".docx":
                return await self._extract_docx_text(file_path)
            elif file_type.lower() == ".txt":
                return await self._extract_txt_text(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_type}")
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return ""
    
    async def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF using multiple methods"""
        text_content = ""
        
        try:
            # Method 1: Try PyMuPDF first (faster and better for text-based PDFs)
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += page.get_text()
            doc.close()
            
            # If we got reasonable text, return it
            if len(text_content.strip()) > 100:
                logger.info(f"Extracted text using PyMuPDF: {len(text_content)} characters")
                return text_content
            
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {str(e)}")
        
        try:
            # Method 2: Try pdfplumber (better for tables and complex layouts)
            text_content = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            
            if len(text_content.strip()) > 100:
                logger.info(f"Extracted text using pdfplumber: {len(text_content)} characters")
                return text_content
                
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {str(e)}")
        
        try:
            # Method 3: OCR as last resort (for scanned PDFs)
            text_content = await self._ocr_pdf(file_path)
            logger.info(f"Extracted text using OCR: {len(text_content)} characters")
            return text_content
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
        
        return text_content
    
    async def _ocr_pdf(self, file_path: str) -> str:
        """Extract text from PDF using OCR"""
        text_content = ""
        
        try:
            doc = fitz.open(file_path)
            for page_num in range(min(10, len(doc))):  # Limit OCR to first 10 pages
                page = doc.load_page(page_num)
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # Perform OCR
                ocr_text = pytesseract.image_to_string(img, lang='eng')
                text_content += ocr_text + "\n"
            
            doc.close()
            return text_content
            
        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            return ""
    
    async def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX files"""
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(file_path)
            text_content = ""
            
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
            
            return text_content
            
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            return ""
    
    async def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except:
                    continue
        except Exception as e:
            logger.error(f"Error extracting TXT text: {str(e)}")
        
        return ""
    
    async def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers (common patterns)
        text = re.sub(r'\n\d+\n', '\n', text)  # Page numbers on separate lines
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        
        # Remove excessive line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Fix common OCR errors
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between words
        text = re.sub(r'(\w)(\d)', r'\1 \2', text)  # Space between word and number
        text = re.sub(r'(\d)(\w)', r'\1 \2', text)  # Space between number and word
        
        # Normalize quotes and dashes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r'[''']', "'", text)
        text = re.sub(r'[—–]', '-', text)
        
        return text.strip()
    
    async def extract_metadata(self, text: str, file_type: str) -> Dict[str, any]:
        """Extract metadata and legal entities from text"""
        metadata = {}
        
        try:
            # Extract legal citations
            citations = self._extract_citations(text)
            metadata['citations'] = citations
            
            # Extract case names
            case_names = self._extract_case_names(text)
            metadata['case_names'] = case_names
            
            # Extract statutes and regulations
            statutes = self._extract_statutes(text)
            metadata['statutes'] = statutes
            
            # Extract dates
            dates = self._extract_dates(text)
            metadata['dates'] = dates
            
            # Determine document type
            doc_type = self._determine_document_type(text)
            metadata['document_type'] = doc_type
            
            # Extract jurisdiction
            jurisdiction = self._extract_jurisdiction(text)
            metadata['jurisdiction'] = jurisdiction
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
        
        return metadata
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract legal citations from text"""
        citations = []
        
        # Common citation patterns
        patterns = [
            r'\d+\s+[A-Z][a-z]+\.?\s+\d+',  # Volume Reporter Page
            r'\d+\s+U\.S\.C\.?\s+§?\s*\d+',  # USC citations
            r'\d+\s+F\.?\s*\d*d?\s+\d+',  # Federal Reporter
            r'\d+\s+S\.?\s*Ct\.?\s+\d+',  # Supreme Court Reporter
            r'\d+\s+L\.?\s*Ed\.?\s*\d*d?\s+\d+',  # Lawyers Edition
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            citations.extend(matches)
        
        return list(set(citations))  # Remove duplicates
    
    def _extract_case_names(self, text: str) -> List[str]:
        """Extract case names from text"""
        # Pattern for case names (simplified)
        pattern = r'([A-Z][a-zA-Z\s&.,-]+)\s+v\.?\s+([A-Z][a-zA-Z\s&.,-]+)'
        matches = re.findall(pattern, text)
        
        case_names = []
        for match in matches:
            case_name = f"{match[0].strip()} v. {match[1].strip()}"
            if len(case_name) < 100:  # Filter out overly long matches
                case_names.append(case_name)
        
        return list(set(case_names))
    
    def _extract_statutes(self, text: str) -> List[str]:
        """Extract statute references"""
        patterns = [
            r'\d+\s+U\.S\.C\.?\s+§?\s*\d+',
            r'Section\s+\d+[a-z]?',
            r'§\s*\d+[a-z]?',
        ]
        
        statutes = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            statutes.extend(matches)
        
        return list(set(statutes))
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',
            r'\b[A-Za-z]+ \d{1,2}, \d{4}\b',
            r'\b\d{4}\b',  # Years
        ]
        
        dates = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return list(set(dates))
    
    def _determine_document_type(self, text: str) -> str:
        """Determine the type of legal document"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['opinion', 'judgment', 'court', 'appeal']):
            return 'court_decision'
        elif any(word in text_lower for word in ['constitution', 'amendment']):
            return 'constitutional'
        elif any(word in text_lower for word in ['statute', 'code', 'act', 'law']):
            return 'statute'
        elif any(word in text_lower for word in ['regulation', 'rule', 'cfr']):
            return 'regulation'
        elif any(word in text_lower for word in ['contract', 'agreement', 'lease']):
            return 'contract'
        else:
            return 'unknown'
    
    def _extract_jurisdiction(self, text: str) -> str:
        """Extract jurisdiction information"""
        text_lower = text.lower()
        
        # Federal indicators
        if any(word in text_lower for word in ['federal', 'u.s.', 'united states', 'supreme court']):
            return 'federal'
        
        # State patterns
        states = ['california', 'new york', 'texas', 'florida', 'illinois']  # Add more as needed
        for state in states:
            if state in text_lower:
                return state
        
        return 'unknown'
    
    async def create_chunks(self, text: str, document_id: int) -> List[DocumentChunk]:
        """Create intelligent chunks from document text"""
        chunks = []
        
        try:
            # Method 1: Try semantic chunking first
            semantic_chunks = await self._create_semantic_chunks(text)
            
            if semantic_chunks:
                for i, chunk_text in enumerate(semantic_chunks):
                    chunk = self._create_chunk_object(
                        text=chunk_text,
                        document_id=document_id,
                        chunk_index=i,
                        method="semantic"
                    )
                    chunks.append(chunk)
            else:
                # Method 2: Fallback to sentence-based chunking
                sentence_chunks = await self._create_sentence_chunks(text)
                
                for i, chunk_text in enumerate(sentence_chunks):
                    chunk = self._create_chunk_object(
                        text=chunk_text,
                        document_id=document_id,
                        chunk_index=i,
                        method="sentence"
                    )
                    chunks.append(chunk)
            
        except Exception as e:
            logger.error(f"Error creating chunks: {str(e)}")
            # Simple paragraph-based chunking as last resort
            paragraphs = text.split('\n\n')
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph.strip()) > 50:  # Skip very short paragraphs
                    chunk = self._create_chunk_object(
                        text=paragraph.strip(),
                        document_id=document_id,
                        chunk_index=i,
                        method="paragraph"
                    )
                    chunks.append(chunk)
        
        return chunks
    
    async def _create_semantic_chunks(self, text: str) -> List[str]:
        """Create chunks based on semantic similarity"""
        # Split into sentences
        sentences = sent_tokenize(text)
        
        if len(sentences) < 3:
            return [text]  # Too short to chunk meaningfully
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            
            # Check if adding this sentence would exceed chunk size
            if current_length + sentence_length > settings.CHUNK_SIZE and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add the last chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    async def _create_sentence_chunks(self, text: str) -> List[str]:
        """Create chunks based on sentence boundaries"""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            words = word_tokenize(sentence)
            sentence_length = len(words)
            
            if current_length + sentence_length > settings.CHUNK_SIZE and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _create_chunk_object(self, text: str, document_id: int, chunk_index: int, method: str) -> DocumentChunk:
        """Create a DocumentChunk object with metadata"""
        
        # Calculate basic statistics
        word_count = len(text.split())
        char_count = len(text)
        
        # Extract chunk-specific metadata
        chunk_citations = self._extract_citations(text)
        chunk_concepts = self._extract_legal_concepts(text)
        
        # Create chunk object (not saved to DB yet)
        chunk = DocumentChunk(
            document_id=document_id,
            text=text,
            chunk_index=chunk_index,
            word_count=word_count,
            char_count=char_count,
            legal_concepts=chunk_concepts,
            citations=chunk_citations
        )
        
        return chunk
    
    def _extract_legal_concepts(self, text: str) -> List[str]:
        """Extract legal concepts from text chunk"""
        concepts = []
        
        # Legal concept patterns
        concept_patterns = {
            'contract_law': r'\b(contract|agreement|consideration|breach|damages)\b',
            'tort_law': r'\b(negligence|liability|duty|damages|injury)\b',
            'criminal_law': r'\b(criminal|felony|misdemeanor|prosecution|defendant)\b',
            'constitutional_law': r'\b(constitutional|amendment|rights|due process)\b',
            'property_law': r'\b(property|ownership|title|easement|zoning)\b',
        }
        
        for concept, pattern in concept_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                concepts.append(concept)
        
        return concepts 