/**
 * API endpoint constants for PRD Reviewer frontend.
 *
 * This module centralizes all API endpoint URLs and configuration.
 */

// Use relative paths to leverage Vite proxy, or full URL if VITE_API_URL is set
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const API_ENDPOINTS = {
  // Health check
  HEALTH: '/health',
  
  // Analysis endpoints
  ANALYZE: `${API_BASE_URL}/analyze`,
  ANALYSIS: (id: string) => `${API_BASE_URL}/analysis/${id}`,
  ANALYSIS_BY_PRD: (prdId: string) => `${API_BASE_URL}/analysis/by-prd/${prdId}`,
  ANALYSIS_STATUS: (id: string) => `${API_BASE_URL}/analysis/${id}/status`,
  
  // Export endpoints
  EXPORT: `${API_BASE_URL}/export`,
} as const;

export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
} as const;
