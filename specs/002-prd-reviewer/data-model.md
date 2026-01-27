# Data Model: PRD Reviewer Web Application

**Date**: 2024-12-19  
**Feature**: 002-prd-reviewer

## Overview

This document defines the core data models for the PRD Reviewer application. For MVP (Phase 1), most data is session-based and transient. Phase 2 will introduce persistent storage with user accounts and review history.

## Core Entities

### PRD (Product Requirements Document)

**Purpose**: Represents the uploaded or pasted PRD content

**Fields**:
- `id` (string, UUID): Unique identifier for the PRD
- `content` (string): Full text content of the PRD
- `filename` (string, optional): Original filename if uploaded
- `file_type` (enum: "txt" | "md" | "docx"): Format of the original file
- `uploaded_at` (datetime): Timestamp when PRD was uploaded/pasted
- `size` (integer): Size in bytes
- `metadata` (object, optional): Additional metadata (word count, page count, etc.)

**Validation Rules**:
- Content must not be empty
- Content length must be < 10MB (after extraction)
- File type must be in allowed list: txt, md, docx

**State Transitions**:
- `uploaded` → `analyzing` → `analyzed` → `exported` (optional)

### Analysis

**Purpose**: Represents an analysis run on a PRD

**Fields**:
- `id` (string, UUID): Unique identifier for the analysis
- `prd_id` (string, UUID): Reference to the PRD being analyzed
- `status` (enum: "pending" | "processing" | "completed" | "failed"): Analysis status
- `started_at` (datetime): When analysis started
- `completed_at` (datetime, optional): When analysis completed
- `error_message` (string, optional): Error message if status is "failed"
- `summary` (object, optional): Analysis summary statistics
  - `total_suggestions` (integer)
  - `suggestions_by_category` (object): Count per category
  - `suggestions_by_priority` (object): Count per priority level

**Validation Rules**:
- Must reference a valid PRD
- Status transitions must be valid

**State Transitions**:
- `pending` → `processing` → `completed`
- `pending` → `processing` → `failed`

### Suggestion

**Purpose**: Represents a single improvement suggestion for the PRD

**Fields**:
- `id` (string, UUID): Unique identifier
- `analysis_id` (string, UUID): Reference to the parent analysis
- `category` (enum): Category of suggestion
  - "structure" | "clarity" | "completeness" | "best_practices" | "technical_quality"
- `priority` (enum: "high" | "medium" | "low"): Priority level
- `title` (string): Short title/summary of the suggestion
- `explanation` (string): Detailed explanation of the issue
- `location` (object, optional): Location in document where issue occurs
  - `section` (string, optional): Section name
  - `paragraph_index` (integer, optional): Paragraph number
  - `line_range` (object, optional): { start: integer, end: integer }
- `example` (string, optional): Example of how to fix the issue
- `template` (string, optional): Template or snippet to use

**Validation Rules**:
- Must reference a valid analysis
- Category must be valid enum value
- Priority must be valid enum value
- Title and explanation must not be empty

**Relationships**:
- Many Suggestions belong to one Analysis
- One Analysis has many Suggestions

### Export

**Purpose**: Represents an exported analysis result

**Fields**:
- `id` (string, UUID): Unique identifier
- `analysis_id` (string, UUID): Reference to the analysis being exported
- `format` (enum: "pdf" | "markdown" | "json"): Export format
- `created_at` (datetime): When export was created
- `file_url` (string, optional): URL or path to exported file (if stored)
- `file_size` (integer, optional): Size of exported file in bytes

**Validation Rules**:
- Must reference a valid analysis
- Format must be valid enum value

**Relationships**:
- One Export belongs to one Analysis
- One Analysis can have many Exports

## Phase 2 Entities (Future)

### User

**Fields**:
- `id` (string, UUID)
- `email` (string, unique)
- `name` (string)
- `created_at` (datetime)
- `last_login` (datetime, optional)

### ReviewHistory

**Fields**:
- `id` (string, UUID)
- `user_id` (string, UUID)
- `prd_id` (string, UUID)
- `analysis_id` (string, UUID)
- `created_at` (datetime)
- `improvement_score` (integer, optional): Score showing improvement over time

## Data Relationships

```
PRD (1) ──< (many) Analysis (1) ──< (many) Suggestion
                │
                └──< (many) Export
```

**Phase 2 Relationships**:
```
User (1) ──< (many) ReviewHistory (many) ──> (1) Analysis
```

## API Response Models

### AnalysisResponse

```typescript
{
  id: string;
  status: "pending" | "processing" | "completed" | "failed";
  prd: {
    id: string;
    filename?: string;
    file_type: string;
    content_preview: string; // First 500 chars
  };
  summary?: {
    total_suggestions: number;
    suggestions_by_category: Record<string, number>;
    suggestions_by_priority: Record<string, number>;
  };
  suggestions?: Suggestion[];
  error_message?: string;
}
```

### SuggestionResponse

```typescript
{
  id: string;
  category: string;
  priority: "high" | "medium" | "low";
  title: string;
  explanation: string;
  location?: {
    section?: string;
    paragraph_index?: number;
    line_range?: { start: number; end: number };
  };
  example?: string;
  template?: string;
}
```

## Storage Strategy

### Phase 1 (MVP)
- **PRD**: Stored in memory (backend) or localStorage (frontend)
- **Analysis**: Stored in memory with TTL (time-to-live) of 1 hour
- **Suggestions**: Embedded in Analysis object
- **Export**: Generated on-demand, not persisted

### Phase 2
- **PRD**: Stored in PostgreSQL with text content in database
- **Analysis**: Stored in PostgreSQL with JSON column for summary
- **Suggestions**: Stored in separate table with foreign key to Analysis
- **Export**: Stored in file storage (S3, local filesystem) with metadata in database
- **User**: Stored in PostgreSQL
- **ReviewHistory**: Stored in PostgreSQL

## Indexing Strategy (Phase 2)

- `PRD.user_id` - Index for user's PRDs
- `Analysis.prd_id` - Index for analysis lookups
- `Suggestion.analysis_id` - Index for suggestion queries
- `ReviewHistory.user_id` - Index for user history
- `ReviewHistory.created_at` - Index for chronological queries

## Data Validation

### PRD Content Validation
- Maximum size: 10MB (after text extraction)
- Minimum size: 100 characters (to ensure meaningful content)
- Character encoding: UTF-8
- Sanitization: Remove potentially malicious content, normalize whitespace

### Suggestion Validation
- Title: 5-200 characters
- Explanation: 20-5000 characters
- Priority: Must be one of: high, medium, low
- Category: Must be valid category enum

## Migration Path (Phase 1 → Phase 2)

1. Add user authentication
2. Create database schema
3. Migrate session data to database (optional, users can re-upload)
4. Add user_id foreign keys to all entities
5. Implement review history tracking
6. Add data retention policies
