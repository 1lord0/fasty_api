# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 19:51:05 2026

@author: eren
"""

import uuid
import hashlib
import io  # ✅ Eklenmeli
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from services.vector_service import add_to_vectorstore, is_pdf_exists

def get_pdf_hash(file_bytes):
    """PDF'in MD5 hash'ini hesapla"""
    return hashlib.md5(file_bytes).hexdigest()

def get_chunk_params(text):
    """Metin uzunluğuna göre dinamik chunk parametreleri"""
    length = len(text)
    if length < 10_000:
        return 300, 50
    elif length < 50_000:
        return 500, 100
    else:
        return 800, 150

async def process_pdf(file):
    """PDF dosyasını işle ve vector store'a ekle"""
    try:
        doc_id = str(uuid.uuid4())
        
        # PDF binary oku
        file_bytes = await file.read()
        pdf_hash = get_pdf_hash(file_bytes)
        
        # ✅ DÜZELTME: BytesIO kullan
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        
        # PDF text extraction
        texts = []
        total_pages = len(reader.pages)
        print(f"PDF işleniyor: {total_pages} sayfa")
        
        for i, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                texts.append(page_text)
            if i % 50 == 0:  # Her 50 sayfada progress
                print(f"İşlenen sayfa: {i}/{total_pages}")
        
        if not texts:
            return {
                "status": "error",
                "message": "PDF'den metin çıkarılamadı"
            }
        
        full_text = "\n".join(texts)
        print(f"Toplam metin uzunluğu: {len(full_text)} karakter")
        
        # Dinamik chunk ayarı
        chunk_size, chunk_overlap = get_chunk_params(full_text)
        print(f"Chunk parametreleri: size={chunk_size}, overlap={chunk_overlap}")
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        chunks = splitter.split_text(full_text)
        print(f"Oluşturulan chunk sayısı: {len(chunks)}")
        
        # ✅ Metadata ile vector db'ye ekle
        add_to_vectorstore(
            chunks=chunks,
            doc_id=doc_id,
            pdf_hash=pdf_hash,  # Metadata'ya eklenecek
            filename=file.filename if hasattr(file, 'filename') else 'unknown.pdf'
        )
        
        return {
            "status": "success",
            "doc_id": doc_id,
            "pdf_hash": pdf_hash,
            "pages": total_pages,
            "chunks": len(chunks),
            "chunk_size": chunk_size
        }
    
    except Exception as e:
        print(f"❌ PDF işleme hatası: {e}")
        return {
            "status": "error",
            "message": str(e)
        }