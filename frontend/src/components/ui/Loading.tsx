/**
 * Loading spinner component
 * Provides consistent loading indicators throughout the app
 */

import { cn } from '@/lib/utils';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'white' | 'gray';
  className?: string;
  text?: string;
  fullScreen?: boolean;
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
  xl: 'w-12 h-12',
};

const colorClasses = {
  primary: 'text-blue-600',
  secondary: 'text-gray-600',
  white: 'text-white',
  gray: 'text-gray-400',
};

export function LoadingSpinner({
  size = 'md',
  color = 'primary',
  className,
  ...props
}: Omit<LoadingProps, 'text' | 'fullScreen'>) {
  return (
    <svg
      className={cn(
        'animate-spin',
        sizeClasses[size],
        colorClasses[color],
        className
      )}
      fill="none"
      viewBox="0 0 24 24"
      {...props}
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

export function LoadingDots({
  size = 'md',
  color = 'primary',
  className
}: Omit<LoadingProps, 'text' | 'fullScreen'>) {
  const dotSize = size === 'sm' ? 'w-2 h-2' : size === 'lg' ? 'w-4 h-4' : 'w-3 h-3';

  return (
    <div className={cn('flex space-x-1', className)}>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={cn(
            'rounded-full animate-pulse',
            dotSize,
            colorClasses[color].replace('text-', 'bg-')
          )}
          style={{
            animationDelay: `${i * 0.15}s`,
            animationDuration: '0.6s',
          }}
        />
      ))}
    </div>
  );
}

export function LoadingBars({
  size = 'md',
  color = 'primary',
  className
}: Omit<LoadingProps, 'text' | 'fullScreen'>) {
  const barHeight = size === 'sm' ? 'h-6' : size === 'lg' ? 'h-12' : 'h-8';
  const barWidth = size === 'sm' ? 'w-1' : size === 'lg' ? 'w-2' : 'w-1.5';

  return (
    <div className={cn('flex items-end space-x-1', className)}>
      {[0, 1, 2, 3, 4].map((i) => (
        <div
          key={i}
          className={cn(
            'animate-pulse',
            barWidth,
            barHeight,
            colorClasses[color].replace('text-', 'bg-')
          )}
          style={{
            animationDelay: `${i * 0.1}s`,
            animationDuration: '1s',
            transform: 'scaleY(0.4)',
            transformOrigin: 'bottom',
          }}
        />
      ))}
    </div>
  );
}

export function LoadingSkeleton({
  className,
  lines = 1,
  ...props
}: {
  className?: string;
  lines?: number;
}) {
  return (
    <div className={cn('animate-pulse', className)} {...props}>
      {Array.from({ length: lines }, (_, i) => (
        <div
          key={i}
          className={cn(
            'bg-gray-200 rounded',
            i === lines - 1 ? 'w-3/4' : 'w-full',
            lines > 1 ? 'h-4 mb-2' : 'h-4'
          )}
        />
      ))}
    </div>
  );
}

export function Loading({
  size = 'md',
  color = 'primary',
  className,
  text,
  fullScreen = false,
}: LoadingProps) {
  const content = (
    <div className={cn(
      'flex flex-col items-center justify-center',
      fullScreen ? 'min-h-screen' : 'py-8',
      className
    )}>
      <LoadingSpinner size={size} color={color} />
      {text && (
        <p className={cn(
          'mt-3 text-sm font-medium',
          colorClasses[color]
        )}>
          {text}
        </p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white bg-opacity-75 z-50 flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
}

// Component variants for different use cases
export function ButtonLoading({
  size = 'sm',
  className
}: {
  size?: 'sm' | 'md';
  className?: string;
}) {
  return (
    <LoadingSpinner
      size={size}
      color="white"
      className={cn('mr-2', className)}
    />
  );
}

export function PageLoading({ text = 'Loading...' }: { text?: string }) {
  return (
    <Loading
      size="lg"
      text={text}
      className="min-h-[400px]"
    />
  );
}

export function CardLoading({ className }: { className?: string }) {
  return (
    <div className={cn('p-4 space-y-4', className)}>
      <LoadingSkeleton className="h-48 w-full" />
      <LoadingSkeleton lines={2} />
      <LoadingSkeleton className="h-6 w-24" />
    </div>
  );
}

export function ProductCardLoading({ className }: { className?: string }) {
  return (
    <div className={cn('p-4 space-y-4', className)}>
      <LoadingSkeleton className="h-48 w-full rounded-lg" />
      <div className="space-y-2">
        <LoadingSkeleton className="h-4 w-3/4" />
        <LoadingSkeleton className="h-4 w-1/2" />
        <LoadingSkeleton className="h-6 w-20" />
      </div>
    </div>
  );
}

export function ListLoading({
  items = 5,
  className
}: {
  items?: number;
  className?: string;
}) {
  return (
    <div className={cn('space-y-4', className)}>
      {Array.from({ length: items }, (_, i) => (
        <div key={i} className="flex items-center space-x-4">
          <LoadingSkeleton className="h-12 w-12 rounded-full" />
          <div className="flex-1">
            <LoadingSkeleton lines={2} />
          </div>
        </div>
      ))}
    </div>
  );
}

export function TableLoading({
  rows = 5,
  columns = 4,
  className
}: {
  rows?: number;
  columns?: number;
  className?: string;
}) {
  return (
    <div className={cn('space-y-4', className)}>
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
          {Array.from({ length: columns }, (_, j) => (
            <LoadingSkeleton key={j} className="h-4" />
          ))}
        </div>
      ))}
    </div>
  );
}

export default Loading;