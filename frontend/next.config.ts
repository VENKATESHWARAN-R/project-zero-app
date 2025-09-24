import type { NextConfig } from "next";

// Only require bundle analyzer if not in test environment
const withBundleAnalyzer = process.env.NODE_ENV === 'test'
  ? (config: NextConfig) => config
  : require('@next/bundle-analyzer')({
      enabled: process.env.ANALYZE === 'true',
    });

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8004',
        pathname: '/images/**',
      },
      {
        protocol: 'https',
        hostname: 'example.com',
        pathname: '/images/**',
      },
    ],
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },
  env: {
    NEXT_PUBLIC_AUTH_API_URL: process.env.NEXT_PUBLIC_AUTH_API_URL,
    NEXT_PUBLIC_PRODUCTS_API_URL: process.env.NEXT_PUBLIC_PRODUCTS_API_URL,
    NEXT_PUBLIC_CART_API_URL: process.env.NEXT_PUBLIC_CART_API_URL,
  },
  experimental: {
    optimizePackageImports: ['lucide-react'],
    turbo: {
      rules: {
        '*.svg': {
          loaders: ['@svgr/webpack'],
          as: '*.js',
        },
      },
    },
  },
  webpack: (config) => {
    // Optimize bundle splitting
    config.optimization = {
      ...config.optimization,
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          default: {
            minChunks: 2,
            reuseExistingChunk: true,
          },
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: 10,
            chunks: 'all',
            enforce: true,
          },
          ui: {
            test: /[\\/]src[\\/]components[\\/]ui[\\/]/,
            name: 'ui-components',
            priority: 20,
            chunks: 'all',
            minChunks: 2,
          },
          common: {
            name: 'common',
            minChunks: 2,
            priority: 5,
            chunks: 'all',
            reuseExistingChunk: true,
          },
        },
      },
    };

    return config;
  },
};

export default withBundleAnalyzer(nextConfig);
