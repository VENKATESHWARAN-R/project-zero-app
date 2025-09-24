/**
 * Quantity Control Component
 * Reusable quantity input with increment/decrement controls
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Plus, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface QuantityControlProps {
  value: number;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  loading?: boolean;
  onChange: (value: number) => void;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  label?: string;
}

export function QuantityControl({
  value,
  min = 1,
  max = 99,
  step = 1,
  disabled = false,
  loading = false,
  onChange,
  className,
  size = 'md',
  showLabel = false,
  label = 'Quantity'
}: QuantityControlProps) {
  const [displayValue, setDisplayValue] = useState(value.toString());
  const [isEditing, setIsEditing] = useState(false);

  // Update display value when prop value changes
  useEffect(() => {
    if (!isEditing) {
      setDisplayValue(value.toString());
    }
  }, [value, isEditing]);

  const sizeStyles = {
    sm: {
      container: 'h-8',
      button: 'w-6 h-6',
      input: 'w-10 text-sm',
      icon: 'w-3 h-3'
    },
    md: {
      container: 'h-10',
      button: 'w-8 h-8',
      input: 'w-12 text-base',
      icon: 'w-4 h-4'
    },
    lg: {
      container: 'h-12',
      button: 'w-10 h-10',
      input: 'w-16 text-lg',
      icon: 'w-5 h-5'
    }
  };

  const styles = sizeStyles[size];

  const handleDecrement = () => {
    const newValue = Math.max(min, value - step);
    if (newValue !== value) {
      onChange(newValue);
    }
  };

  const handleIncrement = () => {
    const newValue = Math.min(max, value + step);
    if (newValue !== value) {
      onChange(newValue);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    setDisplayValue(inputValue);

    // Allow empty string while editing
    if (inputValue === '') return;

    const numericValue = parseInt(inputValue, 10);
    if (!isNaN(numericValue)) {
      const clampedValue = Math.max(min, Math.min(max, numericValue));
      if (clampedValue !== value) {
        onChange(clampedValue);
      }
    }
  };

  const handleInputFocus = () => {
    setIsEditing(true);
  };

  const handleInputBlur = () => {
    setIsEditing(false);

    const numericValue = parseInt(displayValue, 10);
    if (isNaN(numericValue) || displayValue === '') {
      setDisplayValue(value.toString());
    } else {
      const clampedValue = Math.max(min, Math.min(max, numericValue));
      setDisplayValue(clampedValue.toString());
      if (clampedValue !== value) {
        onChange(clampedValue);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.currentTarget.blur();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      handleIncrement();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      handleDecrement();
    }
  };

  const canDecrement = !disabled && !loading && value > min;
  const canIncrement = !disabled && !loading && value < max;

  return (
    <div className={cn('space-y-2', className)}>
      {showLabel && (
        <label className="text-sm font-medium text-gray-700">
          {label}
        </label>
      )}

      <div className={cn(
        'flex items-center border border-gray-300 rounded-lg bg-white',
        styles.container,
        disabled && 'opacity-50 cursor-not-allowed',
        'focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500'
      )}>
        {/* Decrement Button */}
        <button
          type="button"
          onClick={handleDecrement}
          disabled={!canDecrement}
          className={cn(
            'flex items-center justify-center text-gray-600 hover:text-gray-800 hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent rounded-l-lg',
            styles.button
          )}
          aria-label="Decrease quantity"
        >
          <Minus className={styles.icon} />
        </button>

        {/* Input Field */}
        <input
          type="text"
          value={loading ? '...' : displayValue}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          onKeyDown={handleKeyDown}
          disabled={disabled || loading}
          className={cn(
            'text-center border-0 focus:outline-none focus:ring-0 font-medium bg-transparent',
            styles.input
          )}
          min={min}
          max={max}
          aria-label="Quantity"
        />

        {/* Increment Button */}
        <button
          type="button"
          onClick={handleIncrement}
          disabled={!canIncrement}
          className={cn(
            'flex items-center justify-center text-gray-600 hover:text-gray-800 hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent rounded-r-lg',
            styles.button
          )}
          aria-label="Increase quantity"
        >
          <Plus className={styles.icon} />
        </button>
      </div>

      {/* Helper Text */}
      {(min > 1 || max < 99) && (
        <div className="text-xs text-gray-500">
          Min: {min}, Max: {max}
        </div>
      )}
    </div>
  );
}

// Inline Quantity Control (more compact)
export interface InlineQuantityControlProps extends Omit<QuantityControlProps, 'showLabel' | 'label' | 'className'> {
  className?: string;
}

export function InlineQuantityControl({
  value,
  min = 1,
  max = 99,
  step = 1,
  disabled = false,
  loading = false,
  onChange,
  className,
  size = 'md'
}: InlineQuantityControlProps) {
  const sizeStyles = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-2',
    lg: 'text-base px-4 py-2'
  };

  const handleDecrement = () => {
    const newValue = Math.max(min, value - step);
    if (newValue !== value) {
      onChange(newValue);
    }
  };

  const handleIncrement = () => {
    const newValue = Math.min(max, value + step);
    if (newValue !== value) {
      onChange(newValue);
    }
  };

  const canDecrement = !disabled && !loading && value > min;
  const canIncrement = !disabled && !loading && value < max;

  return (
    <div className={cn('flex items-center space-x-1', className)}>
      <button
        type="button"
        onClick={handleDecrement}
        disabled={!canDecrement}
        className={cn(
          'flex items-center justify-center w-8 h-8 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed',
          sizeStyles[size]
        )}
        aria-label="Decrease quantity"
      >
        <Minus className="w-4 h-4" />
      </button>

      <span className={cn(
        'font-medium text-gray-900 min-w-[2rem] text-center',
        sizeStyles[size]
      )}>
        {loading ? '...' : value}
      </span>

      <button
        type="button"
        onClick={handleIncrement}
        disabled={!canIncrement}
        className={cn(
          'flex items-center justify-center w-8 h-8 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed',
          sizeStyles[size]
        )}
        aria-label="Increase quantity"
      >
        <Plus className="w-4 h-4" />
      </button>
    </div>
  );
}

// Quantity Selector with preset options
export interface QuantitySelectorProps {
  value: number;
  options: number[];
  disabled?: boolean;
  onChange: (value: number) => void;
  className?: string;
}

export function QuantitySelector({
  value,
  options,
  disabled = false,
  onChange,
  className
}: QuantitySelectorProps) {
  return (
    <div className={cn('space-y-2', className)}>
      <label className="text-sm font-medium text-gray-700">
        Quantity
      </label>
      <select
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value, 10))}
        disabled={disabled}
        className={cn(
          'block w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed',
          className
        )}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
}

export default QuantityControl;