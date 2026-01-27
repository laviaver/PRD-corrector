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

  return post<AnalyzeResponse>(API_ENDPOINTS.ANALYZE, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
}

/**
 * Paste PRD text content for analysis.
 */
export async function pastePRDText(text: string): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('text', text);

  return post<AnalyzeResponse>(API_ENDPOINTS.ANALYZE, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
}
