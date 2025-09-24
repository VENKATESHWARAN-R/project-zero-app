'use client'

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'
import { persistentCache } from '@/lib/cache'

interface OfflineContextType {
  isOnline: boolean
  isSlowConnection: boolean
  effectiveType: string | undefined
  showOfflineBanner: boolean
  dismissOfflineBanner: () => void
  offlineData: {
    hasOfflineProducts: boolean
    hasOfflineCart: boolean
    lastSync: number | null
  }
}

const OfflineContext = createContext<OfflineContextType | undefined>(undefined)

export function useOffline() {
  const context = useContext(OfflineContext)
  if (context === undefined) {
    throw new Error('useOffline must be used within an OfflineProvider')
  }
  return context
}

interface OfflineProviderProps {
  children: ReactNode
}

export function OfflineProvider({ children }: OfflineProviderProps) {
  const { isOnline, isSlowConnection, effectiveType } = useNetworkStatus()
  const [showOfflineBanner, setShowOfflineBanner] = useState(false)
  const [dismissedAt, setDismissedAt] = useState<number | null>(null)

  // Check for offline data
  const [offlineData, setOfflineData] = useState({
    hasOfflineProducts: false,
    hasOfflineCart: false,
    lastSync: null as number | null,
  })

  useEffect(() => {
    // Check for offline data availability
    const checkOfflineData = () => {
      try {
        const hasProducts = !!persistentCache.get('products:{}') // Default products
        const hasCart = !!persistentCache.get('cart_summary')
        const lastSyncString = localStorage.getItem('last_sync')
        const lastSync = lastSyncString ? parseInt(lastSyncString, 10) : null

        setOfflineData({
          hasOfflineProducts: hasProducts,
          hasOfflineCart: hasCart,
          lastSync,
        })
      } catch (error) {
        console.warn('Failed to check offline data:', error)
      }
    }

    checkOfflineData()

    // Update last sync when coming back online
    if (isOnline && !dismissedAt) {
      try {
        localStorage.setItem('last_sync', Date.now().toString())
        checkOfflineData()
      } catch (error) {
        console.warn('Failed to update sync timestamp:', error)
      }
    }

    // Show offline banner when going offline (but not immediately dismissed)
    if (!isOnline && (!dismissedAt || Date.now() - dismissedAt > 5 * 60 * 1000)) {
      setShowOfflineBanner(true)
    }

    // Hide banner when back online
    if (isOnline) {
      setShowOfflineBanner(false)
      setDismissedAt(null)
    }
  }, [isOnline, dismissedAt])

  const dismissOfflineBanner = () => {
    setShowOfflineBanner(false)
    setDismissedAt(Date.now())
  }

  return (
    <OfflineContext.Provider
      value={{
        isOnline,
        isSlowConnection,
        effectiveType,
        showOfflineBanner,
        dismissOfflineBanner,
        offlineData,
      }}
    >
      {children}
    </OfflineContext.Provider>
  )
}

export default OfflineProvider