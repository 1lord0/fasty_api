"""
Database models for document metadata and tracking
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Document(Base):
    """Document metadata table"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(36), unique=True, index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    pdf_hash = Column(String(32), index=True, nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    pages = Column(Integer, nullable=False)
    chunks = Column(Integer, nullable=False)
    chunk_size = Column(Integer, nullable=False)
    processing_time = Column(Float, nullable=True)  # seconds
    status = Column(String(20), default="completed")  # completed, processing, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Document(filename='{self.filename}', doc_id='{self.doc_id}')>"

class Query(Base):
    """Query history table"""
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    doc_id = Column(String(36), index=True, nullable=True)
    k_value = Column(Integer, default=5)
    response_time = Column(Float, nullable=True)  # seconds
    chunks_used = Column(Integer, nullable=True)
    status = Column(String(20), default="success")  # success, no_results, error
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Query(question='{self.question[:50]}...', status='{self.status}')>"

class APIKey(Base):
    """API Key management table"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    rate_limit = Column(Integer, default=100)  # requests per hour
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<APIKey(name='{self.name}', is_active={self.is_active})>"
