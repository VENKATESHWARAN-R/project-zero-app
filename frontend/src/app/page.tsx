'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useProductStore } from '@/store/products'
import { ProductCard } from '@/components/product/ProductCard'
import Loading from '@/components/ui/Loading'
import { Product } from '@/types/product'

export default function Home() {
  const { products, isLoading, error, loadProducts } = useProductStore()
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([])

  useEffect(() => {
    loadProducts({ limit: 8 })
  }, [loadProducts])

  useEffect(() => {
    setFeaturedProducts(products.slice(0, 8))
  }, [products])

  if (isLoading) {
    return <Loading />
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold text-red-600 mb-4">Error Loading Products</h1>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={() => loadProducts({ limit: 8 })}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <section className="text-center py-16 mb-12">
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
          Welcome to <span className="text-blue-600">Project Zero Store</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Discover amazing products at great prices. Shop the latest electronics, gadgets, and more.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/products"
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Shop Now
          </Link>
          <Link
            href="/products?category=electronics"
            className="border-2 border-blue-600 text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
          >
            Browse Electronics
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="grid md:grid-cols-3 gap-8 mb-16">
        <div className="text-center p-6">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7h18l-2 13H5L3 7zM3 7l-1-4H1m6 4v4a4 4 0 008 0V7" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold mb-2">Easy Shopping</h3>
          <p className="text-gray-600">Intuitive shopping experience with secure checkout</p>
        </div>
        <div className="text-center p-6">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold mb-2">Best Prices</h3>
          <p className="text-gray-600">Competitive prices on all our products</p>
        </div>
        <div className="text-center p-6">
          <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold mb-2">Fast Delivery</h3>
          <p className="text-gray-600">Quick and reliable shipping to your doorstep</p>
        </div>
      </section>

      {/* Featured Products */}
      <section>
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Featured Products</h2>
          <Link
            href="/products"
            className="text-blue-600 hover:text-blue-800 font-semibold"
          >
            View All Products →
          </Link>
        </div>

        {featuredProducts.length > 0 ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {featuredProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg">No products available at the moment.</p>
            <p className="text-gray-500 mt-2">Please check back later.</p>
          </div>
        )}
      </section>
    </div>
  )
}
