"""
RAG (Retrieval-Augmented Generation) interface for future extension.

This module defines the interface for RAG capabilities that can be
integrated with the chatbot system in the future.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Document:
    """Represents a document in the knowledge base."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class SearchResult:
    """Represents a search result from the knowledge base."""
    document: Document
    score: float
    relevance: float


class RAGInterface(ABC):
    """
    Abstract interface for RAG capabilities.
    
    This interface defines the contract for implementing retrieval-augmented
    generation features that can enhance chatbot responses with external knowledge.
    """
    
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the knowledge base.
        
        Args:
            documents: List of documents to add
        """
        pass
    
    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of search results ordered by relevance
        """
        pass
    
    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the knowledge base.
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            True if document was deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def clear_knowledge_base(self) -> None:
        """Clear all documents from the knowledge base."""
        pass
    
    @abstractmethod
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.
        
        Returns:
            Dictionary containing knowledge base statistics
        """
        pass
