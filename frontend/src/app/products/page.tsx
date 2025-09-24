'use client'

import { useEffect, useState, useCallback } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { useProductStore } from '@/store/products'
import { ProductCard } from '@/components/product/ProductCard'
import { ProductFilters } from '@/components/product/ProductFilters'
import { SearchBar } from '@/components/product/SearchBar'
import Loading from '@/components/ui/Loading'
import { ProductFilters as ProductFiltersType } from '@/types/product'

export default function ProductsPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { products, categories, isLoading, error, loadProducts, loadCategories, filters, setFilters } = useProductStore()

  const [currentPage, setCurrentPage] = useState(1)
  const [sortBy, setSortBy] = useState<'name' | 'price' | 'created_at'>('name')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const itemsPerPage = 20

  // Initialize filters from URL params
  useEffect(() => {
    const category = searchParams.get('category')
    const search = searchParams.get('search')
    const minPrice = searchParams.get('min_price')
    const maxPrice = searchParams.get('max_price')

    const urlFilters: Partial<ProductFiltersType> = {}
    if (category) urlFilters.category = category
    if (search) urlFilters.search = search
    if (minPrice && maxPrice) {
      urlFilters.priceRange = [parseInt(minPrice), parseInt(maxPrice)]
    }

    if (Object.keys(urlFilters).length > 0) {
      setFilters(urlFilters)
    }
  }, [searchParams, setFilters])

  // Load categories on mount
  useEffect(() => {
    loadCategories()
  }, [loadCategories])

  // Load products when filters change
  useEffect(() => {
    const loadData = async () => {
      const searchFilters = {
        ...filters,
        page: currentPage,
        limit: itemsPerPage,
        sort: sortBy,
        order: sortOrder
      }
      await loadProducts(searchFilters)
    }

    loadData()
  }, [filters, currentPage, sortBy, sortOrder, loadProducts])

  const handleFilterChange = useCallback((newFilters: Partial<ProductFiltersType>) => {
    setFilters(newFilters)
    setCurrentPage(1) // Reset to first page when filters change

    // Update URL params
    const params = new URLSearchParams()
    if (newFilters.category) params.set('category', newFilters.category)
    if (newFilters.search) params.set('search', newFilters.search)
    if (newFilters.priceRange) {
      params.set('min_price', newFilters.priceRange[0].toString())
      params.set('max_price', newFilters.priceRange[1].toString())
    }

    const newUrl = params.toString() ? `/products?${params.toString()}` : '/products'
    router.replace(newUrl)
  }, [setFilters, router])

  const handleSearch = useCallback((searchTerm: string) => {
    handleFilterChange({ ...filters, search: searchTerm })
  }, [filters, handleFilterChange])

  const handleSortChange = useCallback((field: 'name' | 'price' | 'created_at', order: 'asc' | 'desc') => {
    setSortBy(field)
    setSortOrder(order)
  }, [])

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold text-red-600 mb-4">Error Loading Products</h1>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={() => loadProducts()}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Products</h1>
        <SearchBar onSearch={handleSearch} initialValue={filters.search || ''} />
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Filters Sidebar */}
        <aside className="lg:w-1/4">
          <ProductFilters
            categories={categories}
            filters={filters}
            onFiltersChange={handleFilterChange}
          />
        </aside>

        {/* Products Grid */}
        <main className="lg:w-3/4">
          {/* Sort Controls */}
          <div className="flex justify-between items-center mb-6">
            <p className="text-gray-600">
              {products.length > 0
                ? `Showing ${products.length} products`
                : 'No products found'
              }
            </p>
            <div className="flex items-center gap-4">
              <label className="text-sm font-medium text-gray-700">Sort by:</label>
              <select
                value={`${sortBy}-${sortOrder}`}
                onChange={(e) => {
                  const [field, order] = e.target.value.split('-')
                  handleSortChange(field as 'name' | 'price' | 'created_at', order as 'asc' | 'desc')
                }}
                className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="name-asc">Name (A-Z)</option>
                <option value="name-desc">Name (Z-A)</option>
                <option value="price-asc">Price (Low to High)</option>
                <option value="price-desc">Price (High to Low)</option>
                <option value="created_at-desc">Newest First</option>
                <option value="created_at-asc">Oldest First</option>
              </select>
            </div>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="flex justify-center py-12">
              <Loading />
            </div>
          )}

          {/* Products Grid */}
          {!isLoading && products.length > 0 && (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {products.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          )}

          {/* Empty State */}
          {!isLoading && products.length === 0 && (
            <div className="text-center py-12">
              <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m0 0V9a2 2 0 012-2h2a2 2 0 012 2v4.01" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">No products found</h3>
              <p className="text-gray-500 mb-4">Try adjusting your search or filter criteria</p>
              <button
                onClick={() => handleFilterChange({})}
                className="text-blue-600 hover:text-blue-800 font-semibold"
              >
                Clear all filters
              </button>
            </div>
          )}

          {/* Pagination */}
          {!isLoading && products.length > 0 && (
            <div className="flex justify-center items-center gap-4">
              <button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="text-gray-700">
                Page {currentPage}
              </span>
              <button
                onClick={() => setCurrentPage(prev => prev + 1)}
                disabled={products.length < itemsPerPage}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}