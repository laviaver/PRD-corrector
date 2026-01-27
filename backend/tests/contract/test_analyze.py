"""
Contract tests for POST /api/analyze endpoint.

Tests API contract compliance, request/response formats, and error handling.

Uses LLM_PROVIDER=ollama so the app starts without needing Groq/OpenAI clients
(it only checks request/response shape; analysis runs in background).
"""

import os

# Force ollama for contract tests so app boots without Groq/OpenAI client
os.environ["LLM_PROVIDER"] = "ollama"

import pytest
from fastapi.testclient import TestClient
from io import BytesIO

from src.main import app

client = TestClient(app)


class TestAnalyzeEndpoint:
    """Test suite for POST /api/analyze endpoint."""

    def test_analyze_with_file_upload_txt(self):
        """Test analyze endpoint with .txt file upload."""
        file_content = b"Test PRD content from file"
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
        
        response = client.post("/api/analyze", files=files)
        
        assert response.status_code == 201
        data = response.json()
        assert "prd_id" in data
        assert "analysis_id" in data
        assert "message" in data
        assert "Analysis initiated" in data["message"] or "PRD uploaded successfully" in data["message"]

    def test_analyze_with_file_upload_md(self):
        """Test analyze endpoint with .md file upload."""
        file_content = b"# PRD Title\n\nContent here"
        files = {"file": ("test.md", BytesIO(file_content), "text/markdown")}
        
        response = client.post("/api/analyze", files=files)
        
        assert response.status_code == 201
        data = response.json()
        assert "prd_id" in data

    def test_analyze_with_text_paste(self):
        """Test analyze endpoint with text paste."""
        data = {"text": "Pasted PRD content"}
        
        response = client.post("/api/analyze", data=data)
        
        assert response.status_code == 201
        result = response.json()
        assert "prd_id" in result
        assert "message" in result

    def test_analyze_no_input(self):
        """Test that analyze endpoint requires input."""
        response = client.post("/api/analyze")
        
        # May return 400 or 422 (validation error)
        assert response.status_code in [400, 422]
        data = response.json()
        # Check for error message in either "detail" or "error" field
        error_msg = data.get("detail") or data.get("error", "")
        assert "Provide either file upload or text content" in str(error_msg) or response.status_code == 422

    def test_analyze_both_file_and_text(self):
        """Test that providing both file and text raises error."""
        file_content = b"Test content"
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
        form_data = {"text": "Pasted content"}
        
        response = client.post("/api/analyze", files=files, data=form_data)
        
        assert response.status_code == 400
        result = response.json()
        error_msg = result.get("detail") or result.get("error", "")
        assert "not both" in str(error_msg)

    def test_analyze_invalid_file_type(self):
        """Test that invalid file type returns error."""
        file_content = b"Test content"
        files = {"file": ("test.pdf", BytesIO(file_content), "application/pdf")}
        
        response = client.post("/api/analyze", files=files)
        
        assert response.status_code == 400
        data = response.json()
        # Error handler may return "error" or "detail"
        assert "error" in data or "detail" in data

    def test_analyze_file_too_large(self):
        """Test that file too large returns error."""
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("large.txt", BytesIO(large_content), "text/plain")}
        
        response = client.post("/api/analyze", files=files)
        
        assert response.status_code == 400
        data = response.json()
        # Error handler may return "error" or "detail"
        assert "error" in data or "detail" in data

    def test_analyze_empty_text(self):
        """Test that empty text returns error."""
        form_data = {"text": ""}
        
        response = client.post("/api/analyze", data=form_data)
        
        assert response.status_code in [400, 422]
        result = response.json()
        # Error may be in "detail" or "error" field
        assert "detail" in result or "error" in result
