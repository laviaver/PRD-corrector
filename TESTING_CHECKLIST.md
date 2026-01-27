# PRD Reviewer - Testing Checklist

**Last Updated**: 2024-12-19  
**Status**: Ready for Testing

---

## 🎯 Testing Strategy

This checklist covers all user stories, edge cases, and integration scenarios for the PRD Reviewer application.

---

## ✅ Core User Flows (MVP - Must Test)

### US1: Upload/Input PRD Content

#### File Upload - Success Cases
- [ ] **Upload .txt file**
  - Drag and drop a `.txt` file
  - Click to select a `.txt` file
  - Verify file is accepted
  - Verify preview shows file content
  - Verify "Upload & Analyze" button appears

- [ ] **Upload .md file**
  - Drag and drop a `.md` file
  - Click to select a `.md` file
  - Verify file is accepted
  - Verify preview shows markdown content

- [ ] **Upload .docx file**
  - Drag and drop a `.docx` file
  - Click to select a `.docx` file
  - Verify file is accepted
  - Verify preview shows file info (name, size)

#### File Upload - Error Cases
- [ ] **Invalid file type**
  - Try uploading `.pdf`, `.jpg`, `.exe`
  - Verify error message: "Unsupported file type"
  - Verify file is rejected

- [ ] **File too large**
  - Try uploading file > 10MB
  - Verify error message: "File size exceeds 10MB limit"
  - Verify file is rejected

- [ ] **Empty file**
  - Try uploading empty `.txt` file
  - Verify error message
  - Verify file is rejected

#### Text Paste - Success Cases
- [ ] **Paste valid PRD text**
  - Paste text into text area
  - Verify text is accepted
  - Click "Submit PRD"
  - Verify navigation to results page

- [ ] **Paste markdown content**
  - Paste markdown-formatted text
  - Verify formatting is preserved
  - Submit and verify analysis works

#### Text Paste - Error Cases
- [ ] **Empty text**
  - Try submitting empty text area
  - Verify error message
  - Verify submission is blocked

- [ ] **Very long text (> 100KB)**
  - Paste extremely long text
  - Verify system handles it (or shows appropriate error)

---

### US2: AI-Powered PRD Analysis

#### Analysis Flow - Success Cases
- [ ] **Analysis initiates correctly**
  - Upload a PRD file
  - Verify "Analysis initiated" message
  - Verify analysis_id is returned
  - Verify navigation to results page

- [ ] **Analysis status polling**
  - Upload PRD
  - Verify status shows "pending" or "processing"
  - Verify status updates automatically
  - Verify status changes to "completed" when done

- [ ] **Analysis completes successfully**
  - Upload a valid PRD
  - Wait for analysis to complete (< 30 seconds)
  - Verify suggestions are generated
  - Verify no error messages

#### Analysis Flow - Error Cases
- [ ] **Missing OpenAI API key**
  - Remove or invalidate API key in `.env`
  - Upload PRD
  - Verify error message: "OpenAI API key not configured"
  - Verify error is displayed to user

- [ ] **Network timeout**
  - Simulate slow network
  - Verify timeout handling
  - Verify appropriate error message

- [ ] **Analysis failure**
  - Upload invalid/malformed content
  - Verify error handling
  - Verify status shows "failed"

---

### US3: View Suggestions

#### Suggestions Display - Success Cases
- [ ] **Suggestions are displayed**
  - Complete analysis
  - Verify suggestions appear on results page
  - Verify suggestions are grouped by category
  - Verify each suggestion shows priority (High/Medium/Low)

- [ ] **Suggestion details**
  - Click on a suggestion card
  - Verify details expand
  - Verify shows: title, explanation, location (if applicable)
  - Verify shows example/template (if applicable)

- [ ] **Suggestion filtering/sorting**
  - Verify suggestions can be filtered by category
  - Verify suggestions can be sorted by priority
  - Verify filter/sort works correctly

- [ ] **Analysis summary**
  - Verify summary shows total suggestions
  - Verify summary shows count by category
  - Verify summary shows count by priority

#### Suggestions Display - Edge Cases
- [ ] **No suggestions generated**
  - Upload a perfect PRD (if possible)
  - Verify "No suggestions" message
  - Verify page doesn't crash

- [ ] **Many suggestions (50+)**
  - Upload a very poor PRD
  - Verify all suggestions display
  - Verify pagination or scrolling works
  - Verify performance is acceptable

---

### US4: Export/Share Results

#### Export - Success Cases
- [ ] **Export as Markdown**
  - Complete analysis
  - Click "Export Markdown"
  - Verify file downloads
  - Verify file contains suggestions
  - Verify file format is correct

- [ ] **Export as JSON**
  - Complete analysis
  - Click "Export JSON"
  - Verify file downloads
  - Verify JSON is valid
  - Verify contains all analysis data

- [ ] **Copy to clipboard**
  - Complete analysis
  - Click "Copy to Clipboard"
  - Verify content is copied
  - Paste and verify content is correct

#### Export - Error Cases
- [ ] **Export with no analysis**
  - Try to export before analysis completes
  - Verify error handling
  - Verify appropriate message

---

## 🔄 Integration Testing

### Frontend-Backend Communication
- [ ] **API endpoint connectivity**
  - Verify frontend can reach backend
  - Verify CORS is configured correctly
  - Verify no CORS errors in browser console

- [ ] **FormData handling**
  - Upload file via frontend
  - Verify backend receives file correctly
  - Verify file content is parsed correctly

- [ ] **Error handling**
  - Simulate backend error (stop server)
  - Verify frontend shows "Network error" message
  - Verify error message is user-friendly

- [ ] **ID handling**
  - Upload PRD
  - Verify navigation uses correct analysis_id
  - Verify results page loads with correct ID
  - Verify fallback to PRD ID works if needed

---

## 🧪 API Endpoint Testing

### POST /api/analyze

#### File Upload
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@test-prd.txt"
```
- [ ] Returns 201 status
- [ ] Returns `prd_id` and `analysis_id`
- [ ] Returns success message

#### Text Paste
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "text=Sample PRD content"
```
- [ ] Returns 201 status
- [ ] Returns `prd_id` and `analysis_id`
- [ ] Returns success message

#### Error Cases
- [ ] Both file and text provided → 400 error
- [ ] Neither file nor text → 400 error
- [ ] Invalid file type → 400 error
- [ ] File too large → 400 error

### GET /api/analysis/{analysis_id}
```bash
curl http://localhost:8000/api/analysis/{analysis_id}
```
- [ ] Returns 200 status
- [ ] Returns analysis object
- [ ] Returns suggestions array
- [ ] Invalid ID → 404 error
- [ ] Invalid format → 400 error

### GET /api/analysis/by-prd/{prd_id}
```bash
curl http://localhost:8000/api/analysis/by-prd/{prd_id}
```
- [ ] Returns 200 status
- [ ] Returns analysis for PRD
- [ ] Invalid PRD ID → 404 error
- [ ] Invalid format → 400 error

### GET /api/analysis/{analysis_id}/status
```bash
curl http://localhost:8000/api/analysis/{analysis_id}/status
```
- [ ] Returns 200 status
- [ ] Returns status object with: status, started_at, completed_at, error_message
- [ ] Status values: "pending", "processing", "completed", "failed"
- [ ] Invalid ID → 404 error

### POST /api/export
```bash
curl -X POST http://localhost:8000/api/export \
  -H "Content-Type: application/json" \
  -d '{"analysis_id": "...", "format": "markdown"}'
```
- [ ] Returns 200 status
- [ ] Returns export file (or download link)
- [ ] Supports formats: "markdown", "json", "pdf"
- [ ] Invalid analysis_id → 404 error
- [ ] Invalid format → 400 error

### GET /health
```bash
curl http://localhost:8000/health
```
- [ ] Returns 200 status
- [ ] Returns `{"status": "healthy"}`

---

## 🎨 UI/UX Testing

### Visual Design
- [ ] **Layout is clean and modern**
  - Verify spacing is consistent
  - Verify colors are appropriate
  - Verify typography is readable

- [ ] **Responsive design**
  - Test on desktop (1920x1080)
  - Test on tablet (768x1024)
  - Test on mobile (375x667)
  - Verify layout adapts correctly

### User Experience
- [ ] **Loading states**
  - Verify loading indicators appear during upload
  - Verify loading indicators appear during analysis
  - Verify loading states are clear and informative

- [ ] **Error messages**
  - Verify error messages are clear
  - Verify error messages are actionable
  - Verify error messages are not technical jargon

- [ ] **Navigation**
  - Verify "Back to Upload" button works
  - Verify navigation flow is intuitive
  - Verify browser back button works correctly

- [ ] **Accessibility**
  - Verify keyboard navigation works
  - Verify screen reader compatibility (if applicable)
  - Verify focus indicators are visible

---

## 🔍 Edge Cases & Error Scenarios

### File Handling
- [ ] **Special characters in filename**
  - Upload file with special chars: `test (1).txt`
  - Verify file is handled correctly

- [ ] **Very long filename**
  - Upload file with 200+ character name
  - Verify system handles it

- [ ] **Unicode content**
  - Upload file with emoji, Chinese, Arabic characters
  - Verify content is parsed correctly

### Network Scenarios
- [ ] **Slow network**
  - Throttle network to "Slow 3G"
  - Verify upload still works
  - Verify timeout handling

- [ ] **Network interruption**
  - Start upload, disconnect network
  - Verify error handling
  - Verify user can retry

- [ ] **Backend restart**
  - Start analysis, restart backend
  - Verify frontend handles disconnection
  - Verify user can retry

### Data Scenarios
- [ ] **Very short PRD (< 100 chars)**
  - Upload minimal content
  - Verify analysis still works
  - Verify suggestions are relevant

- [ ] **Very long PRD (> 50KB text)**
  - Upload large document
  - Verify system handles it
  - Verify analysis completes

- [ ] **Malformed content**
  - Upload file with binary data
  - Verify error handling
  - Verify appropriate error message

---

## 🚀 Performance Testing

### Response Times
- [ ] **File upload**
  - Upload 1MB file
  - Verify upload completes in < 5 seconds

- [ ] **Analysis initiation**
  - Upload PRD
  - Verify analysis starts in < 2 seconds

- [ ] **Analysis completion**
  - Upload typical PRD (5-10 pages)
  - Verify analysis completes in < 30 seconds

- [ ] **Page load**
  - Verify initial page load < 2 seconds
  - Verify results page load < 2 seconds

### Concurrent Users
- [ ] **Multiple simultaneous uploads**
  - Open 3 browser tabs
  - Upload PRDs simultaneously
  - Verify all complete successfully
  - Verify no conflicts

---

## 🔐 Security Testing

### Input Validation
- [ ] **File type validation**
  - Try uploading executable files
  - Verify they are rejected
  - Verify no code execution

- [ ] **File size limits**
  - Try uploading 20MB file
  - Verify it is rejected
  - Verify error message

- [ ] **XSS prevention**
  - Paste HTML/JavaScript in text input
  - Verify it is sanitized
  - Verify no script execution

### API Security
- [ ] **Rate limiting**
  - Make 100 rapid requests
  - Verify rate limiting kicks in
  - Verify appropriate error

- [ ] **CORS configuration**
  - Verify only allowed origins can access
  - Verify CORS headers are correct

---

## 📱 Browser Compatibility

Test on:
- [ ] **Chrome** (latest)
- [ ] **Firefox** (latest)
- [ ] **Safari** (latest)
- [ ] **Edge** (latest)

For each browser:
- [ ] File upload works
- [ ] Text paste works
- [ ] Analysis displays correctly
- [ ] Export works
- [ ] No console errors

---

## 🧹 Cleanup & Reset Testing

- [ ] **Clear browser data**
  - Clear localStorage
  - Verify app still works
  - Verify no errors

- [ ] **Restart servers**
  - Restart backend
  - Restart frontend
  - Verify app still works
  - Verify in-memory data is cleared (expected)

---

## 📊 Test Data

### Sample PRD Files

Create these test files:

1. **good-prd.txt** - Well-structured PRD with all sections
2. **minimal-prd.txt** - Minimal PRD with basic content
3. **poor-prd.txt** - PRD missing many sections
4. **large-prd.txt** - Large PRD (> 20KB)
5. **unicode-prd.txt** - PRD with special characters

### Sample Test Scenarios

1. **Happy Path**: Upload good PRD → Get suggestions → Export
2. **Error Path**: Upload invalid file → See error → Retry with valid file
3. **Edge Case**: Paste empty text → See error → Paste valid text
4. **Performance**: Upload large file → Verify timeout handling

---

## ✅ Acceptance Criteria Checklist

### US1 Acceptance Criteria
- [x] User can upload .docx, .txt, .md files (max 10MB)
- [x] User can paste text directly into a text area
- [x] System validates file format and size
- [x] System extracts text content from uploaded files
- [x] User sees a preview of extracted content before review

### US2 Acceptance Criteria
- [x] System analyzes PRD content using AI/LLM
- [x] System checks against PRD best practices checklist
- [x] System generates categorized suggestions
- [x] Suggestions include specific line/paragraph references where applicable
- [x] Analysis completes within 30 seconds for typical PRDs

### US3 Acceptance Criteria
- [x] Suggestions are grouped by category
- [x] Each suggestion has a priority level (High, Medium, Low)
- [x] Each suggestion includes: Title, Explanation, Location, Example
- [x] User can expand/collapse suggestion details
- [x] User can see original PRD content alongside suggestions

### US4 Acceptance Criteria
- [x] User can export suggestions as PDF or Markdown
- [x] User can copy suggestions to clipboard
- [x] Export includes original PRD content with inline annotations

---

## 🎯 Priority Testing Order

1. **Critical Path** (Test First):
   - File upload (.txt)
   - Analysis flow
   - View suggestions
   - Export markdown

2. **Important** (Test Second):
   - File upload (.md, .docx)
   - Text paste
   - Error handling
   - API endpoints

3. **Nice to Have** (Test Third):
   - Edge cases
   - Performance
   - Browser compatibility
   - Accessibility

---

## 📝 Test Results Template

For each test:
- **Test ID**: [e.g., T-001]
- **Test Name**: [e.g., Upload .txt file]
- **Status**: ✅ Pass / ❌ Fail / ⚠️ Partial
- **Notes**: [Any observations or issues]
- **Screenshots**: [If applicable]

---

## 🐛 Known Issues to Verify Fixed

- [x] Network error on upload → Fixed (FormData handling)
- [x] CORS issues → Fixed (Vite proxy)
- [x] Analysis ID vs PRD ID mismatch → Fixed (Navigation with analysis_id)
- [ ] OpenAI API key error handling → Verify user-friendly message
- [ ] Analysis timeout handling → Verify appropriate timeout and error

---

## 🚀 Next Steps After Testing

1. Document any bugs found
2. Create GitHub issues for bugs
3. Update this checklist with test results
4. Create test report summary
5. Fix critical bugs before deployment

---

**Happy Testing! 🎉**
