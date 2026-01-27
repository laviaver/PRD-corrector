/**
 * Error handling utilities for PRD Reviewer frontend.
 *
 * This module provides centralized error handling, formatting, and user-friendly
 * error messages.
 */

export interface AppError {
  message: string;
  code?: string;
  statusCode?: number;
  details?: unknown;
}

/**
 * Format error for display to user.
 */
export function formatError(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  if (error && typeof error === 'object' && 'message' in error) {
    return String((error as { message: unknown }).message);
  }
  
  return 'An unexpected error occurred';
}

/**
 * Check if error is a network error.
 */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof Error) {
    return (
      error.message.includes('Network error') ||
      error.message.includes('No response from server') ||
      error.message.includes('timeout')
    );
  }
  return false;
}

/**
 * Check if error is a validation error.
 */
export function isValidationError(error: unknown): boolean {
  if (error instanceof Error) {
    return (
      error.message.includes('Validation error') ||
      error.message.includes('Bad request') ||
      error.message.includes('422')
    );
  }
  return false;
}

/**
 * Check if error is a not found error.
 */
export function isNotFoundError(error: unknown): boolean {
  if (error instanceof Error) {
    return (
      error.message.includes('not found') ||
      error.message.includes('404')
    );
  }
  return false;
}

/**
 * Create a user-friendly error message.
 */
export function getUserFriendlyError(error: unknown): string {
  if (isNetworkError(error)) {
    return 'Unable to connect to the server. Please check your internet connection and try again.';
  }
  
  if (isNotFoundError(error)) {
    return 'The requested resource was not found.';
  }
  
  if (isValidationError(error)) {
    return 'Please check your input and try again.';
  }
  
  return formatError(error);
}

/**
 * Log error to console (and potentially to error tracking service).
 */
export function logError(error: unknown, context?: string): void {
  const errorMessage = formatError(error);
  const contextMessage = context ? `[${context}] ` : '';
  
  console.error(`${contextMessage}Error:`, errorMessage, error);
  
  // TODO: In production, send to error tracking service (e.g., Sentry)
  // if (import.meta.env.PROD) {
  //   Sentry.captureException(error, { tags: { context } });
  // }
}
