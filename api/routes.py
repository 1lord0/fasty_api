"""
API Routes with enhanced features
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query as QueryParam
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import time
from datetime import datetime
from typing import Optional, List

from services.pdf_processor import process_pdf
from services.vector_service import search_vector_db
from services.llm_service import ask_llm
from models.schemas import (
    QuestionRequest, QuestionResponse, DocumentUploadResponse,
    HealthCheck, StatsResponse, DocumentInfo, QueryHistory
)
from db.database import get_db
from db.models import Document, Query
from config.settings import settings
from utils.logger import logger

router = APIRouter()

# ============= Question Answering =============

@router.post(
    "/ask",
    response_model=QuestionResponse,
    tags=["RAG"],
    summary="Ask a question",
    description="Ask a question and get an answer based on uploaded documents"
)
async def ask_question(
    question: str = QueryParam(..., min_length=3, max_length=1000, description="Your question"),
    k: int = QueryParam(default=5, ge=1, le=20, description="Number of context chunks to retrieve"),
    doc_id: Optional[str] = QueryParam(None, description="Search in specific document"),
    db: AsyncSession = Depends(get_db)
):
    """Ask a question and get RAG-based answer"""
    start_time = time.time()
    
    try:
        logger.info(f"📝 Question received: {question[:100]}...")
        
        # 1️⃣ Search vector database
        context_chunks = search_vector_db(question, k=k, doc_id=doc_id)
        
        if not context_chunks:
            # Save query to database
            query_record = Query(
                question=question,
                k_value=k,
                doc_id=doc_id,
                status="no_results",
                response_time=time.time() - start_time
            )
            db.add(query_record)
            await db.commit()
            
            return QuestionResponse(
                status="no_results",
                message="No relevant documents found. Please upload PDFs first.",
                question=question,
                answer=None,
                sources=[],
                count=0,
                response_time=time.time() - start_time
            )
        
        # 2️⃣ Build context
        context = "\n\n".join([chunk["content"] for chunk in context_chunks])
        
        # 3️⃣ Create RAG prompt
        prompt = f"""You are an academic assistant. Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't know based on the provided documents."

Context:
{context}

Question:
{question}

Answer:"""
        
        # 4️⃣ Get LLM response
        logger.info("🤖 Calling LLM...")
        answer = ask_llm(prompt)
        
        # 5️⃣ Save to database
        query_record = Query(
            question=question,
            answer=answer,
            k_value=k,
            doc_id=doc_id,
            chunks_used=len(context_chunks),
            status="success",
            response_time=time.time() - start_time
        )
        db.add(query_record)
        await db.commit()
        
        logger.info(f"✅ Question answered in {time.time() - start_time:.2f}s")
        
        return QuestionResponse(
            status="success",
            question=question,
            answer=answer.strip(),
            sources=context_chunks,
            count=len(context_chunks),
            response_time=time.time() - start_time
        )
        
    except Exception as e:
        logger.error(f"❌ Error in ask endpoint: {e}", exc_info=True)
        
        # Save error to database
        try:
            query_record = Query(
                question=question,
                k_value=k,
                doc_id=doc_id,
                status="error",
                error_message=str(e),
                response_time=time.time() - start_time
            )
            db.add(query_record)
            await db.commit()
        except:
            pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Error answering question: {str(e)}"
        )

# ============= Document Upload =============

@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    tags=["Documents"],
    summary="Upload PDF",
    description="Upload and process a PDF document"
)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file to upload"),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process PDF document"""
    start_time = time.time()
    
    try:
        # Validate file type
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )
        
        # Check file size
        file_size = 0
        file_bytes = await file.read()
        file_size = len(file_bytes)
        await file.seek(0)  # Reset file pointer
        
        max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        logger.info(f"📄 Processing PDF: {file.filename} ({file_size / 1024 / 1024:.2f}MB)")
        
        # Process PDF
        result = await process_pdf(file)
        
        if result["status"] == "error":
            # Save error to database
            doc_record = Document(
                doc_id=result.get("doc_id", "error"),
                filename=file.filename,
                pdf_hash=result.get("pdf_hash", "error"),
                file_size=file_size,
                pages=0,
                chunks=0,
                chunk_size=0,
                status="failed",
                error_message=result.get("message"),
                processing_time=time.time() - start_time
            )
            db.add(doc_record)
            await db.commit()
            
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )
        
        # Save to database
        doc_record = Document(
            doc_id=result["doc_id"],
            filename=file.filename,
            pdf_hash=result["pdf_hash"],
            file_size=file_size,
            pages=result["pages"],
            chunks=result["chunks"],
            chunk_size=result["chunk_size"],
            status="completed",
            processing_time=time.time() - start_time
        )
        db.add(doc_record)
        await db.commit()
        
        logger.info(f"✅ PDF processed successfully in {time.time() - start_time:.2f}s")
        
        return DocumentUploadResponse(
            status="success",
            doc_id=result["doc_id"],
            pdf_hash=result["pdf_hash"],
            filename=file.filename,
            pages=result["pages"],
            chunks=result["chunks"],
            chunk_size=result["chunk_size"],
            processing_time=time.time() - start_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error uploading PDF: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )

# ============= Health & Status =============

@router.get(
    "/health",
    response_model=HealthCheck,
    tags=["System"],
    summary="Health check",
    description="Check API health status"
)
async def health_check():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy",
        message="API is running",
        version=settings.APP_VERSION,
        timestamp=datetime.now()
    )

@router.get(
    "/stats",
    response_model=StatsResponse,
    tags=["System"],
    summary="System statistics",
    description="Get system usage statistics"
)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get system statistics"""
    try:
        # Count documents
        doc_count = await db.scalar(select(func.count()).select_from(Document))
        
        # Count queries
        query_count = await db.scalar(select(func.count()).select_from(Query))
        
        # Count chunks
        chunks_result = await db.execute(select(func.sum(Document.chunks)))
        total_chunks = chunks_result.scalar() or 0
        
        # Average response time
        avg_time_result = await db.execute(
            select(func.avg(Query.response_time)).where(Query.response_time.isnot(None))
        )
        avg_response_time = avg_time_result.scalar()
        
        return StatsResponse(
            total_documents=doc_count or 0,
            total_queries=query_count or 0,
            total_chunks=int(total_chunks),
            avg_response_time=float(avg_response_time) if avg_response_time else None
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= Document Management =============

@router.get(
    "/documents",
    response_model=List[DocumentInfo],
    tags=["Documents"],
    summary="List documents",
    description="Get list of all uploaded documents"
)
async def list_documents(
    limit: int = QueryParam(default=50, ge=1, le=100),
    offset: int = QueryParam(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List all uploaded documents"""
    try:
        result = await db.execute(
            select(Document)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        documents = result.scalars().all()
        return documents
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/queries",
    response_model=List[QueryHistory],
    tags=["Queries"],
    summary="Query history",
    description="Get query history"
)
async def get_query_history(
    limit: int = QueryParam(default=50, ge=1, le=100),
    offset: int = QueryParam(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get query history"""
    try:
        result = await db.execute(
            select(Query)
            .order_by(Query.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        queries = result.scalars().all()
        return queries
    except Exception as e:
        logger.error(f"Error getting query history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
