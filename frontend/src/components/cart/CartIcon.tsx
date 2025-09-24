'use client';

import Link from 'next/link';
import { useCartStore } from '@/store/cart';
import { useAuthStore } from '@/store/auth';

interface CartIconProps {
  className?: string;
  showLabel?: boolean;
}

export function CartIcon({ className = '', showLabel = false }: CartIconProps) {
  const cart = useCartStore((state) => state.cart);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isCartLoading = useCartStore((state) => state.isLoading);

  const itemCount = cart?.itemCount || 0;

  if (!isAuthenticated) {
    return (
      <Link
        href="/login"
        className={`relative flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors ${className}`}
        aria-label="Login to access cart"
      >
        <div className="relative">
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.68 8.2a.75.75 0 01-.76.8H3m0 0v-2m14 4v2a2 2 0 01-2 2h-8a2 2 0 01-2-2v-2"
            />
          </svg>
        </div>
        {showLabel && <span className="text-sm font-medium">Cart</span>}
      </Link>
    );
  }

  return (
    <Link
      href="/cart"
      className={`relative flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors ${className}`}
      aria-label={`View cart with ${itemCount} items`}
    >
      <div className="relative">
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-1.68 8.2a.75.75 0 01-.76.8H3m0 0v-2m14 4v2a2 2 0 01-2 2h-8a2 2 0 01-2-2v-2"
          />
        </svg>

        {/* Cart badge */}
        {itemCount > 0 && !isCartLoading && (
          <span className="absolute -top-2 -right-2 bg-blue-600 text-white text-xs font-semibold rounded-full h-5 w-5 flex items-center justify-center min-w-[1.25rem]">
            {itemCount > 99 ? '99+' : itemCount}
          </span>
        )}

        {/* Loading indicator */}
        {isCartLoading && (
          <span className="absolute -top-1 -right-1 w-3 h-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
          </span>
        )}
      </div>

      {showLabel && (
        <div className="flex flex-col items-start">
          <span className="text-sm font-medium">Cart</span>
          {itemCount > 0 && !isCartLoading && (
            <span className="text-xs text-gray-500">
              {itemCount} item{itemCount !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      )}
    </Link>
  );
}