'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { CartItem as CartItemType } from '@/types/cart';
import { Button } from '@/components/ui/Button';
import { useCartStore } from '@/store/cart';
import { formatCurrency } from '@/lib/utils';

interface CartItemProps {
  item: CartItemType;
  className?: string;
}

export function CartItem({ item, className = '' }: CartItemProps) {
  const updateItemQuantity = useCartStore((state) => state.updateItemQuantity);
  const removeItem = useCartStore((state) => state.removeItem);
  const isLoading = useCartStore((state) => state.isLoading);

  const [quantity, setQuantity] = useState(item.quantity);
  const [isUpdating, setIsUpdating] = useState(false);

  const handleQuantityChange = async (newQuantity: number) => {
    if (newQuantity <= 0 || newQuantity > item.product.stockQuantity) return;

    setQuantity(newQuantity);
    setIsUpdating(true);

    try {
      await updateItemQuantity(item.id, newQuantity);
    } catch (error) {
      // Revert quantity on error
      setQuantity(item.quantity);
      console.error('Failed to update quantity:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleRemove = async () => {
    setIsUpdating(true);
    try {
      await removeItem(item.id);
    } catch (error) {
      console.error('Failed to remove item:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const itemTotal = item.product.price * item.quantity;

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-3 sm:p-4 ${className}`}>
      <div className="flex items-start space-x-3 sm:space-x-4">
        {/* Product Image */}
        <Link href={`/products/${item.product.id}`} className="flex-shrink-0">
          <div className="relative w-20 h-20 sm:w-24 sm:h-24">
            <Image
              src={item.product.imageUrl}
              alt={item.product.name}
              fill
              className="object-cover rounded-md"
              sizes="96px"
            />
          </div>
        </Link>

        {/* Product Details */}
        <div className="flex-grow min-w-0">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between">
            <div className="flex-grow min-w-0 mb-2 sm:mb-0">
              <Link
                href={`/products/${item.product.id}`}
                className="text-lg font-medium text-gray-900 hover:text-blue-600 transition-colors line-clamp-2"
              >
                {item.product.name}
              </Link>

              {item.product.description && (
                <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                  {item.product.description}
                </p>
              )}

              {item.product.category && (
                <p className="text-sm text-gray-500 mt-1 capitalize">
                  {item.product.category}
                </p>
              )}

              <div className="flex items-center text-sm text-gray-500 mt-2">
                <span>Added on {new Date(item.addedAt).toLocaleDateString()}</span>
              </div>
            </div>

            {/* Price */}
            <div className="text-right flex-shrink-0">
              <div className="text-lg font-semibold text-gray-900">
                {formatCurrency(item.product.price, item.product.currency)}
              </div>
              <div className="text-sm text-gray-500">per item</div>
            </div>
          </div>

          {/* Quantity and Actions */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mt-4 space-y-3 sm:space-y-0">
            <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
              {/* Stock Status */}
              <div className="flex items-center text-sm">
                {item.product.inStock ? (
                  <div className="flex items-center text-green-600">
                    <span className="w-2 h-2 bg-green-600 rounded-full mr-1"></span>
                    In stock ({item.product.stockQuantity} available)
                  </div>
                ) : (
                  <div className="flex items-center text-red-600">
                    <span className="w-2 h-2 bg-red-600 rounded-full mr-1"></span>
                    Out of stock
                  </div>
                )}
              </div>

              {/* Quantity Controls */}
              <div className="flex items-center space-x-2 border border-gray-300 rounded-md">
                <button
                  onClick={() => handleQuantityChange(quantity - 1)}
                  disabled={quantity <= 1 || isUpdating || !item.product.inStock}
                  className="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-gray-800 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Decrease quantity"
                >
                  −
                </button>
                <span className="w-12 text-center text-sm font-medium">
                  {isUpdating ? '...' : quantity}
                </span>
                <button
                  onClick={() => handleQuantityChange(quantity + 1)}
                  disabled={
                    quantity >= item.product.stockQuantity ||
                    isUpdating ||
                    !item.product.inStock
                  }
                  className="w-8 h-8 flex items-center justify-center text-gray-600 hover:text-gray-800 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Increase quantity"
                >
                  +
                </button>
              </div>
            </div>

            {/* Item Total and Actions */}
            <div className="flex items-center justify-between sm:space-x-4">
              <div className="text-right">
                <div className="text-lg font-semibold text-gray-900">
                  {formatCurrency(itemTotal, item.product.currency)}
                </div>
                <div className="text-sm text-gray-500">subtotal</div>
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={handleRemove}
                disabled={isUpdating || isLoading}
                className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-300 ml-2 sm:ml-0"
              >
                {isUpdating ? 'Removing...' : 'Remove'}
              </Button>
            </div>
          </div>

          {/* Stock Warning */}
          {item.product.inStock && quantity > item.product.stockQuantity && (
            <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded-md">
              <p className="text-sm text-yellow-800">
                Only {item.product.stockQuantity} items available. Please adjust quantity.
              </p>
            </div>
          )}

          {/* Out of Stock Warning */}
          {!item.product.inStock && (
            <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-800">
                This item is currently out of stock. Remove it from your cart or save it for later.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}