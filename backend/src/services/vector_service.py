"""
Vector store service for RAG functionality using ChromaDB.
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from config import settings as app_settings
import hashlib
from datetime import datetime


class VectorService:
    """Service for managing vector embeddings and semantic search."""
    
    def __init__(self, persist_directory: str = None):
        """
        Initialize ChromaDB client.
        
        Args:
            persist_directory: Directory to persist the database
        """
        persist_dir = persist_directory or app_settings.vector_db_path
        
        self.client = chromadb.Client(Settings(
            persist_directory=persist_dir,
            anonymized_telemetry=False
        ))
        
        # Get or create collection for analysis history
        self.collection = self.client.get_or_create_collection(
            name="analysis_history",
            metadata={"description": "Historical analysis queries and results"}
        )
    
    def add_analysis(
        self,
        query: str,
        result: str,
        dataset_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add an analysis to the vector store.
        
        Args:
            query: User query
            result: Analysis result
            dataset_id: Dataset identifier
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        # Create unique ID
        doc_id = hashlib.md5(
            f"{query}_{dataset_id}_{datetime.now().isoformat()}".encode()
        ).hexdigest()
        
        # Combine query and result for embedding
        document = f"Query: {query}\nResult: {result}"
        
        # Prepare metadata
        doc_metadata = {
            "dataset_id": dataset_id,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        # Add to collection
        self.collection.add(
            documents=[document],
            metadatas=[doc_metadata],
            ids=[doc_id]
        )
        
        return doc_id
    
    def search_similar(
        self,
        query: str,
        dataset_id: Optional[str] = None,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search for similar analyses.
        
        Args:
            query: Search query
            dataset_id: Filter by dataset ID
            n_results: Number of results to return
            
        Returns:
            List of similar analyses with metadata
        """
        # Build where clause for filtering
        where = None
        if dataset_id:
            where = {"dataset_id": dataset_id}
        
        # Query collection
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'document': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None
                })
        
        return formatted_results
    
    def get_context(
        self,
        query: str,
        dataset_id: Optional[str] = None,
        n_results: int = 3
    ) -> str:
        """
        Get context from similar past analyses.
        
        Args:
            query: Current query
            dataset_id: Dataset ID to filter by
            n_results: Number of similar analyses to retrieve
            
        Returns:
            Formatted context string
        """
        similar = self.search_similar(query, dataset_id, n_results)
        
        if not similar:
            return "No relevant past analyses found."
        
        context = "Relevant past analyses:\n\n"
        for i, result in enumerate(similar, 1):
            context += f"{i}. {result['document']}\n\n"
        
        return context
    
    def clear_dataset(self, dataset_id: str):
        """
        Remove all analyses for a specific dataset.
        
        Args:
            dataset_id: Dataset identifier
        """
        # Get all IDs for this dataset
        results = self.collection.get(
            where={"dataset_id": dataset_id}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])


# Global vector service instance
vector_service = VectorService()
