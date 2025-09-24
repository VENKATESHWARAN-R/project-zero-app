/**
 * Global API error handler hook
 * Provides centralized error handling and user feedback for API operations
 */

import { useCallback } from 'react';
import { useToast } from '@/components/ui/Toast';
import { ApiError } from '@/types/api';

export interface ApiErrorHandlerOptions {
  showToast?: boolean;
  context?: string;
  onError?: (error: ApiError) => void;
  customMessage?: string;
}

export function useApiErrorHandler() {
  const toast = useToast();

  const handleError = useCallback(
    (error: unknown, options: ApiErrorHandlerOptions = {}) => {
      const {
        showToast = true,
        context,
        onError,
        customMessage
      } = options;

      // Convert error to ApiError format
      let apiError: ApiError;

      if (error && typeof error === 'object' && 'detail' in error) {
        apiError = error as ApiError;
      } else if (error instanceof Error) {
        apiError = {
          detail: error.message,
          code: 'UNKNOWN_ERROR'
        };
      } else {
        apiError = {
          detail: 'An unexpected error occurred',
          code: 'UNKNOWN_ERROR'
        };
      }

      // Log error for debugging
      console.error(`API Error${context ? ` (${context})` : ''}:`, apiError);

      // Show user feedback via toast
      if (showToast) {
        const message = customMessage || getErrorMessage(apiError);
        toast.error(message, {
          title: context || 'Error',
          duration: getErrorDuration(apiError.code),
          action: apiError.code === 'NETWORK_ERROR' ? {
            label: 'Retry',
            onClick: () => window.location.reload()
          } : undefined
        });
      }

      // Call custom error handler if provided
      if (onError) {
        onError(apiError);
      }

      return apiError;
    },
    [toast]
  );

  // Wrapper for async API calls with automatic error handling
  const withErrorHandling = useCallback(
    async <T>(
      apiCall: () => Promise<T>,
      options: ApiErrorHandlerOptions = {}
    ): Promise<T | null> => {
      try {
        return await apiCall();
      } catch (error) {
        handleError(error, options);
        return null;
      }
    },
    [handleError]
  );

  // Wrapper for async API calls that throws errors after handling
  const withErrorHandlingAndThrow = useCallback(
    async <T>(
      apiCall: () => Promise<T>,
      options: ApiErrorHandlerOptions = {}
    ): Promise<T> => {
      try {
        return await apiCall();
      } catch (error) {
        const apiError = handleError(error, options);
        throw apiError;
      }
    },
    [handleError]
  );

  return {
    handleError,
    withErrorHandling,
    withErrorHandlingAndThrow
  };
}

// Helper function to get user-friendly error messages
function getErrorMessage(error: ApiError): string {
  // Handle specific error codes
  switch (error.code) {
    case 'NETWORK_ERROR':
      return 'Unable to connect to the server. Please check your internet connection.';
    case 'HTTP_401':
      return 'Your session has expired. Please log in again.';
    case 'HTTP_403':
      return 'You do not have permission to perform this action.';
    case 'HTTP_404':
      return 'The requested resource was not found.';
    case 'HTTP_409':
      return 'This operation conflicts with existing data.';
    case 'HTTP_422':
      return 'Please check your input and try again.';
    case 'HTTP_429':
      return 'Too many requests. Please wait a moment and try again.';
    case 'HTTP_500':
    case 'HTTP_502':
    case 'HTTP_503':
      return 'Server error. Please try again later.';
    default:
      return error.detail || 'An unexpected error occurred. Please try again.';
  }
}

// Helper function to determine toast duration based on error severity
function getErrorDuration(errorCode: string): number {
  switch (errorCode) {
    case 'NETWORK_ERROR':
    case 'HTTP_500':
    case 'HTTP_502':
    case 'HTTP_503':
      return 8000; // 8 seconds for critical errors
    case 'HTTP_401':
    case 'HTTP_403':
      return 6000; // 6 seconds for auth errors
    case 'HTTP_422':
    case 'HTTP_409':
      return 7000; // 7 seconds for validation errors
    default:
      return 5000; // 5 seconds for other errors
  }
}

// Helper hook for form submission errors
export function useFormErrorHandler() {
  const { handleError } = useApiErrorHandler();

  const handleFormError = useCallback(
    (error: unknown, fieldName?: string) => {
      const apiError = handleError(error, {
        showToast: false, // Don't show toast for form errors
        context: fieldName ? `Form field: ${fieldName}` : 'Form submission'
      });

      // Return field-specific errors if available
      if (apiError.errors && apiError.errors.length > 0) {
        return apiError.errors.reduce((acc, err) => {
          acc[err.field || 'general'] = err.message;
          return acc;
        }, {} as Record<string, string>);
      }

      // Return general error
      return {
        general: apiError.detail || 'Form submission failed'
      };
    },
    [handleError]
  );

  return { handleFormError };
}

export default useApiErrorHandler;