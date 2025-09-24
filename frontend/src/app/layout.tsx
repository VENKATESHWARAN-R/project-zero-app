import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Layout from '@/components/layout/Layout'
import ErrorBoundary from '@/components/ui/ErrorBoundary'
import { AuthProvider } from '@/providers/AuthProvider'
import { ToastProvider } from '@/components/ui/Toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Project Zero Store',
  description: 'E-commerce demonstration platform built with Next.js',
  keywords: ['ecommerce', 'nextjs', 'react', 'typescript', 'demo'],
  authors: [{ name: 'Project Zero Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} antialiased`}>
        <ToastProvider>
          <ErrorBoundary>
            <AuthProvider>
              <Layout>
                {children}
              </Layout>
            </AuthProvider>
          </ErrorBoundary>
        </ToastProvider>
      </body>
    </html>
  );
}
