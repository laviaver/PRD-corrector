# PRD Reviewer API Documentation

## Overview

The PRD Reviewer API provides endpoints for uploading PRDs, analyzing them with AI, and retrieving results.

## Base URL

```
http://localhost:8000/api
```

## Authentication

Currently, the API does not require authentication (MVP). Future versions will support user authentication.

## Endpoints

### Health Check

**GET** `/health`

Returns API health status.

**Response:**
```json
{
  "status": "healthy"
}
```

### Analyze PRD

**POST** `/api/analyze`

Upload a PRD file or paste text content for analysis.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file` (optional): PRD file (.txt, .md, .docx, max 10MB)
  - `text` (optional): PRD text content

**Response:**
```json
{
  "prd_id": "uuid",
  "analysis_id": "uuid",
  "message": "PRD uploaded successfully. Analysis initiated."
}
```

### Get Analysis

**GET** `/api/analysis/{analysis_id}`

Retrieve analysis results with suggestions.

**Response:**
```json
{
  "analysis": {
    "id": "uuid",
    "prd_id": "uuid",
    "status": "completed",
    "started_at": "2024-12-19T10:00:00Z",
    "completed_at": "2024-12-19T10:00:30Z",
    "summary": {
      "total_suggestions": 5,
      "suggestions_by_category": {...},
      "suggestions_by_priority": {...}
    }
  },
  "suggestions": [...]
}
```

### Get Analysis Status

**GET** `/api/analysis/{analysis_id}/status`

Poll analysis status.

**Response:**
```json
{
  "status": "processing",
  "started_at": "2024-12-19T10:00:00Z",
  "completed_at": null,
  "error_message": null
}
```

### Export Analysis

**POST** `/api/export`

Export analysis results.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `analysis_id`: Analysis identifier
  - `format`: Export format (pdf, markdown, json)

**Response:**
```json
{
  "export_id": "uuid",
  "analysis_id": "uuid",
  "format": "markdown",
  "file_path": "/tmp/analysis_123.md",
  "created_at": "2024-12-19T10:05:00Z"
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": "Error type",
  "message": "Error description",
  "status_code": 400
}
```

## Rate Limiting

API requests are rate-limited to 60 requests per minute per IP address.

## OpenAPI Specification

Full OpenAPI 3.0 specification available at `/docs` (Swagger UI) or `/redoc`.
