/**
 * API client service for PRD Reviewer frontend.
 *
 * This module provides a centralized HTTP client with error handling,
 * request/response interceptors, and type-safe API methods.
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import { API_ENDPOINTS, API_CONFIG } from '../constants/api';

const CONNECTION_ERROR_GUIDE =
  'Cannot reach the API. (1) Open the app at http://localhost:5173 (run in frontend: npm run dev). (2) Start the backend: cd backend && ./run.sh — then reload.';

function isConnectionLikeError(message: string): boolean {
  const lower = message.toLowerCase();
  return (
    lower.includes('connection') ||
    lower.includes('network error') ||
    lower.includes('failed to fetch') ||
    lower.includes('load failed') ||
    lower === 'connection error.' ||
    lower === 'connection error'
  );
}

function connectionErrorMessage(isTimeout: boolean): string {
  if (isTimeout) {
    return 'Request timed out. The server may be busy or the file is large—try again.';
  }
  return CONNECTION_ERROR_GUIDE;
}

/**
 * Create configured Axios instance.
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: '', // Use relative paths to leverage Vite proxy
  timeout: API_CONFIG.TIMEOUT,
  // Don't set default Content-Type - will be set per request
});

/**
 * Request interceptor for adding auth tokens, logging, etc.
 */
apiClient.interceptors.request.use(
  (config) => {
    // Remove Content-Type header for FormData - browser will set it with boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    
    // Add any auth tokens here in the future
    // const token = getAuthToken();
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for error handling.
 */
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    // Handle common errors
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data = error.response.data;
      // #region agent log
      try {
        const dataType = data === null || data === undefined ? 'null' : typeof data;
        const snippet = typeof data === 'string' ? data.slice(0, 300) : (typeof data === 'object' ? JSON.stringify(data).slice(0, 300) : String(data));
        fetch('http://127.0.0.1:7242/ingest/aaa3e728-00f3-429e-b53a-5c8d5e3b776b', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ location: 'api.ts:response_error', message: '500 or error response', data: { status, dataType, snippet, url: error.config?.url }, timestamp: Date.now(), sessionId: 'debug-session', hypothesisId: 'E' }) }).catch(() => {});
      } catch (_) {}
      // #endregion
      const obj = data && typeof data === 'object' ? (data as { detail?: string; message?: string; error?: string }) : null;
      const msg = obj?.detail ?? obj?.message ?? obj?.error ?? (typeof data === 'string' ? data.slice(0, 200) : null);

      switch (status) {
        case 400:
          throw new Error(msg || 'Bad request');
        case 401:
          throw new Error('Unauthorized');
        case 404:
          throw new Error(msg || 'Resource not found');
        case 422:
          throw new Error(msg || 'Validation error');
        case 500:
          throw new Error(
            msg ||
              'Server error with no details. The backend may not be running. Start it with: ./backend/run.sh or: cd backend && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 (use python -m uvicorn, not uvicorn directly)'
          );
        default:
          throw new Error(msg || `Request failed with status ${status}`);
      }
    } else if (error.request) {
      // Request made but no response received (backend down, timeout, or connection reset)
      const isTimeout = error.code === 'ECONNABORTED' || error.message?.toLowerCase().includes('timeout');
      throw new Error(connectionErrorMessage(isTimeout));
    } else {
      // Error setting up request (e.g. Connection error, Failed to fetch, CORS) — show same guidance
      const msg = (error.message || '').trim();
      if (isConnectionLikeError(msg)) {
        throw new Error(connectionErrorMessage(false));
      }
      throw new Error(msg || 'Request setup error');
    }
  }
);

/**
 * Generic GET request helper.
 */
export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  // Use full URL if it starts with http, otherwise use relative path (Vite proxy)
  const fullUrl = url.startsWith('http') ? url : url;
  const response = await apiClient.get<T>(fullUrl, config);
  return response.data;
}

/**
 * Generic POST request helper.
 */
export async function post<T>(
  url: string,
  data?: unknown,
  config?: AxiosRequestConfig
): Promise<T> {
  // Merge config to ensure FormData handling
  const mergedConfig: AxiosRequestConfig = {
    ...config,
    // Remove Content-Type if FormData - let browser set it
    headers: {
      ...config?.headers,
      ...(data instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
    },
  };
  
  // Use full URL if it starts with http, otherwise use relative path (Vite proxy)
  const fullUrl = url.startsWith('http') ? url : url;
  const response = await apiClient.post<T>(fullUrl, data, mergedConfig);
  return response.data;
}

/**
 * Generic PUT request helper.
 */
export async function put<T>(
  url: string,
  data?: unknown,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.put<T>(url, data, config);
  return response.data;
}

/**
 * Generic DELETE request helper.
 */
export async function del<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.delete<T>(url, config);
  return response.data;
}

/**
 * Health check endpoint.
 */
export async function healthCheck(): Promise<{ status: string }> {
  return get<{ status: string }>(API_ENDPOINTS.HEALTH);
}

// Export the configured client for advanced usage
export { apiClient };
export default apiClient;
