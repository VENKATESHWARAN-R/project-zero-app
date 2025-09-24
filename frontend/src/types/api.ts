/**
 * API response types
 * Common API response patterns and error types
 */

export interface ApiError {
  detail: string;
  code: string;
  errors?: {
    field: string;
    message: string;
  }[];
}

export interface ApiResponse<T = unknown> {
  data?: T;
  error?: ApiError;
  status: number;
  message?: string;
}

export interface PaginatedResponse<T = unknown> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  filters_applied?: Record<string, unknown>;
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  service: string;
  version?: string;
  checks?: {
    database?: 'healthy' | 'unhealthy';
    [key: string]: 'healthy' | 'unhealthy' | undefined;
  };
}

export interface RequestConfig {
  baseURL?: string;
  timeout?: number;
  headers?: Record<string, string>;
  withCredentials?: boolean;
}

export interface RequestOptions {
  headers?: Record<string, string>;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
}

// HTTP Status Codes
export enum HttpStatus {
  OK = 200,
  CREATED = 201,
  NO_CONTENT = 204,
  BAD_REQUEST = 400,
  UNAUTHORIZED = 401,
  FORBIDDEN = 403,
  NOT_FOUND = 404,
  CONFLICT = 409,
  UNPROCESSABLE_ENTITY = 422,
  TOO_MANY_REQUESTS = 429,
  INTERNAL_SERVER_ERROR = 500,
  BAD_GATEWAY = 502,
  SERVICE_UNAVAILABLE = 503,
}

// Rate Limiting
export interface RateLimitInfo {
  limit: number;
  remaining: number;
  reset: number;
  retryAfter?: number;
}

// Generic success response
export interface SuccessResponse<T = unknown> {
  success: true;
  data: T;
  message?: string;
}

// Generic error response
export interface ErrorResponse {
  success: false;
  error: string | ApiError;
  status: number;
}
