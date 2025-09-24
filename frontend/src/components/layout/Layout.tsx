/**
 * Main layout component
 * Wraps the entire application with header, footer, and common providers
 */

'use client';

import React, { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Header from './Header';
import Footer from './Footer';
import { ErrorBoundaryWrapper } from '@/components/ui/ErrorBoundary';
import { ToastProvider } from '@/components/ui/Toast';
import { Loading } from '@/components/ui/Loading';
import OfflineBanner from '@/components/ui/OfflineBanner';
import { OfflineProvider } from '@/providers/OfflineProvider';
import { useAuthStore } from '@/store/auth';
import { cn } from '@/lib/utils';

interface LayoutProps {
  children: React.ReactNode;
  className?: string;
  showHeader?: boolean;
  showFooter?: boolean;
  containerClassName?: string;
}

export function Layout({
  children,
  className,
  showHeader = true,
  showFooter = true,
  containerClassName
}: LayoutProps) {
  const pathname = usePathname();
  const { initialize, isInitializing } = useAuthStore();

  // Initialize auth state on app load
  useEffect(() => {
    initialize();
  }, [initialize]);

  // Pages that might have different layouts
  const isAuthPage = pathname?.startsWith('/login') || pathname?.startsWith('/register');
  const isCheckoutPage = pathname?.startsWith('/checkout');
  const isAdminPage = pathname?.startsWith('/admin');

  // Show loading while initializing auth
  if (isInitializing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loading size="lg" text="Loading..." />
      </div>
    );
  }

  return (
    <OfflineProvider>
      <ToastProvider>
        <ErrorBoundaryWrapper>
          <div className={cn('min-h-screen flex flex-col', className)}>
            {/* Offline Banner */}
            <OfflineBanner />

            {/* Header */}
            {showHeader && !isAdminPage && <Header />}

            {/* Main Content */}
            <main className={cn('flex-1', containerClassName)}>
              <ErrorBoundaryWrapper
                showDetails={process.env.NODE_ENV === 'development'}
              >
                {children}
              </ErrorBoundaryWrapper>
            </main>

            {/* Footer */}
            {showFooter && !isAuthPage && !isCheckoutPage && !isAdminPage && <Footer />}
          </div>
        </ErrorBoundaryWrapper>
      </ToastProvider>
    </OfflineProvider>
  );
}

// Specialized layout components for different page types
export function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <Layout showFooter={false} className="bg-gray-50">
      <div className="flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          {children}
        </div>
      </div>
    </Layout>
  );
}

export function CheckoutLayout({ children }: { children: React.ReactNode }) {
  return (
    <Layout showFooter={false} containerClassName="bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </div>
    </Layout>
  );
}

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <Layout showHeader={false} showFooter={false}>
      <div className="flex h-screen bg-gray-100">
        {/* Sidebar would go here */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Dashboard header would go here */}
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100">
            <div className="container mx-auto px-6 py-8">
              {children}
            </div>
          </main>
        </div>
      </div>
    </Layout>
  );
}

export function ContainerLayout({
  children,
  size = 'default',
  className
}: {
  children: React.ReactNode;
  size?: 'sm' | 'default' | 'lg' | 'xl' | 'full';
  className?: string;
}) {
  const containerSizes = {
    sm: 'max-w-3xl',
    default: 'max-w-7xl',
    lg: 'max-w-[1400px]',
    xl: 'max-w-[1600px]',
    full: 'max-w-none',
  };

  return (
    <div className={cn(
      'mx-auto px-4 sm:px-6 lg:px-8',
      containerSizes[size],
      className
    )}>
      {children}
    </div>
  );
}

export function PageLayout({
  children,
  title,
  description,
  breadcrumbs,
  actions,
  containerSize = 'default',
  className
}: {
  children: React.ReactNode;
  title?: string;
  description?: string;
  breadcrumbs?: React.ReactNode;
  actions?: React.ReactNode;
  containerSize?: 'sm' | 'default' | 'lg' | 'xl' | 'full';
  className?: string;
}) {
  return (
    <Layout>
      <ContainerLayout size={containerSize} className={cn('py-8', className)}>
        {/* Page Header */}
        {(title || breadcrumbs || actions) && (
          <div className="mb-8">
            {breadcrumbs && (
              <div className="mb-4">
                {breadcrumbs}
              </div>
            )}

            <div className="flex items-center justify-between">
              <div>
                {title && (
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    {title}
                  </h1>
                )}
                {description && (
                  <p className="text-gray-600 max-w-2xl">
                    {description}
                  </p>
                )}
              </div>

              {actions && (
                <div className="flex items-center space-x-4">
                  {actions}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Page Content */}
        {children}
      </ContainerLayout>
    </Layout>
  );
}

// Loading layout for pages
export function LoadingLayout({
  title = 'Loading...',
  description
}: {
  title?: string;
  description?: string;
}) {
  return (
    <Layout>
      <ContainerLayout className="py-16">
        <div className="text-center">
          <Loading size="lg" text={title} />
          {description && (
            <p className="mt-4 text-gray-600">{description}</p>
          )}
        </div>
      </ContainerLayout>
    </Layout>
  );
}

// Error layout for error pages
export function ErrorLayout({
  title = 'Something went wrong',
  description = 'An unexpected error occurred. Please try again.',
  actions
}: {
  title?: string;
  description?: string;
  actions?: React.ReactNode;
}) {
  return (
    <Layout>
      <ContainerLayout className="py-16">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            {title}
          </h1>
          <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
            {description}
          </p>
          {actions && (
            <div className="flex justify-center space-x-4">
              {actions}
            </div>
          )}
        </div>
      </ContainerLayout>
    </Layout>
  );
}

export default Layout;