import { lazy } from 'react'

export const LazyProductFilters = lazy(() => import('@/components/product/ProductFilters').then(module => ({ default: module.ProductFilters })))