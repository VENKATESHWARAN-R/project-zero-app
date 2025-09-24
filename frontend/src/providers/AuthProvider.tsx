'use client'

import { useEffect } from 'react'
import { useAuthStore } from '@/store/auth'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { refreshToken, isAuthenticated } = useAuthStore()

  useEffect(() => {
    // Check for existing token on app load
    const initAuth = async () => {
      const storedTokens = localStorage.getItem('auth-tokens')
      if (storedTokens && !isAuthenticated) {
        try {
          await refreshToken()
        } catch (error) {
          console.error('Failed to refresh token:', error)
          // Clear invalid tokens
          localStorage.removeItem('auth-tokens')
        }
      }
    }

    initAuth()
  }, [refreshToken, isAuthenticated])

  return <>{children}</>
}