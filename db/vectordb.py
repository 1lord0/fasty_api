from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma  # Güncel import
import os

# Embedding modeli
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Persist dizinini oluştur (yoksa)
persist_dir = "data/chroma"
os.makedirs(persist_dir, exist_ok=True)

# Vectorstore'u başlat
vectorstore = Chroma(
    persist_directory=persist_dir,
    embedding_function=embedding_model
)

def add_to_vectorstore(chunks, doc_id):
    """
    Metin parçalarını vector store'a ekler
    
    Args:
        chunks: Eklenecek metin parçaları listesi
        doc_id: Doküman ID'si
    """
    if not chunks:
        print("Eklenecek chunk bulunamadı!")
        return
    
    # Metadata oluştur
    metadatas = [{"doc_id": doc_id} for _ in chunks]
    
    # Vector store'a ekle
    try:
        vectorstore.add_texts(texts=chunks, metadatas=metadatas)
        print(f"{len(chunks)} chunk başarıyla eklendi (doc_id: {doc_id})")
    except Exception as e:
        print(f"Ekleme hatası: {e}")

# Kullanım örneği
if __name__ == "__main__":
    sample_chunks = [
        "Bu bir test metnidir.",
        "Vector store kullanımı örneği.",
        "LangChain ile Chroma entegrasyonu."
    ]
    add_to_vectorstore(sample_chunks, doc_id="test_doc_1")