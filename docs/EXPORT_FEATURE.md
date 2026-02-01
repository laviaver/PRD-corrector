# Export (Markdown / JSON) – What It Does and Whether It’s Needed

## What the export function does

- **Backend**: The `/api/export` endpoint accepts an `analysis_id` and a `format` (`markdown` or `json`). The export service:
  - **Markdown**: Builds a report with analysis metadata, summary, and suggestions grouped by category (title, priority, explanation, and optional example).
  - **JSON**: Builds a JSON object with the full analysis (scores, summary, status, etc.) and all suggestions (title, priority, category, explanation, location, example, template, etc.).
- The backend generates this content in memory and returns a JSON response with `export_id`, `analysis_id`, `format`, `file_path` (e.g. `/tmp/analysis_xxx.md`), and a success message. It does **not** return the file contents or stream a download; the file is not sent to the browser.
- **Frontend**: The "Export as Markdown" and "Export as JSON" buttons call this API and show an alert with the success message. No file is downloaded to the user’s machine.

## Are they needed?

- **Yes.** Export is useful for:
  - Sharing the analysis report (e.g. as a `.md` file).
  - Offline or archival use.
  - Feeding the analysis into other tools (JSON).
- The feature is **needed**, but the current implementation is **incomplete**: the file is created on the server (or represented in memory) and the user only gets a success message, not an actual download. To make it end-to-end useful, the backend would need to return the file content (or a download URL), and the frontend would need to trigger a file download (e.g. via a blob and a download link).

## Summary

| Aspect              | Status                                                                 |
|---------------------|------------------------------------------------------------------------|
| What export does    | Generates Markdown or JSON of the analysis on the server               |
| Download to user    | Not implemented (API returns metadata only)                           |
| Are they needed?    | Yes – for sharing, offline use, and integration                        |
| Next step           | Add API support to return file content and frontend download trigger  |
