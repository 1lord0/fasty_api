import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="PDF RAG Assistant", page_icon="📄")
st.title("📄 PDF RAG Assistant")
st.write("PDF yükle, sorunu sor, dokümandan cevap al")

# -------------------
# PDF UPLOAD
# -------------------
st.subheader("1️⃣ PDF Yükle")

uploaded_file = st.file_uploader("PDF dosyasını seç", type=["pdf"])

if uploaded_file:
    if st.button("PDF Yükle ve İşle"):
        with st.spinner("PDF işleniyor..."):
            try:
                files = {"file": uploaded_file.getvalue()}
                response = requests.post(
                    f"{API_URL}/upload",
                    files={"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                )

                if response.status_code == 200:
                    st.success("PDF başarıyla yüklendi ve işlendi.")
                    st.json(response.json())
                else:
                    st.error("PDF yükleme başarısız")
                    st.text(response.text)

            except Exception as e:
                st.error("FastAPI çalışıyor mu?")
                st.text(str(e))

# -------------------
# ASK QUESTION
# -------------------
st.subheader("2️⃣ Soru Sor")

question = st.text_input("Sorunu yaz:")

k = st.slider("Kaç parça bağlam kullanılsın?", min_value=1, max_value=10, value=5)

if st.button("Sor"):
    if question.strip() == "":
        st.warning("Lütfen bir soru gir.")
    else:
        with st.spinner("Yanıt aranıyor..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    params={"question": question, "k": k}
                )

                if response.status_code == 200:
                    data = response.json()

                    if data["status"] == "no_results":
                        st.warning(data["message"])
                    else:
                        st.success("Cevap:")
                        st.write(data["answer"])

                        with st.expander("🔍 Kaynaklar"):
                            for i, src in enumerate(data["sources"], 1):
                                st.markdown(f"**Parça {i}:**")
                                st.write(src["content"])

                else:
                    st.error("API hata verdi")
                    st.text(response.text)

            except Exception as e:
                st.error("FastAPI çalışıyor mu?")
                st.text(str(e))
