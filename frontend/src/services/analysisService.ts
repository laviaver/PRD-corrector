/**
 * Analysis service for frontend API calls.
 *
 * Handles analysis status polling and result retrieval.
 */

import { get } from './api';
import { API_ENDPOINTS } from '../constants/api';

export interface AnalysisScores {
  structure_score: number;
  completeness_score: number;
  total_score: number;
}

export interface SectionStatusEntry {
  section_id: string;
  status: 'ok' | 'timeout' | 'error';
}

export interface AnalysisStatus {
  status: 'converting' | 'pending' | 'processing' | 'completed' | 'failed';
  prd_id?: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  scores?: AnalysisScores;
  section_status?: SectionStatusEntry[];
  incomplete_sections?: string[];
}

export interface Suggestion {
  id: string;
  analysis_id: string;
  category: string;
  priority: 'high' | 'medium' | 'low';
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

export interface AnalysisResult {
  analysis: {
    id: string;
    prd_id?: string | null;
    status: string;
    started_at: string;
    completed_at: string | null;
    error_message: string | null;
    summary?: {
      total_suggestions: number;
      suggestions_by_category: Record<string, number>;
      suggestions_by_priority: Record<string, number>;
    };
    scores?: AnalysisScores;
    section_status?: SectionStatusEntry[];
    incomplete_sections?: string[];
  };
  suggestions: Suggestion[];
}

/**
 * Get analysis status.
 */
export async function getAnalysisStatus(analysisId: string): Promise<AnalysisStatus> {
  // Use relative path for Vite proxy
  return get<AnalysisStatus>(API_ENDPOINTS.ANALYSIS_STATUS(analysisId));
}

/**
 * Get analysis results with suggestions by analysis ID.
 */
export async function getAnalysis(analysisId: string): Promise<AnalysisResult> {
  // Use relative path for Vite proxy
  return get<AnalysisResult>(API_ENDPOINTS.ANALYSIS(analysisId));
}

/**
 * Get analysis results with suggestions by PRD ID.
 */
export async function getAnalysisByPRD(prdId: string): Promise<AnalysisResult> {
  // Use relative path for Vite proxy
  return get<AnalysisResult>(API_ENDPOINTS.ANALYSIS_BY_PRD(prdId));
}
