import Link from 'next/link'
import { Metadata } from 'next'
import { BuildSafeProductsService } from '@/lib/build-safe-api'
import { FeaturedProducts } from '@/components/home/FeaturedProducts'
import { Product } from '@/types/product'

export const metadata: Metadata = {
  title: 'Project Zero Store - Premium Electronics & Gadgets',
  description: 'Discover amazing products at great prices. Shop the latest electronics, gadgets, and more at Project Zero Store.',
  keywords: 'electronics, gadgets, shopping, online store, project zero',
}

// Enable static generation with revalidation
export const revalidate = 3600 // Revalidate every hour

export default async function Home() {
  // Fetch featured products server-side with build-time safety
  let featuredProducts: Product[] = []
  let error: string | null = null

  try {
    featuredProducts = await BuildSafeProductsService.getFeaturedProducts(8)
  } catch (err) {
    error = err instanceof Error ? err.message : 'Failed to load products'
    console.warn('Failed to load products on homepage:', err)
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold text-red-600 mb-4">Error Loading Products</h1>
        <p className="text-gray-600 mb-4">{error}</p>
        <Link
          href="/products"
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors inline-block"
        >
          Browse All Products
        </Link>
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
      <FeaturedProducts initialProducts={featuredProducts} />
    </div>
  )
}
