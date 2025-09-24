'use client';

import { Cart } from '@/types/cart';
import { Button } from '@/components/ui/Button';
import { formatCurrency } from '@/lib/utils';
import { useRouter } from 'next/navigation';

interface CartSummaryProps {
  cart: Cart | null;
  className?: string;
  showCheckoutButton?: boolean;
  isLoading?: boolean;
}

export function CartSummary({
  cart,
  className = '',
  showCheckoutButton = true,
  isLoading = false
}: CartSummaryProps) {
  const router = useRouter();

  if (!cart || cart.items.length === 0) {
    return (
      <div className={`bg-gray-50 rounded-lg p-6 text-center ${className}`}>
        <div className="text-gray-400 text-4xl mb-2">🛒</div>
        <h3 className="text-lg font-medium text-gray-900 mb-1">Your cart is empty</h3>
        <p className="text-gray-500 text-sm">Add some items to get started!</p>
      </div>
    );
  }

  // Calculate summary details
  const subtotal = cart.totalAmount;
  const shipping = 0; // Free shipping for demo
  const tax = Math.round(subtotal * 0.08); // 8% tax estimate
  const total = subtotal + shipping + tax;

  const hasOutOfStockItems = cart.items.some(item => !item.product.inStock);
  const hasStockIssues = cart.items.some(
    item => item.quantity > item.product.stockQuantity
  );

  const handleCheckout = () => {
    if (hasOutOfStockItems || hasStockIssues) {
      // Could show a modal or alert here
      return;
    }
    router.push('/checkout');
  };

  const handleContinueShopping = () => {
    router.push('/products');
  };

  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4 w-32"></div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex justify-between">
                <div className="h-4 bg-gray-200 rounded w-20"></div>
                <div className="h-4 bg-gray-200 rounded w-16"></div>
              </div>
            ))}
          </div>
          <div className="h-10 bg-gray-200 rounded mt-6"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow ${className}`}>
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Summary</h3>

        <div className="space-y-3 mb-6">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">
              Subtotal ({cart.itemCount} item{cart.itemCount !== 1 ? 's' : ''})
            </span>
            <span className="font-medium">
              {formatCurrency(subtotal, cart.currency)}
            </span>
          </div>

          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Shipping</span>
            <span className="font-medium text-green-600">
              {shipping === 0 ? 'FREE' : formatCurrency(shipping, cart.currency)}
            </span>
          </div>

          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Estimated Tax</span>
            <span className="font-medium">
              {formatCurrency(tax, cart.currency)}
            </span>
          </div>

          <div className="border-t pt-3">
            <div className="flex justify-between">
              <span className="text-base font-semibold text-gray-900">Total</span>
              <span className="text-lg font-bold text-gray-900">
                {formatCurrency(total, cart.currency)}
              </span>
            </div>
          </div>
        </div>

        {/* Warnings */}
        {(hasOutOfStockItems || hasStockIssues) && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <div className="flex items-start">
              <div className="text-yellow-600 text-sm">
                ⚠️ Please resolve cart issues before proceeding to checkout
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        {showCheckoutButton && (
          <div className="space-y-3">
            <Button
              onClick={handleCheckout}
              disabled={hasOutOfStockItems || hasStockIssues || isLoading}
              className="w-full py-3 text-base font-medium"
            >
              {hasOutOfStockItems || hasStockIssues
                ? 'Fix Cart Issues'
                : 'Proceed to Checkout'}
            </Button>

            <Button
              variant="outline"
              onClick={handleContinueShopping}
              className="w-full py-2"
            >
              Continue Shopping
            </Button>
          </div>
        )}

        {/* Additional Info */}
        <div className="mt-6 text-xs text-gray-500 space-y-1">
          <p>• Free shipping on all orders</p>
          <p>• 30-day return policy</p>
          <p>• Secure payment processing</p>
        </div>
      </div>

      {/* Promo Code Section */}
      <div className="border-t px-6 py-4 bg-gray-50">
        <div className="flex items-center space-x-3">
          <input
            type="text"
            placeholder="Enter promo code"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <Button size="sm" variant="outline">
            Apply
          </Button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Promo codes will be applied at checkout
        </p>
      </div>
    </div>
  );
}