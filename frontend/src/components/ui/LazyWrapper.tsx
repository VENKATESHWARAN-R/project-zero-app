'use client'

import { Suspense } from 'react'
import Loading from './Loading'

interface LazyWrapperProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export default function LazyWrapper({ children, fallback = <Loading /> }: LazyWrapperProps) {
  return (
    <Suspense fallback={fallback}>
      {children}
    </Suspense>
  )
}