"""
Simplified Vector Service - Without Heavy ML Dependencies
Uses in-memory storage as fallback
"""
from typing import List, Dict, Optional
from utils.logger import logger

# In-memory storage as fallback
_documents_store = []

def add_to_vectorstore(chunks: List[str], doc_id: str, pdf_hash: str = None, filename: str = None):
    """
    Add chunks to in-memory store (simplified version)
    For full vector search, install: pip install sentence-transformers chromadb langchain-chroma
    """
    try:
        logger.warning("⚠️ Using simplified in-memory storage. Install full dependencies for vector search.")
        
        for i, chunk in enumerate(chunks):
            _documents_store.append({
                "id": f"{doc_id}_{i}",
                "content": chunk,
                "metadata": {
                    "doc_id": doc_id,
                    "pdf_hash": pdf_hash,
                    "filename": filename,
                    "chunk_index": i
                }
            })
        
        logger.info(f"✅ Added {len(chunks)} chunks to storage (doc_id: {doc_id})")
        return {"success": True, "chunks_added": len(chunks)}
        
    except Exception as e:
        logger.error(f"❌ Error adding to store: {e}")
        return {"success": False, "error": str(e)}

def search_vector_db(query: str, k: int = 5, doc_id: Optional[str] = None) -> List[Dict]:
    """
    Simple keyword-based search (fallback)
    For semantic search, install: pip install sentence-transformers chromadb
    """
    try:
        logger.warning("⚠️ Using simple keyword search. Install full dependencies for semantic search.")
        
        # Filter by doc_id if provided
        docs = _documents_store
        if doc_id:
            docs = [d for d in docs if d["metadata"].get("doc_id") == doc_id]
        
        if not docs:
            logger.info("No documents found in storage")
            return []
        
        # Simple keyword matching
        query_lower = query.lower()
        results = []
        
        for doc in docs:
            content_lower = doc["content"].lower()
            # Simple relevance score based on keyword presence
            score = sum(1 for word in query_lower.split() if word in content_lower)
            
            if score > 0:
                results.append({
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "score": float(score)
                })
        
        # Sort by score and return top k
        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:k]
        
        logger.info(f"🔍 Found {len(results)} results using keyword search")
        return results
        
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        return []

def is_pdf_exists(pdf_hash: str) -> bool:
    """Check if PDF exists in storage"""
    return any(d["metadata"].get("pdf_hash") == pdf_hash for d in _documents_store)

def search_similar(query: str, k: int = 5, doc_id: Optional[str] = None) -> List[Dict]:
    """Alias for search_vector_db"""
    return search_vector_db(query, k, doc_id)

# Fallback message
logger.info("📦 Vector service loaded in SIMPLIFIED mode")
logger.info("💡 For full semantic search, install: pip install sentence-transformers chromadb langchain-chroma langchain-huggingface")