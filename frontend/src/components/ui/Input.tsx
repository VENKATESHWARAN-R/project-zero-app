/**
 * Input component
 * Reusable input component with various types and validation states
 */

import React, { forwardRef, useState } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { Eye, EyeOff, AlertCircle, CheckCircle, Search, X } from 'lucide-react';
import { cn } from '@/lib/utils';

const inputVariants = cva(
  'flex w-full rounded-lg border bg-transparent px-3 py-2 text-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'border-gray-300 focus-visible:ring-blue-500',
        error: 'border-red-500 focus-visible:ring-red-500',
        success: 'border-green-500 focus-visible:ring-green-500',
      },
      size: {
        default: 'h-10',
        sm: 'h-9 px-2 text-xs',
        lg: 'h-11 px-4',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> {
  label?: string;
  error?: string;
  success?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  clearable?: boolean;
  onClear?: () => void;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({
    className,
    variant,
    size,
    type = 'text',
    label,
    error,
    success,
    helperText,
    leftIcon,
    rightIcon,
    clearable = false,
    onClear,
    id,
    value,
    ...props
  }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substring(2, 9)}`;
    const hasError = !!error;
    const hasSuccess = !!success && !hasError;
    const computedVariant = hasError ? 'error' : hasSuccess ? 'success' : variant;

    const showClearButton = clearable && value && typeof value === 'string' && value.length > 0;

    return (
      <div className="space-y-2">
        {label && (
          <label
            htmlFor={inputId}
            className="text-sm font-medium text-gray-700"
          >
            {label}
          </label>
        )}

        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
              {leftIcon}
            </div>
          )}

          <input
            type={type}
            className={cn(
              inputVariants({ variant: computedVariant, size, className }),
              leftIcon && 'pl-10',
              (rightIcon || showClearButton || hasError || hasSuccess) && 'pr-10'
            )}
            ref={ref}
            id={inputId}
            value={value}
            {...props}
          />

          {/* Right side icons */}
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
            {showClearButton && (
              <button
                type="button"
                onClick={onClear}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            )}

            {hasError && (
              <AlertCircle className="w-4 h-4 text-red-500" />
            )}

            {hasSuccess && (
              <CheckCircle className="w-4 h-4 text-green-500" />
            )}

            {rightIcon && !showClearButton && !hasError && !hasSuccess && (
              <span className="text-gray-400">{rightIcon}</span>
            )}
          </div>
        </div>

        {/* Helper text, error, or success message */}
        {(error || success || helperText) && (
          <div className="text-sm">
            {error && (
              <p className="text-red-600 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {error}
              </p>
            )}
            {success && !error && (
              <p className="text-green-600 flex items-center">
                <CheckCircle className="w-4 h-4 mr-1" />
                {success}
              </p>
            )}
            {helperText && !error && !success && (
              <p className="text-gray-500">{helperText}</p>
            )}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

// Password Input Component
export interface PasswordInputProps extends Omit<InputProps, 'type' | 'rightIcon'> {
  showToggle?: boolean;
}

export const PasswordInput = forwardRef<HTMLInputElement, PasswordInputProps>(
  ({ showToggle = true, ...props }, ref) => {
    const [showPassword, setShowPassword] = useState(false);

    const togglePassword = () => {
      setShowPassword(prev => !prev);
    };

    return (
      <Input
        {...props}
        ref={ref}
        type={showPassword ? 'text' : 'password'}
        rightIcon={
          showToggle ? (
            <button
              type="button"
              onClick={togglePassword}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          ) : undefined
        }
      />
    );
  }
);

PasswordInput.displayName = 'PasswordInput';

// Search Input Component
export interface SearchInputProps extends Omit<InputProps, 'leftIcon' | 'type'> {
  onSearch?: (value: string) => void;
  placeholder?: string;
}

export const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(
  ({
    onSearch,
    placeholder = 'Search...',
    clearable = true,
    onChange,
    onKeyDown,
    ...props
  }, ref) => {
    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter' && onSearch) {
        onSearch(e.currentTarget.value);
      }
      onKeyDown?.(e);
    };

    return (
      <Input
        {...props}
        ref={ref}
        type="search"
        placeholder={placeholder}
        leftIcon={<Search className="w-4 h-4" />}
        clearable={clearable}
        onChange={onChange}
        onKeyDown={handleKeyDown}
      />
    );
  }
);

SearchInput.displayName = 'SearchInput';

// Textarea Component
export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  success?: string;
  helperText?: string;
  resize?: 'none' | 'both' | 'horizontal' | 'vertical';
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({
    className,
    label,
    error,
    success,
    helperText,
    resize = 'vertical',
    id,
    ...props
  }, ref) => {
    const textareaId = id || `textarea-${Math.random().toString(36).substring(2, 9)}`;
    const hasError = !!error;
    const hasSuccess = !!success && !hasError;

    const resizeClass = {
      none: 'resize-none',
      both: 'resize',
      horizontal: 'resize-x',
      vertical: 'resize-y',
    }[resize];

    return (
      <div className="space-y-2">
        {label && (
          <label
            htmlFor={textareaId}
            className="text-sm font-medium text-gray-700"
          >
            {label}
          </label>
        )}

        <textarea
          className={cn(
            'flex min-h-[80px] w-full rounded-lg border bg-transparent px-3 py-2 text-sm transition-colors placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
            hasError
              ? 'border-red-500 focus-visible:ring-red-500'
              : hasSuccess
                ? 'border-green-500 focus-visible:ring-green-500'
                : 'border-gray-300 focus-visible:ring-blue-500',
            resizeClass,
            className
          )}
          ref={ref}
          id={textareaId}
          {...props}
        />

        {/* Helper text, error, or success message */}
        {(error || success || helperText) && (
          <div className="text-sm">
            {error && (
              <p className="text-red-600 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {error}
              </p>
            )}
            {success && !error && (
              <p className="text-green-600 flex items-center">
                <CheckCircle className="w-4 h-4 mr-1" />
                {success}
              </p>
            )}
            {helperText && !error && !success && (
              <p className="text-gray-500">{helperText}</p>
            )}
          </div>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

// Input Group Component
export interface InputGroupProps {
  children: React.ReactNode;
  className?: string;
}

export function InputGroup({ children, className }: InputGroupProps) {
  return (
    <div className={cn('flex', className)}>
      {React.Children.map(children, (child, index) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as React.ReactElement<any>, {
            className: cn(
              (child.props as any)?.className,
              index === 0 ? 'rounded-r-none' : 'rounded-l-none border-l-0',
              'focus-visible:z-10'
            ),
          });
        }
        return child;
      })}
    </div>
  );
}

// File Input Component
export interface FileInputProps extends Omit<InputProps, 'type'> {
  accept?: string;
  multiple?: boolean;
  maxSize?: number;
  onFileSelect?: (files: FileList | null) => void;
}

export const FileInput = forwardRef<HTMLInputElement, FileInputProps>(
  ({
    accept,
    multiple,
    maxSize,
    onFileSelect,
    onChange,
    label,
    error,
    helperText,
    ...props
  }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;

      // Validate file size if maxSize is provided
      if (maxSize && files) {
        for (let i = 0; i < files.length; i++) {
          if (files[i].size > maxSize) {
            console.error(`File ${files[i].name} exceeds maximum size of ${maxSize} bytes`);
            return;
          }
        }
      }

      onFileSelect?.(files);
      onChange?.(e);
    };

    return (
      <Input
        {...props}
        ref={ref}
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleChange}
        label={label}
        error={error}
        helperText={helperText}
      />
    );
  }
);

FileInput.displayName = 'FileInput';

export { Input, inputVariants };
export default Input;