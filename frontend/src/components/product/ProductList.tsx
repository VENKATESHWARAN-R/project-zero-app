import { Product } from '@/types/product';
import { ProductCard } from './ProductCard';
import { Loading } from '@/components/ui/Loading';

interface ProductListProps {
  products: Product[];
  isLoading?: boolean;
  error?: string | null;
  className?: string;
  emptyMessage?: string;
}

export function ProductList({
  products,
  isLoading = false,
  error = null,
  className = '',
  emptyMessage = 'No products found'
}: ProductListProps) {
  if (isLoading) {
    return (
      <div className={`flex justify-center items-center py-12 ${className}`}>
        <Loading size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-6 text-center ${className}`}>
        <div className="text-red-600 font-medium mb-2">Error loading products</div>
        <div className="text-red-500 text-sm">{error}</div>
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className={`bg-gray-50 border border-gray-200 rounded-lg p-12 text-center ${className}`}>
        <div className="text-gray-400 text-6xl mb-4">📦</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">{emptyMessage}</h3>
        <p className="text-gray-500">Try adjusting your search or filters to find what you&apos;re looking for.</p>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Responsive grid with enhanced breakpoints and animations */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4 sm:gap-6 lg:gap-8">
        {products.map((product, index) => (
          <div
            key={product.id}
            className="opacity-0 animate-fade-in-up h-full"
            style={{
              animationDelay: `${Math.min(index * 100, 500)}ms`,
              animationFillMode: 'forwards'
            }}
          >
            <ProductCard
              product={product}
              className="h-full transition-all duration-300 hover:scale-[1.02] hover:shadow-lg"
            />
          </div>
        ))}
      </div>

      {/* Grid info with responsive text sizing */}
      <div className="mt-8 text-center text-sm sm:text-base text-gray-500">
        Showing <span className="font-medium text-gray-700">{products.length}</span> product{products.length !== 1 ? 's' : ''}
      </div>
    </div>
  );
}