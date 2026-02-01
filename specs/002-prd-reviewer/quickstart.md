# Quickstart Guide: PRD Reviewer Web Application

**Date**: 2024-12-19  
**Feature**: 002-prd-reviewer

## Overview

This guide provides step-by-step instructions for setting up and running the PRD Reviewer application locally for development and testing.

## Prerequisites

- **Python 3.11+** installed
- **Node.js 18+** and npm/yarn installed
- **OpenAI API key** (or Anthropic API key as alternative)
- **Git** for version control

## Setup Steps

### 1. Clone Repository

```bash
git clone <repository-url>
cd PRD-corrector
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Backend Configuration

Create a `.env` file in the `backend/` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
# OR use Anthropic:
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Server configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS (for local development)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 4. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
# or
yarn install
```

### 5. Frontend Configuration

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:8000/api
```

## Running the Application

### Start Backend Server

```bash
# From project root (easiest — no need to type uvicorn):
./backend/run.sh

# Or from backend/ with venv activated:
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

> If you get **"uvicorn: command not found"**, use `python -m uvicorn` (or `python3 -m uvicorn`) as above; do not run `uvicorn` directly.

The API will be available at `http://localhost:8000`
API documentation (Swagger UI) at `http://localhost:8000/docs`

### Start Frontend Development Server

```bash
# From frontend/ directory
npm run dev
# or
yarn dev
```

The frontend will be available at `http://localhost:5173` (or port shown in terminal)

## Testing the Application

### Test Scenario 1: Upload a PRD File

1. Open `http://localhost:5173` in your browser
2. Click "Upload PRD" or drag-and-drop a `.txt`, `.md`, or `.docx` file
3. Wait for analysis to complete (should take < 30 seconds)
4. Review suggestions organized by category and priority

### Test Scenario 2: Paste PRD Content

1. Open the application
2. Click "Paste Text" option
3. Paste PRD content into the text area
4. Click "Analyze"
5. Review the generated suggestions

### Test Scenario 3: Export Results

1. After analysis completes, click "Export"
2. Choose format (PDF, Markdown, or JSON)
3. Download and verify the exported file

### Sample PRD for Testing

Create a file `test-prd.txt`:

```
# Product Requirements Document: Sample Feature

## Overview
This is a sample PRD for testing the reviewer application.

## Goals
- Test the analysis functionality
- Verify suggestion generation

## User Stories
As a user, I want to test the system.

## Technical Requirements
The system should work.
```

## API Testing with cURL

### Upload and Analyze PRD

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@test-prd.txt" \
  -H "Content-Type: multipart/form-data"
```

### Get Analysis Results

```bash
# Replace {analysis_id} with ID from previous response
curl http://localhost:8000/api/analysis/{analysis_id}
```

### Check Analysis Status

```bash
curl http://localhost:8000/api/analysis/{analysis_id}/status
```

### Export Analysis

```bash
curl -X POST http://localhost:8000/api/export \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "{analysis_id}",
    "format": "pdf"
  }' \
  --output export.pdf
```

## Development Workflow

### Running Tests

**Backend Tests:**
```bash
cd backend
pytest
# With coverage:
pytest --cov=src --cov-report=html
```

**Frontend Tests:**
```bash
cd frontend
npm test
# or
yarn test
```

### Code Formatting

**Backend:**
```bash
cd backend
black src/
isort src/
```

**Frontend:**
```bash
cd frontend
npm run format
# or
yarn format
```

### Linting

**Backend:**
```bash
cd backend
flake8 src/
mypy src/
```

**Frontend:**
```bash
cd frontend
npm run lint
# or
yarn lint
```

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError` when running backend
- **Solution**: Ensure virtual environment is activated and dependencies are installed

**Issue**: `OpenAI API key not found`
- **Solution**: Check `.env` file exists and contains `OPENAI_API_KEY`

**Issue**: Port 8000 already in use
- **Solution**: Change `PORT` in `.env` or kill process using port 8000

### Frontend Issues

**Issue**: Cannot connect to API
- **Solution**: Verify `VITE_API_URL` in frontend `.env` matches backend URL
- **Solution**: Check CORS settings in backend

**Issue**: Build errors
- **Solution**: Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`

### Analysis Issues

**Issue**: Analysis takes too long (> 30 seconds)
- **Solution**: Check OpenAI API status, verify API key is valid
- **Solution**: Check network connectivity

**Issue**: No suggestions generated
- **Solution**: Verify PRD content is meaningful (not empty, has structure)
- **Solution**: Check backend logs for errors

## Next Steps

1. Review the [specification](../spec.md) for full feature list
2. Check [data model](data-model.md) for entity relationships
3. Review [API contracts](contracts/api.yaml) for endpoint details
4. See [implementation plan](plan.md) for architecture decisions

## Production Deployment

For production deployment, see deployment documentation (to be created). Key considerations:
- Use environment variables for all secrets
- Set up proper CORS configuration
- Configure rate limiting
- Set up monitoring and logging
- Use production-grade database (PostgreSQL) for Phase 2
