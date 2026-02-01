/**
 * PRD service for frontend API calls.
 *
 * Handles PRD upload, text paste, and related operations.
 */

import { post } from './api';
import { API_ENDPOINTS, API_CONFIG } from '../constants/api';

export interface AnalyzeResponse {
  /** null for file uploads until conversion completes */
  prd_id: string | null;
  analysis_id: string | null;
  message: string;
}

/**
 * Upload a PRD file for analysis.
 */
export async function uploadPRDFile(file: File): Promise<AnalyzeResponse> {
  // #region agent log
  try {
    fetch('http://127.0.0.1:7242/ingest/aaa3e728-00f3-429e-b53a-5c8d5e3b776b', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ location: 'prdService.ts:uploadPRDFile_before_post', message: 'about to POST analyze', data: { filename: file.name, size: file.size }, timestamp: Date.now(), sessionId: 'debug-session', hypothesisId: 'A' }) }).catch(() => {});
  } catch (_) {}
  // #endregion
  const formData = new FormData();
  formData.append('file', file);

  // Longer timeout for upload + backend conversion handoff
  return post<AnalyzeResponse>(API_ENDPOINTS.ANALYZE, formData, {
    timeout: API_CONFIG.UPLOAD_TIMEOUT_MS,
  });
}

/**
 * Paste PRD text content for analysis.
 */
export async function pastePRDText(text: string): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('text', text);

  // Don't set Content-Type header - let browser set it with boundary
  return post<AnalyzeResponse>(API_ENDPOINTS.ANALYZE, formData);
}

export interface PreviewMarkdownResponse {
  markdown: string;
}

/**
 * Get markdown version of an uploaded PRD file (same conversion as analysis).
 */
export async function getMarkdownPreview(file: File): Promise<PreviewMarkdownResponse> {
  const formData = new FormData();
  formData.append('file', file);

  return post<PreviewMarkdownResponse>(API_ENDPOINTS.PREVIEW_MARKDOWN, formData, {
    timeout: API_CONFIG.UPLOAD_TIMEOUT_MS,
  });
}
