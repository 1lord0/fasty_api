"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# ============= Request Models =============

class QuestionRequest(BaseModel):
    """Question request with validation"""
    question: str = Field(..., min_length=3, max_length=1000, description="Question to ask")
    k: int = Field(default=5, ge=1, le=20, description="Number of context chunks")
    doc_id: Optional[str] = Field(None, description="Specific document ID to search in")
    
    @validator('question')
    def question_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty or whitespace')
        return v.strip()

class DocumentUploadResponse(BaseModel):
    """Response for document upload"""
    status: str = Field(..., description="Upload status")
    doc_id: Optional[str] = None
    pdf_hash: Optional[str] = None
    filename: Optional[str] = None
    pages: Optional[int] = None
    chunks: Optional[int] = None
    chunk_size: Optional[int] = None
    processing_time: Optional[float] = None
    message: Optional[str] = None

# ============= Response Models =============

class ContextChunk(BaseModel):
    """Context chunk with metadata"""
    content: str
    metadata: Dict[str, Any]
    score: float

class QuestionResponse(BaseModel):
    """Response for question answering"""
    status: str
    question: str
    answer: Optional[str] = None
    sources: List[ContextChunk] = []
    count: int = 0
    response_time: Optional[float] = None
    message: Optional[str] = None

class DocumentInfo(BaseModel):
    """Document information"""
    id: int
    doc_id: str
    filename: str
    pdf_hash: str
    pages: int
    chunks: int
    chunk_size: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class QueryHistory(BaseModel):
    """Query history entry"""
    id: int
    question: str
    answer: Optional[str]
    doc_id: Optional[str]
    k_value: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    message: str
    version: str
    timestamp: datetime

class StatsResponse(BaseModel):
    """System statistics"""
    total_documents: int
    total_queries: int
    total_chunks: int
    avg_response_time: Optional[float] = None
    cache_hit_rate: Optional[float] = None

# ============= Error Models =============

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
