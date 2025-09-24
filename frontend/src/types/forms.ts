/**
 * Form type definitions
 * Types for form data, validation, and UI states
 */

import { z } from 'zod';

// Login form
export const LoginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  password: z
    .string()
    .min(6, 'Password must be at least 6 characters long')
    .max(100, 'Password cannot exceed 100 characters'),
});

export type LoginFormData = z.infer<typeof LoginSchema>;

// Registration form
export const RegisterSchema = z
  .object({
    firstName: z
      .string()
      .min(2, 'First name must be at least 2 characters long')
      .max(50, 'First name cannot exceed 50 characters')
      .regex(/^[a-zA-Z\s'-]+$/, 'First name can only contain letters, spaces, hyphens, and apostrophes'),
    lastName: z
      .string()
      .min(2, 'Last name must be at least 2 characters long')
      .max(50, 'Last name cannot exceed 50 characters')
      .regex(/^[a-zA-Z\s'-]+$/, 'Last name can only contain letters, spaces, hyphens, and apostrophes'),
    email: z
      .string()
      .min(1, 'Email is required')
      .email('Please enter a valid email address'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters long')
      .max(100, 'Password cannot exceed 100 characters')
      .regex(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
        'Password must contain at least one lowercase letter, one uppercase letter, and one number'
      ),
    confirmPassword: z
      .string()
      .min(1, 'Please confirm your password'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

export type RegisterFormData = z.infer<typeof RegisterSchema>;

// Profile update form
export const ProfileUpdateSchema = z.object({
  firstName: z
    .string()
    .min(2, 'First name must be at least 2 characters long')
    .max(50, 'First name cannot exceed 50 characters'),
  lastName: z
    .string()
    .min(2, 'Last name must be at least 2 characters long')
    .max(50, 'Last name cannot exceed 50 characters'),
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
});

export type ProfileUpdateFormData = z.infer<typeof ProfileUpdateSchema>;

// Product search form
export const ProductSearchSchema = z.object({
  query: z.string().optional(),
  category: z.string().optional(),
  minPrice: z
    .number()
    .min(0, 'Minimum price cannot be negative')
    .optional(),
  maxPrice: z
    .number()
    .min(0, 'Maximum price cannot be negative')
    .optional(),
  inStock: z.boolean().optional(),
  sort: z.enum(['name', 'price', 'created_at']).optional(),
  order: z.enum(['asc', 'desc']).optional(),
}).refine((data) => {
  if (data.minPrice !== undefined && data.maxPrice !== undefined) {
    return data.minPrice <= data.maxPrice;
  }
  return true;
}, {
  message: 'Maximum price must be greater than or equal to minimum price',
  path: ['maxPrice'],
});

export type ProductSearchFormData = z.infer<typeof ProductSearchSchema>;

// Contact form
export const ContactSchema = z.object({
  name: z
    .string()
    .min(2, 'Name must be at least 2 characters long')
    .max(100, 'Name cannot exceed 100 characters'),
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  subject: z
    .string()
    .min(5, 'Subject must be at least 5 characters long')
    .max(200, 'Subject cannot exceed 200 characters'),
  message: z
    .string()
    .min(10, 'Message must be at least 10 characters long')
    .max(2000, 'Message cannot exceed 2000 characters'),
});

export type ContactFormData = z.infer<typeof ContactSchema>;

// Form UI states
export interface FormState<T = Record<string, unknown>> {
  data: T;
  errors: Record<string, string>;
  isSubmitting: boolean;
  isValid: boolean;
  isDirty: boolean;
  touchedFields: Record<string, boolean>;
}

export interface FormFieldProps {
  name: string;
  label: string;
  type?: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
  helperText?: string;
}

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface FormSelectProps extends FormFieldProps {
  options: SelectOption[];
  multiple?: boolean;
  searchable?: boolean;
}

// Form submission responses
export interface FormSubmissionResponse<T = unknown> {
  success: boolean;
  data?: T;
  errors?: Record<string, string>;
  message?: string;
}

// Validation error types
export interface ValidationError {
  field: string;
  message: string;
  code?: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

// Form hooks return types
export interface UseFormReturn<T> {
  register: (name: keyof T) => {
    name: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void;
    onBlur: () => void;
    value: T[keyof T] | undefined;
    error?: string;
  };
  handleSubmit: (onSubmit: (data: T) => void | Promise<void>) => (e: React.FormEvent) => Promise<void>;
  formState: FormState<T>;
  setValue: (name: keyof T, value: T[keyof T] | undefined) => void;
  clearErrors: () => void;
  reset: (data?: Partial<T>) => void;
}
