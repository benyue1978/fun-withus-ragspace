"""
RAG Text Splitter for intelligent document chunking
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ChunkConfig:
    """Configuration for text chunking"""
    chunk_size: int = 500
    chunk_overlap: int = 100
    separators: List[str] = None
    
    def __post_init__(self):
        if self.separators is None:
            self.separators = ["\n\n", "\n", ".", " "]


class RAGTextSplitter:
    """Intelligent text splitter for RAG document processing"""
    
    def __init__(self, config: Optional[ChunkConfig] = None):
        """Initialize text splitter with configuration"""
        self.config = config or ChunkConfig()
        
        # Different configurations for different content types
        self.text_config = ChunkConfig(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", " "]
        )
        
        self.code_config = ChunkConfig(
            chunk_size=300,
            chunk_overlap=50,
            separators=["\nclass ", "\ndef ", "\n", " "]
        )
        
        self.markdown_config = ChunkConfig(
            chunk_size=400,
            chunk_overlap=80,
            separators=["\n## ", "\n### ", "\n\n", "\n", ".", " "]
        )
    
    def split_text(self, text: str, content_type: str = "text") -> List[Dict]:
        """
        Split text into chunks based on content type
        
        Args:
            text: Text to split
            content_type: Type of content ('text', 'code', 'markdown')
            
        Returns:
            List of chunk dictionaries with metadata
        """
        if not text or not text.strip():
            return []
        
        # Choose configuration based on content type
        if content_type == "code":
            config = self.code_config
        elif content_type == "markdown":
            config = self.markdown_config
        else:
            config = self.text_config
        
        # Clean and normalize text
        text = self._clean_text(text)
        
        # Split text into chunks
        chunks = self._split_by_separators(text, config)
        
        # Add metadata to chunks
        return self._add_chunk_metadata(chunks, content_type)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    def _split_by_separators(self, text: str, config: ChunkConfig) -> List[str]:
        """Split text using specified separators"""
        if len(text) <= config.chunk_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by separators
        parts = self._split_text_by_separators(text, config.separators)
        
        for part in parts:
            # If adding this part would exceed chunk size
            if len(current_chunk) + len(part) > config.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap
                overlap_start = max(0, len(current_chunk) - config.chunk_overlap)
                current_chunk = current_chunk[overlap_start:] + part
            else:
                current_chunk += part
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_text_by_separators(self, text: str, separators: List[str]) -> List[str]:
        """Split text by separators in order of preference"""
        parts = [text]
        
        for separator in separators:
            new_parts = []
            for part in parts:
                if separator in part:
                    split_parts = part.split(separator)
                    for i, split_part in enumerate(split_parts):
                        if i > 0:  # Add separator back except for first part
                            new_parts.append(separator + split_part)
                        else:
                            new_parts.append(split_part)
                else:
                    new_parts.append(part)
            parts = new_parts
        
        return parts
    
    def _add_chunk_metadata(self, chunks: List[str], content_type: str) -> List[Dict]:
        """Add metadata to chunks"""
        result = []
        
        for i, chunk in enumerate(chunks):
            metadata = {
                "chunk_index": i,
                "content_type": content_type,
                "chunk_size": len(chunk),
                "word_count": len(chunk.split()),
                "has_code": self._contains_code(chunk),
                "has_markdown": self._contains_markdown(chunk),
            }
            
            result.append({
                "content": chunk,
                "metadata": metadata
            })
        
        return result
    
    def _contains_code(self, text: str) -> bool:
        """Check if text contains code patterns"""
        code_patterns = [
            r'def\s+\w+\s*\(',
            r'class\s+\w+',
            r'import\s+',
            r'from\s+\w+\s+import',
            r'if\s+__name__\s*==\s*[\'"]__main__[\'"]',
            r'return\s+',
            r'print\s*\(',
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _contains_markdown(self, text: str) -> bool:
        """Check if text contains markdown patterns"""
        markdown_patterns = [
            r'^#+\s+',  # Headers
            r'\*\*.*\*\*',  # Bold
            r'\*.*\*',  # Italic
            r'\[.*\]\(.*\)',  # Links
            r'`.*`',  # Inline code
            r'```',  # Code blocks
        ]
        
        for pattern in markdown_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def split_document(self, document: Dict) -> List[Dict]:
        """
        Split a document into chunks
        
        Args:
            document: Document dictionary with content and metadata
            
        Returns:
            List of chunk dictionaries
        """
        content = document.get('content', '')
        doc_type = document.get('type', 'text')
        doc_name = document.get('name', 'Unknown')
        
        # Determine content type
        content_type = self._determine_content_type(content, doc_type)
        
        # Split content
        chunks = self.split_text(content, content_type)
        
        # Add document metadata
        for chunk in chunks:
            chunk['document_name'] = doc_name
            chunk['document_type'] = doc_type
            chunk['document_id'] = document.get('id')
        
        return chunks
    
    def _determine_content_type(self, content: str, doc_type: str) -> str:
        """Determine the content type for chunking strategy"""
        if doc_type in ['code', 'github_file']:
            return 'code'
        elif doc_type in ['markdown', 'readme', 'github_readme']:
            return 'markdown'
        else:
            # Analyze content to determine type
            if self._contains_code(content):
                return 'code'
            elif self._contains_markdown(content):
                return 'markdown'
            else:
                return 'text'
