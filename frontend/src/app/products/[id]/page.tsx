'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Image from 'next/image'
import Link from 'next/link'
import { useProductStore } from '@/store/products'
import { useCartStore } from '@/store/cart'
import { useAuthStore } from '@/store/auth'
import Loading from '@/components/ui/Loading'
import { ProductCard } from '@/components/product/ProductCard'
import { formatPrice } from '@/lib/utils'
import { Product } from '@/types/product'

export default function ProductDetailPage() {
  const params = useParams()
  const router = useRouter()
  const productId = params.id as string

  const { currentProduct, isLoading, error, loadProduct, loadProducts } = useProductStore()
  const { addItem, isLoading: cartLoading } = useCartStore()
  const { isAuthenticated } = useAuthStore()

  const [quantity, setQuantity] = useState(1)
  const [selectedImage, setSelectedImage] = useState(0)
  const [relatedProducts, setRelatedProducts] = useState<Product[]>([])
  const [addedToCart, setAddedToCart] = useState(false)

  useEffect(() => {
    if (productId) {
      loadProduct(productId)
    }
  }, [productId, loadProduct])

  // Load related products when current product loads
  useEffect(() => {
    if (currentProduct?.category) {
      loadProducts({ category: currentProduct.category, limit: 4 }).then(() => {
        // Filter out current product from related products
        const related = useProductStore.getState().products.filter(
          p => p.id !== currentProduct.id
        ).slice(0, 4)
        setRelatedProducts(related)
      })
    }
  }, [currentProduct, loadProducts])

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      router.push('/login?redirect=/products/' + productId)
      return
    }

    if (!currentProduct) return

    try {
      await addItem(currentProduct.id, quantity)
      setAddedToCart(true)
      setTimeout(() => setAddedToCart(false), 3000) // Hide message after 3 seconds
    } catch (error) {
      console.error('Error adding to cart:', error)
    }
  }

  const handleQuantityChange = (newQuantity: number) => {
    if (newQuantity >= 1 && currentProduct && newQuantity <= currentProduct.stockQuantity) {
      setQuantity(newQuantity)
    }
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Loading />
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold text-red-600 mb-4">Error Loading Product</h1>
        <p className="text-gray-600 mb-4">{error}</p>
        <div className="flex gap-4 justify-center">
          <button
            onClick={() => loadProduct(productId)}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
          <Link
            href="/products"
            className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition-colors"
          >
            Back to Products
          </Link>
        </div>
      </div>
    )
  }

  if (!currentProduct) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold text-gray-700 mb-4">Product Not Found</h1>
        <p className="text-gray-600 mb-4">The product you&apos;re looking for doesn&apos;t exist.</p>
        <Link
          href="/products"
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Browse Products
        </Link>
      </div>
    )
  }

  const product = currentProduct
  const images = product.images || [product.imageUrl]

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <nav className="mb-8">
        <ol className="flex items-center space-x-2 text-sm text-gray-600">
          <li><Link href="/" className="hover:text-blue-600">Home</Link></li>
          <li>/</li>
          <li><Link href="/products" className="hover:text-blue-600">Products</Link></li>
          <li>/</li>
          <li><Link href={`/products?category=${product.category}`} className="hover:text-blue-600 capitalize">{product.category}</Link></li>
          <li>/</li>
          <li className="text-gray-400 truncate">{product.name}</li>
        </ol>
      </nav>

      <div className="grid md:grid-cols-2 gap-12 mb-16">
        {/* Product Images */}
        <div className="space-y-4">
          {/* Main Image */}
          <div className="aspect-square bg-white border border-gray-200 rounded-lg overflow-hidden">
            <Image
              src={images[selectedImage]}
              alt={product.name}
              width={600}
              height={600}
              className="w-full h-full object-cover"
            />
          </div>

          {/* Thumbnail Images */}
          {images.length > 1 && (
            <div className="flex space-x-2">
              {images.map((image, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedImage(index)}
                  className={`w-20 h-20 border-2 rounded-lg overflow-hidden ${
                    selectedImage === index ? 'border-blue-600' : 'border-gray-200'
                  }`}
                >
                  <Image
                    src={image}
                    alt={`${product.name} ${index + 1}`}
                    width={80}
                    height={80}
                    className="w-full h-full object-cover"
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{product.name}</h1>
            <p className="text-lg text-gray-600 capitalize">{product.category}</p>
          </div>

          <div className="text-3xl font-bold text-blue-600">
            {formatPrice(product.price)}
          </div>

          <div className="prose prose-gray max-w-none">
            <p>{product.description}</p>
          </div>

          {/* Stock Status */}
          <div className="flex items-center space-x-2">
            {product.inStock ? (
              <>
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-green-700 font-medium">In Stock ({product.stockQuantity} available)</span>
              </>
            ) : (
              <>
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <span className="text-red-700 font-medium">Out of Stock</span>
              </>
            )}
          </div>

          {/* Specifications */}
          {product.specifications && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Specifications</h3>
              <dl className="grid grid-cols-1 gap-2">
                {Object.entries(product.specifications).map(([key, value]) => (
                  <div key={key} className="flex justify-between border-b border-gray-100 pb-1">
                    <dt className="text-gray-600 capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</dt>
                    <dd className="text-gray-900 font-medium">{typeof value === 'string' || typeof value === 'number' ? value : String(value)}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}

          {/* Add to Cart Section */}
          {product.inStock && (
            <div className="space-y-4 border-t pt-6">
              <div className="flex items-center space-x-4">
                <label className="text-sm font-medium text-gray-700">Quantity:</label>
                <div className="flex items-center border border-gray-300 rounded-md">
                  <button
                    onClick={() => handleQuantityChange(quantity - 1)}
                    className="px-3 py-1 hover:bg-gray-100"
                    disabled={quantity <= 1}
                  >
                    -
                  </button>
                  <span className="px-4 py-1 border-x border-gray-300">{quantity}</span>
                  <button
                    onClick={() => handleQuantityChange(quantity + 1)}
                    className="px-3 py-1 hover:bg-gray-100"
                    disabled={quantity >= product.stockQuantity}
                  >
                    +
                  </button>
                </div>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={handleAddToCart}
                  disabled={cartLoading}
                  className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {cartLoading ? 'Adding...' : 'Add to Cart'}
                </button>
                <button className="px-6 py-3 border-2 border-gray-300 rounded-lg hover:border-gray-400 transition-colors">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </button>
              </div>

              {addedToCart && (
                <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-md">
                  Product added to cart successfully!
                </div>
              )}

              {!isAuthenticated && (
                <p className="text-sm text-gray-600">
                  <Link href="/login" className="text-blue-600 hover:text-blue-800 font-semibold">
                    Sign in
                  </Link>
                  {' '}to add items to your cart
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Related Products */}
      {relatedProducts.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Related Products</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {relatedProducts.map((relatedProduct) => (
              <ProductCard key={relatedProduct.id} product={relatedProduct} />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}