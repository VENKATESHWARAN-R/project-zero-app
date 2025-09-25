/**
 * Client component for featured products with interactive features
 */
'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ProductCard } from '@/components/product/ProductCard'
import { Product } from '@/types/product'

interface FeaturedProductsProps {
  initialProducts: Product[]
}

export function FeaturedProducts({ initialProducts }: FeaturedProductsProps) {
  const [products] = useState<Product[]>(initialProducts)

  return (
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

      {products.length > 0 ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map((product) => (
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
  )
}