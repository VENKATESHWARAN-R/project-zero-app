'use client'

import { useState, useCallback, useRef, useMemo } from 'react'
import { useNetworkStatus } from './useNetworkStatus'

export interface RetryConfig {
  maxRetries: number
  baseDelay: number
  maxDelay: number
  backoffFactor: number
}

export interface ErrorRecoveryState {
  retryCount: number
  isRetrying: boolean
  lastError: Error | null
  canRetry: boolean
}

const DEFAULT_CONFIG: RetryConfig = {
  maxRetries: 3,
  baseDelay: 1000,
  maxDelay: 10000,
  backoffFactor: 2,
}

export function useErrorRecovery<T extends (...args: unknown[]) => Promise<unknown>>(
  asyncFn: T,
  config: Partial<RetryConfig> = {}
) {
  const { isOnline } = useNetworkStatus()
  const fullConfig = useMemo(() => ({ ...DEFAULT_CONFIG, ...config }), [config])
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)

  const [state, setState] = useState<ErrorRecoveryState>({
    retryCount: 0,
    isRetrying: false,
    lastError: null,
    canRetry: true,
  })

  const calculateDelay = useCallback((attemptNumber: number): number => {
    const delay = Math.min(
      fullConfig.baseDelay * Math.pow(fullConfig.backoffFactor, attemptNumber),
      fullConfig.maxDelay
    )
    // Add jitter to prevent thundering herd
    return delay + Math.random() * 1000
  }, [fullConfig])

  const isRetryableError = useCallback((error: unknown): boolean => {
    // Network errors
    if (!isOnline) return true

    // Type guard for error object
    if (typeof error === 'object' && error !== null) {
      // HTTP status codes that are retryable
      if ('status' in error && typeof error.status === 'number') {
        return error.status >= 500 ||
               error.status === 429 ||
               error.status === 408 ||
               error.status === 0
      }

      // Network-related error messages
      if ('message' in error && typeof error.message === 'string') {
        const errorMessage = error.message;
        const networkErrors = [
          'network error',
          'fetch error',
          'connection failed',
          'timeout',
          'aborted',
          'dns',
          'unreachable'
        ]
        return networkErrors.some(keyword =>
          errorMessage.toLowerCase().includes(keyword)
        )
      }
    }

    return false
  }, [isOnline])

  const executeWithRetry = useCallback(async (
    ...args: Parameters<T>
  ): Promise<ReturnType<T>> => {
    const execute = async (attemptNumber: number = 0): Promise<ReturnType<T>> => {
      try {
        setState(prev => ({
          ...prev,
          isRetrying: attemptNumber > 0,
          retryCount: attemptNumber,
        }))

        const result = await asyncFn(...args) as Awaited<ReturnType<T>>

        // Success - reset state
        setState({
          retryCount: 0,
          isRetrying: false,
          lastError: null,
          canRetry: true,
        })

        return result
      } catch (error) {
        const currentError = error as Error
        const shouldRetry =
          attemptNumber < fullConfig.maxRetries &&
          isRetryableError(currentError) &&
          isOnline

        setState(prev => ({
          ...prev,
          lastError: currentError,
          isRetrying: false,
          canRetry: shouldRetry,
          retryCount: attemptNumber,
        }))

        if (shouldRetry) {
          const delay = calculateDelay(attemptNumber)

          return new Promise<Awaited<ReturnType<T>>>((resolve, reject) => {
            timeoutRef.current = setTimeout(async () => {
              try {
                const result = await execute(attemptNumber + 1)
                resolve(result)
              } catch (retryError) {
                reject(retryError)
              }
            }, delay)
          })
        } else {
          throw currentError
        }
      }
    }

    return execute()
  }, [asyncFn, fullConfig, isRetryableError, isOnline, calculateDelay])

  const retry = useCallback(async (...args: Parameters<T>): Promise<ReturnType<T>> => {
    if (!state.canRetry) {
      throw new Error('Cannot retry - maximum attempts reached or error is not retryable')
    }

    return executeWithRetry(...args)
  }, [executeWithRetry, state.canRetry])

  const reset = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    setState({
      retryCount: 0,
      isRetrying: false,
      lastError: null,
      canRetry: true,
    })
  }, [])

  // Cleanup timeout on unmount
  const cleanup = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
  }, [])

  return {
    ...state,
    executeWithRetry,
    retry,
    reset,
    cleanup,
    isNetworkError: state.lastError ? isRetryableError(state.lastError) : false,
    nextRetryDelay: state.canRetry ? calculateDelay(state.retryCount) : null,
  }
}

export default useErrorRecovery