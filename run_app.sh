#!/bin/bash

# FastAPI'yi arka planda başlat
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Streamlit'i ön planda başlat (Fly bu portu dinleyecek)
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0