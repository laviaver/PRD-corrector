/**
 * Export service for frontend API calls.
 *
 * Handles exporting analysis results.
 */

import { post } from './api';
import { API_ENDPOINTS } from '../constants/api';

export interface ExportResponse {
  export_id: string;
  analysis_id: string;
  format: string;
  file_path: string;
  created_at: string;
  message: string;
}

/**
 * Export analysis results.
 */
export async function exportAnalysis(
  analysisId: string,
  format: 'pdf' | 'markdown' | 'json' = 'markdown'
): Promise<ExportResponse> {
  const formData = new FormData();
  formData.append('analysis_id', analysisId);
  formData.append('format', format);

  // Don't set Content-Type header - let browser set it with boundary
  return post<ExportResponse>(API_ENDPOINTS.EXPORT, formData);
}
