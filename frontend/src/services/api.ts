/**
 * API client service for PRD Reviewer frontend.
 *
 * This module provides a centralized HTTP client with error handling,
 * request/response interceptors, and type-safe API methods.
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import { API_ENDPOINTS, API_CONFIG } from '../constants/api';

/**
 * Create configured Axios instance.
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: '', // Don't set baseURL since endpoints already include full URLs
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor for adding auth tokens, logging, etc.
 */
apiClient.interceptors.request.use(
  (config) => {
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
      const data = error.response.data as { error?: string; message?: string };
      
      switch (status) {
        case 400:
          throw new Error(data.message || 'Bad request');
        case 401:
          throw new Error('Unauthorized');
        case 404:
          throw new Error('Resource not found');
        case 422:
          throw new Error(data.message || 'Validation error');
        case 500:
          throw new Error('Internal server error');
        default:
          throw new Error(data.message || `Request failed with status ${status}`);
      }
    } else if (error.request) {
      // Request made but no response received
      throw new Error('Network error: No response from server');
    } else {
      // Error setting up request
      throw new Error(error.message || 'Request setup error');
    }
  }
);

/**
 * Generic GET request helper.
 */
export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  // Use full URL if it starts with http, otherwise use baseURL
  const fullUrl = url.startsWith('http') ? url : `${API_CONFIG.BASE_URL}${url}`;
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
  // Use full URL if it starts with http, otherwise use baseURL
  const fullUrl = url.startsWith('http') ? url : `${API_CONFIG.BASE_URL}${url}`;
  const response = await apiClient.post<T>(fullUrl, data, config);
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
