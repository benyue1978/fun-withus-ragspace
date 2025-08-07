"""
RAG Response Generator for generating contextual responses
"""

import os
import logging
from typing import List, Dict, Optional, Any, AsyncGenerator
import openai
from dotenv import load_dotenv
import time

from .rag_retriever import RAGRetriever

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGResponseGenerator:
    """RAG response generator for contextual answer generation"""
    
    def __init__(self, model_name: str = "openai"):
        """Initialize RAG response generator"""
        self.model_name = model_name
        self.retriever = RAGRetriever(model_name)
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        
        self.openai_client = openai.OpenAI(api_key=api_key)
        
        # LLM model configuration
        self.llm_model = "gpt-3.5-turbo"
        
        # Response generation configuration
        self.max_context_length = 4000  # Maximum context length for LLM
        self.max_response_length = 1000  # Maximum response length
        
        logger.info(f"✅ RAG response generator initialized with model: {self.llm_model}")
    
    async def generate_response(self, query: str, docsets: Optional[List[str]] = None,
                              conversation_history: Optional[List[Dict]] = None,
                              stream: bool = True) -> AsyncGenerator[str, None]:
        """
        Generate response using RAG pipeline
        
        Args:
            query: User query
            docsets: Optional list of docset names to search in
            conversation_history: Optional conversation history
            stream: Whether to stream the response
            
        Yields:
            Response chunks as they are generated
        """
        try:
            # Retrieve relevant chunks
            retrieval_result = await self.retriever.hybrid_retrieve(query, docsets)
            
            if retrieval_result["status"] != "success":
                yield f"❌ Error retrieving context: {retrieval_result.get('error', 'Unknown error')}"
                return
            
            chunks = retrieval_result["chunks"]
            
            if not chunks:
                yield "❌ No relevant information found in the knowledge base. Please try rephrasing your question or add more documents to the knowledge base."
                return
            
            # Assemble context from chunks
            context = self._assemble_context(chunks)
            
            # Generate response
            if stream:
                async for chunk in self._generate_streaming_response(query, context, conversation_history):
                    yield chunk
            else:
                response = await self._generate_complete_response(query, context, conversation_history)
                yield response
                
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            yield f"❌ Error generating response: {str(e)}"
    
    def _assemble_context(self, chunks: List[Dict]) -> str:
        """
        Assemble context from retrieved chunks
        
        Args:
            chunks: List of retrieved chunks
            
        Returns:
            Assembled context string
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks):
            source_info = f"Source {i+1}: {chunk.get('document_name', 'Unknown')}"
            content = chunk.get('content', '')
            
            # Truncate content if too long
            if len(content) > 800:
                content = content[:800] + "..."
            
            context_parts.append(f"{source_info}\n{content}\n")
        
        context = "\n".join(context_parts)
        
        # Limit context length
        if len(context) > self.max_context_length:
            context = context[:self.max_context_length] + "..."
        
        return context
    
    async def _generate_streaming_response(self, query: str, context: str,
                                         conversation_history: Optional[List[Dict]] = None) -> AsyncGenerator[str, None]:
        """Generate streaming response"""
        try:
            # Prepare messages
            messages = self._prepare_messages(query, context, conversation_history)
            
            # Generate streaming response
            response = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=self.max_response_length
            )
            
            # Stream response chunks
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"❌ Error in streaming response generation: {e}")
            yield f"❌ Error generating response: {str(e)}"
    
    async def _generate_complete_response(self, query: str, context: str,
                                        conversation_history: Optional[List[Dict]] = None) -> str:
        """Generate complete response"""
        try:
            # Prepare messages
            messages = self._prepare_messages(query, context, conversation_history)
            
            # Generate response
            response = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=0.7,
                max_tokens=self.max_response_length
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Error in complete response generation: {e}")
            return f"❌ Error generating response: {str(e)}"
    
    def _prepare_messages(self, query: str, context: str,
                         conversation_history: Optional[List[Dict]] = None) -> List[Dict]:
        """Prepare messages for LLM"""
        system_prompt = """You are a helpful AI assistant with access to a knowledge base. 
Your task is to answer questions based on the provided context from the knowledge base.

Guidelines:
1. Answer questions based ONLY on the provided context
2. If the context doesn't contain enough information, say so clearly
3. Always cite your sources when possible
4. Be concise but comprehensive
5. If the question is about code, provide code examples when available
6. If you're unsure about something, acknowledge the uncertainty

Format your response clearly and provide source citations when possible."""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            # Limit history to last 10 messages to avoid token limits
            recent_history = conversation_history[-10:]
            messages.extend(recent_history)
        
        # Add current query with context
        user_message = f"""Context from knowledge base:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above."""
        
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    async def generate_response_with_metadata(self, query: str, docsets: Optional[List[str]] = None,
                                            conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Generate response with metadata
        
        Args:
            query: User query
            docsets: Optional list of docset names
            conversation_history: Optional conversation history
            
        Returns:
            Response with metadata
        """
        try:
            start_time = time.time()
            
            # Retrieve chunks
            retrieval_result = await self.retriever.hybrid_retrieve(query, docsets)
            
            if retrieval_result["status"] != "success":
                return {
                    "status": "error",
                    "query": query,
                    "error": retrieval_result.get("error", "Unknown error"),
                    "response": "",
                    "sources": [],
                    "metadata": {}
                }
            
            chunks = retrieval_result["chunks"]
            
            if not chunks:
                return {
                    "status": "success",
                    "query": query,
                    "response": "No relevant information found in the knowledge base.",
                    "sources": [],
                    "metadata": {
                        "chunks_retrieved": 0,
                        "retrieval_time": retrieval_result.get("retrieval_time", 0),
                        "generation_time": 0
                    }
                }
            
            # Assemble context
            context = self._assemble_context(chunks)
            
            # Generate response
            generation_start = time.time()
            response = await self._generate_complete_response(query, context, conversation_history)
            generation_time = time.time() - generation_start
            
            # Prepare sources
            sources = self._prepare_sources(chunks)
            
            # Calculate total time
            total_time = time.time() - start_time
            
            return {
                "status": "success",
                "query": query,
                "response": response,
                "sources": sources,
                "metadata": {
                    "chunks_retrieved": len(chunks),
                    "retrieval_time": retrieval_result.get("retrieval_time", 0),
                    "generation_time": generation_time,
                    "total_time": total_time,
                    "context_length": len(context),
                    "response_length": len(response)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error in response generation with metadata: {e}")
            return {
                "status": "error",
                "query": query,
                "error": str(e),
                "response": "",
                "sources": [],
                "metadata": {}
            }
    
    def _prepare_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Prepare source information for response"""
        sources = []
        
        for chunk in chunks:
            source = {
                "document_name": chunk.get("document_name", "Unknown"),
                "docset_name": chunk.get("docset_name", "Unknown"),
                "content_preview": chunk.get("content", "")[:200] + "..." if len(chunk.get("content", "")) > 200 else chunk.get("content", ""),
                "chunk_index": chunk.get("chunk_index", 0)
            }
            sources.append(source)
        
        return sources
    
    async def test_rag_pipeline(self, query: str, docsets: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Test RAG pipeline components
        
        Args:
            query: Test query
            docsets: Optional docset names
            
        Returns:
            Test results
        """
        try:
            results = {}
            
            # Test retrieval
            retrieval_result = await self.retriever.hybrid_retrieve(query, docsets)
            results["retrieval"] = retrieval_result
            
            # Test response generation if retrieval successful
            if retrieval_result["status"] == "success" and retrieval_result["chunks"]:
                response_result = await self.generate_response_with_metadata(query, docsets)
                results["generation"] = response_result
            
            return {
                "status": "success",
                "query": query,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Error testing RAG pipeline: {e}")
            return {
                "status": "error",
                "query": query,
                "error": str(e)
            }
