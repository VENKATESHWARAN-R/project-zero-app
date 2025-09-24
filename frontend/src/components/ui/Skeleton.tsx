/**
 * Skeleton Components
 * Loading states and skeleton placeholders for various content types
 */

'use client';

import React from 'react';
import { cn } from '@/lib/utils';

// Base Skeleton Component
export interface SkeletonProps {
  className?: string;
  animate?: boolean;
}

export function Skeleton({ className, animate = true }: SkeletonProps) {
  return (
    <div
      className={cn(
        'bg-gray-200 rounded',
        animate && 'animate-pulse',
        className
      )}
    />
  );
}

// Skeleton Text Lines
export interface SkeletonTextProps {
  lines?: number;
  className?: string;
  animate?: boolean;
}

export function SkeletonText({ lines = 3, className, animate = true }: SkeletonTextProps) {
  return (
    <div className={cn('space-y-2', className)}>
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          className={cn(
            'h-4',
            index === lines - 1 ? 'w-3/4' : 'w-full'
          )}
          animate={animate}
        />
      ))}
    </div>
  );
}

// Product Card Skeleton
export interface SkeletonProductCardProps {
  className?: string;
  animate?: boolean;
}

export function SkeletonProductCard({ className, animate = true }: SkeletonProductCardProps) {
  return (
    <div className={cn('bg-white rounded-lg border border-gray-200 overflow-hidden', className)}>
      {/* Image Skeleton */}
      <Skeleton className="w-full aspect-square" animate={animate} />

      {/* Content Skeleton */}
      <div className="p-4 space-y-3">
        {/* Title */}
        <Skeleton className="h-5 w-3/4" animate={animate} />

        {/* Description */}
        <div className="space-y-2">
          <Skeleton className="h-3 w-full" animate={animate} />
          <Skeleton className="h-3 w-2/3" animate={animate} />
        </div>

        {/* Price and Button */}
        <div className="flex items-center justify-between pt-2">
          <Skeleton className="h-6 w-20" animate={animate} />
          <Skeleton className="h-9 w-24 rounded-lg" animate={animate} />
        </div>
      </div>
    </div>
  );
}

// Product Grid Skeleton
export interface SkeletonProductGridProps {
  count?: number;
  className?: string;
  animate?: boolean;
}

export function SkeletonProductGrid({ count = 8, className, animate = true }: SkeletonProductGridProps) {
  return (
    <div className={cn(
      'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4 sm:gap-6 lg:gap-8',
      className
    )}>
      {Array.from({ length: count }).map((_, index) => (
        <SkeletonProductCard key={index} animate={animate} />
      ))}
    </div>
  );
}

// Cart Item Skeleton
export interface SkeletonCartItemProps {
  className?: string;
  animate?: boolean;
}

export function SkeletonCartItem({ className, animate = true }: SkeletonCartItemProps) {
  return (
    <div className={cn('bg-white border border-gray-200 rounded-lg p-3 sm:p-4', className)}>
      <div className="flex items-start space-x-3 sm:space-x-4">
        {/* Image Skeleton */}
        <Skeleton className="w-20 h-20 sm:w-24 sm:h-24 rounded-md flex-shrink-0" animate={animate} />

        {/* Content */}
        <div className="flex-grow min-w-0 space-y-3">
          {/* Title and Price */}
          <div className="flex flex-col sm:flex-row sm:items-start justify-between">
            <div className="flex-grow min-w-0 space-y-2">
              <Skeleton className="h-5 w-3/4" animate={animate} />
              <Skeleton className="h-4 w-1/2" animate={animate} />
              <Skeleton className="h-3 w-1/4" animate={animate} />
            </div>
            <div className="text-right space-y-1 mt-2 sm:mt-0">
              <Skeleton className="h-6 w-16" animate={animate} />
              <Skeleton className="h-3 w-12" animate={animate} />
            </div>
          </div>

          {/* Quantity Controls and Actions */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
            <div className="flex items-center space-x-3">
              <Skeleton className="h-4 w-24" animate={animate} />
              <Skeleton className="h-8 w-24 rounded-md" animate={animate} />
            </div>
            <div className="flex items-center justify-between sm:space-x-4">
              <div className="text-right space-y-1">
                <Skeleton className="h-5 w-16" animate={animate} />
                <Skeleton className="h-3 w-12" animate={animate} />
              </div>
              <Skeleton className="h-8 w-16 rounded" animate={animate} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Profile Skeleton
export interface SkeletonProfileProps {
  className?: string;
  animate?: boolean;
}

export function SkeletonProfile({ className, animate = true }: SkeletonProfileProps) {
  return (
    <div className={cn('bg-white rounded-lg border border-gray-200 p-6', className)}>
      {/* Avatar and Basic Info */}
      <div className="flex items-center space-x-4 mb-6">
        <Skeleton className="w-16 h-16 rounded-full" animate={animate} />
        <div className="space-y-2 flex-1">
          <Skeleton className="h-6 w-48" animate={animate} />
          <Skeleton className="h-4 w-32" animate={animate} />
        </div>
      </div>

      {/* Form Fields */}
      <div className="space-y-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="space-y-2">
            <Skeleton className="h-4 w-24" animate={animate} />
            <Skeleton className="h-10 w-full rounded-lg" animate={animate} />
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="flex space-x-3 mt-6">
        <Skeleton className="h-10 w-24 rounded-lg" animate={animate} />
        <Skeleton className="h-10 w-20 rounded-lg" animate={animate} />
      </div>
    </div>
  );
}

// Table Skeleton
export interface SkeletonTableProps {
  rows?: number;
  columns?: number;
  className?: string;
  animate?: boolean;
}

export function SkeletonTable({ rows = 5, columns = 4, className, animate = true }: SkeletonTableProps) {
  return (
    <div className={cn('bg-white rounded-lg border border-gray-200 overflow-hidden', className)}>
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
          {Array.from({ length: columns }).map((_, index) => (
            <Skeleton key={index} className="h-4 w-20" animate={animate} />
          ))}
        </div>
      </div>

      {/* Rows */}
      <div className="divide-y divide-gray-200">
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={rowIndex} className="p-4">
            <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
              {Array.from({ length: columns }).map((_, colIndex) => (
                <Skeleton key={colIndex} className="h-4 w-full" animate={animate} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Page Header Skeleton
export interface SkeletonPageHeaderProps {
  className?: string;
  animate?: boolean;
  showBreadcrumb?: boolean;
  showActions?: boolean;
}

export function SkeletonPageHeader({
  className,
  animate = true,
  showBreadcrumb = true,
  showActions = false
}: SkeletonPageHeaderProps) {
  return (
    <div className={cn('space-y-4', className)}>
      {showBreadcrumb && (
        <div className="flex items-center space-x-2">
          <Skeleton className="h-4 w-12" animate={animate} />
          <span className="text-gray-300">/</span>
          <Skeleton className="h-4 w-16" animate={animate} />
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" animate={animate} />
          <Skeleton className="h-4 w-96" animate={animate} />
        </div>

        {showActions && (
          <div className="flex space-x-2">
            <Skeleton className="h-10 w-24 rounded-lg" animate={animate} />
            <Skeleton className="h-10 w-32 rounded-lg" animate={animate} />
          </div>
        )}
      </div>
    </div>
  );
}

// Stats Cards Skeleton
export interface SkeletonStatsProps {
  count?: number;
  className?: string;
  animate?: boolean;
}

export function SkeletonStats({ count = 4, className, animate = true }: SkeletonStatsProps) {
  return (
    <div className={cn('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4', className)}>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <Skeleton className="h-4 w-16" animate={animate} />
              <Skeleton className="h-8 w-20" animate={animate} />
            </div>
            <Skeleton className="w-10 h-10 rounded-lg" animate={animate} />
          </div>
        </div>
      ))}
    </div>
  );
}

// Loading Page Component
export interface SkeletonPageProps {
  type: 'products' | 'product-detail' | 'cart' | 'profile' | 'dashboard';
  className?: string;
}

export function SkeletonPage({ type, className }: SkeletonPageProps) {
  const renderContent = () => {
    switch (type) {
      case 'products':
        return (
          <div className="space-y-6">
            <SkeletonPageHeader showBreadcrumb />
            <div className="flex space-x-4">
              {/* Filters Sidebar */}
              <div className="w-64 space-y-4">
                {Array.from({ length: 3 }).map((_, index) => (
                  <div key={index} className="bg-white rounded-lg border border-gray-200 p-4 space-y-3">
                    <Skeleton className="h-5 w-20" />
                    <div className="space-y-2">
                      {Array.from({ length: 4 }).map((_, i) => (
                        <div key={i} className="flex items-center space-x-2">
                          <Skeleton className="w-4 h-4" />
                          <Skeleton className="h-4 w-24" />
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Products Grid */}
              <div className="flex-1">
                <SkeletonProductGrid />
              </div>
            </div>
          </div>
        );

      case 'product-detail':
        return (
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Images */}
            <div className="space-y-4">
              <Skeleton className="w-full aspect-square rounded-lg" />
              <div className="flex space-x-2">
                {Array.from({ length: 4 }).map((_, index) => (
                  <Skeleton key={index} className="w-20 h-20 rounded-lg" />
                ))}
              </div>
            </div>

            {/* Details */}
            <div className="space-y-6">
              <div className="space-y-4">
                <Skeleton className="h-8 w-3/4" />
                <Skeleton className="h-6 w-32" />
                <div className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-2/3" />
                </div>
              </div>

              <div className="space-y-4">
                <Skeleton className="h-10 w-40" />
                <Skeleton className="h-12 w-full rounded-lg" />
              </div>
            </div>
          </div>
        );

      case 'cart':
        return (
          <div className="space-y-6">
            <SkeletonPageHeader showBreadcrumb />
            <div className="grid lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-4">
                {Array.from({ length: 3 }).map((_, index) => (
                  <SkeletonCartItem key={index} />
                ))}
              </div>
              <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
                <Skeleton className="h-6 w-32" />
                <div className="space-y-3">
                  {Array.from({ length: 4 }).map((_, index) => (
                    <div key={index} className="flex justify-between">
                      <Skeleton className="h-4 w-16" />
                      <Skeleton className="h-4 w-20" />
                    </div>
                  ))}
                </div>
                <Skeleton className="h-12 w-full rounded-lg" />
              </div>
            </div>
          </div>
        );

      case 'profile':
        return (
          <div className="space-y-6">
            <SkeletonPageHeader />
            <SkeletonProfile />
          </div>
        );

      case 'dashboard':
        return (
          <div className="space-y-6">
            <SkeletonPageHeader showActions />
            <SkeletonStats />
            <div className="grid lg:grid-cols-2 gap-6">
              <SkeletonTable />
              <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
                <Skeleton className="h-6 w-32" />
                <div className="space-y-3">
                  {Array.from({ length: 5 }).map((_, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <Skeleton className="w-8 h-8 rounded-full" />
                      <div className="flex-1 space-y-1">
                        <Skeleton className="h-4 w-3/4" />
                        <Skeleton className="h-3 w-1/2" />
                      </div>
                      <Skeleton className="h-4 w-12" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return <SkeletonText lines={10} />;
    }
  };

  return (
    <div className={cn('container mx-auto px-4 py-8', className)}>
      {renderContent()}
    </div>
  );
}

export default Skeleton;