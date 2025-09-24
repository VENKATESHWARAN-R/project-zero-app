'use client'

import { useState, useEffect } from 'react'

export interface NetworkStatus {
  isOnline: boolean
  isSlowConnection: boolean
  effectiveType: string | undefined
}

export function useNetworkStatus(): NetworkStatus {
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus>({
    isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
    isSlowConnection: false,
    effectiveType: undefined,
  })

  useEffect(() => {
    const updateOnlineStatus = () => {
      setNetworkStatus(prev => ({
        ...prev,
        isOnline: navigator.onLine,
      }))
    }

    const updateNetworkInfo = () => {
      const connection = (navigator as any).connection ||
                        (navigator as any).mozConnection ||
                        (navigator as any).webkitConnection

      if (connection) {
        const isSlowConnection =
          connection.effectiveType === '2g' ||
          connection.effectiveType === 'slow-2g' ||
          (connection.downlink && connection.downlink < 1.5)

        setNetworkStatus(prev => ({
          ...prev,
          isSlowConnection,
          effectiveType: connection.effectiveType,
        }))
      }
    }

    // Set up event listeners
    window.addEventListener('online', updateOnlineStatus)
    window.addEventListener('offline', updateOnlineStatus)

    // Listen for connection changes if supported
    const connection = (navigator as any).connection ||
                      (navigator as any).mozConnection ||
                      (navigator as any).webkitConnection

    if (connection) {
      connection.addEventListener('change', updateNetworkInfo)
      updateNetworkInfo() // Initial check
    }

    return () => {
      window.removeEventListener('online', updateOnlineStatus)
      window.removeEventListener('offline', updateOnlineStatus)

      if (connection) {
        connection.removeEventListener('change', updateNetworkInfo)
      }
    }
  }, [])

  return networkStatus
}

export default useNetworkStatus