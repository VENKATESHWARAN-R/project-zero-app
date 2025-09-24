import Image from 'next/image';
import Link from 'next/link';
import { Product } from '@/types/product';
import { Button } from '@/components/ui/Button';
import { useCartStore } from '@/store/cart';
import { useAuthStore } from '@/store/auth';
import { formatCurrency } from '@/lib/utils';

interface ProductCardProps {
  product: Product;
  className?: string;
}

export function ProductCard({ product, className = '' }: ProductCardProps) {
  const addItem = useCartStore((state) => state.addItem);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isCartLoading = useCartStore((state) => state.isLoading);

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      // Redirect to login page
      window.location.href = '/login';
      return;
    }

    try {
      await addItem(product.id, 1);
    } catch (error) {
      console.error('Failed to add item to cart:', error);
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 ${className}`}>
      <Link href={`/products/${product.id}`} className="block">
        <div className="relative h-48 w-full">
          <Image
            src={product.imageUrl}
            alt={product.name}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 25vw"
          />
          {!product.inStock && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
              <span className="text-white font-semibold text-lg">Out of Stock</span>
            </div>
          )}
        </div>
      </Link>

      <div className="p-4">
        <Link href={`/products/${product.id}`} className="block">
          <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors line-clamp-2">
            {product.name}
          </h3>
        </Link>

        <p className="text-sm text-gray-600 mt-1 line-clamp-2">
          {product.description}
        </p>

        <div className="mt-2 flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-xl font-bold text-gray-900">
              {formatCurrency(product.price, product.currency)}
            </span>
            <span className="text-sm text-gray-500 capitalize">
              {product.category}
            </span>
          </div>

          <div className="flex flex-col items-end">
            {product.inStock ? (
              <div className="flex items-center text-green-600 text-sm mb-2">
                <span className="w-2 h-2 bg-green-600 rounded-full mr-1"></span>
                {product.stockQuantity} in stock
              </div>
            ) : (
              <div className="flex items-center text-red-600 text-sm mb-2">
                <span className="w-2 h-2 bg-red-600 rounded-full mr-1"></span>
                Out of stock
              </div>
            )}

            <Button
              onClick={handleAddToCart}
              disabled={!product.inStock || isCartLoading}
              size="sm"
              className="min-w-[80px]"
            >
              {isCartLoading ? 'Adding...' : 'Add to Cart'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}