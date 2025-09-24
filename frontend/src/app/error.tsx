'use client'

import { useEffect } from 'react'
import Link from 'next/link'

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Application error:', error)
  }, [error])

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center items-center px-4">
      <div className="text-center">
        {/* Error Illustration */}
        <div className="mb-8">
          <div className="w-32 h-32 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-16 h-16 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>

        {/* Error Message */}
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Something went wrong!</h1>
        <p className="text-xl text-gray-600 mb-8 max-w-md mx-auto">
          We encountered an unexpected error. Don't worry, our team has been notified.
        </p>

        {/* Error Details (Development Only) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mb-8 max-w-2xl mx-auto">
            <details className="bg-red-50 border border-red-200 rounded-lg p-4">
              <summary className="cursor-pointer font-medium text-red-800 mb-2">
                Error Details (Development)
              </summary>
              <pre className="text-sm text-red-700 overflow-x-auto">
                {error.message}
                {error.stack && (
                  <>
                    <br />
                    <br />
                    {error.stack}
                  </>
                )}
              </pre>
            </details>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
          <button
            onClick={reset}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
          <Link
            href="/"
            className="border-2 border-blue-600 text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
          >
            Go Home
          </Link>
        </div>

        {/* Help Options */}
        <div className="max-w-2xl mx-auto">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Need help? Try these options:
          </h2>
          <div className="grid sm:grid-cols-3 gap-4">
            <button
              onClick={() => window.location.reload()}
              className="p-4 bg-white rounded-lg shadow-sm border border-gray-200 hover:border-blue-300 transition-colors"
            >
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </div>
              <h3 className="font-medium text-gray-900">Refresh Page</h3>
              <p className="text-sm text-gray-600">Reload the page</p>
            </button>

            <button
              onClick={() => {
                localStorage.clear()
                sessionStorage.clear()
                window.location.reload()
              }}
              className="p-4 bg-white rounded-lg shadow-sm border border-gray-200 hover:border-blue-300 transition-colors"
            >
              <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </div>
              <h3 className="font-medium text-gray-900">Clear Data</h3>
              <p className="text-sm text-gray-600">Reset app data</p>
            </button>

            <Link
              href="/products"
              className="p-4 bg-white rounded-lg shadow-sm border border-gray-200 hover:border-blue-300 transition-colors"
            >
              <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10" />
                </svg>
              </div>
              <h3 className="font-medium text-gray-900">Browse Products</h3>
              <p className="text-sm text-gray-600">Continue shopping</p>
            </Link>
          </div>
        </div>

        {/* Additional Info */}
        <div className="mt-8 text-sm text-gray-500">
          <p>
            If the problem persists, please contact our support team.
            {error.digest && (
              <>
                <br />
                Error ID: <code className="font-mono bg-gray-100 px-1 rounded">{error.digest}</code>
              </>
            )}
          </p>
        </div>
      </div>
    </div>
  )
}