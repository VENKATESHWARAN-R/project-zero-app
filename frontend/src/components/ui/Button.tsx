/**
 * Button component
 * Reusable button component with multiple variants and sizes
 */

import React, { forwardRef } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import { ButtonLoading } from './Loading';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-lg font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background',
  {
    variants: {
      variant: {
        default:
          'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 shadow-sm',
        destructive:
          'bg-red-600 text-white hover:bg-red-700 active:bg-red-800 shadow-sm',
        outline:
          'border border-gray-300 bg-transparent text-gray-700 hover:bg-gray-50 active:bg-gray-100',
        secondary:
          'bg-gray-100 text-gray-900 hover:bg-gray-200 active:bg-gray-300',
        ghost:
          'text-gray-700 hover:bg-gray-100 active:bg-gray-200',
        link:
          'text-blue-600 underline-offset-4 hover:underline',
        success:
          'bg-green-600 text-white hover:bg-green-700 active:bg-green-800 shadow-sm',
        warning:
          'bg-yellow-600 text-white hover:bg-yellow-700 active:bg-yellow-800 shadow-sm',
      },
      size: {
        default: 'h-10 py-2 px-4 text-sm',
        sm: 'h-9 px-3 text-sm',
        lg: 'h-11 px-8 text-base',
        xl: 'h-12 px-10 text-base',
        icon: 'h-10 w-10',
      },
      fullWidth: {
        true: 'w-full',
        false: 'w-auto',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
      fullWidth: false,
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({
    className,
    variant,
    size,
    fullWidth,
    loading = false,
    leftIcon,
    rightIcon,
    children,
    disabled,
    ...props
  }, ref) => {
    const isDisabled = disabled || loading;

    return (
      <button
        className={cn(buttonVariants({ variant, size, fullWidth, className }))}
        ref={ref}
        disabled={isDisabled}
        {...props}
      >
        {loading && <ButtonLoading size={size === 'sm' ? 'sm' : 'md'} />}
        {!loading && leftIcon && (
          <span className={cn('mr-2', size === 'icon' && 'mr-0')}>
            {leftIcon}
          </span>
        )}
        {size !== 'icon' && children}
        {!loading && rightIcon && (
          <span className={cn('ml-2', size === 'icon' && 'ml-0')}>
            {rightIcon}
          </span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

// Button Group Component
export interface ButtonGroupProps {
  children: React.ReactNode;
  className?: string;
  size?: 'sm' | 'default' | 'lg';
  variant?: 'default' | 'outline';
  orientation?: 'horizontal' | 'vertical';
}

export function ButtonGroup({
  children,
  className,
  size = 'default',
  variant = 'outline',
  orientation = 'horizontal',
}: ButtonGroupProps) {
  return (
    <div
      className={cn(
        'inline-flex',
        orientation === 'horizontal' ? 'flex-row' : 'flex-col',
        '[&>button]:rounded-none',
        '[&>button:first-child]:rounded-l-lg',
        '[&>button:last-child]:rounded-r-lg',
        orientation === 'vertical' && [
          '[&>button:first-child]:rounded-t-lg [&>button:first-child]:rounded-l-none',
          '[&>button:last-child]:rounded-b-lg [&>button:last-child]:rounded-r-none',
        ],
        variant === 'outline' && [
          '[&>button:not(:last-child)]:border-r-0',
          orientation === 'vertical' && '[&>button:not(:last-child)]:border-b-0 [&>button:not(:last-child)]:border-r',
        ],
        className
      )}
    >
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child) && child.type === Button) {
          return React.cloneElement(child as React.ReactElement<ButtonProps>, {
            size,
            variant,
          });
        }
        return child;
      })}
    </div>
  );
}

// Icon Button Component
export interface IconButtonProps extends Omit<ButtonProps, 'leftIcon' | 'rightIcon' | 'children'> {
  icon: React.ReactNode;
  'aria-label': string;
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ icon, ...props }, ref) => {
    return (
      <Button
        ref={ref}
        size="icon"
        {...props}
      >
        {icon}
      </Button>
    );
  }
);

IconButton.displayName = 'IconButton';

// Social Button Component
export interface SocialButtonProps extends Omit<ButtonProps, 'variant'> {
  provider: 'google' | 'facebook' | 'twitter' | 'github' | 'apple';
}

const socialIcons = {
  google: (
    <svg className="w-5 h-5" viewBox="0 0 24 24">
      <path
        fill="currentColor"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="currentColor"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="currentColor"
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
      />
      <path
        fill="currentColor"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      />
    </svg>
  ),
  facebook: (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
    </svg>
  ),
  twitter: (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
      <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
    </svg>
  ),
  github: (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
    </svg>
  ),
  apple: (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12.017 0C8.396 0 8.025.038 7.706.147c-.356.123-.64.27-.856.404-.216.134-.388.248-.53.335-.142.087-.248.134-.291.154C5.677 1.26 5.52 1.378 5.378 1.5c-.142.122-.248.233-.316.335-.068.102-.104.199-.104.291v.058c0 .058.019.104.058.133.038.029.104.044.199.044h.116c.174 0 .348-.015.522-.044.174-.029.335-.073.483-.133.148-.06.276-.142.386-.248.11-.105.199-.234.267-.386.068-.152.116-.32.145-.502.029-.182.044-.376.044-.581C7.177.773 7.177.682 7.177.552 7.177.421 7.177.306 7.177.204 7.177.102 7.177.029 7.177 0h4.84z" />
    </svg>
  ),
};

const socialColors = {
  google: 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50',
  facebook: 'bg-blue-600 text-white hover:bg-blue-700',
  twitter: 'bg-blue-400 text-white hover:bg-blue-500',
  github: 'bg-gray-900 text-white hover:bg-gray-800',
  apple: 'bg-black text-white hover:bg-gray-900',
};

export const SocialButton = forwardRef<HTMLButtonElement, SocialButtonProps>(
  ({ provider, children, className, ...props }, ref) => {
    return (
      <Button
        ref={ref}
        className={cn(socialColors[provider], className)}
        leftIcon={socialIcons[provider]}
        {...props}
      >
        {children}
      </Button>
    );
  }
);

SocialButton.displayName = 'SocialButton';

export { Button, buttonVariants };
export default Button;