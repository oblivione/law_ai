#!/usr/bin/env python3
"""
Script to process existing PDF files in the pdf directory.
This script will:
1. Scan the pdf directory for PDF files
2. Process each PDF using the document processor
3. Add them to the vector database
4. Generate metadata and analysis
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import List

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStore
from app.services.ai_analyzer import AIAnalyzer
from app.models.document import Document
from app.schemas.document import DocumentCreate

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """Process existing PDF files and add them to the system."""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.ai_analyzer = AIAnalyzer()
        self.pdf_directory = Path("pdf")
        
    async def initialize(self):
        """Initialize services."""
        logger.info("Initializing services...")
        await self.vector_store.initialize()
        logger.info("Services initialized")
        
    def find_pdf_files(self) -> List[Path]:
        """Find all PDF files in the pdf directory."""
        if not self.pdf_directory.exists():
            logger.error(f"PDF directory {self.pdf_directory} does not exist")
            return []
            
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")
        return pdf_files
        
    async def process_pdf_file(self, pdf_path: Path) -> bool:
        """Process a single PDF file."""
        try:
            logger.info(f"Processing {pdf_path.name}...")
            
            # Check if file already exists in database
            db = SessionLocal()
            try:
                existing = db.query(Document).filter(
                    Document.original_filename == pdf_path.name
                ).first()
                
                if existing:
                    logger.info(f"File {pdf_path.name} already processed, skipping")
                    return True
                    
            finally:
                db.close()
            
            # Read file content
            with open(pdf_path, 'rb') as f:
                file_content = f.read()
                
            # Process document
            logger.info(f"Extracting text from {pdf_path.name}...")
            text_content = self.document_processor.extract_text(file_content, pdf_path.suffix)
            
            if not text_content.strip():
                logger.warning(f"No text content extracted from {pdf_path.name}")
                return False
                
            # Extract metadata
            logger.info(f"Extracting metadata from {pdf_path.name}...")
            metadata = self.document_processor.extract_metadata(text_content)
            
            # Create document chunks
            logger.info(f"Creating chunks for {pdf_path.name}...")
            chunks = self.document_processor.create_chunks(
                text_content, 
                metadata={"filename": pdf_path.name}
            )
            
            # Determine document type and other metadata
            document_type = self._determine_document_type(pdf_path.name, text_content)
            jurisdiction = self._determine_jurisdiction(text_content)
            
            # Create document record
            document_data = DocumentCreate(
                title=self._generate_title(pdf_path.name, text_content),
                original_filename=pdf_path.name,
                document_type=document_type,
                jurisdiction=jurisdiction,
                content=text_content,
                file_size=len(file_content),
                metadata=metadata
            )
            
            # Save to database
            db = SessionLocal()
            try:
                db_document = Document(**document_data.dict())
                db.add(db_document)
                db.commit()
                db.refresh(db_document)
                
                logger.info(f"Saved document {pdf_path.name} with ID {db_document.id}")
                
            finally:
                db.close()
            
            # Add to vector store
            logger.info(f"Adding {pdf_path.name} to vector store...")
            await self.vector_store.add_document(
                document_id=db_document.id,
                chunks=chunks,
                metadata={
                    "filename": pdf_path.name,
                    "document_type": document_type,
                    "jurisdiction": jurisdiction,
                    **metadata
                }
            )
            
            # Generate AI analysis (optional, can be resource intensive)
            if settings.ENABLE_AI_ANALYSIS:
                try:
                    logger.info(f"Generating AI analysis for {pdf_path.name}...")
                    analysis = await self.ai_analyzer.analyze_document(text_content)
                    
                    # Update document with analysis
                    db = SessionLocal()
                    try:
                        db_document = db.query(Document).filter(Document.id == db_document.id).first()
                        if db_document:
                            db_document.analysis = analysis
                            db.commit()
                    finally:
                        db.close()
                        
                except Exception as e:
                    logger.warning(f"AI analysis failed for {pdf_path.name}: {e}")
            
            logger.info(f"Successfully processed {pdf_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path.name}: {e}")
            return False
            
    def _determine_document_type(self, filename: str, content: str) -> str:
        """Determine document type based on filename and content."""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Check filename patterns
        if any(term in filename_lower for term in ['constitution', 'const']):
            return 'constitution'
        elif any(term in filename_lower for term in ['code', 'procedure', 'cpc']):
            return 'statute'
        elif any(term in filename_lower for term in ['contract', 'agreement']):
            return 'contract'
        elif any(term in filename_lower for term in ['property', 'real_estate']):
            return 'property_law'
        elif any(term in filename_lower for term in ['criminal', 'penal', 'bns', 'bnss', 'bsa']):
            return 'criminal_law'
        elif any(term in filename_lower for term in ['civil', 'tort']):
            return 'civil_law'
        elif any(term in filename_lower for term in ['case', 'judgment', 'decision']):
            return 'court_decision'
        elif 'easement' in filename_lower:
            return 'statute'
            
        # Check content patterns
        if any(term in content_lower for term in ['supreme court', 'high court', 'district court']):
            return 'court_decision'
        elif any(term in content_lower for term in ['section', 'clause', 'article', 'chapter']):
            return 'statute'
        elif any(term in content_lower for term in ['constitution', 'fundamental rights']):
            return 'constitution'
            
        return 'legal_document'
        
    def _determine_jurisdiction(self, content: str) -> str:
        """Determine jurisdiction based on content."""
        content_lower = content.lower()
        
        if any(term in content_lower for term in ['india', 'indian', 'delhi', 'mumbai', 'supreme court of india']):
            return 'india'
        elif any(term in content_lower for term in ['united states', 'u.s.', 'federal', 'supreme court']):
            return 'federal'
        elif any(term in content_lower for term in ['state of', 'california', 'new york', 'texas']):
            return 'state'
            
        return 'other'
        
    def _generate_title(self, filename: str, content: str) -> str:
        """Generate a meaningful title for the document."""
        # Remove file extension
        base_name = Path(filename).stem
        
        # Clean up filename
        title = base_name.replace('_', ' ').replace('-', ' ').title()
        
        # Special handling for known documents
        title_mapping = {
            'Constitution Of India': 'Constitution of India',
            'Bns': 'Bharatiya Nyaya Sanhita (BNS)',
            'Bnss': 'Bharatiya Nagarik Suraksha Sanhita (BNSS)', 
            'Bsa': 'Bharatiya Sakshya Adhiniyam (BSA)',
            'Contract': 'Indian Contract Act',
            'Easement Act': 'Indian Easements Act',
            'The Code Of Civil Procedure, 1908': 'The Code of Civil Procedure, 1908',
            '51 Property Law': 'Property Law - Chapter 51'
        }
        
        for key, value in title_mapping.items():
            if key.lower() in title.lower():
                return value
                
        # Try to extract title from content (first significant line)
        lines = content.split('\n')[:10]  # Check first 10 lines
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 200:  # Reasonable title length
                if not line.isdigit() and 'page' not in line.lower():
                    # This might be a title
                    return line
                    
        return title
        
    async def process_all_pdfs(self):
        """Process all PDF files in the directory."""
        pdf_files = self.find_pdf_files()
        
        if not pdf_files:
            logger.warning("No PDF files found to process")
            return
            
        logger.info(f"Starting to process {len(pdf_files)} PDF files...")
        
        successful = 0
        failed = 0
        
        for pdf_path in pdf_files:
            success = await self.process_pdf_file(pdf_path)
            if success:
                successful += 1
            else:
                failed += 1
                
        logger.info(f"Processing completed: {successful} successful, {failed} failed")
        
async def main():
    """Main function."""
    processor = PDFProcessor()
    
    try:
        await processor.initialize()
        await processor.process_all_pdfs()
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        sys.exit(1)
        
    logger.info("PDF processing completed successfully")

if __name__ == "__main__":
    # Check if pdf directory exists
    if not Path("pdf").exists():
        print("Error: pdf directory not found")
        print("Please ensure you're running this script from the project root directory")
        sys.exit(1)
        
    # Run the async main function
    asyncio.run(main()) 