"""ChromaDB vector store for semantic caching and search."""
import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Any, Optional
import config


class VectorStore:
    """ChromaDB wrapper for semantic search and caching."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize ChromaDB client.
        
        Args:
            db_path: Path to ChromaDB directory. Defaults to config.CHROMA_DB_PATH
        """
        self.db_path = db_path or config.CHROMA_DB_PATH
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="research_cache",
            metadata={"description": "Research results cache"}
        )
    
    def add(
        self,
        query: str,
        results: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add research results to vector store.
        
        Args:
            query: Original research query
            results: Research results dictionary
            metadata: Additional metadata
        """
        import hashlib
        
        # Generate ID from query
        doc_id = hashlib.md5(query.encode()).hexdigest()
        
        # Combine query and results for embedding
        document_text = f"Query: {query}\n\nResults: {str(results)}"
        
        # Prepare metadata
        from datetime import datetime
        doc_metadata = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        try:
            # Add to collection
            self.collection.add(
                ids=[doc_id],
                documents=[document_text],
                metadatas=[doc_metadata]
            )
        except Exception as e:
            # Silently fail if vector store fails
            pass
    
    def search(
        self,
        query: str,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Search for similar research queries.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of similar research results
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'document': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return formatted_results
        except Exception as e:
            # Return empty list on error
            return []
    
    def clear(self) -> None:
        """Clear all entries from vector store."""
        try:
            self.client.delete_collection(name="research_cache")
            self.collection = self.client.get_or_create_collection(
                name="research_cache",
                metadata={"description": "Research results cache"}
            )
        except Exception:
            pass

