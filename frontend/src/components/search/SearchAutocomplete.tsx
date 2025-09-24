/**
 * Search Autocomplete Component
 * Advanced search with autocomplete, suggestions, and filters
 */

'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import Image from 'next/image';
import { Search, X, Filter, ChevronDown, Clock, TrendingUp } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useDebounce } from '@/hooks/useDebounce';

export interface SearchSuggestion {
  id: string;
  text: string;
  type: 'product' | 'category' | 'recent' | 'popular';
  category?: string;
  imageUrl?: string;
}

export interface SearchFilter {
  id: string;
  label: string;
  type: 'category' | 'price' | 'rating' | 'availability';
  options: Array<{
    value: string;
    label: string;
    count?: number;
  }>;
}

export interface SearchAutocompleteProps {
  placeholder?: string;
  suggestions?: SearchSuggestion[];
  filters?: SearchFilter[];
  recentSearches?: string[];
  popularSearches?: string[];
  isLoading?: boolean;
  onSearch: (query: string, filters?: Record<string, string[]>) => void;
  onSuggestionClick?: (suggestion: SearchSuggestion) => void;
  className?: string;
}

interface FilterDropdownProps {
  filter: SearchFilter;
  selectedValues: string[];
  onSelectionChange: (values: string[]) => void;
}

function FilterDropdown({ filter, selectedValues, onSelectionChange }: FilterDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleOptionToggle = (value: string) => {
    const newSelection = selectedValues.includes(value)
      ? selectedValues.filter(v => v !== value)
      : [...selectedValues, value];
    onSelectionChange(newSelection);
  };

  const hasSelection = selectedValues.length > 0;

  return (
    <div ref={dropdownRef} className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg bg-white text-sm font-medium hover:bg-gray-50 transition-colors',
          hasSelection && 'border-blue-500 bg-blue-50 text-blue-700',
          isOpen && 'ring-2 ring-blue-500'
        )}
      >
        <span>{filter.label}</span>
        {hasSelection && (
          <span className="bg-blue-100 text-blue-800 text-xs rounded-full px-2 py-0.5">
            {selectedValues.length}
          </span>
        )}
        <ChevronDown className={cn(
          'w-4 h-4 transition-transform',
          isOpen && 'transform rotate-180'
        )} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
          <div className="p-2 space-y-1">
            {filter.options.map((option) => {
              const isSelected = selectedValues.includes(option.value);
              return (
                <label
                  key={option.value}
                  className="flex items-center space-x-2 p-2 hover:bg-gray-50 cursor-pointer rounded-md"
                >
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => handleOptionToggle(option.value)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="flex-1 text-sm text-gray-700">{option.label}</span>
                  {option.count && (
                    <span className="text-xs text-gray-500">({option.count})</span>
                  )}
                </label>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export function SearchAutocomplete({
  placeholder = "Search products...",
  suggestions = [],
  filters = [],
  recentSearches = [],
  popularSearches = [],
  isLoading = false,
  onSearch,
  onSuggestionClick,
  className
}: SearchAutocompleteProps) {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedFilters, setSelectedFilters] = useState<Record<string, string[]>>({});
  const [activeIndex, setActiveIndex] = useState(-1);

  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const debouncedQuery = useDebounce(query, 300);

  // Generate suggestions based on debounced query
  const filteredSuggestions = React.useMemo(() => {
    if (!debouncedQuery.trim()) {
      const recent = recentSearches.slice(0, 5).map((text, index) => ({
        id: `recent-${index}`,
        text,
        type: 'recent' as const
      }));
      const popular = popularSearches.slice(0, 5).map((text, index) => ({
        id: `popular-${index}`,
        text,
        type: 'popular' as const
      }));
      return [...recent, ...popular];
    }

    return suggestions.filter(s =>
      s.text.toLowerCase().includes(debouncedQuery.toLowerCase()) ||
      (s.category && s.category.toLowerCase().includes(debouncedQuery.toLowerCase()))
    );
  }, [debouncedQuery, suggestions, recentSearches, popularSearches]);

  const handleSearch = useCallback((searchQuery?: string) => {
    const queryToSearch = searchQuery || query;
    if (queryToSearch.trim()) {
      const hasActiveFilters = Object.values(selectedFilters).some(arr => arr.length > 0);
      onSearch(queryToSearch.trim(), hasActiveFilters ? selectedFilters : undefined);
      setIsOpen(false);
    }
  }, [query, selectedFilters, onSearch]);

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    setQuery(suggestion.text);
    setIsOpen(false);
    if (onSuggestionClick) {
      onSuggestionClick(suggestion);
    } else {
      handleSearch(suggestion.text);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    setIsOpen(true);
    setActiveIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setActiveIndex(prev => Math.min(prev + 1, filteredSuggestions.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setActiveIndex(prev => Math.max(prev - 1, -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (activeIndex >= 0 && filteredSuggestions[activeIndex]) {
          handleSuggestionClick(filteredSuggestions[activeIndex]);
        } else {
          handleSearch();
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setActiveIndex(-1);
        break;
    }
  };

  const clearSearch = () => {
    setQuery('');
    setIsOpen(false);
    inputRef.current?.focus();
  };

  const clearFilters = () => {
    setSelectedFilters({});
  };

  const handleFilterChange = (filterId: string, values: string[]) => {
    setSelectedFilters(prev => ({
      ...prev,
      [filterId]: values
    }));
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setActiveIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const hasActiveFilters = Object.values(selectedFilters).some(arr => arr.length > 0);
  const totalActiveFilters = Object.values(selectedFilters).reduce((sum, arr) => sum + arr.length, 0);

  const getSuggestionIcon = (type: SearchSuggestion['type']) => {
    switch (type) {
      case 'recent':
        return <Clock className="w-4 h-4 text-gray-400" />;
      case 'popular':
        return <TrendingUp className="w-4 h-4 text-gray-400" />;
      default:
        return <Search className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div ref={searchRef} className={cn('relative w-full max-w-2xl', className)}>
      {/* Search Input */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="w-5 h-5 text-gray-400" />
        </div>

        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          disabled={isLoading}
        />

        <div className="absolute inset-y-0 right-0 flex items-center space-x-1 pr-3">
          {query && (
            <button
              type="button"
              onClick={clearSearch}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}

          {filters.length > 0 && (
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={cn(
                'text-gray-400 hover:text-gray-600 transition-colors',
                (hasActiveFilters || showFilters) && 'text-blue-600'
              )}
            >
              <Filter className="w-4 h-4" />
              {totalActiveFilters > 0 && (
                <span className="absolute -top-1 -right-1 bg-blue-600 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                  {totalActiveFilters}
                </span>
              )}
            </button>
          )}
        </div>

        {isLoading && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          </div>
        )}
      </div>

      {/* Filters */}
      {showFilters && filters.length > 0 && (
        <div className="mt-2 p-4 bg-white border border-gray-200 rounded-lg shadow-lg">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-700">Filters</h3>
            {hasActiveFilters && (
              <button
                type="button"
                onClick={clearFilters}
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                Clear all
              </button>
            )}
          </div>

          <div className="flex flex-wrap gap-2">
            {filters.map((filter) => (
              <FilterDropdown
                key={filter.id}
                filter={filter}
                selectedValues={selectedFilters[filter.id] || []}
                onSelectionChange={(values) => handleFilterChange(filter.id, values)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Suggestions Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto">
          {filteredSuggestions.length > 0 ? (
            <div className="py-2">
              {!query && recentSearches.length > 0 && (
                <div className="px-3 py-1 text-xs font-medium text-gray-500 uppercase tracking-wide">
                  Recent Searches
                </div>
              )}

              {filteredSuggestions.map((suggestion, index) => (
                <button
                  key={suggestion.id}
                  type="button"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className={cn(
                    'w-full px-3 py-2 text-left hover:bg-gray-50 flex items-center space-x-3',
                    activeIndex === index && 'bg-blue-50 text-blue-700'
                  )}
                >
                  {getSuggestionIcon(suggestion.type)}
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900 truncate">
                      {suggestion.text}
                    </div>
                    {'category' in suggestion && suggestion.category && (
                      <div className="text-xs text-gray-500">
                        in {suggestion.category}
                      </div>
                    )}
                  </div>
                  {'imageUrl' in suggestion && suggestion.imageUrl && (
                    <Image
                      src={suggestion.imageUrl}
                      alt=""
                      width={32}
                      height={32}
                      className="w-8 h-8 rounded object-cover"
                    />
                  )}
                </button>
              ))}
            </div>
          ) : query && !isLoading ? (
            <div className="px-3 py-4 text-center text-gray-500 text-sm">
              No suggestions found for &quot;{query}&quot;
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}

export default SearchAutocomplete;