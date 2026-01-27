/**
 * PRD service for frontend API calls.
 *
 * Handles PRD upload, text paste, and related operations.
 */

import { post } from './api';
import { API_ENDPOINTS } from '../constants/api';

export interface AnalyzeResponse {
  prd_id: string;
  analysis_id: string | null;
  message: string;
}

/**
 * Upload a PRD file for analysis.
 */
export async function uploadPRDFile(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('file', file);

  // Don't set Content-Type header - let browser set it with boundary
  return post<AnalyzeResponse>(API_ENDPOINTS.ANALYZE, formData);
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
