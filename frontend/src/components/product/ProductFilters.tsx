'use client';

import { useState, useEffect } from 'react';
import { Category, ProductFilters as FilterType } from '@/types/product';
import { Button } from '@/components/ui/Button';
import { formatCurrency } from '@/lib/utils';

interface ProductFiltersProps {
  filters: FilterType;
  categories: Category[];
  onFiltersChange: (filters: Partial<FilterType>) => void;
  className?: string;
  isLoading?: boolean;
}

export function ProductFilters({
  filters,
  categories,
  onFiltersChange,
  className = '',
  isLoading = false
}: ProductFiltersProps) {
  const [localFilters, setLocalFilters] = useState<FilterType>(filters);
  const [priceRange, setPriceRange] = useState({
    min: filters.min_price || '',
    max: filters.max_price || ''
  });

  // Update local filters when external filters change
  useEffect(() => {
    setLocalFilters(filters);
    setPriceRange({
      min: filters.min_price || '',
      max: filters.max_price || ''
    });
  }, [filters]);

  const handleCategoryChange = (categoryId: string) => {
    const newCategory = localFilters.category === categoryId ? null : categoryId;
    const updatedFilters = { ...localFilters, category: newCategory };
    setLocalFilters(updatedFilters);
    onFiltersChange({ category: newCategory });
  };

  const handleStockFilterChange = (inStock: boolean | undefined) => {
    const updatedFilters = { ...localFilters, in_stock: inStock };
    setLocalFilters(updatedFilters);
    onFiltersChange({ in_stock: inStock });
  };

  const handleSortChange = (sort: string) => {
    const [field, order] = sort.split('_');
    const updatedFilters = {
      ...localFilters,
      sort: field as any,
      order: order as 'asc' | 'desc'
    };
    setLocalFilters(updatedFilters);
    onFiltersChange({ sort: field as any, order: order as 'asc' | 'desc' });
  };

  const handlePriceRangeChange = () => {
    const minPrice = priceRange.min ? parseInt(String(priceRange.min)) * 100 : undefined; // Convert to cents
    const maxPrice = priceRange.max ? parseInt(String(priceRange.max)) * 100 : undefined;

    const updatedFilters = {
      ...localFilters,
      min_price: minPrice,
      max_price: maxPrice
    };
    setLocalFilters(updatedFilters);
    onFiltersChange({ min_price: minPrice, max_price: maxPrice });
  };

  const handleClearFilters = () => {
    const clearedFilters: FilterType = {
      category: null,
      search: '',
      min_price: undefined,
      max_price: undefined,
      in_stock: undefined,
      sort: 'name',
      order: 'asc'
    };
    setLocalFilters(clearedFilters);
    setPriceRange({ min: '', max: '' });
    onFiltersChange(clearedFilters);
  };

  const hasActiveFilters = () => {
    return localFilters.category ||
           localFilters.min_price ||
           localFilters.max_price ||
           localFilters.in_stock !== undefined ||
           (localFilters.sort !== 'name' || localFilters.order !== 'asc');
  };

  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded mb-4 w-24"></div>
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-6 bg-gray-200 rounded w-32"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
        {hasActiveFilters() && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleClearFilters}
            className="text-sm"
          >
            Clear All
          </Button>
        )}
      </div>

      <div className="space-y-6">
        {/* Categories */}
        {categories.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Category</h4>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {categories.map((category) => (
                <label
                  key={category.id}
                  className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 p-2 rounded"
                >
                  <input
                    type="radio"
                    name="category"
                    checked={localFilters.category === category.id}
                    onChange={() => handleCategoryChange(category.id)}
                    className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">
                    {category.name}
                    <span className="text-gray-500 ml-1">({category.productCount})</span>
                  </span>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Price Range */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Price Range</h4>
          <div className="flex items-center space-x-2">
            <input
              type="number"
              placeholder="Min"
              value={priceRange.min}
              onChange={(e) => setPriceRange(prev => ({ ...prev, min: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <span className="text-gray-500">-</span>
            <input
              type="number"
              placeholder="Max"
              value={priceRange.max}
              onChange={(e) => setPriceRange(prev => ({ ...prev, max: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <Button
            size="sm"
            onClick={handlePriceRangeChange}
            className="mt-2 w-full"
            disabled={!priceRange.min && !priceRange.max}
          >
            Apply Price Filter
          </Button>
        </div>

        {/* Stock Status */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Availability</h4>
          <div className="space-y-2">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="radio"
                name="stock"
                checked={localFilters.in_stock === undefined}
                onChange={() => handleStockFilterChange(undefined)}
                className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">All products</span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="radio"
                name="stock"
                checked={localFilters.in_stock === true}
                onChange={() => handleStockFilterChange(true)}
                className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">In stock only</span>
            </label>
          </div>
        </div>

        {/* Sort Options */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">Sort By</h4>
          <select
            value={`${localFilters.sort}_${localFilters.order}`}
            onChange={(e) => handleSortChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="name_asc">Name: A to Z</option>
            <option value="name_desc">Name: Z to A</option>
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
            <option value="created_at_desc">Newest First</option>
            <option value="created_at_asc">Oldest First</option>
          </select>
        </div>
      </div>
    </div>
  );
}