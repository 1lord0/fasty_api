from services.vector_service import search_vector_db
from services.llm_service import ask_llm


def answer_with_rag(question: str, k: int = 5):
    """
    Soruya VectorDB'den bağlam çekerek LLM ile cevap üretir
    """

    # 1️⃣ Vector DB'den en alakalı parçaları getir
    results = search_vector_db(question, k=k)

    if not results:
        return {
            "answer": "Bu soruya cevap verecek yeterli bilgi bulunamadı.",
            "sources": []
        }

    # 2️⃣ Context oluştur
    context = "\n\n".join(results)

    # 3️⃣ RAG Prompt
    prompt = f"""
You are an academic assistant.
Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't know based on the provided document."

Context:
{context}

Question:
{question}

Answer:
"""

    # 4️⃣ LLM'e sor
    answer = ask_llm(prompt)

    # 5️⃣ Response
    return {
        "answer": answer.strip(),
        "sources": results
    }
