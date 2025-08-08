"""
Embedding worker for processing document embeddings
"""

import os
import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import openai
from dotenv import load_dotenv

from .text_splitter import RAGTextSplitter
from ...storage.supabase_manager import SupabaseDocsetManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingWorker:
    """Async worker for processing document embeddings"""
    
    def __init__(self, model_name: str = "openai"):
        """Initialize embedding worker"""
        self.model_name = model_name
        self.text_splitter = RAGTextSplitter()
        self.storage = SupabaseDocsetManager()
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        
        self.openai_client = openai.OpenAI(api_key=api_key)
        
        # Embedding model configuration
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimensions = 1536
        
        logger.info(f"✅ Embedding worker initialized with model: {self.embedding_model}")
    
    async def process_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Process a single document for embedding
        
        Args:
            doc_id: Document ID to process
            
        Returns:
            Processing result dictionary
        """
        try:
            # Update status to processing
            self._update_document_status(doc_id, "processing")
            
            # Get document from database
            document = self._get_document(doc_id)
            if not document:
                raise ValueError(f"Document {doc_id} not found")
            
            # Split document into chunks
            chunks = self.text_splitter.split_document(document)
            if not chunks:
                logger.warning(f"No chunks generated for document {doc_id}")
                self._update_document_status(doc_id, "error")
                return {"status": "error", "message": "No chunks generated"}
            
            # Generate embeddings for chunks
            embeddings = await self._generate_embeddings([chunk['content'] for chunk in chunks])
            
            # Store chunks with embeddings
            stored_chunks = self._store_chunks(document, chunks, embeddings)
            
            # Update document status
            self._update_document_status(doc_id, "done")
            
            logger.info(f"✅ Successfully processed document {doc_id}: {len(stored_chunks)} chunks")
            
            return {
                "status": "success",
                "document_id": doc_id,
                "chunks_processed": len(stored_chunks),
                "embedding_model": self.embedding_model
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing document {doc_id}: {e}")
            self._update_document_status(doc_id, "error")
            return {"status": "error", "message": str(e)}
    
    async def batch_process(self, docset_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Batch process pending documents
        
        Args:
            docset_name: Optional docset name to filter documents
            
        Returns:
            Batch processing result
        """
        try:
            # Get pending documents
            pending_docs = self._get_pending_documents(docset_name)
            
            if not pending_docs:
                return {"status": "success", "message": "No pending documents to process"}
            
            logger.info(f"🔄 Starting batch processing of {len(pending_docs)} documents")
            
            # Process documents concurrently (with rate limiting)
            semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
            
            async def process_with_semaphore(doc):
                async with semaphore:
                    return await self.process_document(doc['id'])
            
            # Process documents
            tasks = [process_with_semaphore(doc) for doc in pending_docs]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count results
            successful = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'success')
            failed = len(results) - successful
            
            logger.info(f"✅ Batch processing completed: {successful} successful, {failed} failed")
            
            return {
                "status": "success",
                "total_documents": len(pending_docs),
                "successful": successful,
                "failed": failed,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Error in batch processing: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            # Batch process embeddings
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            embeddings = [embedding.embedding for embedding in response.data]
            
            logger.info(f"✅ Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {e}")
            raise
    
    def _get_document(self, doc_id: str) -> Optional[Dict]:
        """Get document from database"""
        try:
            result = self.storage.supabase.table("documents").select("*").eq("id", doc_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Error getting document {doc_id}: {e}")
            return None
    
    def _get_pending_documents(self, docset_name: Optional[str] = None) -> List[Dict]:
        """Get pending documents for processing"""
        try:
            query = self.storage.supabase.table("documents").select("*").eq("embedding_status", "pending")
            
            if docset_name:
                # Get docset ID
                docset_result = self.storage.supabase.table("docsets").select("id").eq("name", docset_name).execute()
                if docset_result.data:
                    docset_id = docset_result.data[0]['id']
                    query = query.eq("docset_id", docset_id)
            
            result = query.execute()
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Error getting pending documents: {e}")
            return []
    
    def _update_document_status(self, doc_id: str, status: str):
        """Update document embedding status"""
        try:
            self.storage.supabase.table("documents").update({
                "embedding_status": status,
                "embedding_updated_at": datetime.now().isoformat()
            }).eq("id", doc_id).execute()
            
            logger.info(f"✅ Updated document {doc_id} status to: {status}")
            
        except Exception as e:
            logger.error(f"❌ Error updating document status: {e}")
    
    def _store_chunks(self, document: Dict, chunks: List[Dict], embeddings: List[List[float]]) -> List[Dict]:
        """
        Store chunks with embeddings in database
        
        Args:
            document: Original document
            chunks: List of chunk dictionaries
            embeddings: List of embedding vectors
            
        Returns:
            List of stored chunk data
        """
        try:
            # Get docset name from the document's docset_id
            docset_name = 'default'
            if document.get('docset_id'):
                try:
                    docset_result = self.storage.supabase.table("docsets").select("name").eq("id", document['docset_id']).execute()
                    if docset_result.data:
                        docset_name = docset_result.data[0]['name']
                except Exception as e:
                    logger.warning(f"⚠️ Could not get docset name for docset_id {document['docset_id']}: {e}")
            
            # Prepare chunks for storage
            chunks_data = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                # Enhanced metadata with source information
                enhanced_metadata = self._enhance_chunk_metadata(chunk, document, i)
                
                chunk_data = {
                    "docset_name": docset_name,
                    "document_name": document.get('name', 'Unknown'),
                    "document_id": document['id'],
                    "chunk_index": i,
                    "content": chunk['content'],
                    "embedding": embedding,
                    "metadata": enhanced_metadata
                }
                chunks_data.append(chunk_data)
            
            # Log chunk data for debugging
            chunk_indices = [chunk['chunk_index'] for chunk in chunks_data]
            logger.info(f"📝 Preparing to insert {len(chunks_data)} chunks with indices: {chunk_indices}")
            
            # Use UPSERT operation to handle duplicates gracefully
            # This will update existing chunks or insert new ones
            result = self.storage.supabase.table("chunks").upsert(
                chunks_data,
                on_conflict="document_id,chunk_index"
            ).execute()
            
            logger.info(f"✅ Stored {len(result.data)} chunks for document {document['id']}")
            
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Error storing chunks for document {document.get('id', 'unknown')}: {e}")
            return []
    
    def _enhance_chunk_metadata(self, chunk: Dict, document: Dict, chunk_index: int) -> Dict:
        """
        Enhance chunk metadata with source information for document attribution
        
        Args:
            chunk: Original chunk metadata
            document: Original document
            chunk_index: Index of the chunk
            
        Returns:
            Enhanced metadata dictionary
        """
        # Start with original chunk metadata
        enhanced_metadata = chunk.get('metadata', {}).copy()
        
        # Add document-level information
        enhanced_metadata.update({
            "document_id": document.get('id'),
            "document_name": document.get('name', 'Unknown'),
            "docset_name": document.get('docset_name', 'default'),
            "chunk_index": chunk_index,
            "source_type": self._determine_source_type(document),
            "url": document.get('url', ''),
            "doc_type": document.get('type', 'file'),
            "timestamp": document.get('added_date', ''),
        })
        
        # Add source-specific information
        source_type = enhanced_metadata.get('source_type', 'unknown')
        
        if source_type == "github":
            # GitHub-specific metadata
            enhanced_metadata.update({
                "repo": document.get('metadata', {}).get('repo', ''),
                "owner": document.get('metadata', {}).get('owner', ''),
                "branch": document.get('metadata', {}).get('branch', 'main'),
                "path": document.get('metadata', {}).get('path', ''),
                "sha": document.get('metadata', {}).get('sha', ''),
                "file_path": document.get('metadata', {}).get('path', ''),
            })
            
            # Add line number information if available
            if 'start_line' in chunk.get('metadata', {}):
                enhanced_metadata['start_line'] = chunk['metadata']['start_line']
            if 'end_line' in chunk.get('metadata', {}):
                enhanced_metadata['end_line'] = chunk['metadata']['end_line']
        
        elif source_type == "website":
            # Website-specific metadata
            enhanced_metadata.update({
                "title": document.get('metadata', {}).get('title', ''),
                "depth": document.get('metadata', {}).get('depth', 0),
                "content_size": document.get('metadata', {}).get('content_size', 0),
            })
        
        elif source_type == "file":
            # File upload-specific metadata
            enhanced_metadata.update({
                "file_size": document.get('metadata', {}).get('size', 0),
                "file_type": document.get('metadata', {}).get('file_type', ''),
                "upload_date": document.get('added_date', ''),
            })
        
        return enhanced_metadata
    
    def _determine_source_type(self, document: Dict) -> str:
        """
        Determine source type based on document information
        
        Args:
            document: Document dictionary
            
        Returns:
            Source type string
        """
        doc_type = document.get('type', 'file')
        doc_metadata = document.get('metadata', {})
        
        # Check metadata for GitHub information first
        if doc_metadata.get('repo') and doc_metadata.get('owner'):
            return 'github'
        elif doc_metadata.get('url') and doc_type in ['website', 'url']:
            return 'website'
        elif doc_type == 'file':
            return 'file'
        elif doc_type in ['github_file', 'github_readme', 'github_repo']:
            return 'github'
        elif doc_type in ['website', 'url']:
            return 'website'
        else:
            return 'unknown'
    
    def get_embedding_status_summary(self, docset_name: Optional[str] = None) -> Dict[str, int]:
        """
        Get embedding status summary
        
        Args:
            docset_name: Optional docset name to filter
            
        Returns:
            Dictionary with status counts
        """
        try:
            query = self.storage.supabase.table("documents").select("embedding_status")
            
            if docset_name:
                # Get docset ID
                docset_result = self.storage.supabase.table("docsets").select("id").eq("name", docset_name).execute()
                if docset_result.data:
                    docset_id = docset_result.data[0]['id']
                    query = query.eq("docset_id", docset_id)
            
            result = query.execute()
            
            # Count statuses
            status_counts = {}
            for doc in result.data:
                status = doc.get('embedding_status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return status_counts
            
        except Exception as e:
            logger.error(f"❌ Error getting embedding status summary: {e}")
            return {}
    
    def trigger_embedding_for_docset(self, docset_name: str) -> Dict[str, Any]:
        """
        Trigger embedding process for all documents in a docset
        
        Args:
            docset_name: Name of the docset
            
        Returns:
            Trigger result
        """
        try:
            # Get all documents in docset
            docset = self.storage.get_docset_by_name(docset_name)
            if not docset:
                return {"status": "error", "message": f"DocSet '{docset_name}' not found"}
            
            # Update all documents to pending status
            result = self.storage.supabase.table("documents").update({
                "embedding_status": "pending",
                "embedding_updated_at": datetime.now().isoformat()
            }).eq("docset_id", docset['id']).execute()
            
            logger.info(f"✅ Triggered embedding for {len(result.data)} documents in docset '{docset_name}'")
            
            return {
                "status": "success",
                "docset_name": docset_name,
                "documents_triggered": len(result.data)
            }
            
        except Exception as e:
            logger.error(f"❌ Error triggering embedding for docset '{docset_name}': {e}")
            return {"status": "error", "message": str(e)}
