/**
 * Toast notification component
 * Provides toast notifications for user feedback
 */

'use client';

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  title?: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastContextType {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  removeAllToasts: () => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

// Toast Provider Component
export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToastRef = useRef<(id: string) => void>(() => {});
  
  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);
  
  // Update the ref whenever removeToast changes
  useEffect(() => {
    removeToastRef.current = removeToast;
  }, [removeToast]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const newToast: Toast = {
      id,
      duration: 5000, // Default 5 seconds
      ...toast,
    };

    setToasts(prev => [...prev, newToast]);

    // Auto remove toast after duration
    if (newToast.duration && newToast.duration > 0) {
      setTimeout(() => {
        removeToastRef.current(id);
      }, newToast.duration);
    }

    return id;
  }, []);

  const removeAllToasts = useCallback(() => {
    setToasts([]);
  }, []);

  return (
    <ToastContext.Provider
      value={{
        toasts,
        addToast,
        removeToast,
        removeAllToasts,
      }}
    >
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  );
}

// Hook to use toast
export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }

  const { addToast, removeToast, removeAllToasts } = context;

  return {
    toast: addToast,
    dismiss: removeToast,
    dismissAll: removeAllToasts,
    success: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) =>
      addToast({ type: 'success', message, ...options }),
    error: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) =>
      addToast({ type: 'error', message, ...options }),
    warning: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) =>
      addToast({ type: 'warning', message, ...options }),
    info: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) =>
      addToast({ type: 'info', message, ...options }),
  };
}

// Toast Container Component
function ToastContainer() {
  const { toasts } = useContext(ToastContext) || { toasts: [] };

  return (
    <div
      className="fixed top-4 right-4 z-50 flex flex-col space-y-2 pointer-events-none"
      aria-live="polite"
      aria-label="Notifications"
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} />
      ))}
    </div>
  );
}

// Individual Toast Item Component
interface ToastItemProps {
  toast: Toast;
}

function ToastItem({ toast }: ToastItemProps) {
  const { removeToast } = useContext(ToastContext)!;
  const [isVisible, setIsVisible] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);

  useEffect(() => {
    // Trigger enter animation
    setTimeout(() => setIsVisible(true), 10);
  }, []);

  const handleRemove = () => {
    setIsRemoving(true);
    setTimeout(() => {
      removeToast(toast.id);
    }, 300); // Match the exit animation duration
  };

  const iconMap = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info,
  };

  const colorMap = {
    success: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      icon: 'text-green-400',
      text: 'text-green-800',
      title: 'text-green-900',
    },
    error: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      icon: 'text-red-400',
      text: 'text-red-800',
      title: 'text-red-900',
    },
    warning: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      icon: 'text-yellow-400',
      text: 'text-yellow-800',
      title: 'text-yellow-900',
    },
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      icon: 'text-blue-400',
      text: 'text-blue-800',
      title: 'text-blue-900',
    },
  };

  const Icon = iconMap[toast.type];
  const colors = colorMap[toast.type];

  return (
    <div
      className={cn(
        'pointer-events-auto w-full max-w-sm overflow-hidden rounded-lg border shadow-lg transition-all duration-300 ease-in-out',
        colors.bg,
        colors.border,
        isVisible && !isRemoving
          ? 'translate-x-0 opacity-100'
          : 'translate-x-full opacity-0'
      )}
      role="alert"
    >
      <div className="p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <Icon className={cn('h-6 w-6', colors.icon)} aria-hidden="true" />
          </div>
          <div className="ml-3 w-0 flex-1">
            {toast.title && (
              <h3 className={cn('text-sm font-medium', colors.title)}>
                {toast.title}
              </h3>
            )}
            <p className={cn('text-sm', colors.text, toast.title ? 'mt-1' : '')}>
              {toast.message}
            </p>
            {toast.action && (
              <div className="mt-3">
                <button
                  type="button"
                  className={cn(
                    'text-sm font-medium underline hover:no-underline focus:outline-none',
                    colors.title
                  )}
                  onClick={toast.action.onClick}
                >
                  {toast.action.label}
                </button>
              </div>
            )}
          </div>
          <div className="ml-4 flex flex-shrink-0">
            <button
              type="button"
              className={cn(
                'inline-flex rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2',
                'text-gray-400 hover:text-gray-500 focus:ring-gray-500'
              )}
              onClick={handleRemove}
            >
              <span className="sr-only">Close</span>
              <X className="h-5 w-5" aria-hidden="true" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Utility functions for common toast patterns
export const createToast = {
  success: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => ({
    type: 'success' as const,
    message,
    ...options,
  }),
  error: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => ({
    type: 'error' as const,
    message,
    ...options,
  }),
  warning: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => ({
    type: 'warning' as const,
    message,
    ...options,
  }),
  info: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => ({
    type: 'info' as const,
    message,
    ...options,
  }),
};

// Toast API type for external usage
interface ToastAPI {
  toast: (toast: Omit<Toast, 'id'>) => string;
  dismiss: (id: string) => void;
  dismissAll: () => void;
  success: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => void;
  error: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => void;
  warning: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => void;
  info: (message: string, options?: Partial<Omit<Toast, 'id' | 'type' | 'message'>>) => void;
}

// Promise-based toast for async operations
export const promiseToast = {
  loading: (toast: ToastAPI, promise: Promise<unknown>, messages: {
    loading: string;
    success: string;
    error: string;
  }) => {
    const loadingId = toast.info(messages.loading, { duration: 0 });

    return promise
      .then((result) => {
        toast.dismiss(loadingId);
        toast.success(messages.success);
        return result;
      })
      .catch((error) => {
        toast.dismiss(loadingId);
        toast.error(messages.error);
        throw error;
      });
  },
};

// Export default hook for convenience
export default useToast;