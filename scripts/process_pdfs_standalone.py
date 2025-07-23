#!/usr/bin/env python3
"""
Standalone PDF Processing Script for Legal AI System

This script can be run independently to process PDF files and add them to the database.
It's designed to work both in local environments and containerized deployments.

Usage:
    python process_pdfs_standalone.py [options]

Options:
    --pdf-dir PATH          Directory containing PDF files (default: ./pdf)
    --output-dir PATH       Directory for processed files (default: ./processed)
    --database-url URL      Database connection URL
    --batch-size N          Number of PDFs to process in each batch (default: 5)
    --concurrent N          Number of concurrent processing threads (default: 2)
    --force                 Reprocess existing documents
    --dry-run              Show what would be processed without actually processing
    --verbose              Enable verbose logging
    --config PATH          Path to configuration file
    --help                 Show this help message
"""

import os
import sys
import asyncio
import logging
import argparse
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import hashlib
import mimetypes

# Add backend to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "backend"))

try:
    from app.core.config import settings
    from app.core.database import SessionLocal, engine
    from app.services.document_processor import DocumentProcessor
    from app.services.vector_store import VectorStore
    from app.services.ai_analyzer import AIAnalyzer
    from app.models.document import Document, Base
    from app.schemas.document import DocumentCreate
except ImportError as e:
    print(f"Error importing backend modules: {e}")
    print("Please ensure you're running this script from the project root directory")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFProcessorStandalone:
    """Standalone PDF processor with enhanced features."""
    
    def __init__(self, 
                 pdf_dir: Path = None,
                 output_dir: Path = None,
                 batch_size: int = 5,
                 concurrent: int = 2,
                 force: bool = False,
                 dry_run: bool = False,
                 verbose: bool = False):
        
        self.pdf_dir = pdf_dir or Path("pdf")
        self.output_dir = output_dir or Path("processed")
        self.batch_size = batch_size
        self.concurrent = concurrent
        self.force = force
        self.dry_run = dry_run
        
        # Set logging level
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
            
        # Initialize components
        self.document_processor = DocumentProcessor()
        self.vector_store = None
        self.ai_analyzer = None
        
        # Statistics
        self.stats = {
            'total_found': 0,
            'already_processed': 0,
            'successfully_processed': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': datetime.now()
        }
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
    async def initialize(self):
        """Initialize async components."""
        logger.info("Initializing PDF processor...")
        
        try:
            # Initialize vector store
            self.vector_store = VectorStore()
            await self.vector_store.initialize()
            
            # Initialize AI analyzer if enabled
            if getattr(settings, 'ENABLE_AI_ANALYSIS', False):
                self.ai_analyzer = AIAnalyzer()
                logger.info("AI analysis enabled")
            else:
                logger.info("AI analysis disabled")
                
            # Ensure database tables exist
            Base.metadata.create_all(bind=engine)
            
            logger.info("Initialization completed")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise
            
    def find_pdf_files(self) -> List[Path]:
        """Find all PDF files in the specified directory."""
        if not self.pdf_dir.exists():
            logger.error(f"PDF directory {self.pdf_dir} does not exist")
            return []
            
        # Find PDF files recursively
        pdf_files = []
        for pattern in ['*.pdf', '*.PDF']:
            pdf_files.extend(self.pdf_dir.rglob(pattern))
            
        # Sort by file size (process smaller files first)
        pdf_files.sort(key=lambda p: p.stat().st_size)
        
        logger.info(f"Found {len(pdf_files)} PDF files in {self.pdf_dir}")
        self.stats['total_found'] = len(pdf_files)
        
        return pdf_files
        
    def get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file for duplicate detection."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    def is_already_processed(self, pdf_path: Path) -> Optional[Document]:
        """Check if file is already processed in database."""
        db = SessionLocal()
        try:
            # Check by filename first
            existing = db.query(Document).filter(
                Document.original_filename == pdf_path.name
            ).first()
            
            if existing and not self.force:
                # If force is not enabled, skip
                return existing
                
            # Check by file hash for more robust duplicate detection
            file_hash = self.get_file_hash(pdf_path)
            existing_by_hash = db.query(Document).filter(
                Document.metadata.contains({'file_hash': file_hash})
            ).first()
            
            if existing_by_hash and not self.force:
                return existing_by_hash
                
            return None
            
        finally:
            db.close()
            
    async def process_pdf_file(self, pdf_path: Path) -> Tuple[bool, str]:
        """Process a single PDF file."""
        try:
            logger.info(f"Processing {pdf_path.name}...")
            
            if self.dry_run:
                logger.info(f"DRY RUN: Would process {pdf_path.name}")
                return True, "Dry run - not actually processed"
                
            # Check if already processed
            existing = self.is_already_processed(pdf_path)
            if existing:
                logger.info(f"File {pdf_path.name} already processed (ID: {existing.id}), skipping")
                self.stats['already_processed'] += 1
                return True, f"Already processed (ID: {existing.id})"
                
            # Read file content
            with open(pdf_path, 'rb') as f:
                file_content = f.read()
                
            # Calculate file hash
            file_hash = self.get_file_hash(pdf_path)
            file_size = len(file_content)
            
            logger.debug(f"File size: {file_size} bytes, Hash: {file_hash}")
            
            # Extract text content
            logger.debug(f"Extracting text from {pdf_path.name}...")
            text_content = self.document_processor.extract_text(file_content, pdf_path.suffix)
            
            if not text_content.strip():
                logger.warning(f"No text content extracted from {pdf_path.name}")
                self.stats['skipped'] += 1
                return False, "No text content extracted"
                
            # Extract metadata
            logger.debug(f"Extracting metadata from {pdf_path.name}...")
            metadata = self.document_processor.extract_metadata(text_content)
            
            # Add file-specific metadata
            metadata.update({
                'filename': pdf_path.name,
                'file_path': str(pdf_path),
                'file_size': file_size,
                'file_hash': file_hash,
                'processed_date': datetime.now().isoformat(),
                'processor_version': '1.0.0'
            })
            
            # Create document chunks
            logger.debug(f"Creating chunks for {pdf_path.name}...")
            chunks = self.document_processor.create_chunks(
                text_content, 
                metadata={"filename": pdf_path.name}
            )
            
            # Determine document properties
            document_type = self._determine_document_type(pdf_path.name, text_content)
            jurisdiction = self._determine_jurisdiction(text_content)
            title = self._generate_title(pdf_path.name, text_content)
            
            # Create document record
            document_data = DocumentCreate(
                title=title,
                original_filename=pdf_path.name,
                document_type=document_type,
                jurisdiction=jurisdiction,
                content=text_content,
                file_size=file_size,
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
            if self.vector_store:
                logger.debug(f"Adding {pdf_path.name} to vector store...")
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
            
            # Generate AI analysis if enabled
            if self.ai_analyzer:
                try:
                    logger.debug(f"Generating AI analysis for {pdf_path.name}...")
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
            
            # Save processed file info
            self._save_processing_info(pdf_path, db_document.id, metadata)
            
            logger.info(f"Successfully processed {pdf_path.name}")
            self.stats['successfully_processed'] += 1
            return True, f"Successfully processed (ID: {db_document.id})"
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path.name}: {e}")
            self.stats['failed'] += 1
            return False, str(e)
            
    def _save_processing_info(self, pdf_path: Path, document_id: int, metadata: Dict):
        """Save processing information to output directory."""
        info_file = self.output_dir / f"{pdf_path.stem}_info.json"
        
        processing_info = {
            'document_id': document_id,
            'original_file': str(pdf_path),
            'filename': pdf_path.name,
            'processed_at': datetime.now().isoformat(),
            'metadata': metadata
        }
        
        with open(info_file, 'w') as f:
            json.dump(processing_info, f, indent=2)
            
    def _determine_document_type(self, filename: str, content: str) -> str:
        """Determine document type based on filename and content."""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Enhanced document type detection
        type_patterns = {
            'constitution': ['constitution', 'const', 'fundamental law'],
            'statute': ['act', 'code', 'procedure', 'cpc', 'ipc', 'crpc', 'easement'],
            'contract': ['contract', 'agreement', 'deed', 'mou', 'memorandum'],
            'property_law': ['property', 'real estate', 'land', 'title deed'],
            'criminal_law': ['criminal', 'penal', 'bns', 'bnss', 'bsa', 'police'],
            'civil_law': ['civil', 'tort', 'damages', 'liability'],
            'court_decision': ['judgment', 'order', 'decision', 'ruling', 'verdict'],
            'regulation': ['regulation', 'rule', 'guideline', 'circular'],
            'legal_opinion': ['opinion', 'advice', 'counsel', 'brief']
        }
        
        # Check filename patterns
        for doc_type, patterns in type_patterns.items():
            if any(pattern in filename_lower for pattern in patterns):
                return doc_type
                
        # Check content patterns
        for doc_type, patterns in type_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                return doc_type
                
        # Check for specific legal document indicators
        if any(term in content_lower for term in ['section', 'clause', 'article', 'chapter']):
            return 'statute'
        elif any(term in content_lower for term in ['plaintiff', 'defendant', 'court']):
            return 'court_decision'
            
        return 'legal_document'
        
    def _determine_jurisdiction(self, content: str) -> str:
        """Determine jurisdiction based on content."""
        content_lower = content.lower()
        
        jurisdiction_patterns = {
            'india': ['india', 'indian', 'delhi', 'mumbai', 'supreme court of india', 'high court'],
            'federal': ['united states', 'u.s.', 'federal', 'supreme court'],
            'state': ['state of', 'california', 'new york', 'texas'],
            'international': ['international', 'treaty', 'convention', 'protocol']
        }
        
        for jurisdiction, patterns in jurisdiction_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                return jurisdiction
                
        return 'other'
        
    def _generate_title(self, filename: str, content: str) -> str:
        """Generate a meaningful title for the document."""
        # Remove file extension
        base_name = Path(filename).stem
        
        # Clean up filename
        title = base_name.replace('_', ' ').replace('-', ' ').title()
        
        # Enhanced title mapping
        title_mapping = {
            'Constitution Of India': 'Constitution of India',
            'Bns': 'Bharatiya Nyaya Sanhita (BNS)',
            'Bnss': 'Bharatiya Nagarik Suraksha Sanhita (BNSS)', 
            'Bsa': 'Bharatiya Sakshya Adhiniyam (BSA)',
            'Contract': 'Indian Contract Act',
            'Easement Act': 'Indian Easements Act',
            'The Code Of Civil Procedure, 1908': 'The Code of Civil Procedure, 1908',
            '51 Property Law': 'Property Law - Chapter 51',
            'Ipc': 'Indian Penal Code',
            'Crpc': 'Code of Criminal Procedure'
        }
        
        for key, value in title_mapping.items():
            if key.lower() in title.lower():
                return value
                
        # Try to extract title from content (first significant line)
        lines = content.split('\n')[:15]  # Check first 15 lines
        for line in lines:
            line = line.strip()
            if 20 <= len(line) <= 200:  # Reasonable title length
                if not line.isdigit() and 'page' not in line.lower():
                    # Clean the extracted title
                    cleaned_title = ' '.join(line.split())
                    if cleaned_title:
                        return cleaned_title
                        
        return title
        
    async def process_batch(self, pdf_files: List[Path]) -> List[Tuple[Path, bool, str]]:
        """Process a batch of PDF files concurrently."""
        logger.info(f"Processing batch of {len(pdf_files)} files...")
        
        results = []
        
        # Use ThreadPoolExecutor for I/O bound operations
        with ThreadPoolExecutor(max_workers=self.concurrent) as executor:
            # Submit all tasks
            tasks = []
            for pdf_path in pdf_files:
                task = asyncio.create_task(self.process_pdf_file(pdf_path))
                tasks.append((pdf_path, task))
            
            # Collect results
            for pdf_path, task in tasks:
                try:
                    success, message = await task
                    results.append((pdf_path, success, message))
                except Exception as e:
                    logger.error(f"Batch processing error for {pdf_path}: {e}")
                    results.append((pdf_path, False, str(e)))
                    
        return results
        
    async def process_all_pdfs(self):
        """Process all PDF files in batches."""
        pdf_files = self.find_pdf_files()
        
        if not pdf_files:
            logger.warning("No PDF files found to process")
            return
            
        logger.info(f"Starting to process {len(pdf_files)} PDF files in batches of {self.batch_size}...")
        
        # Process in batches
        all_results = []
        for i in range(0, len(pdf_files), self.batch_size):
            batch = pdf_files[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(pdf_files) + self.batch_size - 1) // self.batch_size
            
            logger.info(f"Processing batch {batch_num}/{total_batches}...")
            
            batch_results = await self.process_batch(batch)
            all_results.extend(batch_results)
            
            # Log batch summary
            batch_success = sum(1 for _, success, _ in batch_results if success)
            logger.info(f"Batch {batch_num} completed: {batch_success}/{len(batch)} successful")
            
        self._generate_report(all_results)
        
    def _generate_report(self, results: List[Tuple[Path, bool, str]]):
        """Generate processing report."""
        # Calculate final statistics
        end_time = datetime.now()
        self.stats['end_time'] = end_time
        self.stats['total_time'] = (end_time - self.stats['start_time']).total_seconds()
        
        # Create detailed report
        report = {
            'summary': self.stats,
            'details': []
        }
        
        for pdf_path, success, message in results:
            report['details'].append({
                'file': str(pdf_path),
                'filename': pdf_path.name,
                'success': success,
                'message': message
            })
            
        # Save report
        report_file = self.output_dir / f"processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        # Print summary
        logger.info("=" * 60)
        logger.info("PROCESSING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total files found: {self.stats['total_found']}")
        logger.info(f"Already processed: {self.stats['already_processed']}")
        logger.info(f"Successfully processed: {self.stats['successfully_processed']}")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info(f"Skipped: {self.stats['skipped']}")
        logger.info(f"Total time: {self.stats['total_time']:.2f} seconds")
        logger.info(f"Report saved to: {report_file}")
        logger.info("=" * 60)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Standalone PDF Processor for Legal AI System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Process PDFs in ./pdf directory
  %(prog)s --pdf-dir /path/to/pdfs   # Process PDFs in custom directory
  %(prog)s --dry-run --verbose       # Test run with detailed output
  %(prog)s --force --concurrent 4    # Reprocess all files with 4 threads
  %(prog)s --batch-size 10           # Process 10 files per batch
        """
    )
    
    parser.add_argument(
        '--pdf-dir', 
        type=Path, 
        default=Path('pdf'),
        help='Directory containing PDF files (default: ./pdf)'
    )
    
    parser.add_argument(
        '--output-dir', 
        type=Path, 
        default=Path('processed'),
        help='Directory for processed files (default: ./processed)'
    )
    
    parser.add_argument(
        '--database-url', 
        type=str,
        help='Database connection URL (overrides environment)'
    )
    
    parser.add_argument(
        '--batch-size', 
        type=int, 
        default=5,
        help='Number of PDFs to process in each batch (default: 5)'
    )
    
    parser.add_argument(
        '--concurrent', 
        type=int, 
        default=2,
        help='Number of concurrent processing threads (default: 2)'
    )
    
    parser.add_argument(
        '--force', 
        action='store_true',
        help='Reprocess existing documents'
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be processed without actually processing'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--config', 
        type=Path,
        help='Path to configuration file'
    )
    
    return parser.parse_args()

async def main():
    """Main function."""
    args = parse_arguments()
    
    # Override database URL if provided
    if args.database_url:
        os.environ['DATABASE_URL'] = args.database_url
        
    # Load configuration file if provided
    if args.config and args.config.exists():
        try:
            with open(args.config) as f:
                config = json.load(f)
                # Apply config settings
                for key, value in config.items():
                    if hasattr(args, key):
                        setattr(args, key, value)
        except Exception as e:
            logger.error(f"Failed to load config file {args.config}: {e}")
            
    # Validate directories
    if not args.pdf_dir.exists():
        logger.error(f"PDF directory {args.pdf_dir} does not exist")
        sys.exit(1)
        
    processor = PDFProcessorStandalone(
        pdf_dir=args.pdf_dir,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        concurrent=args.concurrent,
        force=args.force,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    
    try:
        await processor.initialize()
        await processor.process_all_pdfs()
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        sys.exit(1)
        
    logger.info("PDF processing completed successfully")

if __name__ == "__main__":
    asyncio.run(main()) 