/**
 * FormField component
 * Enhanced form field wrapper with improved validation styling and animations
 */

'use client';

import React from 'react';
import { AlertCircle, CheckCircle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface FormFieldProps {
  children: React.ReactNode;
  label?: string;
  labelId?: string;
  error?: string;
  warning?: string;
  success?: string;
  helperText?: string;
  required?: boolean;
  className?: string;
  fieldClassName?: string;
  tooltip?: string;
}

export function FormField({
  children,
  label,
  labelId,
  error,
  warning,
  success,
  helperText,
  required,
  className,
  fieldClassName,
  tooltip
}: FormFieldProps) {
  const fieldId = labelId || `field-${Math.random().toString(36).substring(2, 9)}`;
  const hasError = !!error;
  const hasWarning = !!warning && !hasError;
  const hasSuccess = !!success && !hasError && !hasWarning;

  return (
    <div className={cn('space-y-2', className)}>
      {/* Label */}
      {label && (
        <div className="flex items-center justify-between">
          <label
            htmlFor={fieldId}
            className={cn(
              'text-sm font-medium transition-colors',
              hasError
                ? 'text-red-700'
                : hasWarning
                ? 'text-yellow-700'
                : hasSuccess
                ? 'text-green-700'
                : 'text-gray-700'
            )}
          >
            {label}
            {required && <span className="ml-1 text-red-500">*</span>}
          </label>
          {tooltip && (
            <div className="relative group">
              <Info className="w-4 h-4 text-gray-400 hover:text-gray-600 cursor-help" />
              <div className="absolute right-0 bottom-full mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-10">
                {tooltip}
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900 rotate-45"></div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Field Container */}
      <div className={cn('relative', fieldClassName)}>
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child)) {
            const childProps = child.props as { className?: string };
            return React.cloneElement(child, {
              id: fieldId,
              'aria-invalid': hasError ? 'true' : 'false',
              'aria-describedby': error
                ? `${fieldId}-error`
                : warning
                ? `${fieldId}-warning`
                : success
                ? `${fieldId}-success`
                : helperText
                ? `${fieldId}-helper`
                : undefined,
              className: cn(
                childProps.className,
                'transition-all duration-200',
                hasError
                  ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20'
                  : hasWarning
                  ? 'border-yellow-300 focus:border-yellow-500 focus:ring-yellow-500/20'
                  : hasSuccess
                  ? 'border-green-300 focus:border-green-500 focus:ring-green-500/20'
                  : 'focus:ring-blue-500/20'
              ),
            } as Partial<typeof child.props>);
          }
          return child;
        })}

        {/* Field Status Icon */}
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
          {hasError && (
            <AlertCircle className="w-4 h-4 text-red-500 animate-fade-in-scale" />
          )}
          {hasWarning && (
            <AlertCircle className="w-4 h-4 text-yellow-500 animate-fade-in-scale" />
          )}
          {hasSuccess && (
            <CheckCircle className="w-4 h-4 text-green-500 animate-fade-in-scale" />
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="min-h-[1.25rem]">
        {error && (
          <div
            id={`${fieldId}-error`}
            className="text-sm text-red-600 flex items-start animate-fade-in-up"
          >
            <AlertCircle className="w-4 h-4 mt-0.5 mr-2 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
        {warning && !error && (
          <div
            id={`${fieldId}-warning`}
            className="text-sm text-yellow-600 flex items-start animate-fade-in-up"
          >
            <AlertCircle className="w-4 h-4 mt-0.5 mr-2 flex-shrink-0" />
            <span>{warning}</span>
          </div>
        )}
        {success && !error && !warning && (
          <div
            id={`${fieldId}-success`}
            className="text-sm text-green-600 flex items-start animate-fade-in-up"
          >
            <CheckCircle className="w-4 h-4 mt-0.5 mr-2 flex-shrink-0" />
            <span>{success}</span>
          </div>
        )}
        {helperText && !error && !warning && !success && (
          <div
            id={`${fieldId}-helper`}
            className="text-sm text-gray-500"
          >
            {helperText}
          </div>
        )}
      </div>
    </div>
  );
}

// Form Section Component
export interface FormSectionProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  className?: string;
}

export function FormSection({
  children,
  title,
  subtitle,
  className
}: FormSectionProps) {
  return (
    <div className={cn('space-y-6', className)}>
      {(title || subtitle) && (
        <div className="border-b border-gray-200 pb-4">
          {title && (
            <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          )}
          {subtitle && (
            <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
          )}
        </div>
      )}
      <div className="space-y-4">{children}</div>
    </div>
  );
}

// Form Actions Component
export interface FormActionsProps {
  children: React.ReactNode;
  className?: string;
  justify?: 'start' | 'end' | 'center' | 'between';
  sticky?: boolean;
}

export function FormActions({
  children,
  className,
  justify = 'end',
  sticky = false
}: FormActionsProps) {
  const justifyClass = {
    start: 'justify-start',
    end: 'justify-end',
    center: 'justify-center',
    between: 'justify-between'
  }[justify];

  return (
    <div
      className={cn(
        'flex items-center space-x-4 pt-6 border-t border-gray-200',
        justifyClass,
        sticky && 'sticky bottom-0 bg-white/80 backdrop-blur-sm',
        className
      )}
    >
      {children}
    </div>
  );
}

// Form Container Component
export interface FormContainerProps {
  children: React.ReactNode;
  onSubmit?: (e: React.FormEvent) => void;
  className?: string;
  card?: boolean;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';
}

export function FormContainer({
  children,
  onSubmit,
  className,
  card = true,
  maxWidth = 'md'
}: FormContainerProps) {
  const maxWidthClass = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    full: 'max-w-full'
  }[maxWidth];

  return (
    <div className={cn('mx-auto w-full', maxWidthClass)}>
      <form
        onSubmit={onSubmit}
        className={cn(
          card && 'bg-white rounded-lg shadow-md border border-gray-200 p-6',
          'space-y-6',
          className
        )}
        noValidate
      >
        {children}
      </form>
    </div>
  );
}

// Checkbox Field Component
export interface CheckboxFieldProps {
  label: string;
  description?: string;
  error?: string;
  required?: boolean;
  className?: string;
  inputProps?: React.InputHTMLAttributes<HTMLInputElement>;
}

export function CheckboxField({
  label,
  description,
  error,
  required,
  className,
  inputProps
}: CheckboxFieldProps) {
  const fieldId = `checkbox-${Math.random().toString(36).substring(2, 9)}`;

  return (
    <div className={cn('space-y-2', className)}>
      <div className="relative flex items-start">
        <div className="flex items-center h-5">
          <input
            {...inputProps}
            id={fieldId}
            type="checkbox"
            className={cn(
              'w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-offset-0 transition-colors',
              error && 'border-red-500 focus:ring-red-500',
              inputProps?.className
            )}
            aria-describedby={error ? `${fieldId}-error` : undefined}
          />
        </div>
        <div className="ml-3 text-sm">
          <label
            htmlFor={fieldId}
            className={cn(
              'font-medium cursor-pointer transition-colors',
              error ? 'text-red-700' : 'text-gray-700'
            )}
          >
            {label}
            {required && <span className="ml-1 text-red-500">*</span>}
          </label>
          {description && (
            <p className="text-gray-500 mt-1">{description}</p>
          )}
        </div>
      </div>

      {error && (
        <div
          id={`${fieldId}-error`}
          className="text-sm text-red-600 flex items-start animate-fade-in-up ml-7"
        >
          <AlertCircle className="w-4 h-4 mt-0.5 mr-2 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}

// Radio Group Field Component
export interface RadioOption {
  value: string;
  label: string;
  description?: string;
}

export interface RadioGroupFieldProps {
  name: string;
  label?: string;
  options: RadioOption[];
  value?: string;
  onChange?: (value: string) => void;
  error?: string;
  required?: boolean;
  className?: string;
}

export function RadioGroupField({
  name,
  label,
  options,
  value,
  onChange,
  error,
  required,
  className
}: RadioGroupFieldProps) {
  return (
    <div className={cn('space-y-3', className)}>
      {label && (
        <div className="text-sm font-medium text-gray-700">
          {label}
          {required && <span className="ml-1 text-red-500">*</span>}
        </div>
      )}

      <div className="space-y-2">
        {options.map((option) => {
          const optionId = `${name}-${option.value}`;
          return (
            <div key={option.value} className="relative flex items-start">
              <div className="flex items-center h-5">
                <input
                  id={optionId}
                  name={name}
                  type="radio"
                  value={option.value}
                  checked={value === option.value}
                  onChange={(e) => onChange?.(e.target.value)}
                  className={cn(
                    'w-4 h-4 border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-offset-0 transition-colors',
                    error && 'border-red-500 focus:ring-red-500'
                  )}
                />
              </div>
              <div className="ml-3 text-sm">
                <label
                  htmlFor={optionId}
                  className={cn(
                    'font-medium cursor-pointer transition-colors',
                    error ? 'text-red-700' : 'text-gray-700'
                  )}
                >
                  {option.label}
                </label>
                {option.description && (
                  <p className="text-gray-500 mt-1">{option.description}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {error && (
        <div className="text-sm text-red-600 flex items-start animate-fade-in-up">
          <AlertCircle className="w-4 h-4 mt-0.5 mr-2 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}

export default FormField;