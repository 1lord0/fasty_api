"""
Tests for the API endpoints
"""
import pytest
from httpx import AsyncClient
from fastapi import status
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "running"
        assert "version" in data

@pytest.mark.asyncio
async def test_stats_endpoint():
    """Test stats endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/stats")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_documents" in data
        assert "total_queries" in data

@pytest.mark.asyncio
async def test_ask_without_documents():
    """Test asking question when no documents uploaded"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/ask",
            params={"question": "What is this about?", "k": 5}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "no_results"

@pytest.mark.asyncio
async def test_upload_invalid_file():
    """Test uploading non-PDF file"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        files = {"file": ("test.txt", b"test content", "text/plain")}
        response = await client.post("/upload", files=files)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_documents_list():
    """Test documents listing endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/documents")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_queries_history():
    """Test queries history endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/queries")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
