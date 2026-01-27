# Tasks: PRD Reviewer Web Application

**Input**: Design documents from `/specs/002-prd-reviewer/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Test-Driven Development (TDD) Workflow

**RED → GREEN → REFACTOR** cycle applies to all implementation tasks:

1. **RED**: Write failing tests first (before implementation)
2. **GREEN**: Implement minimal code to pass tests
3. **REFACTOR**: Clean up while tests pass

**Test Tasks**: Tasks marked with `[TEST]` should be completed BEFORE the corresponding implementation task.

**Test Organization**:
- `backend/tests/unit/` - Unit tests for models, services, utilities
- `backend/tests/integration/` - Integration tests for API endpoints
- `backend/tests/contract/` - Contract tests validating API contracts
- `frontend/tests/unit/` - Component unit tests
- `frontend/tests/integration/` - Integration tests for user flows

**SDD Workflow**: After every task completion, follow the 7-step checklist (see `.cursor/rules/04-sdd-process.mdc`):
1. Verify tests pass
2. Check dependency reflections
3. Update spec.md/plan.md if triggered
4. Stage changes
5. Commit with descriptive message
6. Update progress tracking
7. Only then proceed to next task

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below follow the web application structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure with backend/ and frontend/ directories at repository root
- [x] T002 Initialize Python backend project with FastAPI dependencies in backend/
- [x] T003 [P] Initialize React TypeScript frontend project with Vite in frontend/
- [x] T004 [P] Configure Python linting (black, isort, flake8) in backend/
- [x] T005 [P] Configure TypeScript/ESLint for frontend in frontend/
- [x] T006 [P] Create backend requirements.txt with FastAPI, python-docx, openai, pydantic, uvicorn
- [x] T007 [P] Create frontend package.json with React, TypeScript, react-dropzone, react-pdf dependencies
- [x] T008 Create .env.example files for backend and frontend with placeholder API keys
- [x] T009 [P] Setup gitignore for Python and Node.js artifacts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 Setup FastAPI application structure in backend/src/main.py with CORS middleware
- [x] T011 [P] Create base Pydantic models in backend/src/models/__init__.py
- [x] T012 [P] Configure error handling middleware in backend/src/api/middleware/error_handler.py
- [x] T013 [P] Setup logging infrastructure in backend/src/utils/logger.py
- [x] T014 [P] Create environment configuration management in backend/src/config.py
- [x] T015 [P] Setup React app structure with routing in frontend/src/App.tsx
- [x] T016 [P] Create API client service in frontend/src/services/api.ts
- [x] T017 [P] Setup error handling utilities in frontend/src/utils/errorHandler.ts
- [x] T018 Create in-memory storage service for PRD and Analysis data in backend/src/services/storage.py
- [x] T019 [P] Create frontend constants file for API endpoints in frontend/src/constants/api.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Upload/Input PRD Content (Priority: P1) 🎯 MVP

**Goal**: Enable users to upload PRD files (.docx, .txt, .md) or paste PRD text content, with validation and preview

**Independent Test**: User can upload a .txt file, see content preview, and receive a PRD ID. User can paste text and receive a PRD ID.

### Tests for User Story 1 (TDD: Write these FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T020-TEST [P] [US1] Unit test for PRD model in backend/tests/unit/test_prd.py
- [ ] T021-TEST [P] [US1] Unit test for file parser in backend/tests/unit/test_file_parser.py
- [ ] T022-TEST [US1] Unit test for file validation service in backend/tests/unit/test_validation.py
- [ ] T023-TEST [US1] Contract test for POST /api/analyze in backend/tests/contract/test_analyze.py
- [ ] T024-TEST [US1] Unit test for PRD service in backend/tests/unit/test_prd_service.py
- [ ] T025-TEST [P] [US1] Unit test for FileUpload component in frontend/tests/unit/FileUpload.test.tsx
- [ ] T026-TEST [P] [US1] Unit test for TextInput component in frontend/tests/unit/TextInput.test.tsx
- [ ] T027-TEST [US1] Integration test for UploadPage in frontend/tests/integration/UploadPage.test.tsx
- [ ] T028-TEST [US1] Unit test for PRD service API call in frontend/tests/unit/prdService.test.ts
- [ ] T029-TEST [US1] Unit test for ContentPreview component in frontend/tests/unit/ContentPreview.test.tsx
- [ ] T030-TEST [US1] Integration test for error handling in frontend/tests/integration/errorHandling.test.tsx

### Implementation for User Story 1

- [x] T020 [P] [US1] Create PRD model in backend/src/models/prd.py with id, content, filename, file_type, uploaded_at, size fields
- [ ] T021 [P] [US1] Create file parser utility in backend/src/utils/file_parser.py for .txt, .md, and .docx extraction
- [ ] T022 [US1] Implement file validation service in backend/src/services/validation.py (file type, size limits)
- [ ] T023 [US1] Create POST /api/analyze endpoint in backend/src/api/routes/analyze.py for file upload and text paste
- [ ] T024 [US1] Implement PRD creation service in backend/src/services/prd_service.py to store PRD in memory
- [ ] T025 [P] [US1] Create FileUpload component in frontend/src/components/FileUpload.tsx with drag-and-drop support
- [ ] T026 [P] [US1] Create TextInput component in frontend/src/components/TextInput.tsx for pasting PRD content
- [ ] T027 [US1] Create UploadPage component in frontend/src/pages/UploadPage.tsx integrating FileUpload and TextInput
- [ ] T028 [US1] Implement file upload API call in frontend/src/services/prdService.ts
- [ ] T029 [US1] Add content preview display in frontend/src/components/ContentPreview.tsx showing first 500 chars
- [ ] T030 [US1] Add file validation error handling in frontend components (file type, size errors)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can upload files or paste text and see preview

---

## Phase 4: User Story 2 - AI-Powered PRD Analysis (Priority: P1) 🎯 MVP

**Goal**: Analyze PRD content using AI/LLM and generate categorized suggestions based on best practices

**Independent Test**: User submits a PRD, receives analysis ID, polls for status, and gets completed analysis with suggestions within 30 seconds.

### Tests for User Story 2 (TDD: Write these FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T031-TEST [P] [US2] Unit test for Analysis model in backend/tests/unit/test_analysis.py
- [ ] T032-TEST [P] [US2] Unit test for Suggestion model in backend/tests/unit/test_suggestion.py
- [ ] T033-TEST [US2] Unit test for LLM service (mocked) in backend/tests/unit/test_llm_service.py
- [ ] T034-TEST [US2] Unit test for analyzer service in backend/tests/unit/test_analyzer.py
- [ ] T035-TEST [US2] Unit test for prompt engineering in backend/tests/unit/test_prompts.py
- [ ] T036-TEST [US2] Unit test for task processor in backend/tests/unit/test_task_processor.py
- [ ] T037-TEST [US2] Contract test for POST /api/analyze (analysis initiation) in backend/tests/contract/test_analyze.py
- [ ] T038-TEST [US2] Contract test for GET /api/analysis/{id} in backend/tests/contract/test_analysis.py
- [ ] T039-TEST [US2] Contract test for GET /api/analysis/{id}/status in backend/tests/contract/test_analysis.py
- [ ] T040-TEST [US2] Integration test for analysis service lifecycle in backend/tests/integration/test_analysis_service.py
- [ ] T041-TEST [P] [US2] Unit test for AnalysisStatus component in frontend/tests/unit/AnalysisStatus.test.tsx
- [ ] T042-TEST [US2] Unit test for analysis service API calls in frontend/tests/unit/analysisService.test.ts
- [ ] T043-TEST [US2] Integration test for loading states in frontend/tests/integration/loadingStates.test.tsx
- [ ] T044-TEST [US2] Integration test for error handling in frontend/tests/integration/analysisErrors.test.tsx

### Implementation for User Story 2

- [ ] T031 [P] [US2] Create Analysis model in backend/src/models/analysis.py with id, prd_id, status, started_at, completed_at, error_message, summary fields
- [ ] T032 [P] [US2] Create Suggestion model in backend/src/models/suggestion.py with id, analysis_id, category, priority, title, explanation, location, example, template fields
- [ ] T033 [US2] Implement LLM service in backend/src/services/llm_service.py with OpenAI API integration
- [ ] T034 [US2] Create PRD analyzer service in backend/src/services/analyzer.py that uses LLM to generate suggestions
- [ ] T035 [US2] Implement analysis prompt engineering in backend/src/services/prompts.py with PRD best practices checklist
- [ ] T036 [US2] Create background task processor in backend/src/services/task_processor.py for async analysis
- [ ] T037 [US2] Update POST /api/analyze endpoint to initiate analysis and return analysis_id
- [ ] T038 [US2] Create GET /api/analysis/{analysis_id} endpoint in backend/src/api/routes/analysis.py
- [ ] T039 [US2] Create GET /api/analysis/{analysis_id}/status endpoint for polling analysis status
- [ ] T040 [US2] Implement analysis service in backend/src/services/analysis_service.py to manage analysis lifecycle
- [ ] T041 [P] [US2] Create AnalysisStatus component in frontend/src/components/AnalysisStatus.tsx for polling and status display
- [ ] T042 [US2] Implement analysis API calls in frontend/src/services/analysisService.ts
- [ ] T043 [US2] Add loading states and progress indicators in frontend during analysis
- [ ] T044 [US2] Add error handling for analysis failures in frontend

**Checkpoint**: At this point, User Story 2 should be fully functional - PRD analysis completes and returns suggestions

---

## Phase 5: User Story 3 - View Suggestions (Priority: P1) 🎯 MVP

**Goal**: Display organized, prioritized suggestions grouped by category with expandable details

**Independent Test**: User views analysis results page with suggestions grouped by category (Structure, Clarity, etc.), can expand/collapse details, and see original PRD content.

### Tests for User Story 3 (TDD: Write these FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T045-TEST [P] [US3] Unit test for SuggestionCard component in frontend/tests/unit/SuggestionCard.test.tsx
- [ ] T046-TEST [P] [US3] Unit test for SuggestionList component in frontend/tests/unit/SuggestionList.test.tsx
- [ ] T047-TEST [US3] Integration test for ResultsPage in frontend/tests/integration/ResultsPage.test.tsx
- [ ] T048-TEST [US3] Unit test for suggestion filtering/sorting utilities in frontend/tests/unit/suggestionUtils.test.ts
- [ ] T049-TEST [US3] Unit test for PRD viewer component in frontend/tests/unit/PRDViewer.test.tsx
- [ ] T050-TEST [US3] Unit test for category grouping logic in frontend/tests/unit/categoryGrouping.test.ts
- [ ] T051-TEST [US3] Unit test for SuggestionDetail component in frontend/tests/unit/SuggestionDetail.test.tsx
- [ ] T052-TEST [US3] Integration test for navigation flow in frontend/tests/integration/navigation.test.tsx
- [ ] T053-TEST [US3] Unit test for AnalysisSummary component in frontend/tests/unit/AnalysisSummary.test.tsx

### Implementation for User Story 3

- [ ] T045 [P] [US3] Create SuggestionCard component in frontend/src/components/SuggestionCard.tsx with expand/collapse
- [ ] T046 [P] [US3] Create SuggestionList component in frontend/src/components/SuggestionList.tsx for categorized grouping
- [ ] T047 [US3] Create ResultsPage component in frontend/src/pages/ResultsPage.tsx with three-panel layout (PRD content, suggestions, details)
- [ ] T048 [US3] Implement suggestion filtering and sorting by priority in frontend/src/utils/suggestionUtils.ts
- [ ] T049 [US3] Create PRD viewer component in frontend/src/components/PRDViewer.tsx to display original content
- [ ] T050 [US3] Add suggestion category grouping logic in frontend/src/utils/categoryGrouping.ts
- [ ] T051 [US3] Implement suggestion detail view in frontend/src/components/SuggestionDetail.tsx showing explanation, location, example
- [ ] T052 [US3] Add navigation from UploadPage to ResultsPage after analysis completes
- [ ] T053 [US3] Add summary statistics display in frontend/src/components/AnalysisSummary.tsx (total suggestions, by category, by priority)

**Checkpoint**: At this point, User Story 3 should be fully functional - users can view and explore suggestions

---

## Phase 6: User Story 4 - Export/Share Results (Priority: P1) 🎯 MVP

**Goal**: Export analysis results as PDF or Markdown, copy to clipboard

**Independent Test**: User clicks export button, selects format (PDF/Markdown), downloads file. User clicks copy button, suggestions copied to clipboard.

### Tests for User Story 4 (TDD: Write these FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T054-TEST [P] [US4] Unit test for Export model in backend/tests/unit/test_export.py
- [ ] T055-TEST [US4] Unit test for PDF export service in backend/tests/unit/test_export_service.py
- [ ] T056-TEST [US4] Unit test for Markdown export service in backend/tests/unit/test_export_service.py
- [ ] T057-TEST [US4] Unit test for JSON export service in backend/tests/unit/test_export_service.py
- [ ] T058-TEST [US4] Contract test for POST /api/export in backend/tests/contract/test_export.py
- [ ] T059-TEST [P] [US4] Unit test for ExportButton component in frontend/tests/unit/ExportButton.test.tsx
- [ ] T060-TEST [US4] Unit test for export service API calls in frontend/tests/unit/exportService.test.ts
- [ ] T061-TEST [US4] Unit test for clipboard utilities in frontend/tests/unit/clipboard.test.ts
- [ ] T062-TEST [US4] Unit test for CopyButton component in frontend/tests/unit/CopyButton.test.tsx
- [ ] T063-TEST [US4] Integration test for export flow in frontend/tests/integration/export.test.tsx
- [ ] T064-TEST [US4] Integration test for file download handling in frontend/tests/integration/fileDownload.test.tsx

### Implementation for User Story 4

- [ ] T054 [P] [US4] Create Export model in backend/src/models/export.py with id, analysis_id, format, created_at fields
- [ ] T055 [US4] Implement PDF export service in backend/src/services/export_service.py using reportlab or weasyprint
- [ ] T056 [US4] Implement Markdown export service in backend/src/services/export_service.py
- [ ] T057 [US4] Implement JSON export service in backend/src/services/export_service.py
- [ ] T058 [US4] Create POST /api/export endpoint in backend/src/api/routes/export.py
- [ ] T059 [P] [US4] Create ExportButton component in frontend/src/components/ExportButton.tsx with format selection
- [ ] T060 [US4] Implement export API call in frontend/src/services/exportService.ts
- [ ] T061 [US4] Add clipboard copy functionality in frontend/src/utils/clipboard.ts
- [ ] T062 [US4] Create CopyButton component in frontend/src/components/CopyButton.tsx
- [ ] T063 [US4] Add export options to ResultsPage (PDF, Markdown, JSON, Copy)
- [ ] T064 [US4] Handle export file download in frontend with proper MIME types

**Checkpoint**: At this point, User Story 4 should be fully functional - users can export and share results

---

## Phase 7: User Story 5 - Interactive PRD Editor (Priority: P2)

**Goal**: Allow users to edit PRD content directly in the application with markdown support

**Independent Test**: User opens PRD in editor, makes changes, changes saved to localStorage, user can re-analyze edited PRD.

### Implementation for User Story 5

- [ ] T065 [P] [US5] Install and configure rich text editor library (e.g., react-quill or Slate) in frontend
- [ ] T066 [US5] Create PRDEditor component in frontend/src/components/PRDEditor.tsx with markdown support
- [ ] T067 [US5] Implement localStorage persistence in frontend/src/utils/storage.ts for saving edits
- [ ] T068 [US5] Add auto-save functionality in PRDEditor component (debounced saves)
- [ ] T069 [US5] Integrate PRDEditor into ResultsPage replacing PRDViewer
- [ ] T070 [US5] Add "Re-analyze" button in ResultsPage that submits edited content
- [ ] T071 [US5] Update analysis flow to accept edited content from localStorage

**Checkpoint**: At this point, User Story 5 should be fully functional - users can edit and re-analyze PRDs

---

## Phase 8: User Story 6 - Best Practices Library (Priority: P2)

**Goal**: Provide a library of PRD best practices and templates for users to reference

**Independent Test**: User navigates to library page, browses practices by category, views examples, copies templates.

### Implementation for User Story 6

- [ ] T072 [P] [US6] Create best practices data structure in frontend/src/data/bestPractices.ts
- [ ] T073 [US6] Create BestPracticesLibrary component in frontend/src/components/BestPracticesLibrary.tsx
- [ ] T074 [US6] Create PracticeCard component in frontend/src/components/PracticeCard.tsx for individual practices
- [ ] T075 [US6] Implement category filtering in BestPracticesLibrary
- [ ] T076 [US6] Add template copy functionality in PracticeCard
- [ ] T077 [US6] Create LibraryPage component in frontend/src/pages/LibraryPage.tsx
- [ ] T078 [US6] Add navigation link to LibraryPage in main app navigation

**Checkpoint**: At this point, User Story 6 should be fully functional - users can browse and copy best practices

---

## Phase 9: User Story 7 - Comparison Mode (Priority: P2)

**Goal**: Compare user's PRD against templates to highlight missing sections

**Independent Test**: User selects a template, sees side-by-side comparison, missing sections highlighted.

### Implementation for User Story 7

- [ ] T079 [P] [US7] Create PRD template data structure in frontend/src/data/templates.ts
- [ ] T080 [US7] Create ComparisonView component in frontend/src/components/ComparisonView.tsx with side-by-side layout
- [ ] T081 [US7] Implement section detection and comparison logic in frontend/src/utils/comparisonUtils.ts
- [ ] T082 [US7] Create SectionHighlighter component in frontend/src/components/SectionHighlighter.tsx for missing sections
- [ ] T083 [US7] Add template selector in ComparisonView
- [ ] T084 [US7] Integrate ComparisonView into ResultsPage as optional view mode
- [ ] T085 [US7] Add comparison toggle button in ResultsPage

**Checkpoint**: At this point, User Story 7 should be fully functional - users can compare PRDs against templates

---

## Phase 10: User Story 8 - Version History (Priority: P3)

**Goal**: Track changes across multiple review iterations (requires authentication - Phase 2 feature)

**Independent Test**: User authenticates, submits multiple PRD reviews, views history, sees improvement metrics.

### Implementation for User Story 8

- [ ] T086 [P] [US8] Create User model in backend/src/models/user.py (Phase 2 entity)
- [ ] T087 [US8] Create ReviewHistory model in backend/src/models/review_history.py (Phase 2 entity)
- [ ] T088 [US8] Setup PostgreSQL database and SQLAlchemy ORM in backend (Phase 2 migration)
- [ ] T089 [US8] Implement user authentication service in backend/src/services/auth_service.py
- [ ] T090 [US8] Create review history service in backend/src/services/history_service.py
- [ ] T091 [US8] Create GET /api/history endpoint in backend/src/api/routes/history.py
- [ ] T092 [US8] Create HistoryPage component in frontend/src/pages/HistoryPage.tsx
- [ ] T093 [US8] Implement improvement metrics calculation in backend/src/services/metrics_service.py
- [ ] T094 [US8] Add history navigation and display in frontend

**Note**: This story requires Phase 2 infrastructure (database, authentication). Consider deferring until MVP is complete.

---

## Phase 11: User Story 9 - Team Collaboration (Priority: P3)

**Goal**: Enable multiple users to comment on suggestions and collaborate (requires authentication)

**Independent Test**: Multiple authenticated users access shared review, add comments, mark suggestions resolved.

### Implementation for User Story 9

- [ ] T095 [P] [US9] Create Comment model in backend/src/models/comment.py
- [ ] T096 [US9] Create shared review service in backend/src/services/sharing_service.py
- [ ] T097 [US9] Implement comment service in backend/src/services/comment_service.py
- [ ] T098 [US9] Create POST /api/reviews/{id}/comments endpoint in backend/src/api/routes/comments.py
- [ ] T099 [US9] Create CommentSection component in frontend/src/components/CommentSection.tsx
- [ ] T100 [US9] Add suggestion resolution functionality in backend and frontend
- [ ] T101 [US9] Implement notification service in backend/src/services/notification_service.py
- [ ] T102 [US9] Add real-time updates (polling or WebSocket) for comments

**Note**: This story requires Phase 2 infrastructure. Consider deferring until MVP is complete.

---

## Phase 12: User Story 10 - Custom Best Practices (Priority: P3)

**Goal**: Allow organization admins to define custom best practices and templates

**Independent Test**: Admin authenticates, creates custom checklist, defines template, reviews use custom practices.

### Implementation for User Story 10

- [ ] T103 [P] [US10] Create CustomPractice model in backend/src/models/custom_practice.py
- [ ] T104 [US10] Create admin service in backend/src/services/admin_service.py
- [ ] T105 [US10] Create POST /api/admin/practices endpoint in backend/src/api/routes/admin.py
- [ ] T106 [US10] Create AdminPanel component in frontend/src/pages/AdminPanel.tsx
- [ ] T107 [US10] Implement custom practice editor in frontend
- [ ] T108 [US10] Update analyzer service to use custom practices when available
- [ ] T109 [US10] Add organization context to analysis requests

**Note**: This story requires Phase 2 infrastructure and admin authentication. Consider deferring until MVP is complete.

---

## Phase 13: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T110 [P] Update API documentation in backend/docs/ with OpenAPI spec
- [ ] T111 [P] Add comprehensive error messages and user feedback throughout frontend
- [ ] T112 [P] Implement responsive design for mobile devices in all frontend components
- [ ] T113 [P] Add loading skeletons and better UX indicators
- [ ] T114 [P] Optimize LLM prompt engineering for better suggestion quality
- [ ] T115 [P] Implement caching for analysis results in backend/src/services/cache.py
- [ ] T116 [P] Add rate limiting in backend/src/api/middleware/rate_limiter.py
- [ ] T117 [P] Security hardening: input sanitization, file validation improvements
- [ ] T118 [P] Performance optimization: optimize React re-renders, backend query optimization
- [ ] T119 [P] Accessibility improvements (WCAG 2.1 AA compliance) in frontend
- [ ] T120 Run quickstart.md validation - verify all setup steps work
- [ ] T121 [P] Add comprehensive logging and monitoring
- [ ] T122 [P] Create deployment documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed sequentially in priority order (US1 → US2 → US3 → US4)
  - Or in parallel if team capacity allows (US1 and US2 can partially overlap)
- **Enhanced Features (Phase 7-9)**: Depend on MVP completion (Phase 3-6)
- **Advanced Features (Phase 10-12)**: Depend on Phase 2 infrastructure (database, auth) - consider Phase 2
- **Polish (Phase 13)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Depends on US1 (needs PRD to analyze) - Can start after US1 PRD creation works
- **User Story 3 (P1)**: Depends on US2 (needs analysis results) - Can start after US2 analysis works
- **User Story 4 (P1)**: Depends on US3 (needs suggestions to export) - Can start after US3 display works
- **User Story 5 (P2)**: Depends on US3 (needs results page) - Can enhance existing editor
- **User Story 6 (P2)**: Independent - can start after Foundational
- **User Story 7 (P2)**: Depends on US3 (needs results page) - Can add comparison view
- **User Story 8-10 (P3)**: Depend on Phase 2 infrastructure - Defer until after MVP

### Within Each User Story

- Models before services
- Services before endpoints/UI
- Backend API before frontend integration
- Core implementation before polish
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes:
  - US1 frontend and backend can be worked on in parallel
  - US2 models can be created in parallel with US1 completion
- Different user stories can be worked on sequentially (US1 → US2 → US3 → US4)
- Polish phase tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all parallel tasks for User Story 1 together:
Task: "Create PRD model in backend/src/models/prd.py"
Task: "Create file parser utility in backend/src/utils/file_parser.py"
Task: "Create FileUpload component in frontend/src/components/FileUpload.tsx"
Task: "Create TextInput component in frontend/src/components/TextInput.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1-4 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Upload/Input)
4. Complete Phase 4: User Story 2 (Analysis)
5. Complete Phase 5: User Story 3 (View Suggestions)
6. Complete Phase 6: User Story 4 (Export)
7. **STOP and VALIDATE**: Test all MVP stories independently
8. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Basic upload)
3. Add User Story 2 → Test independently → Deploy/Demo (Analysis works)
4. Add User Story 3 → Test independently → Deploy/Demo (View results)
5. Add User Story 4 → Test independently → Deploy/Demo (Full MVP!)
6. Each story adds value without breaking previous stories

### Sequential Strategy (Recommended for MVP)

With single developer or small team:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Complete User Story 1 fully
   - Then complete User Story 2 fully
   - Then complete User Story 3 fully
   - Then complete User Story 4 fully
3. Stories build on each other sequentially

---

## Notes

### TDD Workflow
- **Tests FIRST**: Write failing tests before implementation (RED phase)
- **Then Implement**: Write minimal code to pass tests (GREEN phase)
- **Then Refactor**: Clean up while tests pass (REFACTOR phase)
- Test tasks marked with `[TEST]` should be completed before corresponding implementation tasks

### SDD Workflow
- Follow 7-step checklist after every task completion (see `.cursor/rules/04-sdd-process.mdc`)
- Update spec.md/plan.md when code changes (see `.cursor/rules/spec-sync-check.mdc`)
- Check dependency reflections before committing (see `.cursor/rules/dependency-reflection.mdc`)

### Task Organization
- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

### Scope
- MVP scope: Focus on User Stories 1-4 (P1) before moving to P2/P3 features
- Phase 2 features (US8-US10) require database and authentication - consider separate phase
