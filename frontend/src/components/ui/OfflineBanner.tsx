'use client'

import React from 'react'
import { X, WifiOff, RefreshCw } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useOffline } from '@/providers/OfflineProvider'

interface OfflineBannerProps {
  className?: string
}

export function OfflineBanner({ className }: OfflineBannerProps) {
  const { showOfflineBanner, dismissOfflineBanner, offlineData, isSlowConnection } = useOffline()

  if (!showOfflineBanner && !isSlowConnection) {
    return null
  }

  const formatLastSync = (timestamp: number | null) => {
    if (!timestamp) return 'Never'

    const now = Date.now()
    const diff = now - timestamp
    const minutes = Math.floor(diff / 60000)

    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`

    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`

    const days = Math.floor(hours / 24)
    return `${days}d ago`
  }

  return (
    <div
      className={cn(
        'fixed top-0 left-0 right-0 z-50 bg-orange-500 text-white px-4 py-3 shadow-lg',
        isSlowConnection && !showOfflineBanner && 'bg-yellow-500 text-yellow-900',
        className
      )}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {showOfflineBanner ? (
            <WifiOff className="w-5 h-5 flex-shrink-0" />
          ) : (
            <RefreshCw className="w-5 h-5 flex-shrink-0 animate-spin" />
          )}

          <div className="flex-1">
            {showOfflineBanner ? (
              <div>
                <p className="font-medium">You&apos;re currently offline</p>
                <p className="text-sm opacity-90 mt-1">
                  {offlineData.hasOfflineProducts || offlineData.hasOfflineCart
                    ? `Some features are available offline. Last synced: ${formatLastSync(offlineData.lastSync)}`
                    : 'Limited functionality available. Please check your internet connection.'
                  }
                </p>
              </div>
            ) : (
              <div>
                <p className="font-medium">Slow connection detected</p>
                <p className="text-sm opacity-90">Some features may load slower than usual.</p>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {offlineData.hasOfflineProducts && showOfflineBanner && (
            <span className="bg-orange-600 text-orange-100 px-2 py-1 rounded text-xs font-medium">
              Offline Mode
            </span>
          )}

          <button
            onClick={dismissOfflineBanner}
            className="p-1 hover:bg-orange-600 rounded transition-colors"
            aria-label="Dismiss offline banner"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default OfflineBanner